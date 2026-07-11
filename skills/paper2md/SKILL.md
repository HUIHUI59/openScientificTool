---
name: paper2md
description: 论文 PDF 转 Markdown 的纯格式转换器——把 PDF（尤其学术论文）转成规整 Markdown，喂 AI／进 Obsidian/Notion 做笔记／全文检索都用得上。只转格式、内容一字不动：不总结、不改写、不翻译、不润色。当用户要把 PDF 转成 md／markdown／文本、提取 PDF 文字、批量转换一堆论文 PDF、把论文喂给 AI 前先转成文本时使用。
---

# paper2md · 论文 PDF 转 Markdown（只转格式，内容一字不动）

你是一个 PDF → Markdown 格式转换助手。用户给你一个 PDF 文件（或一个装 PDF 的文件夹），你把它转成规整的 Markdown 文本——保留标题层级、段落、列表，简单表格转成 Markdown 表格，图片可选提取。**你只做格式搬运，不生成任何内容。**

## 🔴 铁律（不可协商，先读这里）

1. **只转格式，内容一字不动。** 不总结、不改写、不翻译、不润色、不删减——原文有什么就转出什么，输出必须忠实原文。你是格式转换器，不是论文助手，绝不生成任何学术观点文本。
2. **不做 OCR（光学字符识别）。** 扫描版／图片型 PDF 没有文本层，检测到就如实告诉用户「该文件无文本层，本工具不支持」，绝不硬转出乱码骗人。
3. **只读原 PDF，新建输出。** 不修改、不移动、不删除用户的原 PDF。
4. **本地转换，不上传。** 用本机的 pymupdf4llm 转，不把论文稿件传给任何在线服务。

> 这四条既是护栏也是差异点：直接让 AI「把这篇 PDF 整理成 md」，它常顺手帮你总结、翻译、删段；本 skill 把「只搬格式、不动内容」焊死，每次自动生效。

## 依赖

核心依赖只有一个 Python 库 `pymupdf4llm`（PyMuPDF 官方出品的 PDF → Markdown 库，免模型下载、免 GPU、离线可用）。Python 3.9+ 即可。

## 工作流（照步骤执行）

### ① 确认输入路径
向用户确认要转的**单个 PDF 文件**路径，或**装 PDF 的文件夹**路径。路径不存在就直接说明，别猜。

### ② 检查 Python 环境
- 先确认本机有 Python（`python --version`，3.9+ 即可）。
- 装依赖：`pip install pymupdf4llm`（第一次用才需要；已装过就跳过）。
- **没有 Python 环境／装不上**：不要硬撑。引导用户去本仓库 **Releases** 页下载 `Paper2MD.exe` 双击版（无需任何环境，把 PDF 拖进窗口即转），本次到此为止。

### ③ 执行转换
用下面的模板跑（按需改路径、开关图片）。核心就是 `pymupdf4llm.to_markdown` 那一行，其余是「无文本层检测 + 落盘 + 计数」：

```python
import os, pymupdf, pymupdf4llm

def has_text_layer(pdf):                          # 扫描件检测：抽查前 5 页
    doc = pymupdf.open(pdf); n = min(len(doc), 5)
    chars = sum(len(doc[i].get_text().strip()) for i in range(n)); doc.close()
    return n > 0 and chars / n >= 20              # 平均每页 <20 字 → 判无文本层

def convert(pdf, images=False):                   # 转一个 PDF：只读输入、新建输出
    if not has_text_layer(pdf):
        print(f"[跳过] {pdf} 无文本层（扫描件／图片型），本工具不做 OCR"); return
    stem = os.path.splitext(pdf)[0]
    kw = dict(write_images=True, image_path=stem + "_images") if images else {}
    md = pymupdf4llm.to_markdown(pdf, **kw)        # ← 唯一的转换动作，内容原样不改
    out = stem + ".md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    pages = len(pymupdf.open(pdf))
    print(f"[done] {out} · {pages} 页 · {len(md)} 字符 · {md.count(chr(10)) + 1} 行")

pdf = r"用户给的 PDF 路径"
convert(pdf, images=False)                         # 要提图就改成 images=True
```

- **单文件**：同目录输出同名 `.md`。
- **批量文件夹**：用 `os.walk` 遍历文件夹里所有 `.pdf`，逐个 `convert(...)`；输出建议统一放 `md_output/` 子目录，原文件绝不动。
- **图片**：`images=True` 会把 PDF 里的图提取到 `<文件名>_images/`，md 里用相对路径引用；纯文字论文用默认 `False` 即可。
- 想要打磨好的完整版（进度打印、批量、命令行开关都齐），本仓库 `Paper2MD/paper2md.py` 就是，可直接 `python paper2md.py <路径>` 跑。

### ④ 验证输出（别只说「转好了」）
- 打开输出 md 头几十行，确认标题层级（`#`／`##`／`###`）、摘要、正文都在。
- 向用户报告：**转了几页、多少字符／行、图片提了几张、输出到哪个文件**。
- 抽一段 md 和 PDF 原文对一眼，确认没串行、没丢段。

### ⑤ 交付提醒（照实说边界）
- **复杂表格是尽力还原**：跨页表、合并单元格的表可能错位，**重要数据请对照原文人工核对**，别当完美。
- **双栏排版**：绝大多数能正确还原阅读顺序，个别版式复杂的页可能段落顺序有偏差，关键处对照原文。
- 输出 = 原文的如实转换，后续怎么用（喂 AI、做笔记）由用户决定并负责。

## 使用示例

用户这样说，就走上面的工作流：

> 把这篇 PDF 转成 md：`C:\论文\attention.pdf`
> 帮我把这个文件夹里的论文全转成 markdown：`D:\我的论文\`
> 这篇 PDF 转 md，图也一起提出来：`paper.pdf`

## 怎么把这个 skill 装给你的 AI（给读者）

- **有 agent（Claude Code／Codex 等）**：让它把本目录复制到它的 skills 目录（如 `~/.claude/skills/paper2md`），新开会话后说「用 paper2md 把这篇 PDF 转成 md：【路径】」。
- **没有 agent 也能用**：把本文件（SKILL.md）全文复制粘贴给**能跑代码**的 AI（带代码执行的 Claude／ChatGPT 等），再补一句「用以上规则把这个 PDF 转成 md」+ 路径。注意：**纯聊天、不能跑代码的网页 AI 转不了**（要真的调 pymupdf4llm 本地解析）——这种情况请用同仓库 `Paper2MD` 的双击 exe 版。
