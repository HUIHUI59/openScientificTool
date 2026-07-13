#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CiteCheck — 参考文献打假体检器
--------------------------------
把你的参考文献清单(.bib 或纯文本)逐条拿 CrossRef 官方数据库过一遍:
DOI 是真是假、题目/作者/年份对不对得上、缺了哪些字段、格式统不统一,
出一份 ✅/⚠️/🔴 体检报告。

铁律(产品边界, 不可协商):
  ① 只体检你已有的条目, 绝不代找文献、绝不替观点配引用。
  ② 只出报告和修复建议, 不改你的任何文件(输入只读, 报告另存新文件)。
  ③ 报告不是论文内容, 不可粘进论文; 条目怎么改由你自己动手。
  ④ "无法核验"不等于"编造" —— 中文知网/万方文献大多不在 CrossRef 库内。

三种用法:
  1) 双击 exe(最省事)         —— 窗口提示你把 .bib/.txt 拖进来, 出报告。
  2) 把文件拖到 exe 图标上     —— 同样直接体检出报告。
  3) 命令行:
        CiteCheck.exe <清单文件>              # 体检并在旁边生成 _体检报告.txt
        CiteCheck.exe <清单文件> --no-pause   # 脚本调用时用, 结束不暂停

依赖(源码运行时): pip install requests   (bibtexparser 可选, 装了解析更稳)
数据源: CrossRef 官方免费 API(api.crossref.org), 无需注册、无需 key。
"""
import os
import re
import sys
import time
import difflib
import argparse
import datetime

for _s in ("stdin", "stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8")
    except Exception:
        pass

API = "https://api.crossref.org/works"
MAILTO = "phlee@g.dongseo.ac.kr"  # CrossRef 礼貌池(polite pool)标识, 免费 API 的礼貌用法
HEADERS = {"User-Agent": "CiteCheck/1.0 (https://github.com/HUIHUI59/openScientificTool; mailto:%s)" % MAILTO}
PAUSE_BETWEEN_CALLS = 1.0  # 逐条间隔 ≥1 秒, 不轰免费 API

IRON_RULES = [
    "① 只体检你已有的条目, 绝不代找文献、绝不替观点配引用",
    "② 只出报告和修复建议, 不改你的任何文件",
    "③ 报告不是论文内容, 不可粘进论文; 条目怎么改由你自己动手",
    "④ “无法核验”不等于“编造”(中文文献大多不在 CrossRef 库内)",
]

DOI_RE = re.compile(r'10\.\d{4,9}/[^\s"\'<>,;，；]+')
STATUS_MARK = {"pass": ("✅", "通过"), "warn": ("⚠️", "待核"), "risk": ("🔴", "高危")}


# ---------- 基础工具 ----------

def clean_doi(doi):
    doi = str(doi).strip()
    doi = re.sub(r'^(https?://(dx\.)?doi\.org/|doi\s*[:：]\s*)', '', doi, flags=re.I)
    return doi.rstrip('.,;)]}>。，；、')


def norm_text(s):
    s = re.sub(r'[{}]', '', str(s)).lower()
    s = re.sub(r'[^\w\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def title_sim(a, b):
    return difflib.SequenceMatcher(None, norm_text(a), norm_text(b)).ratio()


def title_in_text(title, text):
    """题目的关键词有多大比例出现在整条文本里(粘贴文本没有独立题目字段时用)。"""
    tokens = [w for w in norm_text(title).split() if len(w) > 2]
    if not tokens:
        return 0.0
    txt = norm_text(text)
    return sum(1 for w in tokens if w in txt) / len(tokens)


def years_in(text):
    return set(re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)', text))


def has_chinese(text):
    return bool(re.search(r'[一-鿿]', text))


# ---------- CrossRef 调用(礼貌池 + 间隔) ----------

def _get(url, params=None):
    import requests
    time.sleep(PAUSE_BETWEEN_CALLS)
    return requests.get(url, params=params, headers=HEADERS, timeout=25)


def crossref_doi(doi):
    """返回 ('ok', message) / ('notfound', None) / ('error', 错误说明)。"""
    try:
        from urllib.parse import quote
        r = _get(API + "/" + quote(doi, safe="/"))
        if r.status_code == 404:
            return "notfound", None
        if r.status_code == 200:
            return "ok", r.json()["message"]
        return "error", "HTTP %s" % r.status_code
    except Exception as e:
        return "error", str(e)[:80]


def crossref_fuzzy(query):
    """模糊检索, 返回 ('ok', items) / ('error', 错误说明)。"""
    try:
        r = _get(API, params={"query.bibliographic": query[:300], "rows": 3, "mailto": MAILTO})
        if r.status_code == 200:
            return "ok", r.json()["message"].get("items", [])
        return "error", "HTTP %s" % r.status_code
    except Exception as e:
        return "error", str(e)[:80]


def msg_title(msg):
    t = msg.get("title") or []
    return str(t[0]).strip() if t else ""


def msg_year(msg):
    for k in ("published-print", "published-online", "issued", "created"):
        try:
            y = msg[k]["date-parts"][0][0]
            if y:
                return int(y)
        except Exception:
            continue
    return None


def msg_first_author(msg):
    for a in msg.get("author") or []:
        if a.get("family"):
            return str(a["family"])
    return None


# ---------- 解析: .bib 与纯文本 ----------

FIELD_RE = re.compile(r'([\w-]+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|"[^"]*"|[^,\n]+)', re.S)


def _bib_blocks(text):
    blocks, i = [], 0
    while True:
        m = re.search(r'@\w+\s*\{', text[i:])
        if not m:
            break
        start = i + m.start()
        k, depth = i + m.end() - 1, 0
        while k < len(text):
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        blocks.append(text[start:k + 1])
        i = k + 1
    return blocks


def parse_bib(text):
    entries = []
    for block in _bib_blocks(text):
        head = re.match(r'@(\w+)\s*\{\s*([^,\s]*)', block)
        etype = head.group(1).lower() if head else "misc"
        if etype in ("comment", "preamble", "string"):
            continue
        body = block[block.index(",") + 1:] if "," in block else ""
        fields = {}
        for fm in FIELD_RE.finditer(body):
            val = fm.group(2).strip().strip('{}"').strip()
            fields[fm.group(1).lower()] = re.sub(r'\s+', ' ', val)
        doi = clean_doi(fields.get("doi", "")) if fields.get("doi") else ""
        if not doi:
            m2 = DOI_RE.search(fields.get("url", "") or "")
            doi = clean_doi(m2.group(0)) if m2 else ""
        entries.append({
            "raw": block, "type": etype, "fields": fields, "doi": doi,
            "title": fields.get("title", ""), "year": fields.get("year", "").strip(),
            "author": fields.get("author", ""),
            "head": (fields.get("author", "").split(" and ")[0] + " " + fields.get("year", "") + " " + fields.get("title", "")).strip(),
        })
    return entries


def parse_plaintext(text):
    text = text.replace("\r\n", "\n")
    blocks = [b.strip() for b in re.split(r'\n\s*\n', text) if b.strip()]
    if len(blocks) == 1 and blocks[0].count("\n") >= 2:
        blocks = [l.strip() for l in blocks[0].split("\n") if l.strip()]
    entries = []
    for b in blocks:
        raw = re.sub(r'^\s*(\[\d+\]|\d+\s*[.、)])\s*', '', b)  # 去掉 [1] / 1. 编号
        m = DOI_RE.search(raw)
        ys = sorted(years_in(raw))
        entries.append({
            "raw": raw, "type": "text", "fields": {}, "doi": clean_doi(m.group(0)) if m else "",
            "title": "", "year": ys[0] if len(ys) == 1 else "", "author": "", "head": raw,
        })
    return entries


# ---------- 体检: 真伪 / 一致性 ----------

def check_entry(e):
    """返回 (status, method, findings, advice)。status: pass/warn/risk。"""
    findings, advice = [], []
    status = "pass"
    if e["doi"]:
        method = "DOI 直查(%s)" % e["doi"]
        st, msg = crossref_doi(e["doi"])
        if st == "notfound":
            return ("risk", method,
                    ["DOI 在 CrossRef 返回 404 —— 查无此号, 疑似编造或抄写错误"],
                    ["先自己到 doi.org 粘贴该 DOI 复核一次; 确认不存在就回到原始出处找正确 DOI(本工具不代找)"])
        if st == "error":
            return ("warn", method,
                    ["CrossRef 服务暂不可用(%s), 本条未核验" % msg],
                    ["稍后重跑一次; 未核验不代表有问题"])
        ct, cy, ca = msg_title(msg), msg_year(msg), msg_first_author(msg)
        hard = []  # 明显不一致 → 🔴
        sim = title_sim(e["title"], ct) if e["title"] else title_in_text(ct, e["raw"])
        if ct and sim < 0.5:
            hard.append("题目对不上(该 DOI 的官方题目: %s)" % ct)
        elif ct and sim < 0.85:
            findings.append("题目与官方记录有小出入, 请逐字核对(官方: %s)" % ct)
            status = "warn"
        if cy:
            if e["year"] and e["year"].isdigit():
                diff = abs(int(e["year"]) - cy)
                if diff == 0:
                    pass
                elif diff == 1:
                    findings.append("年份差 1 年(条目 %s / 官方 %s, 常见于在线发表与正式刊出之差), 请按投稿要求统一" % (e["year"], cy))
                    status = "warn" if status == "pass" else status
                else:
                    hard.append("年份对不上(条目 %s / 官方 %s)" % (e["year"], cy))
            else:
                ys = years_in(e["raw"])
                if ys and str(cy) not in ys:
                    hard.append("年份对不上(条目里出现 %s / 官方 %s)" % ("/".join(sorted(ys)), cy))
        if ca and norm_text(ca) and norm_text(ca) not in norm_text(e["author"] + " " + e["raw"]):
            findings.append("第一作者姓在条目里没找到(官方: %s), 请核对作者名单" % ca)
            status = "warn" if status == "pass" else status
        if hard:
            findings = hard + findings
            advice.append("该 DOI 真实存在但字段对不上 —— 常见于把真 DOI 拼给了另一篇文献; 按上面官方值逐字段核对后自己改")
            return "risk", method, findings, advice
        if status == "pass":
            findings.append("DOI 验真通过, 题目/年份与 CrossRef 官方记录一致")
        return status, method, findings, advice

    # 无 DOI → 模糊检索
    method = "无 DOI, 模糊检索(query.bibliographic)"
    q = " ".join(x for x in (e["title"] or e["raw"], e["author"], e["year"]) if x)
    st, items = crossref_fuzzy(q)
    if st == "error":
        return "warn", method, ["CrossRef 服务暂不可用(%s), 本条未核验" % items], ["稍后重跑一次; 未核验不代表有问题"]
    best, best_sim = None, 0.0
    for it in items or []:
        ct = msg_title(it)
        s = title_sim(e["title"], ct) if e["title"] else title_in_text(ct, e["raw"])
        if s > best_sim:
            best, best_sim = it, s
    if best is not None and best_sim >= 0.85:
        cy, cd = msg_year(best), best.get("DOI", "")
        ys = years_in(e["raw"]) if not e["year"] else {e["year"]}
        if cy and ys and str(cy) not in ys:
            return ("warn", method,
                    ["找到高相似命中但年份有出入(官方 %s): %s / DOI %s" % (cy, msg_title(best), cd)],
                    ["请自己到 doi.org 复核该 DOI 是否就是这篇; 确认后把年份和 DOI 一并改对"])
        findings.append("模糊检索高相似命中(相似度 %.2f): %s / DOI %s" % (best_sim, msg_title(best), cd))
        advice.append("条目缺 DOI; 请自己到 doi.org 核对上面命中是否就是这篇, 无误后把 DOI 补进条目")
        return "pass", method, findings, advice
    if has_chinese(e["raw"]):
        return ("warn", method,
                ["无法核验: 中文文献大多不在 CrossRef 收录范围, 本工具核不了它的真伪(不等于编造)"],
                ["请到知网/万方按题名检索自查该文献是否存在; 本报告只对这条做格式与缺项体检"])
    return ("warn", method,
            ["CrossRef 无高相似命中(最高相似度 %.2f) —— 无法核验(不等于编造, 图书/报告/未收录期刊都可能查不到)" % best_sim],
            ["请用 Google Scholar 或出版社官网按题名自查; 确认存在后把 DOI 或标准出处补齐"])


# ---------- 体检: 缺项 / 格式统一 ----------

REQUIRED_FIELDS = {
    "article": ["author", "title", "journal", "year", "volume", "pages"],
    "book": ["author", "title", "publisher", "year"],
    "incollection": ["author", "title", "booktitle", "publisher", "year"],
    "inproceedings": ["author", "title", "booktitle", "year"],
    "phdthesis": ["author", "title", "school", "year"],
    "mastersthesis": ["author", "title", "school", "year"],
}


def missing_fields(e):
    if e["type"] == "text":
        return ["年份"] if not years_in(e["raw"]) else []
    req = REQUIRED_FIELDS.get(e["type"], ["author", "title", "year"])
    return [f for f in req if not e["fields"].get(f)]


def format_checks(entries):
    raws = [e["raw"] for e in entries]
    n, issues = len(raws), []
    if n < 2:
        return issues
    full = sum(1 for r in raws if re.search(r'[，。；：]', r))
    if 0 < full < n:
        issues.append("标点全角/半角混用: %d 条用了全角标点, 其余 %d 条用半角 —— 按投稿刊物要求统一成一种" % (full, n - full))
    if any(re.search(r'\bet al\.?', r, re.I) for r in raws) and any(re.search(r'[一-鿿]等[,，.。 ]', r) for r in raws):
        issues.append("作者省略写法混用: “et al.” 与 “等” 同时出现 —— 按投稿语言统一")
    url_style = sum(1 for r in raws if "doi.org/" in r)
    prefix_style = sum(1 for r in raws if re.search(r'(?<![/.\w])doi\s*[:：]', r, re.I))
    if url_style and prefix_style:
        issues.append("DOI 写法混用: %d 条写 https://doi.org/ 链接, %d 条写 “doi:” 前缀 —— 统一一种" % (url_style, prefix_style))
    if entries[0]["type"] == "text":
        enddot = sum(1 for r in raws if r.rstrip().endswith((".", "。")))
        if 0 < enddot < n:
            issues.append("尾标点不统一: %d 条以句号结尾, 其余 %d 条没有" % (enddot, n - enddot))
    else:
        comma = sum(1 for e in entries if "," in e["author"])
        plain = sum(1 for e in entries if e["author"] and "," not in e["author"])
        if comma and plain:
            issues.append("作者字段写法混用: %d 条是“姓, 名”式, %d 条是“名 姓”式 —— 统一一种" % (comma, plain))
    return issues


# ---------- 报告 ----------

def head_of(e, width=72):
    h = re.sub(r'\s+', ' ', e["head"]).strip() or re.sub(r'\s+', ' ', e["raw"]).strip()
    return h[:width] + ("…" if len(h) > width else "")


def build_report(path, entries, results, fmt_issues):
    L = []
    L.append("=" * 64)
    L.append(" CiteCheck · 参考文献体检报告")
    L.append("-" * 64)
    L.append(" 输入: %s (共 %d 条)" % (os.path.abspath(path), len(entries)))
    L.append(" 数据源: CrossRef 官方 API (api.crossref.org) · 生成: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    L.append(" 铁律: 只体检已有条目, 不代找文献; 本报告不是论文内容, 不可粘进")
    L.append("       论文; 每处修改请你自己核对官方值后动手, 本工具不改任何文件。")
    L.append("=" * 64)
    L.append("")
    L.append("—— 逐条体检 ——")
    L.append("")
    for i, (e, r) in enumerate(zip(entries, results), 1):
        mark, word = STATUS_MARK[r["status"]]
        L.append("[%d] %s %s | %s" % (i, mark, word, head_of(e)))
        L.append("    核验方式: %s" % r["method"])
        for f in r["findings"]:
            L.append("    发现: %s" % f)
        for a in r["advice"]:
            L.append("    建议: %s" % a)
        if r["missing"]:
            L.append("    缺项: %s" % ", ".join(r["missing"]))
        L.append("")
    L.append("—— 格式与缺项体检(整份清单) ——")
    L.append("")
    if fmt_issues:
        for x in fmt_issues:
            L.append("- %s" % x)
    else:
        L.append("- 未发现清单级的格式统一性问题")
    L.append("")
    L.append("—— 汇总 ——")
    cnt = {s: sum(1 for r in results if r["status"] == s) for s in ("pass", "warn", "risk")}
    L.append("✅ 通过 %d 条 | ⚠️ 待核 %d 条 | 🔴 高危 %d 条" % (cnt["pass"], cnt["warn"], cnt["risk"]))
    L.append("")
    L.append("说明: “无法核验”不等于“编造”—— 知网/万方收录的中文文献大多没有")
    L.append("DOI、不在 CrossRef 库内, 请到知网/万方按题名检索自查。报告里给出的")
    L.append("官方值与 DOI 都可以自己到 doi.org 验证, 不必信本工具的一面之词。")
    return "\n".join(L) + "\n"


# ---------- 主流程 ----------

def read_text(path):
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise RuntimeError("读不出文件编码")


def run(path):
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        print("[错误] 文件不存在: %s" % path)
        return
    text = read_text(path)
    is_bib = path.lower().endswith(".bib") or text.lstrip().startswith("@")
    entries = parse_bib(text) if is_bib else parse_plaintext(text)
    if not entries:
        print("[错误] 没解析出任何条目(空文件或格式认不出)。")
        return
    print("\n解析出 %d 条(%s)。开始逐条核验, 每条间隔 %.0f 秒礼貌使用免费 API, 请稍候……\n"
          % (len(entries), ".bib 文件" if is_bib else "纯文本清单", PAUSE_BETWEEN_CALLS))
    results = []
    for i, e in enumerate(entries, 1):
        status, method, findings, advice = check_entry(e)
        miss = missing_fields(e)
        if miss and status == "pass":
            status = "warn"
        results.append({"status": status, "method": method, "findings": findings, "advice": advice, "missing": miss})
        word = STATUS_MARK[status][1]
        first = findings[0] if findings else ""
        print("[%d/%d] [%s] %s\n        %s" % (i, len(entries), word, head_of(e, 56), first))
    fmt_issues = format_checks(entries)
    report = build_report(path, entries, results, fmt_issues)
    out = os.path.splitext(path)[0] + "_体检报告.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)
    cnt = {s: sum(1 for r in results if r["status"] == s) for s in ("pass", "warn", "risk")}
    print("\n" + "=" * 56)
    print("体检完成: 通过 %d | 待核 %d | 高危 %d | 清单格式问题 %d 项" % (cnt["pass"], cnt["warn"], cnt["risk"], len(fmt_issues)))
    print("报告已存到: %s" % out)
    print("(你的原文件一个字都没动; 改哪条、怎么改, 报告里有建议, 由你自己动手。)")
    print("=" * 56)


def main():
    ap = argparse.ArgumentParser(description="CiteCheck — 参考文献打假体检(只体检, 不代找, 不改文件)")
    ap.add_argument("file", nargs="?", default=None, help="参考文献清单(.bib 或 .txt; 不给则双击后交互输入)")
    ap.add_argument("--no-pause", action="store_true", help="结束不暂停(脚本调用时用)")
    args = ap.parse_args()

    interactive = args.file is None
    if interactive:
        print("=" * 60)
        print(" CiteCheck · 参考文献打假体检器")
        print("-" * 60)
        for rule in IRON_RULES:
            print(" 铁律 " + rule)
        print("=" * 60)
        args.file = input("\n把参考文献清单(.bib 或 .txt)拖到本窗口再按回车, 或粘贴路径:\n> ").strip().strip('"').strip("'")
        if not args.file:
            print("没给文件, 退出。")
    try:
        if args.file:
            run(args.file)
    except KeyboardInterrupt:
        print("\n已取消。")
    except Exception as e:
        print("\n[出错] %s" % str(e)[:160])
    finally:
        if not args.no_pause:
            try:
                input("\n按回车键退出……")
            except Exception:
                pass


if __name__ == "__main__":
    main()
