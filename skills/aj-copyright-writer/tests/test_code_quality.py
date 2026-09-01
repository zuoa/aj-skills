from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from argparse import Namespace
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit_originality import audit
from build_code_docx import build_docx, source_lines_for_deposit
from markdown_to_docx import convert_markdown
from validate_outputs import (
    ValidationError,
    infer_standard_dirs,
    validate_code_files,
    validate_deliverable_markdown,
    validate_design_markdown,
    validate_module_function_points,
    validate_originality_report,
    validate_prototype_files,
    validate_source_manifest,
)

MODULE_NAMES = [
    "传感窗口聚合", "异常阈值判定", "追溯链路构建", "设备漂移校正", "冷链批次关联",
    "告警升级处置", "断点数据补偿", "运输时段切片", "责任节点定位", "处置结果复核",
]


def write_modules(root: Path) -> Path:
    module_dir = root / "02.modules"
    module_dir.mkdir()
    for index, name in enumerate(MODULE_NAMES, 1):
        (module_dir / f"{index:02d}.md").write_text(
            f"# {index:02d}. {name}\n\n## 功能点清单\n\n1. {name}计算：处理对应冷链业务。\n2. {name}校验：核对输入。\n3. {name}追踪：记录结果。\n",
            encoding="utf-8",
        )
    return module_dir


def write_code(root: Path, counts: list[int] | None = None, names: list[str] | None = None) -> Path:
    code_dir = root / "05.code"
    code_dir.mkdir()
    counts = counts or [120, 180, 220, 260, 280, 300, 340, 380, 420, 500]
    bodies = [
        "const result_{n} = reading_{n} + threshold_{n};",
        "const result_{n} = reading_{n} - baseline_{n};",
        "const result_{n} = reading_{n} * weight_{n};",
        "const result_{n} = reading_{n} / divisor_{n};",
        "const result_{n} = reading_{n} > limit_{n} ? high_{n} : low_{n};",
        "windowMap.put(key_{n}, value_{n});",
        "traceItems.add(new TraceNode(node_{n}, hop_{n}));",
        "if (activeSet.contains(sensor_{n})) activeCount++;",
        "const result_{n} = Math.max(reading_{n}, threshold_{n});",
        "const result_{n} = enabled_{n} && !suppressed_{n};",
    ]
    for index, count in enumerate(counts, 1):
        name = names[index - 1] if names else f"业务模块{index:02d}"
        lines = [f"// {name}核心业务处理", f"function processModule{index:02d}(context) {{"]
        lines.extend(bodies[index - 1].format(n=f"{index:02d}_{line:04d}") for line in range(1, count + 1))
        lines.append("}")
        (code_dir / f"{index:02d}-{name}.txt").write_text("\n".join(lines), encoding="utf-8")
    return code_dir


