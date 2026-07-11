# paper2md · 论文 PDF 转 Markdown skill

> 把 PDF 论文转成规整 Markdown——喂 AI、进 Obsidian／Notion 做笔记、全文检索都需要这一步。
> 这是同一个工具的 **skill 版**：不是软件，是给 AI 的一份「带规矩的说明书」，复制即装、粘贴即用。
> **只转格式，内容一字不动**：不总结、不改写、不翻译。

---

## 这是什么 / 给谁用

想把 PDF 论文喂给 AI，或在 Obsidian／Notion 里做全文笔记检索，第一步都是「PDF → 可编辑文本」。直接从 PDF 复制粘贴大家都见过：断行乱序、表格糊成一团。

**paper2md 专治这一步。** 它把 PDF 转成规整的 Markdown：标题层级（`#`／`##`／`###`）、段落、列表照排；简单表格转成 Markdown 表格；图片可选提取到子目录并用相对路径引用。

差异点在护栏：直接让 AI「把这篇 PDF 整理成 md」，它常自作主张帮你总结、翻译、删段。本 skill 把「只搬格式、绝不动内容」写进 [`SKILL.md`](./SKILL.md) 铁律区——装上之后你的 AI 每次都自动遵守：**输出忠实原文，一个字不改**。

适合：所有要把论文 PDF 转成文本的社科／科研人。核心依赖只有一个离线 Python 库 `pymupdf4llm`。

---

## 两种用法

### 用法①：skill 口令版（让你的 AI 来转）🔌

把下面这句话原样发给你的 agent（Claude Code／Codex 等）：

> 请安装一个 GitHub skill：仓库是 HUIHUI59/openScientificTool，skill 在 skills/paper2md 目录。把该目录复制到你的 skills 目录（如 `~/.claude/skills/paper2md`），装好后我新开窗口使用。

装好后这样用：

> 用 paper2md 把这篇 PDF 转成 md：`C:\论文\paper.pdf`

没有 agent 也行：把 [`SKILL.md`](./SKILL.md) 全文复制粘贴给**能跑代码**的 AI，补一句「用以上规则把这个 PDF 转成 md」+ 路径即可。（纯聊天、不能跑代码的网页 AI 转不了，请转用法②。）

### 用法②：exe 双击版（不装 Python，双击就转）🖱️

不想碰 AI、也不想配 Python 的话，用同仓库 [`Paper2MD/`](../../Paper2MD/) 的双击 exe：到本仓库 **Releases** 页下载 `Paper2MD.exe`，把 PDF 文件或文件夹拖进窗口按回车即转。用法详见 [`Paper2MD/README.md`](../../Paper2MD/README.md)。

> **两版同源同铁律**：skill 版和 exe 版是同一套逻辑（`pymupdf4llm.to_markdown`），只转格式、不动内容、不做 OCR、只读原 PDF。区别只是入口——skill 版让 AI 代跑（适合已经在用 AI 的人），exe 版双击即用（适合装不上环境的人）。互相指路，按手头条件挑一个。

---

## 铁律（写进 SKILL.md，装上即生效）

1. **只转格式，内容一字不动**——不总结、不改写、不翻译、不润色、不删减，输出忠实原文。
2. **不做 OCR**——扫描件／图片型 PDF 无文本层，如实提示不支持，绝不硬转乱码。
3. **只读原 PDF，新建输出**——不改、不移、不删原文件。
4. **本地转换，不上传**——论文稿件不出你的电脑。

---

## 目录结构

```text
paper2md/
├── SKILL.md    # skill 本体：铁律 + 工作流 + 可直接跑的转换代码模板（挂上 RED Skill 的就是它）
└── README.md   # 本文件 · 说明书
```

> 打磨好的完整参考实现（进度打印、批量、命令行开关）在同仓库 [`Paper2MD/paper2md.py`](../../Paper2MD/paper2md.py)，也是 exe 双击版的源码。

---

## 理念（HITL，人在回路）

AI／脚本只管把格式搬规整，**内容、数据、结论永远是原文的**——这条护栏焊死在 SKILL.md 铁律区。复杂表格是尽力还原，重要数据请对照原文核对后再用。

---

## License

[Apache-2.0](../../LICENSE)（同仓库根）。随便用、随便改，保留版权声明即可。
