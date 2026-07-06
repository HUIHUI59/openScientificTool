#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaperTidy — PDF 文献批量重命名器
--------------------------------
把下载的乱名论文 PDF (1-s2.0-xxx.pdf / download(3).pdf / SSRN-id.pdf ...)
批量改成  作者_年份_标题.pdf。

原理: 用 pdf2doi 从 PDF 提取 DOI / arXiv-id, 再查准确的标题/作者/年份
      (走 Crossref / arXiv 官方 API, 免费、无需 key)。提不到就安全跳过, 绝不乱改。

三种用法:
  1) 双击 exe(最省事)       —— 窗口会提示你把文件夹拖进来, 先看预览再确认。
  2) 把文件夹拖到 exe 图标上 —— 同样先预览、再确认。
  3) 命令行:
        PaperTidy.exe <文件夹>            # 预览 -> 确认 -> 改名
        PaperTidy.exe <文件夹> --dry-run  # 只预览, 不动文件
        PaperTidy.exe <文件夹> --yes      # 不问直接改(给会脚本的人)

依赖(源码运行时): pip install pdf2doi   (需联网查 Crossref/arXiv, 免费无需 key)
"""
import os
import re
import sys
import json
import argparse

for _s in ("stdin", "stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8")
    except Exception:
        pass


def sanitize(text: str) -> str:
    text = re.sub(r'[\\/:*?"<>|\r\n\t]', "", str(text))
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip(" .")


def _first_author_surname(vi: dict):
    authors = vi.get("authors") or vi.get("author")
    if not isinstance(authors, list) or not authors:
        return None
    a0 = authors[0]
    if isinstance(a0, dict):
        if a0.get("family"):
            return sanitize(a0["family"])
        name = a0.get("name") or a0.get("literal") or ""
    else:
        name = str(a0)
    name = name.strip()
    if not name:
        return None
    return sanitize(name.split()[-1])


def _year(vi: dict):
    for key in ("published", "year", "created", "date", "issued", "published-print"):
        val = vi.get(key)
        if val:
            m = re.search(r"(19|20)\d{2}", str(val))
            if m:
                return m.group(0)
    return None


def extract_meta(path: str):
    import pdf2doi
    try:
        pdf2doi.config.set("verbose", False)
    except Exception:
        pass
    try:
        result = pdf2doi.pdf2doi(path)
    except Exception:
        return None
    if isinstance(result, list):
        result = result[0] if result else None
    if not result:
        return None
    vi = result.get("validation_info")
    if isinstance(vi, str):
        try:
            vi = json.loads(vi)
        except Exception:
            vi = {}
    if not isinstance(vi, dict):
        return None
    title = vi.get("title")
    if isinstance(title, list):
        title = title[0] if title else None
    if not title or not str(title).strip():
        return None
    return {"title": str(title).strip(), "author": _first_author_surname(vi), "year": _year(vi)}


def build_name(meta: dict, max_title_len: int = 90) -> str:
    parts = []
    if meta.get("author"):
        parts.append(meta["author"])
    if meta.get("year"):
        parts.append(meta["year"])
    parts.append(sanitize(meta["title"])[:max_title_len].strip())
    return "_".join(p for p in parts if p) + ".pdf"


def unique_path(folder: str, name: str, taken: set) -> str:
    base, ext = os.path.splitext(name)
    cand = name
    i = 2
    while os.path.exists(os.path.join(folder, cand)) or cand.lower() in taken:
        cand = f"{base}_{i}{ext}"
        i += 1
    taken.add(cand.lower())
    return cand


def plan_renames(folder: str):
    """对文件夹里每个 PDF 只查一次元数据, 生成改名计划(不动文件)。"""
    pdfs = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))
    plan = []
    taken = set()
    for f in pdfs:
        path = os.path.join(folder, f)
        try:
            meta = extract_meta(path)
        except Exception as e:
            plan.append({"old": f, "new": None, "action": "err", "note": str(e)[:60]})
            continue
        if not meta:
            plan.append({"old": f, "new": None, "action": "skip", "note": "提不到可靠 DOI/标题, 不乱改"})
            continue
        new_name = build_name(meta)
        if new_name == f:
            plan.append({"old": f, "new": f, "action": "ok", "note": "名字已规范"})
            continue
        new_name = unique_path(folder, new_name, taken)
        note = "" if meta.get("author") else "作者未取到, 省略"
        plan.append({"old": f, "new": new_name, "action": "rename", "note": note})
    return plan


def print_plan(plan, folder, dry_run):
    print("\n=== PaperTidy · %s ===" % ("预览(dry-run)" if dry_run else "改名计划"))
    print(f"目录: {os.path.abspath(folder)}")
    print(f"发现 {len(plan)} 个 PDF\n")
    for item in plan:
        act = item["action"]
        if act == "rename":
            tail = f"  ({item['note']})" if item["note"] else ""
            print(f"[改名] {item['old']}\n    -> {item['new']}{tail}")
        elif act == "ok":
            print(f"[已好] {item['old']}  ({item['note']})")
        elif act == "skip":
            print(f"[跳过] {item['old']}  ({item['note']})")
        elif act == "err":
            print(f"[出错] {item['old']}  ({item['note']})")
    total = len(plan)
    ok = sum(1 for i in plan if i["action"] in ("rename", "ok"))
    skip = sum(1 for i in plan if i["action"] == "skip")
    err = sum(1 for i in plan if i["action"] == "err")
    to_rename = sum(1 for i in plan if i["action"] == "rename")
    print("\n" + "=" * 56)
    print(f"共 {total} 个 | 可改名 {to_rename} | 已规范 {ok - to_rename} | 跳过 {skip} | 出错 {err}")
    print("=" * 56)
    return to_rename


def apply_plan(folder, plan):
    done = 0
    for item in plan:
        if item["action"] == "rename":
            try:
                os.rename(os.path.join(folder, item["old"]), os.path.join(folder, item["new"]))
                done += 1
            except Exception as e:
                print(f"[改名失败] {item['old']}  ({str(e)[:60]})")
    return done


def _run(args, interactive):
    folder = args.folder
    if folder is None:
        print("=" * 56)
        print(" PaperTidy · 论文 PDF 批量改名(作者_年份_标题)")
        print("=" * 56)
        folder = input("\n把要整理的文件夹拖到本窗口再按回车, 或直接粘贴路径:\n> ").strip().strip('"').strip("'")
    if not folder:
        print("没给文件夹, 退出。")
        return
    folder = os.path.abspath(folder)
    if not os.path.isdir(folder):
        print(f"[错误] 文件夹不存在: {folder}")
        return

    print("\n正在读取 PDF 元数据(需联网查 Crossref/arXiv, 请稍候)……")
    plan = plan_renames(folder)
    to_rename = print_plan(plan, folder, dry_run=args.dry_run)

    if args.dry_run:
        print("\n(预览模式, 文件一个都没动。确认无误后去掉 --dry-run, 或直接双击按提示确认即可真改。)")
        return
    if to_rename == 0:
        print("\n没有需要改名的文件, 收工。")
        return
    if not args.yes:
        ans = input(f"\n以上 {to_rename} 个将被改名。确认?(直接回车=确认 / 输入 n=取消): ").strip().lower()
        if ans not in ("", "y", "yes"):
            print("已取消, 一个文件都没动。")
            return
    done = apply_plan(folder, plan)
    print(f"\n✓ 完成, 已改名 {done} 个文件。")


def main():
    ap = argparse.ArgumentParser(description="PaperTidy — PDF 文献批量按元数据改名")
    ap.add_argument("folder", nargs="?", default=None, help="装 PDF 的文件夹(不给则双击后交互输入)")
    ap.add_argument("--dry-run", action="store_true", help="只预览, 不真改")
    ap.add_argument("-y", "--yes", action="store_true", help="不询问直接改(给会命令行的人)")
    ap.add_argument("--no-pause", action="store_true", help="结束不暂停(脚本调用时用)")
    args = ap.parse_args()

    # 交互模式判定: 没给文件夹(多半是双击), 或给了文件夹但没带 --dry-run/--yes(多半是拖拽)
    interactive = (args.folder is None) or not (args.dry_run or args.yes)

    try:
        _run(args, interactive)
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