class CodeQualityTests(unittest.TestCase):
    @staticmethod
    def root_validation_args() -> Namespace:
        return Namespace(
            spec_md=None,
            module_dir=None,
            prototype_mode="html",
            prompt_dir=None,
            html_dir=None,
            style_selection=None,
            prototype_dir=None,
            code_dir=None,
            source_manifest=None,
            originality_report=None,
            document_md=None,
            document_docx=None,
            code_docx=None,
            application_info_txt=None,
            batch_file=None,
            software_name="冷链温湿度异常追溯服务",
        )

    def test_root_validation_accepts_design_specification_as_selected_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document_dir = root / "06.document"
            document_dir.mkdir()
            design_md = document_dir / "冷链温湿度异常追溯服务_软件设计说明书.md"
            design_docx = document_dir / "冷链温湿度异常追溯服务_软件设计说明书.docx"
            design_md.write_text("# 设计说明", encoding="utf-8")
            design_docx.write_bytes(b"placeholder")

            args = self.root_validation_args()
            infer_standard_dirs(root, args)

            self.assertEqual(args.document_md, design_md)
            self.assertEqual(args.document_docx, design_docx)

    def test_root_validation_rejects_ambiguous_two_document_set(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document_dir = root / "06.document"
            document_dir.mkdir()
            manual_md = document_dir / "冷链温湿度异常追溯服务_操作手册.md"
            manual_docx = document_dir / "冷链温湿度异常追溯服务_操作手册.docx"
            design_md = document_dir / "冷链温湿度异常追溯服务_软件设计说明书.md"
            design_docx = document_dir / "冷链温湿度异常追溯服务_软件设计说明书.docx"
            manual_md.write_text("# 操作手册", encoding="utf-8")
            manual_docx.write_bytes(b"placeholder")
            design_md.write_text("# 设计说明", encoding="utf-8")
            design_docx.write_bytes(b"placeholder")

            with self.assertRaisesRegex(ValidationError, "exactly one final selected-document markdown"):
                infer_standard_dirs(root, self.root_validation_args())

    def test_variable_file_lengths_and_manifest_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code_dir = write_code(root)
            manifest_path = root / "source-manifest.json"
            manifest, _ = audit(code_dir, None, None, None)
            manifest["files"] = list(reversed(manifest["files"]))
            for order, entry in enumerate(manifest["files"], 1):
                entry["order"] = order
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False),
                encoding="utf-8",
            )
            selected = validate_code_files(code_dir, source_manifest=manifest_path)
            expected = [entry["path"] for entry in manifest["files"]]
            self.assertEqual([path.name for path in selected], expected)
            self.assertEqual(validate_source_manifest(manifest_path, code_dir), expected)

    def test_explicit_per_file_limit_remains_available(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            code_dir = write_code(Path(temporary))
            with self.assertRaises(ValidationError):
                validate_code_files(code_dir, min_lines=200)

    def test_audit_flags_low_value_placeholder_and_repetition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code_dir = root / "05.code"
            code_dir.mkdir()
            repeated = ["import generated.client.Api;" for _ in range(50)]
            repeated.append("// AUTO-GENERATED CODE - DO NOT EDIT")
            repeated.append("// TODO 待实现")
            repeated.extend(["function emptyComponent() {", "}"])
            (code_dir / "01-空壳模块.txt").write_text("\n".join(repeated), encoding="utf-8")
            _, report = audit(code_dir, None, None, None)
            self.assertEqual(report["status"], "fail")
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("placeholder-code", codes)
            self.assertIn("low-value-file", codes)
            self.assertIn("generated-or-third-party", codes)
            self.assertIn("empty-implementation", codes)

    def test_pass_report_becomes_stale_after_source_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code_dir = write_code(root, names=MODULE_NAMES)
            module_dir = write_modules(root)
            document = root / "design.md"
            names = [item["name"] for item in __import__("audit_originality").read_modules(module_dir)]
            descriptions = [
                "按采样周期归并温湿度读数，并保留窗口起止和缺测标记。",
                "依据货品类别与运输阶段应用分级阈值，输出异常级别。",
                "从批次、车辆和中转节点建立可回溯的责任路径。",
                "比较设备基线与参照探头，修正持续性测量漂移。",
                "使用运单和装卸时间把监测记录关联到冷链批次。",
                "根据持续时长与影响范围升级告警并生成处置任务。",
                "检测上报序列断点，从设备缓存补取并校验重复消息。",
                "按运输、等待和装卸阶段切分时间轴以计算暴露时长。",
                "结合轨迹、交接记录和异常窗口定位责任节点。",
                "复核温控恢复、货品抽检和处置凭证后完成闭环。",
            ]
            document.write_text(
                "\n\n".join(f"## {name}\n{name}{description}系统同时记录输入、处理结果和异常分支。" for name, description in zip(names, descriptions)),
                encoding="utf-8",
            )
            _, report = audit(code_dir, module_dir, document, None)
            self.assertEqual(report["status"], "pass", report["issues"])
            report_path = root / "originality-report.json"
            report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
            validate_originality_report(report_path, code_dir)
            target = sorted(code_dir.glob("*.txt"))[0]
            target.write_text(target.read_text(encoding="utf-8") + "\nchangedBusinessRule = true;", encoding="utf-8")
            with self.assertRaises(ValidationError):
                validate_originality_report(report_path, code_dir)

    def test_deposit_uses_first_and_last_continuous_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.txt"
            second = root / "second.txt"
            first.write_text("\n".join(f"first_{index}" for index in range(2000)), encoding="utf-8")
            second.write_text("\n".join(f"second_{index}" for index in range(2000)), encoding="utf-8")
            selected = source_lines_for_deposit([first, second], 3000)
            self.assertEqual(len(selected), 3000)
            self.assertEqual(selected[0], "first_0")
            self.assertEqual(selected[1499], "first_1499")
            self.assertEqual(selected[1500], "second_500")
            self.assertEqual(selected[-1], "second_1999")

    def test_builder_accepts_current_passed_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code_dir = write_code(root)
            manifest, report = audit(code_dir, None, None, None)
            audit_dir = root / "09.originality-audit"
            audit_dir.mkdir()
            manifest_path = audit_dir / "source-manifest.json"
            report_path = audit_dir / "originality-report.json"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
            output = root / "代码.docx"
            build_docx(code_dir, output, None, False, "冷链追溯服务", "V1.0", manifest_path, report_path)
            self.assertTrue(output.is_file())
            manifest["technology_stack"] = ["ChangedStack"]
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValidationError):
                validate_originality_report(report_path, code_dir, manifest_path)

    def test_formal_document_rejects_process_wording(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "软件设计说明书.md"
            path.write_text("# 设计说明\n\n本文为扩展设定，待申请人核验。\n", encoding="utf-8")
            with self.assertRaises(ValidationError):
                validate_deliverable_markdown(path, "design")

    def test_design_document_rejects_generated_source_mapping_wording(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "种鹅管理系统_软件设计说明书.md"
            path.write_text(
                "# 身份管理设计\n\n本节设计由 01-种鹅个体档案与RFID身份管理.py 落地。\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValidationError, "source-mapping wording"):
                validate_design_markdown(path, "design specification")

    def test_design_document_accepts_logical_symbol_traceability(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "种鹅管理系统_软件设计说明书.md"
            path.write_text(
                "# 设计—实现追踪表\n\n"
                "| 设计单元 | 实现组件 | 核心服务 | 关键入口 |\n"
                "| --- | --- | --- | --- |\n"
                "| RFID 身份绑定 | 个体身份服务 | `RfidIdentityService` | `bindTag` |\n",
                encoding="utf-8",
            )
            validate_design_markdown(path, "design specification")

    def test_design_document_rejects_dense_ai_style_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "种鹅管理系统_软件设计说明书.md"
            path.write_text(
                "# 系统设计\n\n"
                "本系统旨在全面提升种鹅档案管理能力。\n\n"
                "系统打造了完整的业务闭环。\n\n"
                "整体设计具备良好的可扩展性。\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValidationError, "too abstract or repetitive"):
                validate_design_markdown(path, "design specification")

    def test_markdown_docx_uses_chinese_technical_document_fonts_and_a4(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            markdown = root / "种鹅管理系统_软件设计说明书.md"
            output = root / "设计说明书.docx"
            markdown.write_text(
                "# 种鹅管理系统软件设计说明书\n\n"
                "## 身份绑定\n\n"
                "标签绑定前，身份服务先检查 RFID 号是否已被使用。\n\n"
                "- 已绑定的标签不允许重复使用。\n\n"
                "| 字段 | 用途 |\n| --- | --- |\n| `rfidCode` | RFID 标签号 |\n",
                encoding="utf-8",
            )
            convert_markdown(markdown, output, None)

            with zipfile.ZipFile(output) as archive:
                styles = archive.read("word/styles.xml").decode("utf-8")
                document = archive.read("word/document.xml").decode("utf-8")

            self.assertIn('w:eastAsia="宋体"', styles)
            self.assertIn('w:eastAsia="黑体"', styles)
            self.assertIn('w:ascii="Times New Roman"', styles)
            self.assertRegex(document, r'<w:pgSz[^>]*w:w="11906"[^>]*w:h="16838"')
            self.assertIn('w:pStyle w:val="ListBullet"', document)
            self.assertIn('w:tblLayout w:type="fixed"', document)

    def test_more_than_two_generic_modules_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            module_dir = Path(temporary)
            names = ["用户管理", "权限管理", "系统设置"] + [f"冷链业务{index}" for index in range(4, 11)]
            for index, name in enumerate(names, 1):
                (module_dir / f"{index:02d}.md").write_text(
                    f"# {index:02d}. {name}\n\n## 功能点清单\n1. 功能一：说明。\n2. 功能二：说明。\n3. 功能三：说明。\n",
                    encoding="utf-8",
                )
            with self.assertRaises(ValidationError):
                validate_module_function_points(module_dir)

    def test_blank_lines_are_allowed_and_crlf_fingerprints_stay_current(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code_dir = write_code(root)
            for path in code_dir.glob("*.txt"):
                text = path.read_text(encoding="utf-8").replace("\n", "\r\n")
                text = text.replace("\r\n", "\r\n\r\n", 1)
                path.write_bytes(text.encode("utf-8"))
            validate_code_files(code_dir)
            _, report = audit(code_dir, None, None, None)
            self.assertEqual(report["status"], "pass", report["issues"])
            report_path = root / "report.json"
            report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
            validate_originality_report(report_path, code_dir)

    def test_ten_repeated_document_skeletons_are_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code_dir = write_code(root, names=MODULE_NAMES)
            module_dir = write_modules(root)
            document = root / "软件设计说明书.md"
            document.write_text(
                "\n\n".join(
                    f"## {name}\n{name}用于处理「业务对象」；系统校验输入后更新状态并记录异常结果。"
                    for name in MODULE_NAMES
                ),
                encoding="utf-8",
            )
            _, report = audit(code_dir, module_dir, document, None)
            self.assertEqual(report["status"], "fail")
            self.assertIn("document-template-repetition", {issue["code"] for issue in report["issues"]})

    def test_per_file_history_copy_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code_dir = write_code(root)
            corpus = root / "history"
            corpus.mkdir()
            for path in code_dir.glob("*.txt"):
                (corpus / path.name).write_bytes(path.read_bytes())
            _, report = audit(code_dir, None, None, corpus)
            self.assertEqual(report["status"], "fail")
            self.assertIn("code-corpus-similarity", {issue["code"] for issue in report["issues"]})

    def test_missing_explicit_inputs_and_malformed_report_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code_dir = write_code(root)
            _, report = audit(code_dir, root / "missing-modules", root / "missing.md", root / "missing-history")
            self.assertEqual(report["status"], "fail")
            codes = {issue["code"] for issue in report["issues"]}
            self.assertTrue({"module-directory", "selected-document", "comparison-corpus"}.issubset(codes))
            malformed = root / "malformed-report.json"
            malformed.write_text('{"version": 1, "status": "pass", "issues": [], "source_files": ["bad"]}', encoding="utf-8")
            with self.assertRaises(ValidationError):
                validate_originality_report(malformed, code_dir)

    def test_login_prototype_can_be_disabled_for_software_without_authentication(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            prototype_dir = Path(temporary)
            for index in range(1, 11):
                (prototype_dir / f"{index:02d}.jpg").write_bytes(b"jpeg-placeholder")
            validate_prototype_files(prototype_dir, ".jpg", "prototype", require_login=False)
            with self.assertRaises(ValidationError):
                validate_prototype_files(prototype_dir, ".jpg", "prototype", require_login=True)


if __name__ == "__main__":
    unittest.main()
