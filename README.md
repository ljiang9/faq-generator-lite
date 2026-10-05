# faq-generator-lite

零依赖的**文档转 FAQ 工具**：从一篇文档里自动识别定义句（"X 是指……"、"所谓 X，就是……"）和疑问句，生成 `{question, answer}` 问答对 JSON。可选接入 LLM 提炼更多自然问答；没有 key 时本地规则已能产出可用 FAQ。

## 功能简介

- 识别定义句：`X 是指…`、`X 是…`、`所谓 X，就是…` → 生成「什么是 X？」。
- 识别疑问句：以 `？/?` 结尾的句子作为问题，后一句作为答案。
- 自动去重，输出标准 JSON 数组。
- 可选 LLM 输出更自然的问答。

## 快速开始

```bash
python3 cli.py --file doc.txt --pretty

python3 cli.py --text "缓存是指临时存储数据的机制。什么是 CDN？CDN 是内容分发网络。"
```

输出形如：

```json
[
  {"question": "什么是缓存？", "answer": "临时存储数据以加快后续访问的机制"}
]
```

## 无 API key 如何运行

本项目**默认纯规则运行**，无需任何 key，立即输出 FAQ JSON。
仅当你想让 LLM 额外提炼问答时，才需要：

```bash
export OPENAI_API_KEY=sk-xxx
python3 cli.py --file doc.txt --llm
```

## 目录说明

```
faq-generator-lite/
├── faq_generator.py   # 定义/疑问识别 + JSON 输出 + 可选 LLM
├── cli.py           # 命令行入口
├── tests/
│   └── test_faq.py
├── README.md
├── LICENSE
└── .gitignore
```

## 运行测试

```bash
python3 -m unittest discover -s tests
```

## License

MIT License，Copyright (c) 2026 ljiang9。
