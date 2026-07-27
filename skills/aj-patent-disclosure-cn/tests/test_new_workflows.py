from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


office = load_module("office_to_markdown", SKILL_ROOT / "scripts" / "office_to_markdown.py")
validator = load_module("validate_disclosure", SKILL_ROOT / "scripts" / "validate_disclosure.py")


class OfficeConversionTests(unittest.TestCase):
    def test_docx_text_table_and_media(self):
        document_xml = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>系统方案</w:t></w:r></w:p>
    <w:p><w:r><w:t>边缘节点执行步骤 S1。</w:t></w:r></w:p>
    <w:tbl>
      <w:tr><w:tc><w:p><w:r><w:t>参数</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>范围</w:t></w:r></w:p></w:tc></w:tr>
      <w:tr><w:tc><w:p><w:r><w:t>阈值</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>0.5-0.8</w:t></w:r></w:p></w:tc></w:tr>
    </w:tbl>
  </w:body>
</w:document>"""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "design.docx"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("word/document.xml", document_xml)
                archive.writestr("word/media/image1.png", b"fake-png")
            result = office.convert_one(source, root / "out", 32)
            content = Path(result["markdown"]).read_text(encoding="utf-8")
            self.assertIn("# 系统方案", content)
            self.assertIn("边缘节点执行步骤 S1", content)
            self.assertIn("| 参数 | 范围 |", content)
            self.assertEqual(len(result["media"]), 1)

    def test_pptx_slide_and_notes(self):
        slide_xml = """<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>架构评审</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>
</p:sld>"""
        notes_xml = """<?xml version="1.0" encoding="UTF-8"?>
<p:notes xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>失败时回退本地模型</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>
</p:notes>"""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "review.pptx"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("ppt/slides/slide1.xml", slide_xml)
                archive.writestr("ppt/notesSlides/notesSlide1.xml", notes_xml)
            result = office.convert_one(source, root / "out", 32)
            content = Path(result["markdown"]).read_text(encoding="utf-8")
            self.assertIn("## 幻灯片 1", content)
            self.assertIn("架构评审", content)
            self.assertIn("失败时回退本地模型", content)


class RevisionAndValidationTests(unittest.TestCase):
    def test_revision_log_is_append_only_and_hashed(self):
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp)
            base = case_dir / "v1.md"
            artifact = case_dir / "v2.md"
            base.write_text("old", encoding="utf-8")
            artifact.write_text("new", encoding="utf-8")
            command = [
                sys.executable,
                str(SKILL_ROOT / "scripts" / "revision_log.py"),
                "--case-dir",
                str(case_dir),
                "--kind",
                "correction",
                "--base",
                str(base),
                "--artifact",
                str(artifact),
                "--changed-section",
                "实施例1",
                "--summary",
                "纠正阈值来源",
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            subprocess.run(command, check=True, capture_output=True, text=True)
            markdown = (case_dir / "revision_history.md").read_text(encoding="utf-8")
            records = [
                json.loads(line)
                for line in (case_dir / "revision_history.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            self.assertEqual(markdown.count("纠正阈值来源"), 2)
            self.assertEqual(len(records), 2)
            self.assertEqual(len(records[0]["artifacts"][0]["sha256"]), 64)

    def test_retained_innovation_requires_effect_and_support(self):
        payload = {
            "title": "一种测试方法",
            "technical_field": "计算机处理",
            "background": "现有处理存在时延问题。",
            "invention": {
                "technical_problem": "降低处理时延。",
                "solution_steps": [{"id": "S1", "action": "处理", "input": "数据", "output": "结果"}],
                "effects": ["降低处理时延"],
            },
            "embodiments": [{"steps": ["执行S1"], "outputs": ["结果"]}],
            "innovation_candidates": [
                {
                    "id": "P1",
                    "status": "核心候选",
                    "search_status": "全文对比",
                    "distinguishing_features": ["F1"],
                }
            ],
        }
        report = validator.validate_payload(payload, Path("input.json"), final=True)
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("innovation-effect", codes)
        self.assertIn("innovation-support", codes)


if __name__ == "__main__":
    unittest.main()
