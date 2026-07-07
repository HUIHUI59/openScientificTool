#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RefStyle — 参考文献一键多格式转换器
--------------------------------
把一个 .bib 文件里的参考文献,一键排成 APA / MLA / Chicago / 国标 GB/T 7714 等格式,
并写到一个 txt 文件里,复制粘贴进论文即可。

原理: 先用 bibtexparser 稳解析 .bib、剔掉 Zotero 塞进来的 file/abstract 等非引用字段
      (这些字段常含 Windows 路径的反斜杠,会让老库 citeproc 的 LaTeX 解析器崩);
      再用 citeproc-py + citeproc-py-styles(离线自带 2400+ 种期刊 CSL 样式,含国标)渲染;
      并内建修掉两个已知小瑕疵 —— 姓名后双句点、国标把英文标题降小写。

.bib 从哪来: Zotero / Google Scholar / 知网(CNKI) 都能一键导出 BibTeX(.bib)。

用法:
    双击 RefStyle.exe              -> 窗口提示你把 .bib 拖进来
    RefStyle.exe 你的.bib          -> 输出 APA/MLA/Chicago/国标 四种
    RefStyle.exe 你的.bib --style gb   -> 只出国标(可选 apa/mla/chicago/gb/all)

依赖(源码运行): pip install citeproc-py citeproc-py-styles bibtexparser
"""
import os
import re
import sys
import argparse
import warnings

for _s in ("stdin", "stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8")
    except Exception:
        pass
warnings.filterwarnings("ignore")

STYLES = {
    "apa": ("APA · 美国心理学会(社科最常用)", "apa"),
    "mla": ("MLA · 现代语言学会", "modern-language-association"),
    "chicago": ("Chicago · 芝加哥(作者-年份)", "chicago-author-date"),
    "gb": ("国标 GB/T 7714-2015(中文期刊刚需)", "china-national-standard-gb-t-7714-2015-numeric"),
}
DEFAULT_ORDER = ["apa", "mla", "chicago", "gb"]

# Zotero/知网 常塞进来、对排参考文献没用、且常含反斜杠(Windows 路径)会让 citeproc 崩的字段
_DROP_FIELDS = {"file", "abstract", "keywords", "annote", "file-path", "mendeley-tags", "note"}


def _prepare_source(bib_path):
    """用 bibtexparser 稳解析 .bib,剔掉非引用垃圾字段 + 清掉反斜杠,写一个干净临时 .bib。
    返回 (可用路径, 是否临时文件)。清洗失败则回退原文件,让 citeproc 自己试。"""
    try:
        import tempfile
        import bibtexparser
        from bibtexparser.bwriter import BibTexWriter
        with open(bib_path, encoding="utf-8", errors="replace") as f:
            db = bibtexparser.load(f)
        if not db.entries:
            return bib_path, False
        bs = chr(92)  # 反斜杠
        for e in db.entries:
            for k in list(e.keys()):
                if k.lower() in _DROP_FIELDS:
                    del e[k]
                elif isinstance(e[k], str) and bs in e[k]:
                    e[k] = e[k].replace(bs, " ")  # 中和会让 citeproc LaTeX 解析器崩的反斜杠
        writer = BibTexWriter()
        writer.indent = "  "
        text = bibtexparser.dumps(db, writer)
        tf = tempfile.NamedTemporaryFile("w", suffix=".bib", delete=False, encoding="utf-8")
        tf.write(text)
        tf.close()
        return tf.name, True
    except Exception:
        return bib_path, False


def _render(bib_path, csl_id):
    from citeproc.source.bibtex import BibTeX
    from citeproc import CitationStylesStyle, CitationStylesBibliography
    from citeproc import Citation, CitationItem, formatter
    from citeproc_styles import get_style_filepath
    src = BibTeX(bib_path, encoding="utf-8")
    style = CitationStylesStyle(get_style_filepath(csl_id), validate=False)
    bib = CitationStylesBibliography(style, src, formatter.plain)
    for key in src:
        bib.register(Citation([CitationItem(key)]))
    return src, [str(x) for x in bib.bibliography()]


# 输出清理: (a) 姓名缩写双句点 "R. D.." -> "R. D."(负向前瞻保护省略号 ...);
#          (b) Zotero 花括号大小写保护造成的多余空格 —— 标点前空格、词间连字符两侧空格。
def _fix_double_period(s):
    s = re.sub(r'([A-Za-z]\.)\.(?!\.)', r'\1', s)   # 双句点
    s = re.sub(r' +([:;,.])', r'\1', s)          # "SceneAdapt :" -> "SceneAdapt:"
    s = re.sub(r'(\w) *- *(\w)', r'\1-\2', s)     # "Scene -aware" / "Real - Time" -> 紧凑连字符
    return s


# 修复 (b·仅国标): 国标样式把拉丁文标题/刊名降成小写,用 .bib 原文回填还原
def _originals(src):
    out = []
    for key in src:
        ref = src[key]
        for field in ("title", "container_title"):
            val = ref.get(field)
            if val and re.search(r'[A-Za-z]', str(val)):
                out.append(str(val))
    return sorted(set(out), key=len, reverse=True)


def _restore_casing(s, originals):
    for orig in originals:
        s = re.sub(re.escape(orig), lambda m: orig, s, flags=re.IGNORECASE)
    return s


def format_bib(bib_path, style_key):
    csl_id = STYLES[style_key][1]
    src, lines = _render(bib_path, csl_id)
    originals = _originals(src) if style_key == "gb" else []
    fixed_lines = []
    for ln in lines:
        f = _fix_double_period(ln)
        if style_key == "gb":
            f = _restore_casing(f, originals)
        fixed_lines.append(f)
    return fixed_lines


def _run(args, interactive):
    bib_path = args.bib
    if bib_path is None:
        print("=" * 60)
        print(" RefStyle · 参考文献一键多格式(APA / MLA / Chicago / 国标)")
        print("=" * 60)
        print("(.bib 从 Zotero / Google Scholar / 知网 都能一键导出)")
        bib_path = input("\n把你的 .bib 文件拖到本窗口再按回车, 或粘贴路径:\n> ").strip().strip('"').strip("'")
    if not bib_path:
        print("没给文件, 退出。")
        return
    bib_path = os.path.abspath(bib_path)
    if not os.path.isfile(bib_path):
        print(f"[错误] 文件不存在: {bib_path}")
        return
    if not bib_path.lower().endswith(".bib"):
        print("[提示] 建议给 .bib 文件(Zotero/Scholar/知网 导出 BibTeX)。仍尝试解析……")

    if args.style == "all":
        keys = DEFAULT_ORDER
    else:
        keys = [k.strip() for k in args.style.split(",") if k.strip() in STYLES]
        if not keys:
            print(f"[错误] --style 只支持: {'/'.join(STYLES)}/all")
            return

    # 上游清洗:剔掉 Zotero 的 file 等垃圾字段 + 反斜杠,避免 citeproc 崩
    render_path, is_tmp = _prepare_source(bib_path)
    try:
        report = []
        ok_count = 0
        for k in keys:
            title = STYLES[k][0]
            try:
                lines = format_bib(render_path, k)
            except Exception as e:
                print(f"\n### {title}\n[出错] {str(e)[:100]}")
                continue
            print("\n" + "=" * 60)
            print(title)
            print("=" * 60)
            for ln in lines:
                print(ln)
            report.append(f"### {title}\n\n" + "\n".join(lines))
            ok_count += 1

        if ok_count:
            out_path = os.path.splitext(bib_path)[0] + "_参考文献格式.txt"
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write("\n\n\n".join(report) + "\n")
                print("\n" + "-" * 60)
                print(f"✓ {ok_count} 种格式已写到:\n  {out_path}\n  (打开复制粘贴进论文即可)")
            except Exception as e:
                print(f"\n[写文件失败, 但上面已打印] {str(e)[:80]}")
        else:
            print("\n[没排出任何格式] 检查一下这个 .bib 是不是空的 / 格式坏了。")
    finally:
        if is_tmp:
            try:
                os.remove(render_path)
            except Exception:
                pass


def main():
    ap = argparse.ArgumentParser(description="RefStyle — 参考文献一键多格式转换")
    ap.add_argument("bib", nargs="?", default=None, help=".bib 文件(不给则双击后交互输入)")
    ap.add_argument("--style", default="all", help="apa/mla/chicago/gb/all(逗号可多选, 默认 all)")
    ap.add_argument("--no-pause", action="store_true", help="结束不暂停(脚本调用时用)")
    args = ap.parse_args()
    interactive = args.bib is None

    try:
        _run(args, interactive)
    except KeyboardInterrupt:
        print("\n已取消。")
    except Exception as e:
        print(f"\n[出错] {str(e)[:160]}")
    finally:
        if interactive and not args.no_pause:
            try:
                input("\n按回车键退出……")
            except Exception:
                pass


if __name__ == "__main__":
    main()
