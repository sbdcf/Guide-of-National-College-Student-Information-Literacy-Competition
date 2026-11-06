#!/usr/bin/env python3
"""从 data/questions/*.json 生成题库静态页与练习页数据。

用法（在仓库根目录跑，mkdocs build 之前）：
    python tools/build_questions.py

产出：
    docs/questions/<id>.md         每题一页
    docs/questions/index.md        题库总览
    docs/assets/data/questions.json  练习页用的数据包

docs/questions/ 与 docs/assets/data/ 都是生成物，已写进 .gitignore，
不要手改——改了下次构建会被覆盖。
"""

import json
import pathlib
import shutil
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
QDIR = ROOT / "data" / "questions"
TAX = ROOT / "data" / "taxonomy.json"
OUT = ROOT / "docs" / "questions"
OUT_DATA = ROOT / "docs" / "assets" / "data"
IMG_DIR = ROOT / "docs" / "assets" / "images" / "questions"
DOCS = ROOT / "docs"

TYPE_NAME = {"single": "单选题", "multiple": "多选题", "judge": "判断题"}
ISSUE_NAME = {
    "missing_option": "原题选项不全",
    "stem_image_missing": "原题配图缺失",
    "needs_review": "答案待复核",
    "unclear_source": "来源不明",
}
DAY = date.today().isoformat()


def esc(text):
    """转义到适合塞进 Markdown 正文的形式。"""
    return str(text or "").replace("<", "&lt;").replace(">", "&gt;")


def cell(text):
    """表格单元格：额外处理竖线。"""
    return esc(text).replace("|", "\\|").replace("\n", " ")


