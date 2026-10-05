"""faq-generator-lite 命令行入口。

用法示例：
    python3 cli.py --file doc.txt
    python3 cli.py --text "缓存是指临时存储数据的机制。什么是 CDN？CDN 是内容分发网络。它能加速访问。"
"""

from __future__ import annotations

import argparse
import json
import sys

from faq_generator import faqs


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="faq-generator-lite",
        description="从文档识别定义/疑问，生成 FAQ 问答对 JSON（可选 LLM）",
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="直接传入文档文本")
    src.add_argument("--file", help="从文本文件读取")
    p.add_argument("--llm", action="store_true", help="追加 LLM 问答对（需 OPENAI_API_KEY）")
    p.add_argument("--pretty", action="store_true", help="美化打印 JSON")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    text = args.text if args.text else open(args.file, encoding="utf-8").read()
    result = faqs(text, use_llm=args.llm)
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
