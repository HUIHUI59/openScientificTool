#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper2MD — 论文 PDF 转 Markdown(纯格式转换器)
----------------------------------------------
把 PDF 论文转成 Markdown/纯文本——喂 AI、做笔记、全文检索都需要这一步。
保留标题层级和段落, 表格尽力还原, 图片可选提取。全程本地离线运行。

🔴 产品铁律(合规护栏, 与 README 口径一致):
  1. 不总结、不改写、不翻译、不润色、不删减——原文有什么就转出什么, 内容一字不动。
     它是纯格式转换器, 不生成任何学术观点文本。
  2. 不做 OCR(光学字符识别): 扫描版/图片型 PDF 无文本层, 检测到即如实提示
     "该文件无文本层, 本工具不支持", 绝不硬转出乱码。
  3. 不内嵌任何 AI 模型、不调任何 AI API——它是解析器, 不是助手。
  4. 不修改、不移动、不删除用户的原 PDF(只读输入, 新建输出)。

三种用法:
  1) 双击 exe(最省事)          —— 窗口提示你把 PDF 文件或文件夹拖进来, 回车开始。
  2) 把文件/文件夹拖到 exe 图标上 —— 松手即转, 结束暂停不闪退。
  3) 命令行:
        Paper2MD.exe <PDF文件或文件夹>              # 转换(交互询问是否提取图片)
        Paper2MD.exe <路径> --images               # 转换并提取图片
        Paper2MD.exe <路径> --no-images            # 转换且不提取图片(不询问)
        Paper2MD.exe <路径> --no-images --no-pause # 给脚本调用