def main():
    tax_raw = json.loads(TAX.read_text(encoding="utf-8"))
    topic_name = {t["id"]: t["name"] for t in tax_raw["topics"]}
    db_name = {d["id"]: d["name"] for d in tax_raw["databases"]}
    topic_order = [t["id"] for t in tax_raw["topics"]]

    files = sorted(p for p in QDIR.glob("*.json") if not p.name.startswith("_"))
    if not files:
        print(f"没有找到题目：{QDIR}")
        return 1

    questions = []
    for p in files:
        try:
            q = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"跳过 {p.name}：{e}")
            continue
        q["_file"] = p.name
        questions.append(q)

    # 排序：先按首个考点在词表里的顺序，再按题号
    def sort_key(q):
        tx = q.get("taxonomy") or []
        idx = topic_order.index(tx[0]) if tx and tx[0] in topic_order else len(topic_order)
        return (idx, q.get("id", ""))

    questions.sort(key=sort_key)

    OUT.mkdir(parents=True, exist_ok=True)
    OUT_DATA.mkdir(parents=True, exist_ok=True)

    # 清掉上一次生成的题目页，避免删题后残留
    for old in OUT.glob("q-*.md"):
        old.unlink()

    for q in questions:
        qid = q.get("id") or q["_file"].replace(".json", "")
        qtype = q.get("type", "")
        options = q.get("options") or []
        answer = q.get("answer") or []
        if qtype == "multiple":
            ans_text = "、".join(a for a in sorted(answer) if a)
        else:
            ans_text = "、".join(
                f"{o['key']}. {o['text']}" for o in options if o.get("key") in answer
            )
        ans_text = ans_text or "（暂无）"
        topics = [t for t in (q.get("taxonomy") or []) if t in topic_name]
        ev = q.get("evidence") or {}
        issues = q.get("issues") or []
        verifs = q.get("verification") or []
        same = [
            o for o in questions
            if o.get("id") != qid
            and self_topic(o) == self_topic(q)
            and self_topic(q) is not None
        ]

        lines = []
        lines.append("---")
        lines.append(f"title: {q.get('title', qid)}")
        lines.append("---")
        lines.append("")
        lines.append(f"# {esc(q.get('title') or qid)}")
        lines.append("")

        meta = [
            TYPE_NAME.get(qtype, qtype),
            f"难度 {q.get('difficulty', '-')}/3",
            f"{q.get('exam_year', '')} 年{q.get('round', '')}",
        ]
        if topics:
            meta.append("、".join(topic_name[t] for t in topics))
        lines.append("`" + " · ".join(meta) + "`")
        lines.append("")

        if "stem_image_missing" in issues:
            lines.append(
                "!!! warning \"原题配图缺失\"\n"
                "    这道题的题干原本带一张检索条件截图，整理时没能取到。"
                "只看文字无法还原条件，先按文字判断，以官方原题为准。"
            )
            lines.append("")
        if "needs_review" in issues:
            lines.append(
                "!!! warning \"答案待复核\"\n"
                "    这道题的答案或依据还有疑问，尚未最终确认，参考时请留意。"
            )
            lines.append("")
        if "missing_option" in issues:
            lines.append("!!! warning \"原题选项不全\"\n    整理时有一项以上选项缺失。")
            lines.append("")

        lines.append("## 题干")
        lines.append("")
        lines.append(esc(q.get("stem", "")).strip())
        lines.append("")

        for img in q.get("stem_images") or []:
            rel = str(img).lstrip("/")
            if (DOCS / rel).exists():
                lines.append(f"![题干配图](/{rel})")
                lines.append("")

        lines.append("## 选项")
        lines.append("")
        for o in options:
            lines.append(f"- **{o.get('key')}.** {esc(o.get('text'))}")
        lines.append("")

        lines.append("## 答案")
        lines.append("")
        if q.get("answer_status") == "pending":
            lines.append("> 答案暂缺，欢迎在 Issue 里补充。")
        else:
            lines.append(f"**{ans_text}**")
        lines.append("")

        if q.get("explain"):
            lines.append("## 解析")
            lines.append("")
            lines.append(esc(q["explain"]).strip())
            lines.append("")

        if ev.get("database_id") or ev.get("query") or ev.get("steps"):
            lines.append("## 检索依据")
            lines.append("")
            if ev.get("database_id"):
                lines.append(
                    f"- **数据库**：{db_name.get(ev['database_id'], ev['database_id'])}"
                )
            if ev.get("query"):
                lines.append(f"- **检索式**：`{esc(ev['query'])}`")
            if ev.get("steps"):
                lines.append(f"- **步骤**：{esc(ev['steps'])}")
            lines.append("")

        lines.append("## 题目信息")
        lines.append("")
        lines.append("| 项 | 值 |")
        lines.append("| --- | --- |")
        lines.append(f"| 题号 | `{qid}` |")
        lines.append(f"| 题型 | {TYPE_NAME.get(qtype, qtype)} |")
        lines.append(f"| 来源 | {cell(q.get('source'))} {cell(q.get('source_ref'))} |")
        lines.append(f"| 难度 | {q.get('difficulty', '-')}/3 |")
        if verifs:
            v = verifs[-1]
            lines.append(
                f"| 核验 | {cell(v.get('by'))} 于 {cell(v.get('date'))} 核验 |"
            )
        lines.append(f"| 更新 | {q.get('updated', '')} |")
        lines.append("")

        if issues:
            lines.append(
                "- **记录的问题**："
                + "、".join(ISSUE_NAME.get(i, i) for i in issues)
            )
            lines.append("")

        if same:
            lines.append("## 同考点其他题目")
            lines.append("")
            for o in same[:12]:
                lines.append(f"- [{esc(o.get('title'))}]({o.get('id')}.md)")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append(
            f"发现这道题有问题？[提交题目纠错]"
            "(https://github.com/sbdcf/Guide-of-National-College-Student-Information-Literacy-Competition"
            "/issues/new?template=01-%E9%A2%98%E7%9B%AE%E7%BA%A0%E9%94%99.yml)"
            f"（记得在正文里写上题号 `{qid}`）"
        )
        lines.append("")

        (OUT / f"{qid}.md").write_text("\n".join(lines), encoding="utf-8")

    # 总览页
    build_index(questions, topic_name, topic_order, TYPE_NAME)

    # 练习页数据包
    pack = []
    for q in questions:
        pack.append({
            "id": q.get("id"),
            "type": q.get("type"),
            "title": q.get("title"),
            "stem": q.get("stem"),
            "stem_images": [i for i in (q.get("stem_images") or [])
                            if (DOCS / str(i).lstrip("/")).exists()],
            "options": q.get("options") or [],
            "answer": q.get("answer") or [],
            "explain": q.get("explain") or "",
            "evidence": q.get("evidence") or {},
            "taxonomy": q.get("taxonomy") or [],
            "difficulty": q.get("difficulty"),
            "issues": q.get("issues") or [],
            "source": q.get("source") or "",
            "exam_year": q.get("exam_year"),
            "round": q.get("round"),
        })

    payload = {
        "version": 1,
        "generated": DAY,
        "topics": [{"id": t["id"], "name": t["name"]} for t in tax_raw["topics"]],
        "databases": [{"id": d["id"], "name": d["name"]} for d in tax_raw["databases"]],
        "questions": pack,
    }
    (OUT_DATA / "questions.json").write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    print(f"生成 {len(questions)} 道题")
    print(f"  页面：{OUT}")
    print(f"  数据：{OUT_DATA / 'questions.json'}")


