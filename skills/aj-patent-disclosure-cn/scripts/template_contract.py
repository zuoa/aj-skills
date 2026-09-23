"""Literal field contract of the user-supplied 2026-09-22 disclosure form."""
TITLE = "专利申请信息及技术交底书"
INSTRUCTION = "填写下列内容请秉持两个原则，第一原则为：每处内容不空白，哪怕是仅写几个字；第二原则为：确实填不了，请填“代理确定”。"
FALLBACK = "代理确定"
# (Markdown level, exact source paragraph). The original has one eight-row, single-column table.
OUTLINE = (
    (2, "待申报专利的主题名称："),
    (2, "申请人以及发明人名称："),
    (2, "与待申报专利相关的现有技术："),
    (3, "第一，现有技术的名称："),
    (3, "第二，现有技术的来源："),
    (3, "第三，现有技术的技术方案："),
    (3, "第四，现有技术的缺陷/不足："),
    (2, "基于上述缺陷/不足的基础上，想要解决的技术问题以及实现的技术效果："),
    (3, "发明人认为要解决的技术问题："),
    (3, "发明人认为可实现的技术效果："),
    (2, "我方待申报专利的具体技术内容和实现原理："),
    (3, "具体技术内容："),
    (3, "实现原理："),
    (2, "其他内容："),
    (3, "附图："),
    (3, "实验数据："),
    (3, "特定软件分析结果："),
    (2, "专利申报目的，可多选：例如保护技术、授权拿证、申报项目、评职称等"),
    (2, "专利申请人或主要发明人的产品种类、工作内容、所属领域:"),
)
HEADINGS = tuple(label for _, label in OUTLINE)
LEAF_HEADINGS = tuple(label for i, (level, label) in enumerate(OUTLINE)
                      if i == len(OUTLINE)-1 or OUTLINE[i+1][0] <= level)


def verify_template_files():
    """Fail closed when a replaced .doc has not been converted/reviewed yet."""
    import hashlib
    import json
    from pathlib import Path
    directory = Path(__file__).resolve().parents[1] / 'assets/templates'
    record = json.loads((directory / 'template_provenance.json').read_text())
    for key in ('source', 'reference'):
        path = directory / record[key]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record[key+'_sha256']:
            raise ValueError('模板已更新但转换副本/摘要未同步，请重新转换并核对原模板: '+str(path))
