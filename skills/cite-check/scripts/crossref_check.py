#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cite-check 参考实现 — CrossRef 验真 + 模糊检索比对
----------------------------------------------------
agent 可直接跑, 也可只借用 crossref_doi()/crossref_fuzzy() 两个函数,
字段解析(尤其是用户粘贴的乱格式文本)建议 agent 自己语义解析后再喂进来。

用法:
    python crossref_check.py refs.bib          # .bib 清单, 输出 Markdown 体检报告到 stdout
    python crossref_check.py refs.txt          # 纯文本清单(一条一行或空行分隔)
    python crossref_check.py refs.bib --json   # 机读 JSON 结果

铁律(与 SKILL.md 一致, 代码只负责体检):
    只体检已有条目, 不代找文献; 只出报告不改条目; 无法核验 ≠ 编造。

依赖: pip install requests   (bibtexparser 可选)
"""
import os
import re
import sys
import json
import time
import difflib
import argparse
import datetime

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8")
    except Exception:
        pass

API = "https://api.crossref.org/works"
MAILTO = "phlee@g.dongseo.ac.kr"  # CrossRef 礼貌池(polite pool)标识
HEADERS = {"User-Agent": "cite-check/1.0 (https://github.com/HUIHUI59/openScientificTool; mailto:%s)" % MAILTO}
PAUSE = 1.0  # 逐条间隔 ≥1 秒

DOI_RE = re.compile(r'10\.\d{4,9}/[^\s"\'<>,;，；]+')
MARK = {"pass": "✅ 通过", "warn": "⚠️ 待核", "risk": "🔴 高危"}


# ---------- 基础 ----------

def clean_doi(doi):
    doi = re.sub(r'^(https?://(dx\.)?doi\.org/|doi\s*[:：]\s*)', '', str(doi).strip(), flags=re.I)
    return doi.rstrip('.,;)]}>。，；、')


def norm_text(s):
    s = re.sub(r'[{}]', '', str(s)).lower()
    s = re.sub(r'[^\w\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def title_sim(a, b):
    return difflib.SequenceMatcher(None, norm_text(a), norm_text(b)).ratio()


def title_in_text(title, text):
    tokens = [w for w in norm_text(title).split() if len(w) > 2]
    if not tokens:
        return 0.0
    txt = norm_text(text)
    return sum(1 for w in tokens if w in txt) / len(tokens)


def years_in(text):
    return set(re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)', text))


def has_chinese(text):
    return bool(re.search(r'[一-鿿]', text))


# ---------- CrossRef(礼貌池 + 间隔) ----------

def _get(url, params=None):
    import requests
    time.sleep(PAUSE)
    return requests.get(url, params=params, headers=HEADERS, timeout=25)


def crossref_doi(doi):
    """('ok', message) / ('notfound', None) / ('error', 说明)"""
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
    """('ok', items) / ('error', 说明)"""
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


# ---------- 解析 ----------

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
        head = re.match(r'@(\w+)\s*\{', block)
        etype = head.group(1).lower() if head else "misc"
        if etype in ("comment", "preamble", "string"):
            continue
        body = block[block.index(",") + 1:] if "," in block else ""
        fields = {}
        for fm in FIELD_RE.finditer(body):
            fields[fm.group(1).lower()] = re.sub(r'\s+', ' ', fm.group(2).strip().strip('{}"').strip())
        doi = clean_doi(fields.get("doi", "")) if fields.get("doi") else ""
        if not doi:
            m2 = DOI_RE.search(fields.get("url", "") or "")
            doi = clean_doi(m2.group(0)) if m2 else ""
        entries.append({"raw": block, "type": etype, "fields": fields, "doi": doi,
                        "title": fields.get("title", ""), "year": fields.get("year", "").strip(),
                        "author": fields.get("author", "")})
    return entries


def parse_plaintext(text):
    text = text.replace("\r\n", "\n")
    blocks = [b.strip() for b in re.split(r'\n\s*\n', text) if b.strip()]
    if len(blocks) == 1 and blocks[0].count("\n") >= 2:
        blocks = [l.strip() for l in blocks[0].split("\n") if l.strip()]
    entries = []
    for b in blocks:
        raw = re.sub(r'^\s*(\[\d+\]|\d+\s*[.、)])\s*', '', b)
        m = DOI_RE.search(raw)
        ys = sorted(years_in(raw))
        entries.append({"raw": raw, "type": "text", "fields": {}, "doi": clean_doi(m.group(0)) if m else "",
                        "title": "", "year": ys[0] if len(ys) == 1 else "", "author": ""})
    return entries


# ---------- 体检 ----------

def check_entry(e):
    """返回 dict(status, method, findings, advice); status: pass/warn/risk"""
    findings, advice, status = [], [], "pass"
    if e["doi"]:
        method = "DOI 直查(%s)" % e["doi"]
        st, msg = crossref_doi(e["doi"])
        if st == "notfound":
            return {"status": "risk", "method": method,
                    "findings": ["DOI 在 CrossRef 返回 404 —— 查无此号, 疑似编造或抄写错误"],
                    "advice": ["先自己到 doi.org 复核; 确认不存在就回原始出处找正确 DOI(不代找)"]}
        if st == "error":
            return {"status": "warn", "method": method,
                    "findings": ["CrossRef 服务暂不可用(%s), 本条未核验" % msg],
                    "advice": ["稍后重跑; 未核验不代表有问题"]}
        ct, cy, ca = msg_title(msg), msg_year(msg), msg_first_author(msg)
        hard = []
        sim = title_sim(e["title"], ct) if e["title"] else title_in_text(ct, e["raw"])
        if ct and sim < 0.5:
            hard.append("题目对不上(该 DOI 官方题目: %s)" % ct)
        elif ct and sim < 0.85:
            findings.append("题目与官方记录有小出入, 请逐字核对(官方: %s)" % ct)
            status = "warn"
        if cy:
            if e["year"] and e["year"].isdigit():
                d = abs(int(e["year"]) - cy)
                if d == 1:
                    findings.append("年份差 1 年(条目 %s / 官方 %s, 常见于在线发表与正式刊出之差)" % (e["year"], cy))
                    status = "warn" if status == "pass" else status
                elif d >= 2:
                    hard.append("年份对不上(条目 %s / 官方 %s)" % (e["year"], cy))
            else:
                ys = years_in(e["raw"])
                if ys and str(cy) not in ys:
                    hard.append("年份对不上(条目里出现 %s / 官方 %s)" % ("/".join(sorted(ys)), cy))
        if ca and norm_text(ca) and norm_text(ca) not in norm_text(e["author"] + " " + e["raw"]):
            findings.append("第一作者姓在条目里没找到(官方: %s), 请核对作者名单" % ca)
            status = "warn" if status == "pass" else status
        if hard:
            return {"status": "risk", "method": method, "findings": hard + findings,
                    "advice": ["该 DOI 真实存在但字段对不上 —— 常见于真 DOI 拼给了另一篇文献; 按官方值逐字段核对后自己改"]}
        if status == "pass":
            findings.append("DOI 验真通过, 题目/年份与 CrossRef 官方记录一致")
        return {"status": status, "method": method, "findings": findings, "advice": advice}

    method = "无 DOI, 模糊检索(query.bibliographic)"
    q = " ".join(x for x in (e["title"] or e["raw"], e["author"], e["year"]) if x)
    st, items = crossref_fuzzy(q)
    if st == "error":
        return {"status": "warn", "method": method,
                "findings": ["CrossRef 服务暂不可用(%s), 本条未核验" % items], "advice": ["稍后重跑"]}
    best, best_sim = None, 0.0
    for it in items or []:
        s = title_sim(e["title"], msg_title(it)) if e["title"] else title_in_text(msg_title(it), e["raw"])
        if s > best_sim:
            best, best_sim = it, s
    if best is not None and best_sim >= 0.85:
        cy, cd = msg_year(best), best.get("DOI", "")
        ys = years_in(e["raw"]) if not e["year"] else {e["year"]}
        if cy and ys and str(cy) not in ys:
            return {"status": "warn", "method": method,
                    "findings": ["高相似命中但年份有出入(官方 %s): %s / DOI %s" % (cy, msg_title(best), cd)],
                    "advice": ["自己到 doi.org 复核是否同一篇; 确认后把年份与 DOI 一并改对"]}
        return {"status": "pass", "method": method,
                "findings": ["模糊检索高相似命中(相似度 %.2f): %s / DOI %s" % (best_sim, msg_title(best), cd)],
                "advice": ["条目缺 DOI; 自己到 doi.org 核对命中无误后把 DOI 补进条目"]}
    if has_chinese(e["raw"]):
        return {"status": "warn", "method": method,
                "findings": ["无法核验: 中文文献大多不在 CrossRef 收录范围(不等于编造)"],
                "advice": ["到知网/万方按题名检索自查; 本报告只对这条做格式与缺项体检"]}
    return {"status": "warn", "method": method,
            "findings": ["CrossRef 无高相似命中(最高相似度 %.2f) —— 无法核验(不等于编造)" % best_sim],
            "advice": ["用 Google Scholar 或出版社官网按题名自查; 确认存在后补齐 DOI 或标准出处"]}


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
    return [f for f in REQUIRED_FIELDS.get(e["type"], ["author", "title", "year"]) if not e["fields"].get(f)]


def format_checks(entries):
    raws = [e["raw"] for e in entries]
    n, issues = len(raws), []
    if n < 2:
        return issues
    full = sum(1 for r in raws if re.search(r'[，。；：]', r))
    if 0 < full < n:
        issues.append("标点全角/半角混用: %d 条全角, %d 条半角 —— 按投稿刊物统一" % (full, n - full))
    if any(re.search(r'\bet al\.?', r, re.I) for r in raws) and any(re.search(r'[一-鿿]等[,，.。 ]', r) for r in raws):
        issues.append("作者省略写法混用: “et al.” 与 “等” 同时出现 —— 按投稿语言统一")
    u = sum(1 for r in raws if "doi.org/" in r)
    p = sum(1 for r in raws if re.search(r'(?<![/.\w])doi\s*[:：]', r, re.I))
    if u and p:
        issues.append("DOI 写法混用: %d 条链接式, %d 条 “doi:” 前缀式 —— 统一一种" % (u, p))
    if entries[0]["type"] != "text":
        c = sum(1 for e in entries if "," in e["author"])
        pl = sum(1 for e in entries if e["author"] and "," not in e["author"])
        if c and pl:
            issues.append("作者字段写法混用: %d 条“姓, 名”式, %d 条“名 姓”式 —— 统一一种" % (c, pl))
    else:
        enddot = sum(1 for r in raws if r.rstrip().endswith((".", "。")))
        if 0 < enddot < n:
            issues.append("尾标点不统一: %d 条句号结尾, 其余 %d 条没有" % (enddot, n - enddot))
    return issues


# ---------- 输出 ----------

def head_of(e, width=70):
    h = e["title"] or e["raw"]
    h = re.sub(r'\s+', ' ', str(h)).strip()
    return h[:width] + ("…" if len(h) > width else "")


def main():
    ap = argparse.ArgumentParser(description="cite-check 参考实现(只体检, 不代找, 不改条目)")
    ap.add_argument("input", help="参考文献清单: .bib 或 .txt")
    ap.add_argument("--json", action="store_true", help="输出机读 JSON")
    args = ap.parse_args()

    text = None
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            with open(args.input, "r", encoding=enc) as f:
                text = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    if text is None:
        sys.exit("[错误] 读不出文件编码: %s" % args.input)

    is_bib = args.input.lower().endswith(".bib") or text.lstrip().startswith("@")
    entries = parse_bib(text) if is_bib else parse_plaintext(text)
    if not entries:
        sys.exit("[错误] 没解析出任何条目。")

    results = []
    for e in entries:
        r = check_entry(e)
        r["missing"] = missing_fields(e)
        if r["missing"] and r["status"] == "pass":
            r["status"] = "warn"
        r["entry"] = head_of(e)
        results.append(r)
    fmt_issues = format_checks(entries)
    cnt = {s: sum(1 for r in results if r["status"] == s) for s in ("pass", "warn", "risk")}

    if args.json:
        print(json.dumps({"total": len(entries), "summary": cnt, "format_issues": fmt_issues,
                          "results": results}, ensure_ascii=False, indent=2))
        return

    L = ["# 参考文献体检报告", "",
         "- 输入: %s, 共 %d 条" % (os.path.abspath(args.input), len(entries)),
         "- 数据源: CrossRef 官方 API(api.crossref.org) · 生成: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
         "- 铁律: 只体检已有条目, 不代找文献; 本报告不是论文内容, 不可粘进论文;",
         "  每处修改请你核对官方值后自己动手。", "", "## 逐条体检", ""]
    for i, r in enumerate(results, 1):
        L.append("### [%d] %s | %s" % (i, MARK[r["status"]], r["entry"]))
        L.append("- 核验方式: %s" % r["method"])
        for f in r["findings"]:
            L.append("- 发现: %s" % f)
        for a in r["advice"]:
            L.append("- 建议: %s" % a)
        if r["missing"]:
            L.append("- 缺项: %s" % ", ".join(r["missing"]))
        L.append("")
    L += ["## 格式与缺项体检(整份清单)", ""]
    L += ["- %s" % x for x in fmt_issues] or ["- 未发现清单级的格式统一性问题"]
    L += ["", "## 汇总", "",
          "✅ 通过 %d 条 | ⚠️ 待核 %d 条 | 🔴 高危 %d 条" % (cnt["pass"], cnt["warn"], cnt["risk"]), "",
          "说明: “无法核验”不等于“编造” —— 中文文献大多没有 DOI、不在 CrossRef",
          "库内, 请到知网/万方按题名检索自查。报告给出的官方值与 DOI 都可以自己",
          "到 doi.org 验证, 不必信本报告的一面之词。"]
    print("\n".join(L))


if __name__ == "__main__":
    main()
