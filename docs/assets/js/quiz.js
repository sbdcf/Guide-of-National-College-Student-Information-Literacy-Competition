/* 在线练习。纯前端，无外部依赖，离线也能跑（只要站点文件在本地）。 */
(function () {
  "use strict";

  var TYPE_LABEL = { single: "单选题", multiple: "多选题", judge: "判断题" };
  var ISSUE_LABEL = {
    stem_image_missing: "原题配图缺失",
    needs_review: "答案待复核",
    missing_option: "选项不全",
    unclear_source: "来源不明"
  };
  var STORE_KEY = "ai-info-quiz-history";

  var data = null;
  var root = null;
  var deck = [];
  var answers = [];
  var cursor = 0;

  function h(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function topicName(id) {
    var t = (data.topics || []).filter(function (x) { return x.id === id; })[0];
    return t ? t.name : id;
  }

  function stemText(q) {
    return (q.stem || "").trim();
  }

  function sameSet(a, b) {
    if (a.length !== b.length) return false;
    var sa = a.slice().sort().join(",");
    var sb = b.slice().sort().join(",");
    return sa === sb;
  }

  function isCorrect(i) {
    return sameSet(answers[i] || [], deck[i].answer || []);
  }

  function clearRoot() {
    while (root.firstChild) root.removeChild(root.firstChild);
  }

  /* ---------- 设置界面 ---------- */

  function renderSetup() {
    clearRoot();

    var counts = { single: 0, multiple: 0, judge: 0 };
    data.questions.forEach(function (q) { counts[q.type] = (counts[q.type] || 0) + 1; });

    var panel = h("div", "quiz-panel");
    panel.appendChild(h("h3", null, "选题"));
    panel.appendChild(h("p", "quiz-result-line",
      "题库共 " + data.questions.length + " 题，全部为已核验校赛题。"));

    var fsType = h("fieldset", "quiz-fieldset");
    fsType.appendChild(h("legend", null, "题型"));
    var chipsType = h("div", "quiz-chips");
    ["single", "multiple", "judge"].forEach(function (t) {
      chipsType.appendChild(chip("type", t, TYPE_LABEL[t] + "（" + (counts[t] || 0) + "）", true));
    });
    fsType.appendChild(chipsType);
    panel.appendChild(fsType);

    var topicCounts = {};
    data.questions.forEach(function (q) {
      (q.taxonomy || []).forEach(function (t) {
        topicCounts[t] = (topicCounts[t] || 0) + 1;
      });
    });

    var fsTopic = h("fieldset", "quiz-fieldset");
    fsTopic.appendChild(h("legend", null, "考点"));
    var chipsTopic = h("div", "quiz-chips");
    (data.topics || []).forEach(function (t) {
      if (!topicCounts[t.id]) return;
      chipsTopic.appendChild(
        chip("topic", t.id, t.name + "（" + topicCounts[t.id] + "）", true)
      );
    });
    fsTopic.appendChild(chipsTopic);
    panel.appendChild(fsTopic);

    var fsCount = h("fieldset", "quiz-fieldset");
    fsCount.appendChild(h("legend", null, "题量"));
    var selCount = h("select", "quiz-select");
    [10, 20, 30, 0].forEach(function (n) {
      var o = h("option", null, n === 0 ? "全部" : n + " 题");
      o.value = String(n);
      if (n === 20) o.selected = true;
      selCount.appendChild(o);
    });
    fsCount.appendChild(selCount);
    panel.appendChild(fsCount);

    var fsOrder = h("fieldset", "quiz-fieldset");
    fsOrder.appendChild(h("legend", null, "顺序"));
    var selOrder = h("select", "quiz-select");
    var oRandom = h("option", null, "随机打乱");
    oRandom.value = "random";
    var oSeq = h("option", null, "按题库顺序");
    oSeq.value = "seq";
    selOrder.appendChild(oRandom);
    selOrder.appendChild(oSeq);
    fsOrder.appendChild(selOrder);
    panel.appendChild(fsOrder);

    var acts = h("div", "quiz-actions");
    var btnStart = h("button", "quiz-btn", "开始练习");
    btnStart.type = "button";
    btnStart.addEventListener("click", function () {
      start(selCount.value, selOrder.value);
    });
    acts.appendChild(btnStart);
    panel.appendChild(acts);

    root.appendChild(panel);

    var history = loadHistory();
    if (history.length) {
      var hp = h("div", "quiz-panel");
      hp.appendChild(h("h3", null, "最近记录"));
      history.slice(0, 5).forEach(function (r) {
        hp.appendChild(h("div", "quiz-result-line",
          r.date + " · " + r.right + "/" + r.total + " · 正确率 " +
          Math.round((r.right / r.total) * 100) + "%"));
      });
      var btnClear = h("button", "quiz-btn quiz-btn--ghost", "清空记录");
      btnClear.type = "button";
      btnClear.addEventListener("click", function () {
        try { window.localStorage.removeItem(STORE_KEY); } catch (e) {}
        renderSetup();
      });
      var ha = h("div", "quiz-actions");
      ha.appendChild(btnClear);
      hp.appendChild(ha);
      root.appendChild(hp);
    }
  }

  function chip(group, value, label, checked) {
    var wrap = h("label", "quiz-chip");
    var input = document.createElement("input");
    input.type = "checkbox";
    input.value = value;
    input.checked = !!checked;
    input.dataset.group = group;
    wrap.appendChild(input);
    wrap.appendChild(document.createTextNode(label));
    return wrap;
  }

  function pickedValues(group) {
    return Array.prototype.slice
      .call(root.querySelectorAll('input[data-group="' + group + '"]:checked'))
      .map(function (i) { return i.value; });
  }

  /* ---------- 出题 ---------- */

  function start(countValue, orderValue) {
    var types = pickedValues("type");
    var topics = pickedValues("topic");

    if (!types.length || !topics.length) {
      window.alert("至少选一个题型和一个考点。");
      return;
    }

    var pool = data.questions.filter(function (q) {
      if (types.indexOf(q.type) < 0) return false;
      var tx = q.taxonomy || [];
      return tx.some(function (t) { return topics.indexOf(t) >= 0; });
    });

    if (!pool.length) {
      window.alert("这个组合下没有题目，换一组条件试试。");
      return;
    }

    if (orderValue === "random") pool = shuffle(pool);

    var n = parseInt(countValue, 10);
    if (n > 0) pool = pool.slice(0, n);

    deck = pool;
    answers = deck.map(function () { return []; });
    cursor = 0;
    renderQuestion();
  }

  function renderQuestion() {
    clearRoot();
    var q = deck[cursor];
    var multi = q.type === "multiple";

    var panel = h("div", "quiz-panel");

    var head = h("div", "quiz-progress");
    var bits = [
      "第 " + (cursor + 1) + " / " + deck.length + " 题",
      TYPE_LABEL[q.type] || q.type
    ];
    if (q.difficulty) bits.push("难度 " + q.difficulty);
    if (q.taxonomy && q.taxonomy.length) bits.push(topicName(q.taxonomy[0]));
    head.textContent = bits.join(" · ");
    panel.appendChild(head);

    if (q.issues && q.issues.length) {
      var flag = h("p", "quiz-result-line");
      q.issues.forEach(function (i) {
        flag.appendChild(h("span", "quiz-flag", ISSUE_LABEL[i] || i));
      });
      panel.appendChild(flag);
    }

    var stem = h("div", "quiz-stem", stemText(q));
    panel.appendChild(stem);

    (q.stem_images || []).forEach(function (src) {
      var img = document.createElement("img");
      img.src = "../" + String(src).replace(/^\/+/, "");
      img.alt = "题干配图";
      stem.appendChild(img);
    });

    var opts = h("div", "quiz-options");
    (q.options || []).forEach(function (o) {
      var label = h("label", "quiz-opt");
      if ((answers[cursor] || []).indexOf(o.key) >= 0) label.classList.add("is-picked");

      var input = document.createElement("input");
      input.type = multi ? "checkbox" : "radio";
      input.name = "q-" + cursor;
      input.value = o.key;
      input.checked = (answers[cursor] || []).indexOf(o.key) >= 0;
      label.appendChild(input);

      label.appendChild(h("span", "quiz-opt-key", o.key + "."));
      label.appendChild(h("span", "quiz-opt-text", o.text));

      input.addEventListener("change", function () {
        var cur = answers[cursor] || [];
        if (multi) {
          var idx = cur.indexOf(o.key);
          if (idx >= 0) cur.splice(idx, 1);
          else cur.push(o.key);
          answers[cursor] = cur;
          label.classList.toggle("is-picked", cur.indexOf(o.key) >= 0);
        } else {
          answers[cursor] = [o.key];
          Array.prototype.slice.call(opts.children).forEach(function (c) {
            c.classList.remove("is-picked");
          });
          label.classList.add("is-picked");
        }
      });

      opts.appendChild(label);
    });
    panel.appendChild(opts);

    if (multi) {
      var hint = h("p", "quiz-progress", "多选题：选完记得看是不是都选全了。");
      panel.appendChild(hint);
    }

    var acts = h("div", "quiz-actions");
    var btnPrev = h("button", "quiz-btn quiz-btn--ghost", "上一题");
    btnPrev.type = "button";
    btnPrev.disabled = cursor === 0;
    btnPrev.addEventListener("click", function () {
      cursor -= 1;
      renderQuestion();
    });
    acts.appendChild(btnPrev);

    var btnNext = h("button", "quiz-btn", cursor === deck.length - 1 ? "交卷" : "下一题");
    btnNext.type = "button";
    btnNext.addEventListener("click", function () {
      if (cursor === deck.length - 1) {
        renderResult();
      } else {
        cursor += 1;
        renderQuestion();
      }
    });
    acts.appendChild(btnNext);

    var btnQuit = h("button", "quiz-btn quiz-btn--ghost", "退出");
    btnQuit.type = "button";
    btnQuit.addEventListener("click", function () {
      if (window.confirm("退出后这次作答不会保留，确定吗？")) renderSetup();
    });
    acts.appendChild(btnQuit);

    panel.appendChild(acts);
    root.appendChild(panel);
  }

  /* ---------- 结果 ---------- */

  function renderResult() {
    clearRoot();
    var right = 0;
    deck.forEach(function (q, i) { if (isCorrect(i)) right += 1; });

    var panel = h("div", "quiz-panel");
    panel.appendChild(h("h3", null, "结果"));
    var score = h("div", "quiz-score", right + " / " + deck.length);
    panel.appendChild(score);
    panel.appendChild(h("p", "quiz-result-line",
      "正确率 " + Math.round((right / deck.length) * 100) + "%"));

    var acts = h("div", "quiz-actions");
    var wrongIdx = deck.map(function (_, i) { return i; })
      .filter(function (i) { return !isCorrect(i); });

    if (wrongIdx.length) {
      var btnRedo = h("button", "quiz-btn", "只重做错的 " + wrongIdx.length + " 题");
      btnRedo.type = "button";
      btnRedo.addEventListener("click", function () {
        deck = wrongIdx.map(function (i) { return deck[i]; });
        answers = deck.map(function () { return []; });
        cursor = 0;
        renderQuestion();
      });
      acts.appendChild(btnRedo);
    } else {
      panel.appendChild(h("p", "quiz-result-line", "全对。"));
    }

    var btnAgain = h("button", "quiz-btn quiz-btn--ghost", "再练一套");
    btnAgain.type = "button";
    btnAgain.addEventListener("click", function () { renderSetup(); });
    acts.appendChild(btnAgain);
    panel.appendChild(acts);
    root.appendChild(panel);

    saveHistory(right, deck.length);

    var review = h("div", "quiz-panel");
    review.appendChild(h("h3", null, "逐题回顾"));
    deck.forEach(function (q, i) {
      var ok = isCorrect(i);
      var item = h("div", "quiz-review-item quiz-review");

      var line = h("div");
      line.appendChild(h("span", ok ? "quiz-judge-ok" : "quiz-judge-no", ok ? "✓ " : "✗ "));
      line.appendChild(document.createTextNode((i + 1) + "． " + (q.title || stemText(q))));
      item.appendChild(line);

      var mine = (answers[i] || []).slice().sort().join("") || "未作答";
      var rightKeys = (q.answer || []).slice().sort().join("");
      item.appendChild(h("div", null, "你的答案：" + mine + "　正确答案：" + rightKeys));

      if (q.explain) {
        item.appendChild(h("div", "quiz-explain", q.explain));
      }

      var link = h("a", null, "查看题目详情 →");
      link.href = "../questions/" + q.id + "/";
      var wrap = h("div");
      wrap.appendChild(link);
      item.appendChild(wrap);

      review.appendChild(item);
    });
    root.appendChild(review);
  }

  /* ---------- 记录 ---------- */

  function loadHistory() {
    try {
      return JSON.parse(window.localStorage.getItem(STORE_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function saveHistory(right, total) {
    try {
      var list = loadHistory();
      var d = new Date();
      var iso = d.getFullYear() + "-" +
        ("0" + (d.getMonth() + 1)).slice(-2) + "-" +
        ("0" + d.getDate()).slice(-2);
      list.unshift({ date: iso, right: right, total: total });
      window.localStorage.setItem(STORE_KEY, JSON.stringify(list.slice(0, 20)));
    } catch (e) {}
  }

  /* ---------- 入口 ---------- */

  function init() {
    var app = document.getElementById("quiz-app");
    if (!app || app.dataset.ready === "1") return;
    app.dataset.ready = "1";
    root = app;
    root.dataset.ready = "1";

    var url = app.dataset.src;
    fetch(url)
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (payload) {
        data = payload;
        renderSetup();
      })
      .catch(function (err) {
        clearRoot();
        root.appendChild(h("p", "quiz-error",
          "题库数据加载失败（" + err.message + "）。可能是直接用 file:// 打开的本站，" +
          "那样浏览器不允许读取本地数据，请通过网页访问。"));
      });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
