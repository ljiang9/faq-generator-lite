import unittest

from faq_generator import faqs, generate_faqs


DOC = """缓存是指临时存储数据以加快后续访问的机制。
什么是 CDN？
CDN 是部署在多地的内容分发网络。
它能显著加速静态资源访问。
所谓负载均衡，就是把流量分发到多台服务器。
"""


class TestFAQ(unittest.TestCase):
    def test_definition_detected(self):
        result = generate_faqs(DOC)
        questions = [f["question"] for f in result]
        self.assertIn("什么是缓存？", questions)

    def test_question_detected(self):
        result = generate_faqs(DOC)
        questions = [f["question"] for f in result]
        self.assertTrue(any("CDN" in q for q in questions))

    def test_so_called_definition(self):
        result = generate_faqs(DOC)
        questions = [f["question"] for f in result]
        self.assertIn("什么是负载均衡？", questions)

    def test_structure(self):
        result = generate_faqs(DOC)
        for f in result:
            self.assertIn("question", f)
            self.assertIn("answer", f)
            self.assertTrue(f["question"])
            self.assertTrue(f["answer"])

    def test_dedup(self):
        result = generate_faqs(DOC)
        qs = [f["question"] for f in result]
        self.assertEqual(len(qs), len(set(qs)))

    def test_empty(self):
        self.assertEqual(generate_faqs(""), [])

    def test_faqs_no_llm(self):
        result = faqs(DOC, use_llm=False)
        self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()