依赖(源码运行时): pip install pymupdf4llm   (免模型下载、免 GPU、全程离线)
"""
import os
import sys
import time
import argparse

for _s in ("stdin", "stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8")
    except Exception:
        pass

BANNER = "Paper2MD · 论文 PDF 转 Markdown(纯格式转换, 内容一字不动)"

OUTPUT_DIR_NAME = "md_output"   # 批量模式输出子目录, 原文件绝不动


def has_text_layer(pdf_path: str) -> bool:
    """检测 PDF 是否有文本层。扫描件/图片型 PDF 没有文本层, 本工具不做 OCR, 如实跳过。"""
    import pymupdf
    try:
        doc = pymupdf.open(pdf_path)
    except Exception:
        return False
    try:
        n_check = min(len(doc), 5)   # 抽查前 5 页足够判断
        chars = 0
        for i in range(n_check):
            chars += len(doc[i].get_text().strip())
        # 抽查页平均不足 20 个字符 → 判定无文本层(纯扫描/图片型)
        return n_check > 0 and (chars / n_check) >= 20
    finally:
        doc.close()


def convert_one(pdf_path: str, md_path: str, extract_images: bool) -> dict:
    """转换单个 PDF -> Markdown。只读原 PDF, 新建输出文件, 原文件绝不动。"""
    import pymupdf4llm

    t0 = time.time()
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    out_dir = os.path.dirname(md_path) or "."
    os.makedirs(out_dir, exist_ok=True)

    kwargs = {}
    img_dir_name = stem + "_images"
    img_dir_abs = os.path.join(out_dir, img_dir_name)
    if extract_images:
        os.makedirs(img_dir_abs, exist_ok=True)
        kwargs["write_images"] = True
        kwargs["image_path"] = img_dir_abs

    md_text = pymupdf4llm.to_markdown(pdf_path, **kwargs)

    if extract_images:
        # 把 md 里图片引用的绝对路径换成相对路径(便于整个文件夹搬走仍能显示)
        for prefix in (img_dir_abs + os.sep, img_dir_abs.replace(os.sep, "/") + "/"):
            md_text = md_text.replace(prefix, img_dir_name + "/")
        n_imgs = len(os.listdir(img_dir_abs)) if os.path.isdir(img_dir_abs) else 0
        if n_imgs == 0:
            try:
                os.rmdir(img_dir_abs)   # 没提出图片就不留空目录
            except Exception:
                pass
    else:
        n_imgs = 0

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)

    return {
        "md_path": md_path,
        "seconds": time.time() - t0,
        "size_kb": os.path.getsize(md_path) / 1024.0,
        "n_images": n_imgs,
    }


def find_pdfs(folder: str):
    """递归找出文件夹下所有 .pdf(跳过输出目录本身), 返回相对路径列表。"""
    pdfs = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d != OUTPUT_DIR_NAME]
        for f in files:
            if f.lower().endswith(".pdf"):
                pdfs.append(os.path.relpath(os.path.join(root, f), folder))
    return sorted(pdfs)


def run_batch(folder: str, extract_images: bool):
    pdfs = find_pdfs(folder)
    if not pdfs:
        print(f"\n[提示] 该文件夹下没找到任何 .pdf 文件: {folder}")
        return []
    out_root = os.path.join(folder, OUTPUT_DIR_NAME)
    print(f"\n发现 {len(pdfs)} 个 PDF, 输出到: {out_root}")
    print("(原 PDF 只读不动, 全部输出都新建在 md_output/ 里)\n")

    results = []
    for i, rel in enumerate(pdfs, 1):
        src = os.path.join(folder, rel)
        dst = os.path.join(out_root, os.path.splitext(rel)[0] + ".md")
        tag = f"[{i}/{len(pdfs)}]"
        if not has_text_layer(src):
            print(f"{tag} {rel} → 跳过: 无文本层(扫描件/图片型), 本工具不做 OCR, 不硬转乱码")
            results.append({"src": rel, "skipped": True})
            continue
        try:
            r = convert_one(src, dst, extract_images)
            extra = f", 提取图片 {r['n_images']} 张" if extract_images else ""
            print(f"{tag} {rel} → done ({r['seconds']:.1f} 秒, {r['size_kb']:.0f} KB{extra})")
            results.append({"src": rel, "skipped": False, **r})
        except Exception as e:
            print(f"{tag} {rel} → 出错: {str(e)[:80]}")
            results.append({"src": rel, "skipped": True, "error": str(e)[:80]})
    return results


def run_single(pdf_path: str, extract_images: bool):
    md_path = os.path.splitext(pdf_path)[0] + ".md"
    print(f"\n输入: {pdf_path}")
    print(f"输出: {md_path}  (原 PDF 只读不动)\n")
    if not has_text_layer(pdf_path):
        print("[跳过] 该文件无文本层(扫描件/图片型 PDF), 本工具不做 OCR, 不支持这类文件。")
        print("       如需识别扫描件里的文字, 请另寻带 OCR 功能的工具。")
        return []
    r = convert_one(pdf_path, md_path, extract_images)
    extra = f", 提取图片 {r['n_images']} 张" if extract_images else ""
    print(f"[1/1] {os.path.basename(pdf_path)} → done ({r['seconds']:.1f} 秒, {r['size_kb']:.0f} KB{extra})")
    return [{"src": pdf_path, "skipped": False, **r}]


def print_summary(results, target: str):
    done = [r for r in results if not r.get("skipped")]
    skipped = len(results) - len(done)
    print("\n" + "=" * 56)
    print(f"完成 {len(done)} 个 | 跳过/出错 {skipped} 个")
    if done:
        if os.path.isdir(target):
            print(f"输出位置: {os.path.join(os.path.abspath(target), OUTPUT_DIR_NAME)}")
        else:
            print(f"输出位置: {done[0]['md_path']}")
    print("提醒: 输出是原文的如实转换——本工具不总结、不改写、不翻译, 内容一字不动。")
    print("      复杂表格(跨页/合并单元格)是尽力还原, 重要数据请对照原文核对。")
    print("=" * 56)


def _run(args):
    target = args.path
    if target is None:
        print("=" * 56)
        print(" " + BANNER)
        print("=" * 56)
        print("\n · 拖入单个 PDF  → 同目录输出同名 .md")
        print(" · 拖入文件夹    → 递归转换所有 PDF, 输出到 md_output/ 子目录")
        print(" · 扫描件(无文本层)不支持: 本工具不做 OCR, 会如实跳过")
        target = input("\n把 PDF 文件或文件夹拖到本窗口再按回车, 或直接粘贴路径:\n> ").strip().strip('"').strip("'")
    if not target:
        print("没给路径, 退出。")
        return
    target = os.path.abspath(target)

    if os.path.isfile(target):
        if not target.lower().endswith(".pdf"):
            print(f"[错误] 只支持 .pdf 文件: {target}")
            return
        mode = "single"
    elif os.path.isdir(target):
        mode = "batch"
    else:
        print(f"[错误] 路径不存在: {target}")
        return

    # 是否提取图片: 命令行给了 --images/--no-images 就不问; 否则交互询问
    if args.images:
        extract_images = True
    elif args.no_images:
        extract_images = False
    else:
        ans = input("\n是否提取 PDF 里的图片?(提取则存到 <文件名>_images/ 子目录) (y/N): ").strip().lower()
        extract_images = ans in ("y", "yes")

    results = run_single(target, extract_images) if mode == "single" else run_batch(target, extract_images)
    if results:
        print_summary(results, target)


def main():
    ap = argparse.ArgumentParser(
        description="Paper2MD — 论文 PDF 转 Markdown(纯格式转换, 不总结/不改写/不翻译, 不做 OCR)")
    ap.add_argument("path", nargs="?", default=None,
                    help="单个 PDF 文件或装 PDF 的文件夹(不给则双击后交互输入)")
    ap.add_argument("--images", action="store_true", help="提取图片到 <文件名>_images/ 子目录")
    ap.add_argument("--no-images", action="store_true", help="不提取图片(且不询问, 给脚本用)")
    ap.add_argument("--no-pause", action="store_true", help="结束不暂停(脚本调用时用)")
    args = ap.parse_args()

    # 交互模式判定: 没给路径(多半是双击), 或给了路径但没指定图片开关(多半是拖拽)
    interactive = (args.path is None) or not (args.images or args.no_images)

    try:
        _run(args)
    except KeyboardInterrupt:
        print("\n已取消。")
    except Exception as e:
        print(f"\n[出错] {str(e)[:120]}")
    finally:
        if interactive and not args.no_pause:
            try:
                input("\n按回车键退出……")
            except Exception:
                pass


if __name__ == "__main__":
    main()
