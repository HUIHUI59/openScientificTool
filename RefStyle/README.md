# RefStyle · 参考文献一键多格式排版器

> 给一个 `.bib` 文件，一键排成 **APA / MLA / Chicago / 国标 GB/T 7714** 四种参考文献格式，
> 写进一个 txt 里，**复制粘贴进论文即可**。不改你的原始 `.bib`。

```
你的.bib  ──►  你的_参考文献格式.txt
              ├─ APA · 美国心理学会(社科最常用)
              ├─ MLA · 现代语言学会
              ├─ Chicago · 芝加哥(作者-年份)
              └─ 国标 GB/T 7714-2015(中文期刊刚需)
```

（四种格式一次全排好，各占一段，挑你投稿要求的那种复制走。）

---

## 这是什么 / 给谁用

写论文到最后都要交一份**参考文献列表**，可期刊各有各的规矩：投社科期刊要 APA，投文科要 MLA，
国内中文期刊又得按**国标 GB/T 7714**。手动一条条调格式，标点、斜体、作者顺序改到头大。

**RefStyle 专治这个。** 你从文献管理软件导出一个 `.bib` 文件丢给它，它一次把里面所有文献
**同时排成 APA / MLA / Chicago / 国标四种**，存成一个 txt。你打开，按投稿要求挑一种，整段复制进论文。

适合：社科 / 人文 / 理工科的硕博、写文献综述或投稿的科研人员——
凡是「手里有一堆文献、要按某个格式凑出参考文献列表」的场景。**不需要你会写代码。**

---

## `.bib` 从哪来？(三大来源都能一键导出)

`.bib`（BibTeX 文件）就是一份「机器能读的文献清单」，主流工具都能一键导出：

- **Zotero**：选中文献 → 右键 **Export Items / 导出条目** → 格式选 **BibTeX** → 存成 `.bib`。
- **Google Scholar**：搜到文献 → 点「**引用 / Cite**」→ 选 **BibTeX** → 把内容存成 `.bib`。
- **知网 CNKI**：勾选文献 → **导出与分析 / 导出文献** → 选 **BibTeX** → 下载 `.bib`。

导出的 `.bib` 直接喂给 RefStyle 就行，不用手改。

---

## 用法①：双击运行（最省事，首推，不用装 Python）🖱️

1. 到本仓库 **Releases** 页面下载 `RefStyle.exe`（单文件，无需安装任何环境）。
2. **双击 `RefStyle.exe`**，会弹出一个黑色小窗口，提示：
   > 把你的 .bib 文件拖到本窗口再按回车, 或粘贴路径:
3. 把你的 `.bib` 文件直接**拖进那个黑窗口**（或手动粘贴路径），按回车。
4. 它会把四种格式**依次打印在窗口里**，并在 `.bib` 旁边生成一个
   **`你的_参考文献格式.txt`**——打开它复制粘贴进论文即可。
5. 结束后窗口停在「按回车键退出……」，看完再按回车关掉，**不会一闪而过**。

---

## 用法②：把 .bib 拖到 exe 图标上

懒得双击再拖窗口的话，可以**直接把 `.bib` 文件拖到 `RefStyle.exe` 的图标上松手**，
效果和用法①一样：四种格式一次排好、生成 txt。

---

## ⚠️ 首次运行可能弹「Windows 已保护你的电脑」/ 被杀软误报——正常现象

这个 exe 是个人做的、**没花钱买微软代码签名证书**，又是 PyInstaller 打包的，
所以 Windows SmartScreen 第一次会弹蓝色窗口，个别杀毒软件也可能误报——**这不是病毒，是"没签名"**。

- 蓝色窗口：点「**更多信息 / More info**」→「**仍要运行 / Run anyway**」。
- 介意的话，用下面「**从源码运行**」的方式，自己看代码更放心。

---

## 用法③：命令行运行（会用命令行的人）

打开 PowerShell 或 cmd，把 exe 拖进去，后面跟上你的 `.bib`：

```bat
:: 一次排出全部四种格式(默认)
RefStyle.exe "C:\我的\refs.bib"

:: 只要国标 GB/T 7714(中文期刊常用)
RefStyle.exe "C:\我的\refs.bib" --style gb

:: 只要某几种(逗号分隔)
RefStyle.exe "C:\我的\refs.bib" --style apa,mla
```

- `--style`：选格式，可填 `apa` / `mla` / `chicago` / `gb` / `all`（默认 `all` 四种全出，逗号可多选）。
- `--no-pause`：结束不暂停（被别的脚本调用时用）。
- 结果同时**打印在窗口**并**写入 `你的_参考文献格式.txt`**（和 `.bib` 放在同一个文件夹）。

---

## 用法④：从源码运行（会用 Python 的人）

```bash
pip install citeproc-py citeproc-py-styles bibtexparser
python refstyle.py "你的.bib"            # 四种全出
python refstyle.py "你的.bib" --style gb  # 只出国标
```

- Python 3.8+ 即可，依赖见 `requirements.txt`（三个：`citeproc-py` / `citeproc-py-styles` / `bibtexparser`）。
- 仓库里附了一个 `test.bib`（Putnam、Bourdieu、费孝通等公开文献）可以先拿它试跑。

---

## 原理（为什么它排出来不容易崩、不容易错）

1. **先稳解析**：用 [`bibtexparser`](https://github.com/sciunto-org/python-bibtexparser) 解析 `.bib`，
   顺手剔掉 Zotero 塞进来的 `file` / `abstract` 等**非引用字段**（这些常含 Windows 路径的反斜杠，
   会让老排版库崩），得到一份干净的文献数据。
2. **离线渲染**：用 [`citeproc-py`](https://github.com/citeproc-py/citeproc-py) +
   `citeproc-py-styles`（**离线自带 2400+ 种期刊 CSL 样式，含国标**）把每条文献渲染成对应格式，
   **全程不联网、不需要 API key**。
3. **补两个小瑕疵**：内建修掉「作者姓名后多一个句点」和「国标样式把英文标题错误降成小写」——
   让排出来的结果更贴近能直接用的样子。

---

## 已知限制

- **目前只吃 `.bib`**：其它格式（`.ris` / EndNote 等）暂不支持，先在导出时选 BibTeX。
- **中文文献建议用国标格式**：APA / MLA / Chicago 是为西文设计的，中文文献套上去标点会有点别扭；
  中文期刊本来也要求国标 GB/T 7714，用 `--style gb` 最合适。
- **个别条目可能标题重复**：如果某条原始 `.bib` **缺作者字段**，排版库可能把它显示成标题重复——
  这属于**源数据缺字段**的问题，不是排错；补上 `.bib` 里该条的 `author` 即可。
- 排版结果建议**投稿前对着期刊模板扫一眼**，AI 起稿、人来把关。

---

## License

[Apache-2.0](../LICENSE) · Copyright (c) 2026 HUIHUI59
