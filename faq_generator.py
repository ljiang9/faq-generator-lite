"""faq-generator-lite：从文档中识别定义/疑问/关键说明，生成问答对。

规则（无 LLM 时）：
- 疑问句（以 ?/？结尾的句子）直接作为问题，答案取其后一句；
- 定义句（"X 是指…"、"所谓 X，就是…"、"X，即…"）生成 "什么是 X？"；
- 输出统一为 JSON 数组 [{question, answer}]。
可选 LLM 输出更自然的问答 JSON。
"""

from __future__ import annotations

import json
import os
import re
import urllib.request

SENT_SPLIT = re.compile(r"(?<=[。！？!?\n])")
DEF_PATTERNS = [
    re.compile(r"([\u4e00-\u9fa5A-Za-z0-9]{2,12})\s*(?:是指|指的是|即|是一种)[，,:：]?\s*(.+)"),
    re.compile(r"所谓\s*([\u4e00-\u9fa5A-Za-z0-9]{2,12})[，,]\s*就是\s*(.+)"),
]
QUESTION_END = re.compile(r"[?？]\s*$")


def _sentences(text: str) -> list[str]:
    out = []
    for s in SENT_SPLIT.split(text):
        s = s.strip()
        if s:
            out.append(s)
    return out


def generate_faqs(text: str) -> list[dict]:
    """从文档提取问答对。"""
    sents = _sentences(text)
    faqs: list[dict] = []
    seen_q: set[str] = set()

    def add(q: str, a: str):
        q, a = q.strip(), a.strip()
        if q and a and q not in seen_q:
            seen_q.add(q)
            faqs.append({"question": q, "answer": a})

    for i, s in enumerate(sents):
        matched = False
        for pat in DEF_PATTERNS:
            m = pat.search(s)
            if m:
                term = m.group(1).strip()
                ans = m.group(2).strip().rstrip("。.")
                add(f"什么是{term}？", ans)
                matched = True
                break
        if matched:
            continue

        if QUESTION_END.search(s):
            ans = sents[i + 1] if i + 1 < len(sents) else s
            add(s.rstrip("？?"), ans.rstrip("。."))

    return faqs


def generate_faqs_llm(text: str, api_key: str | None = None,
                      base_url: str | None = None,
                      model: str | None = None) -> list[dict]:
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    base_url = (base_url or os.environ.get("OPENAI_BASE_URL")
                or "https://api.openai.com/v1").rstrip("/")
    model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise RuntimeError("未设置 OPENAI_API_KEY")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是文档问答生成器，输出严格 JSON 数组，每个元素 {question, answer}，不要解释。"},
            {"role": "user", "content": f"从下面文档提炼 5 个常见问答对：\n\n{text[:4000]}"},
        ],
        "temperature": 0.3,
    }
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"].strip().strip("`")
    if content.startswith("json"):
        content = content[4:].strip()
    return [{"question": str(x.get("question", "")),
             "answer": str(x.get("answer", ""))} for x in json.loads(content)]


def faqs(text: str, use_llm: bool = False) -> list[dict]:
    """统一入口。"""
    base = generate_faqs(text)
    if use_llm and os.environ.get("OPENAI_API_KEY"):
        try:
            llm = generate_faqs_llm(text)
            return base + llm
        except Exception as exc:
            print(f"[warn] LLM FAQ 失败，使用规则结果：{exc}")
    return base
