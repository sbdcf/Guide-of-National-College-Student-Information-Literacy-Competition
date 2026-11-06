# 贡献指南

这个站点的内容靠大家一点点补起来。**你不需要会写代码**，甚至不需要装 Git——所有操作都能在浏览器里完成。

先看你要做的是哪一类事：

| 你想做的事 | 难度 | 去哪儿 |
| --- | --- | --- |
| 报告一个错误（错字、失效链接、答案有问题） | ★ | [开 Issue](https://github.com/sbdcf/Guide-of-National-College-Student-Information-Literacy-Competition/issues/new/choose) |
| 补一道题 | ★★ | 网页上传一个 JSON 文件 |
| 写一段经验、补考点说明 | ★★ | 网页编辑 Markdown |
| 批量整理、改结构 | ★★★ | 提 Pull Request（需要会 Git） |

---

## 方式一：开 Issue（最快）

点上面表格里的链接，会看到几个模板，选一个填就行。

**报错请写清三件事**：

1. 哪个页面、哪道题（贴链接）
2. 哪里错了
3. 正确的内容是什么，加一句你的依据

反面例子：「题库里第 23 题答案不对」——维护者得先猜是哪份题库的第 23 题。
正面例子：「`/bank/q/q-0023/` 答案写的是 C，我在 CNKI 用 `主题=生态安全格局 AND 单位=浙江大学` 检索，被引最高的一篇是《乡村人居---策略》，应该是 B。链接：[…]」

---

## 方式二：网页上传题目（推荐第一次贡献走这条）

### 1. 打开题库目录

到仓库的 [`data/questions/`](https://github.com/sbdcf/Guide-of-National-College-Student-Information-Literacy-Competition/tree/main/data/questions) 目录。

### 2. 新建文件

右上角 **Add file → Create new file**。

文件名随意但要唯一，建议 `q-tmp-你的拼音-序号.json`，例如 `q-tmp-zhangsan-1.json`。维护者合并时会改成正式编号。

### 3. 粘贴模板

把 [_template.json](https://github.com/sbdcf/Guide-of-National-College-Student-Information-Literacy-Competition/blob/main/data/questions/_template.json) 的内容整段贴进去，然后逐个字段改。

### 4. 关键一步：不要直接提交到 main

页面底部有两个选项：

- ⬜ Commit directly to the `main` branch ← **别选这个**
- ⬛ **Create a new branch for this commit and start a pull request** ← 选这个

然后点 **Propose changes** → **Create pull request**。

直接提交到 `main` 会跳过审核，也会让构建失败（维护者要手工回滚）。

### 5. 等审核

见下面「审核之后会发生什么」。

---

## 一道题长什么样

```json
{
  "schema_version": 1,
  "id": "q-tmp-zhangsan-1",
  "type": "single",
  "title": "ISBN 与中图法归类",
  "stem": "大学生小王在四川省图书馆检索系统找到一本 ISBN 号为 978-7-111-56817-9 的书，根据《中国图书馆分类法》，这本书应归入以下哪一类？",
  "stem_images": [],
  "options": [
    { "key": "A", "text": "工业技术" },
    { "key": "B", "text": "文化、科学、教育、体育" },
    { "key": "C", "text": "交通运输" },
    { "key": "D", "text": "文学" }
  ],
  "answer": ["A"],
  "answer_status": "pending",
  "issues": [],
  "explain": "以 TP 开头的分类号属于工业技术。",
  "evidence": {
    "database_id": "nlc-opac",
    "query": "978-7-111-56817-9",
    "steps": "在国家图书馆联机目录按 ISBN 检索 → 查看分类号 TP311 → 对照中图法简表"
  },
  "verification": [],
  "taxonomy": ["t-ccl"],
  "exam_year": 2026,
  "round": "校赛",
  "source": "信息素养试题整理（三）",
  "source_ref": "第 1 题",
  "difficulty": 2,
  "duplicate_of": null,
  "contributor": "张三",
  "created": "2026-11-05",
  "updated": "2026-11-05"
}
```

### 字段说明

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `schema_version` | ✅ | 固定写 `1`，格式改版时才会变 |
| `id` | ✅ | 文件里用 `q-tmp-xxx`，正式编号由维护者分配 |
| `type` | ✅ | 只能是 `single`（单选）/ `multiple`（多选）/ `judge`（判断） |
| `title` | ✅ | 一句话概括，用于列表和搜索结果，别直接截题干 |
| `stem` | ✅ | 题干纯文本。**逐字照抄，不要自己改写** |
| `stem_images` | | 题干配图的路径数组，没有就写 `[]` |
| `options` | ✅ | 选项数组。判断题固定两项：`A. 正确` / `B. 错误` |
| `answer` | ✅ | 答案数组，**填选项的 key**，比如 `["B"]`、`["A","C"]`（判断题写 `["A"]` / `["B"]`，不要写「正确」）。不知道就写 `[]`，配套 `answer_status: "pending"` |
| `answer_status` | ✅ | `pending` 待答 / `verified` 已核验 / `disputed` 有争议 / `expired` 已过期 |
| `issues` | | 题目本身的缺陷：`missing_option` 选项缺项、`stem_image_missing` 原题配图没取到、`needs_review` 待复核、`unclear_source` 来源不明 |
| `explain` | | 讲「**为什么**是这个答案」。写规则、写知识点 |
| `evidence` | ✅ | 讲「**怎么查**出来的」，见下 |
| `verification` | | 核验记录 `{date, by, result}`，`result` 取 `confirmed` / `changed` / `not_found` |
| `taxonomy` | ✅ | 考点 id 数组，**只能填词表里的**，见 [`data/taxonomy.json`](https://github.com/sbdcf/Guide-of-National-College-Student-Information-Literacy-Competition/blob/main/data/taxonomy.json) |
| `exam_year` | ✅ | 这道题出自哪一年的比赛 |
| `round` | | `校赛` / `省赛` / `全国联赛` |
| `source` | ✅ | 文档级来源，比如「信息素养试题整理（三）」 |
| `source_ref` | | 原文第几题，用于勘误沟通 |
| `difficulty` | | 1 简单 / 2 中等 / 3 难 |
| `duplicate_of` | | 和已有题目重复时，填那题的 id |
| `contributor` | | 你想展示的名字或 GitHub 昵称 |
| `created` / `updated` | ✅ | 日期，`YYYY-MM-DD`。`updated` 维护者合并时会改 |

### 三个最容易踩的坑

**1. `answer` 不知道就留空，不要瞎填。**

填空 + `"answer_status": "pending"`，这题照样能收。填一个错的答案，比空着糟糕得多——同学会照着背。

**2. `evidence` 必须写。**

这套题绝大多数要真的去数据库里查，答案会随数据库更新而失效。所以每题都要能回答「**哪个库、什么检索式、看到什么**」：

```json
"evidence": {
  "database_id": "cnki",          // 受控值：cnki / wanfang / nlc-opac / gov-open 等
  "query": "主题=生态安全 AND 单位=浙江大学",
  "steps": "按被引排序 → 取第一篇 → 记录标题与作者"
}
```

`explain` 和 `evidence.steps` 别混：**`explain` 写「为什么」，`steps` 写「怎么查」**。

**3. `taxonomy` 只能填词表里的 id。**

不要写「中图法」「中国图书馆分类法」这种自由文本——同一个概念会冒出三种写法，筛选器当场报废。词表在 `data/taxonomy.json`，没有合适的就先空着，在 PR 里说一声。

**4. 判断题的 `answer` 填 `A` / `B`，不要填「正确」「错误」。**

判断题的选项是固定的两项：`{"key": "A", "text": "正确"}`、`{"key": "B", "text": "错误"}`。`answer` 里放的永远是**选项 key**，所以对的是 `["A"]`，错的是 `["B"]`。写了「正确」会在 CI 里报「答案不在选项里」。

---

## 题目页是自动生成的，别手改

题库里每一页（`/questions/xxx/`）都是构建时由 `tools/build_questions.py` 从 `data/questions/*.json` 生成的，仓库里没有这些 Markdown 文件。**想改题目内容，改 JSON**——改页面会被下次构建覆盖。

页面上那些「同考点其他题目」、分布统计、在线练习用的数据包，全都是从 JSON 算出来的。

---

## 图片怎么传

题目截图（检索结果、界面截图）走这条：

1. 文件名：`<题目id>-1.webp`，例：`q-tmp-zhangsan-1-1.webp`
2. 宽度不超过 1200px，单张不超过 300KB
3. 传到 `docs/assets/questions/` 目录
4. 在 `stem_images` 里写 `/assets/questions/q-tmp-zhangsan-1-1.webp`

**不会压图？别折腾了**——把原图发给维护者（微信群/Issue 附件都行），对方会压缩入库。

---

## 提交前自查

- [ ] 这确实是**本赛事**的题（不是通用信息素养练习题、不是公务员行测题）
- [ ] 题干和选项**逐字**照抄，一个选项都没漏（尤其别漏 B）
- [ ] `JSON` 能过格式检查——最省事的办法是复制到任何一个 JSON 校验网站看一眼
- [ ] 答案和 `evidence` 对得上
- [ ] 截图里没有别人的姓名、学号、机构水印
- [ ] 搜过题库，这题没进过库

---

## 审核之后会发生什么

1. **CI 自动检查**（几十秒）。它会跑格式校验。红了先自己看一眼报错——多半是少个逗号、或者 `type` 写成了 `single_choice`。红叉不等于你写错了内容。
2. **维护者人工看一遍**：题目本身对不对、依据够不够、有没有和已有题重复。
3. **分配正式编号**：`q-tmp-zhangsan-1` 会变成 `q-0023`，文件名跟着改，你不需要动手。
4. **合并上线**，几分钟后题目页自动出现。

!!! note "看到「等待批准」不是被拒"
    第一次给这个仓库提 PR 的人，GitHub 会要求维护者手动点一次批准，这是全站统一的安全策略。你会看到 PR 停在 `Awaiting approval` / `待批准`，正常流程，不是有人卡你。

---

## 请不要

- **搬运官方付费培训资料、教材原文**。我们不是搬运站。
- **提交带个人信息的截图**：姓名、学号、手机号、机构水印，看到就得上马赛克。
- **一次塞五十题**。维护者审不动，PR 会躺很久。十题以内一次最好。
- **改别人的题不打招呼**。觉得别人的答案错了——开 Issue 讨论，别直接改。

---

## 关于署名

`contributor` 字段会显示在题目页上。不想署名就留空，没人会追问。

题目本身的权利归原作者和赛事主办方，这里是**学习交流性质的学生整理**，不用于商业用途。如果你认为某道题的收录不妥，[开个 Issue](https://github.com/sbdcf/Guide-of-National-College-Student-Information-Literacy-Competition/issues/new/choose) 说一声，我们会撤下。
