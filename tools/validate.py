#!/usr/bin/env python3
"""题库格式校验。

用法：
    python tools/validate.py                # 校验 data/questions/
    python tools/validate.py 某个目录        # 校验指定目录
退出码 0 表示没有错误（警告不算错），1 表示有错误。

设计原则：
- 错误 = 构建会挂或数据自相矛盾，必须改
- 警告 = 大概率有问题但可能是合法的（如题干重复），交人工判断
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOCAB_PATH = ROOT / "data" / "taxonomy.json"
DOCS = ROOT / "docs"

TYPES = {"single", "multiple", "judge"}
ANSWER_STATUS = {"pending", "verified", "disputed", "expired"}
ISSUES = {"missing_option", "stem_image_missing", "needs_review", "unclear_source"}
VERIFY_RESULT = {"confirmed", "changed", "not_found"}

REQUIRED = [
    "schema_version", "id", "type", "title", "stem", "options",
    "answer", "answer_status", "evidence", "taxonomy", "exam_year",
    "source", "created", "updated",
]

MAX_IMAGE_KB = 300
MAX_IMAGE_WIDTH = 1200


def load_vocab():
    with VOCAB_PATH.open(encoding="utf-8") as f:
        v = json.load(f)
    return {
        "taxonomy": {t["id"] for t in v.get("topics", [])},
        "database": {d["id"] for d in v.get("databases", [])},
        "round": set(v.get("rounds", [])),
    }


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "questions"
    if not target.is_absolute():
        target = ROOT / target

    if not target.is_dir():
        print(f"目录不存在: {target}")
        return 1

    vocab = load_vocab()
    errors, warnings = [], []
    seen_ids, seen_stems = {}, {}
    files = sorted(p for p in target.glob("*.json") if not p.name.startswith("_"))

    if not files:
        print(f"{target} 下没有 JSON 文件")
        return 1

    for path in files:
        rel = path.name

        def err(msg):
            errors.append(f"[{rel}] {msg}")

        def warn(msg):
            warnings.append(f"[{rel}] {msg}")

        try:
            q = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            err(f"JSON 解析失败：{e}")
            continue

        if not isinstance(q, dict):
            err("顶层不是对象")
            continue

        # 必填字段
        for k in REQUIRED:
            if k not in q:
                err(f"缺少字段 {k}")

        # id 与文件名一致
        qid = q.get("id", "")
        if qid and qid != path.stem:
            err(f"id 与文件名不一致：id={qid}，文件={path.stem}")
        if qid in seen_ids:
            err(f"id 重复，与 {seen_ids[qid]} 撞号")
        else:
            seen_ids[qid] = rel

        if q.get("schema_version") != 1:
            err(f"schema_version 应为 1，实际 {q.get('schema_version')!r}")

        # 题型
        qtype = q.get("type")
        if qtype not in TYPES:
            err(f"type 非法：{qtype!r}")

        options = q.get("options") or []
        keys = [o.get("key") for o in options if isinstance(o, dict)]
        if len(keys) != len(set(keys)):
            err("选项 key 重复")
        for o in options:
            if not isinstance(o, dict) or not str(o.get("text", "")).strip():
                err(f"选项文本为空：{o!r}")
        if qtype in {"single", "multiple"} and len(options) < 2:
            err(f"{qtype} 至少需要 2 个选项，实际 {len(options)}")
        if qtype == "judge" and len(options) != 2:
            err(f"judge 必须恰好 2 个选项，实际 {len(options)}")

        # 答案
        answer = q.get("answer")
        if not isinstance(answer, list):
            err("answer 必须是数组")
            answer = []
        missing = [a for a in answer if a not in keys]
        if missing:
            err(f"答案 {missing} 不在选项里")
        if qtype == "single" and len(answer) != 1:
            err(f"single 必须有且仅有 1 个答案，实际 {len(answer)}")
        if qtype == "multiple" and len(answer) < 2:
            err(f"multiple 至少 2 个答案，实际 {len(answer)}")
        if qtype == "judge" and len(answer) != 1:
            err(f"judge 必须有且仅有 1 个答案，实际 {len(answer)}")

        # 答案状态
        status = q.get("answer_status")
        if status not in ANSWER_STATUS:
            err(f"answer_status 非法：{status!r}")
        if status in {"verified", "disputed", "expired"} and not answer:
            err(f"answer_status={status} 但 answer 为空")
        verifs = q.get("verification") or []
        if not isinstance(verifs, list):
            err("verification 必须是数组")
            verifs = []
        if status == "verified" and not verifs:
            err("answer_status=verified 但没有 verification 记录")
        for v in verifs:
            if v.get("result") not in VERIFY_RESULT:
                err(f"verification.result 非法：{v.get('result')!r}")

        # 题目缺陷
        for i in q.get("issues") or []:
            if i not in ISSUES:
                err(f"issues 非法值：{i!r}")

        # 词表
        for t in q.get("taxonomy") or []:
            if t not in vocab["taxonomy"]:
                err(f"taxonomy 不在词表里：{t!r}")
        ev = q.get("evidence") or {}
        dbid = ev.get("database_id")
        if dbid and dbid not in vocab["database"]:
            err(f"evidence.database_id 不在词表里：{dbid!r}")
        if answer and not dbid:
            warn("有答案但 evidence.database_id 为空")
        if answer and not str(ev.get("steps", "")).strip():
            warn("有答案但 evidence.steps 为空")
        rnd = q.get("round")
        if rnd and rnd not in vocab["round"]:
            err(f"round 不在词表里：{rnd!r}")

        # 文本
        if not str(q.get("stem", "")).strip():
            err("stem 为空")
        if not str(q.get("title", "")).strip():
            err("title 为空")

        # 图片
        for img in q.get("stem_images") or []:
            p = DOCS / str(img).lstrip("/")
            if not p.exists():
                err(f"图片不存在：{img}")
            elif p.stat().st_size > MAX_IMAGE_KB * 1024:
                err(f"图片超过 {MAX_IMAGE_KB}KB：{img}")

        # 题干查重
        stem = str(q.get("stem", "")).strip()
        if stem:
            norm = "".join(stem.split())
            if norm in seen_stems and seen_stems[norm] != rel:
                warn(f"题干与 {seen_stems[norm]} 完全相同")
            else:
                seen_stems[norm] = rel

    print(f"校验目录：{target}")
    print(f"题目数：{len(files)}")
    for w in warnings:
        print(f"警告 {w}")
    for e in errors:
        print(f"错误 {e}")
    print(f"\n结果：{len(errors)} 个错误，{len(warnings)} 个警告")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
