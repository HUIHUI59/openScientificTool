#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BlindCheck — 匿名处理自查器(双盲投稿 / 学位论文盲审前扫身份泄露)
----------------------------------------------------------------
拖入投稿 docx / PDF, 扫出所有可能暴露作者身份的地方:
文件属性作者名、修订记录/批注署名、PDF 元数据、致谢与基金号、自引式措辞。
输出「身份泄露清单 + 每项的手动修复步骤」。

🔒 四条铁律(写死在代码里, 不可关闭):
  1. 只读扫描 —— 绝不修改你的文件, 修复由你按步骤自己动手。
  2. 只出清单 —— 不生成任何可粘进稿子的文本。
  3. 不承诺安全 —— 覆盖六类常见泄露, 非穷尽, 检出为 0 ≠ 绝对安全。
  4. 零联网 —— 纯本地扫描, 你的稿子不出这台电脑。

三种用法:
  1) 双击 exe(最省事)          —— 窗口会提示你把文件拖进来。
  2) 把 docx/PDF 拖到 exe 图标上 —— 直接出结果, 结尾暂停不闪退。
  3) 命令行: BlindCheck.exe 稿子.docx 稿子.pdf [--no-pause]

依赖(源码运行时): pip install pypdf   (只用于读 PDF; 只查 docx 可不装)
"""
import os
import re
import sys
import argparse
import zipfile
from xml.sax.saxutils import unescape

for _s in ("stdin", "stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8")
    except Exception:
        pass

IRON_RULES = """🔒 铁律(写死在代码里, 不可关闭):
  1. 只读扫描 —— 绝不修改你的文件, 修复由你按步骤自己动手。
  2. 只出清单 —— 不生成任何可粘进稿子的文本。
  3. 不承诺安全 —— 覆盖六类常见泄露, 非穷尽, 检出为 0 ≠ 绝对安全。
  4. 零联网 —— 纯本地扫描, 你的稿子不出这台电脑。"""

SIX = "①docx文件属性 ②修订记录署名 ③批注署名 ④PDF元数据 ⑤致谢与基金号 ⑥自引措辞"
# 按文件类型如实报告: 哪些项本次真的查了、哪些项对该文件不适用(不夸大覆盖面)
CHECKED = {
    "docx": "①docx文件属性 ②修订记录署名 ③批注署名 ⑤致谢与基金号 ⑥自引措辞",
    "pdf":  "④PDF元数据 ⑤致谢与基金号 ⑥自引措辞",
}
NOT_APPLICABLE = {
    "docx": "④PDF元数据(本文件不是 PDF; 若同时要投 PDF 版, 请把 PDF 也拖进来一起查——PDF 元数据是独立泄露源)",
    "pdf":  "①docx文件属性 ②修订记录署名 ③批注署名(这三项只存在于 docx; 建议对 docx 源文件也跑一遍)",
}

# ---------- 模式表(中英双语) ----------
SELF_CITE = re.compile(
    r"(笔者|本文作者|作者本人)(此前|之前|先前|早期)?的?(研究|工作|论文|文章)"
    r"|(我们|本课题组|本团队)(此前|之前|先前|早期|在前期)的?(研究|工作|论文)"
    r"|见拙作|拙文"
    r"|\bin\s+our\s+(previous|earlier|prior)\s+(work|study|studies|paper|research)"
    r"|\bour\s+(previous|earlier|prior)\s+(work|study|studies|paper)"
    r"|\bas\s+we\s+(have\s+)?(previously\s+|earlier\s+)?(shown|argued|demonstrated|reported)",
    re.I)
FUNDING = re.compile(
    r"国家(社会科学|自然科学)基金|教育部人文社科|哲学社会科学(规划)?(基金|项目)|中国博士后科学基金"
    r"|基金项目|课题编号|项目编号|项目批准号|资助项目"
    r"|\b\d{2}[A-Z]{1,4}\d{3,}\b"
    r"|\bgrant\s*(no\.?|number)|\bfunded\s+by\b|\bsupported\s+by\b",
    re.I)
ACK = re.compile(
    r"致\s*谢|acknowledg(e?ments?)\b|\bthe\s+authors?\s+(wish(es)?\s+to\s+)?thank",
    re.I)

# (正则模式, 类别名, 修复步骤键, 等级)
TEXT_PATTERNS = [
    (ACK, "致谢段落(可能含导师/机构名)", "ack_fund", "MED"),
    (FUNDING, "基金号/项目编号", "ack_fund", "MED"),
    (SELF_CITE, "自引式措辞(第一人称指向自己过往成果)", "self_cite", "MED"),
]

FIX = {
    "docx_props": "Word → 文件 → 信息 → 检查问题 → 检查文档 → 勾选「文档属性和个人信息」→ 全部删除, 另存一份再投",
    "docx_rev":   "Word → 审阅 → 接受所有修订并停止修订(署名随修订一起消失); 或走「检查文档」入口",
    "docx_cmt":   "Word → 审阅 → 删除 → 删除文档中的所有批注",
    "pdf_meta":   "回到 Word 源文件, 导出 PDF 时点「选项」取消勾选「文档属性」; 已有 PDF 可在 Acrobat「文件→属性」里清空作者",
    "ack_fund":   "把致谢与基金信息暂时挪到单独的 title page(投稿系统里单独上传), 匿名正文里先删掉——怎么处理由你自己定, 本工具不动你的文件",
    "self_cite":  "把第一人称自引改成与引用他人文献同款的第三人称格式——具体措辞你自己改, 本工具不生成替代句",
}

SEV = {"HIGH": "【高危】", "MED": "【留意】"}


def scan_docx(path):
    """只读扫描 docx。返回 (findings, notes); 单项失败降级, 不崩整体。"""
    findings, notes = [], []
    try:
        z = zipfile.ZipFile(path)
    except Exception as e:
        return findings, ["整个文件无法按 docx 打开(%s), 六类均未检查" % str(e)[:40]]
    with z:
        # ① 文件属性: 作者 / 最后修改者
        try:
            core = z.read("docProps/core.xml").decode("utf-8", "ignore")
            for tag, label in (("creator", "docx文件属性·作者"),
                               ("lastModifiedBy", "docx文件属性·最后修改者")):
                m = re.search(r"<[^>]*\b%s[^>]*>([^<]+)<" % tag, core)
                if m and m.group(1).strip():
                    findings.append(("HIGH", label, "文件→信息→属性",
                                     unescape(m.group(1).strip()), "docx_props"))
        except KeyError:
            pass
        except Exception:
            notes.append("文件属性项无法检查")
        docxml = None
        try:
            docxml = z.read("word/document.xml").decode("utf-8", "ignore")
        except Exception:
            notes.append("正文 document.xml 无法读取, 修订/致谢/基金/自引四项未检查")
        # ② 修订记录署名(开着修订模式的稿子重灾区)
        if docxml is not None:
            try:
                for a in sorted(set(re.findall(r'<w:(?:ins|del)\b[^>]*w:author="([^"]+)"', docxml))):
                    findings.append(("HIGH", "修订记录署名", "审阅→修订", unescape(a), "docx_rev"))
            except Exception:
                notes.append("修订记录项无法检查")
        # ③ 批注署名
        try:
            if "word/comments.xml" in z.namelist():
                cx = z.read("word/comments.xml").decode("utf-8", "ignore")
                for a in sorted(set(re.findall(r'w:author="([^"]+)"', cx))):
                    findings.append(("HIGH", "批注署名", "审阅→批注", unescape(a), "docx_cmt"))
        except Exception:
            notes.append("批注项无法检查")
        # ⑤⑥ 正文敏感段 + 自引措辞(逐段扫, 报段号)
        if docxml is not None:
            try:
                paras = re.findall(r"<w:p[ >].*?</w:p>", docxml, re.S)
                for i, p in enumerate(paras, 1):
                    text = unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)))
                    if not text.strip():
                        continue
                    for pat, label, fixkey, sev in TEXT_PATTERNS:
                        m = pat.search(text)
                        if m:
                            ctx = text[max(0, m.start() - 15): m.end() + 15].strip()
                            findings.append((sev, label, "正文第 %d 段" % i, "…%s…" % ctx, fixkey))
            except Exception:
                notes.append("正文文本项(致谢/基金/自引)无法检查")
    return findings, notes


def scan_pdf(path):
    """只读扫描 PDF 元数据 + 正文文本。返回 (findings, notes)。"""
    findings, notes = [], []
    try:
        from pypdf import PdfReader
    except ImportError:
        return findings, ["pypdf 未安装, PDF 无法检查(源码运行请先: pip install pypdf)"]
    try:
        reader = PdfReader(path)
    except Exception as e:
        return findings, ["PDF 无法打开(%s), 未检查" % str(e)[:40]]
    # ④ PDF 元数据
    try:
        meta = reader.metadata or {}
        for k in ("/Author", "/Creator", "/Producer", "/Title"):
            v = str(meta.get(k, "") or "").strip()
            if not v:
                continue
            # /Author 非空一律报; 其余字段只在疑似含人名/中文文件名时报, 减少噪音
            if k == "/Author" or re.search(r"[一-鿿]{2,}", v):
                findings.append(("HIGH", "PDF元数据 %s" % k, "文件→属性", v, "pdf_meta"))
    except Exception:
        notes.append("PDF 元数据项无法检查")
    # ⑤⑥ PDF 正文敏感段 + 自引措辞(逐页扫, 报页号)
    try:
        for pno, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            if not text.strip():
                continue
            for pat, label, fixkey, sev in TEXT_PATTERNS:
                m = pat.search(text)
                if m:
                    ctx = re.sub(r"\s+", " ", text[max(0, m.start() - 15): m.end() + 15]).strip()
                    findings.append((sev, label, "第 %d 页" % pno, "…%s…" % ctx, fixkey))
    except Exception:
        notes.append("PDF 正文无法抽取, 致谢/基金/自引三项未检查(建议回到 docx 源文件上查)")
    return findings, notes


def report(path, findings, notes, kind):
    print("\n" + "=" * 58)
    print(" 检查对象: %s" % os.path.abspath(path))
    print("=" * 58)
    if findings:
        for n, (sev, label, loc, content, fixkey) in enumerate(findings, 1):
            print("\n%2d. %s %s" % (n, SEV.get(sev, sev), label))
            print("    位置: %s" % loc)
            print("    命中: %s" % content[:80])
            print("    修复: %s" % FIX[fixkey])
    else:
        print("\n  ✓ 本文件适用的检查项均未检出泄露。")
    for note in notes:
        print("\n  ⚠ %s" % note)
    high = sum(1 for f in findings if f[0] == "HIGH")
    print("\n" + "-" * 58)
    print(" 共检出 %d 处(高危 %d · 留意 %d)" % (len(findings), high, len(findings) - high))
    print(" 本文件已检查: %s" % CHECKED[kind])
    print(" 本文件不适用: %s" % NOT_APPLICABLE[kind])
    print(" ⚠ 边界: 只覆盖六类常见泄露, 非穷尽; 检出为 0 也不等于匿名")
    print("   处理绝对完备, 投出前请再人工过一遍。")
    print(" 本工具全程只读, 你的文件一个字节都没被改; 修复请按上面")
    print(" 的手动步骤自己操作。")
    print("-" * 58)


def check_one(path):
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        print("\n[错误] 文件不存在: %s" % path)
        return
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        findings, notes = scan_docx(path)
        kind = "docx"
    elif ext == ".pdf":
        findings, notes = scan_pdf(path)
        kind = "pdf"
    elif ext == ".doc":
        print("\n[跳过] 老格式 .doc 不支持, 请先用 Word 另存为 .docx 再来检查: %s" % path)
        return
    else:
        print("\n[跳过] 只支持 .docx / .pdf: %s" % path)
        return
    report(path, findings, notes, kind)


def main():
    ap = argparse.ArgumentParser(
        description="BlindCheck — 匿名处理自查(只读扫 docx/PDF 六类身份泄露, 不改文件不联网)")
    ap.add_argument("files", nargs="*", help="要检查的 docx / PDF(不给则双击后交互输入)")
    ap.add_argument("--no-pause", action="store_true", help="结束不暂停(被脚本调用时用)")
    args = ap.parse_args()
    need_pause = not args.no_pause
    try:
        if args.files:
            for f in args.files:
                check_one(f.strip().strip('"').strip("'"))
        else:
            print("=" * 58)
            print(" BlindCheck · 匿名处理自查(双盲投稿/盲审前扫身份泄露)")
            print("=" * 58)
            print(IRON_RULES)
            while True:
                raw = input("\n把要检查的 docx/PDF 拖到本窗口再按回车(直接回车=退出):\n> ").strip().strip('"').strip("'")
                if not raw:
                    need_pause = False
                    break
                check_one(raw)
    except KeyboardInterrupt:
        print("\n已取消。")
    except Exception as e:
        print("\n[出错] %s" % str(e)[:120])
    finally:
        if need_pause:
            try:
                input("\n按回车键退出……")
            except Exception:
                pass


if __name__ == "__main__":
    main()