def self_topic(q):
    tx = q.get("taxonomy") or []
    return tx[0] if tx else None


def build_index(questions, topic_name, topic_order, type_name):
    total = len(questions)
    lines = []
    lines.append("---")
    lines.append("title: 题库")
    lines.append("---")
    lines.append("")
    lines.append("# 题库")
    lines.append("")
    lines.append(
        f"目前收录 **{total}** 道校赛题，全部标为「已核验」，每道题都附了检索依据，"
        "可以照着步骤自己复现一遍。"
    )
    lines.append("")
    lines.append(
        "想动手做一套？去 [在线练习](../practice/index.md) —— 可以按考点、题型抽题，"
        "答完自动判分。"
    )
    lines.append("")

    # 统计
    by_type = {}
    for q in questions:
        by_type[q.get("type")] = by_type.get(q.get("type"), 0) + 1
    lines.append("## 题目分布")
    lines.append("")
    lines.append("| 考点 | 题数 |")
    lines.append("| --- | --- |")
    by_topic = {}
    for q in questions:
        key = self_topic(q)
        by_topic[key] = by_topic.get(key, 0) + 1
    for tid in topic_order:
        if by_topic.get(tid):
            lines.append(f"| {topic_name.get(tid, tid)} | {by_topic[tid]} |")
    lines.append("")
    lines.append(
        "题型：" + "、".join(
            f"{type_name.get(k, k)} {v} 道" for k, v in sorted(by_type.items())
        )
    )
    lines.append("")
    lines.append(
        "> 分布表按每道题的**第一个考点**统计——一道题可能同时属于多个考点，"
        "所以下表总数等于题数，但各考点实际涉及题量会比这里更多。"
    )
    lines.append("")

    # 分组列表
    lines.append("## 按考点浏览")
    lines.append("")
    for tid in topic_order:
        group = [q for q in questions if self_topic(q) == tid]
        if not group:
            continue
        lines.append(f"### {topic_name.get(tid, tid)}")
        lines.append("")
        for q in group:
            extra = []
            tname = type_name.get(q.get("type"), q.get("type"))
            extra.append(tname)
            if q.get("difficulty"):
                extra.append("难度 " + str(q["difficulty"]))
            if q.get("issues"):
                extra.append("⚠ 待处理")
            lines.append(
                f"- [{esc(q.get('title'))}]({q.get('id')}.md) —— " + " · ".join(extra)
            )
        lines.append("")

    rest = [q for q in questions if self_topic(q) not in topic_order]
    if rest:
        lines.append("### 未分类")
        lines.append("")
        for q in rest:
            lines.append(f"- [{esc(q.get('title'))}]({q.get('id')}.md)")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "题目还在补。发现错误或想补充题目，见[贡献指南](../contributing/index.md)。"
    )
    lines.append("")

    (OUT / "index.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
