# openScientificTool 🧰

> 我用 Claude Code 做的科研小工具合集。
> *Handy little research tools I built with Claude Code — from one non-CS researcher to another.*

一个**非 AI 科班**的社科类在读博士,在小红书边学边分享 AI 科研工具。踩着坑用 Claude Code 把一些自己每天要用的科研小工具做了出来,顺手开源放在这里。都是能直接跑、能真帮上忙的小东西——一起用,一起学。

---

## 这是什么 / 谁做的

- **是什么**:一批面向科研日常的小工具合集。每个工具只解决一个具体又烦人的小问题(比如"下载的论文文件名乱七八糟"),一个工具一个目录,拿来即用。
- **谁做的**:一个**非 AI 科班**的社科类在读博士 🎓。我不是程序员,是靠 Claude Code 一点点把想法做出来的——所以代码不追求花哨,追求"你也看得懂、也改得动"。
- **为什么开源**:我在小红书分享 AI 科研工具和前沿消息。与其只讲"这个工具好用",不如把东西直接给你。你能用上、能提意见,我也能接着学。

## 来小红书一起学习 👋

我在小红书叫 **挥挥挥挥挥**,主要分享 **AI 科研工具怎么用** + **前沿 AI 消息**。视角是社科硕博的真实科研场景——问卷、量表、回归、访谈、文献管理,而不是炼丹和写 CUDA。

> 📕 小红书主页:https://xhslink.com/m/92MwVP7PzPc

非科班的同路人,一起交流、一起踩坑、一起学习就好。欢迎来找我聊 🙌

## 工具清单

| 工具 | 一句话干什么 | 目录 |
|---|---|---|
| **PaperTidy** | 把下载的乱名论文 PDF 批量改名成「作者_年份_标题.pdf」 | [`./PaperTidy`](./PaperTidy) |
| **RefStyle** | 一个 `.bib` 直接排成 APA / MLA / Chicago / 国标 GB/T 7714 四种参考文献格式 | [`./RefStyle`](./RefStyle) |
| **Paper2MD** | 把 PDF 论文转成规整的 Markdown(标题层级/段落/表格/可选图片),双击即用不装 Python | [`./Paper2MD`](./Paper2MD) |
| **CiteCheck** | 参考文献逐条过 CrossRef 官方数据库核 DOI 真伪,揪出 AI 编造的假文献(只体检不代找) | [`./CiteCheck`](./CiteCheck) |
| **BlindCheck** | 投稿前扫出稿件里六类会暴露身份的位置(文件属性作者名/致谢/自引等),只出泄露清单,只读不改 | [`./BlindCheck`](./BlindCheck) |
| 更多工具陆续加入 🚧 | —— | —— |

## Skill 清单

Skill 不是软件,是给 AI 的一份「带规矩的说明书」——有 Claude Code / Codex 等 agent 的,把目录复制进它的 skills 目录即装;没有 agent 的,把 SKILL.md 全文粘贴给任意网页 AI 也能用。

| Skill | 一句话干什么 | 目录 |
|---|---|---|
| **paper2md** | 把 PDF 论文整段交给 AI 转成规整 Markdown(标题层级/段落/表格),只转格式不总结改写 | [`./skills/paper2md`](./skills/paper2md) |
| **slide-polish** | 把汇报 PPT 的版式交给 AI 重排,内容一个字不动 | [`./skills/slide-polish`](./skills/slide-polish) |
| **cite-check** | 参考文献整段粘给 AI,逐条过 CrossRef 核 DOI 真伪,只出体检报告和修复建议 | [`./skills/cite-check`](./skills/cite-check) |
| **blind-check** | 送审稿整段/文件交给 AI,扫出六类会暴露身份的位置,只出泄露清单,改稿自己动手 | [`./skills/blind-check`](./skills/blind-check) |
| **paper-digest** | 把一篇文献拆成结构化要点卡帮你读懂,只做阅读辅助,不产出任何可提交文本 | [`./skills/paper-digest`](./skills/paper-digest) |

## 仓库结构

一个工具一个子目录;每个子目录里都**统一**放好「自己的 README + 源码 + 依赖清单」,新工具照着摆就行。

```text
openScientificTool/
├── README.md            # 本文件 · 仓库总览与导航(你在这)
├── LICENSE              # Apache-2.0 许可证
│
├── PaperTidy/           # 工具① · 论文 PDF 批量规范改名
│   ├── README.md        #   ← 这个工具怎么用,看这里
│   ├── requirements.txt #   依赖清单
│   └── <源码>           #   源代码
│
├── RefStyle/            # 工具② · 参考文献多格式排版(APA/MLA/Chicago/国标)
│   ├── README.md        #   ← 这个工具怎么用,看这里
│   ├── requirements.txt #   依赖清单
│   └── <源码>           #   源代码
│
└── <下一个工具>/        # 以后每个新工具,都照这个样子摆:
    ├── README.md        #   必备 · 自己的说明书(装什么、怎么跑、示例)
    ├── requirements.txt #   必备 · 依赖清单
    ├── <源码>           #   源代码
    └── (可选) release/  #   如果打包了 exe,放下载/使用说明
```

**放新工具的约定(三件套)**:① 一个独立子目录;② 目录内一份自己的 `README.md`(装什么、怎么跑、给个示例);③ 一份 `requirements.txt`。打包了 exe 的,再补一段 release 下载说明。

## 怎么用

每个工具的**具体用法,看它自己目录下的 `README.md`**——仓库根这层只做导航。

以第一个工具 **PaperTidy** 为例:进入 [`./PaperTidy`](./PaperTidy),按目录里的 `README.md` 走——装一下 `requirements.txt` 里的依赖,把要整理的 PDF 丢进去跑,乱名论文就会被规范成「作者_年份_标题.pdf」。

## 理念 · 一起参与

- **HITL / 诚实派**:这些工具都是 **AI 起稿、人负责**。HITL(Human-in-the-Loop,人在回路 / 人来把关)——Claude Code 帮我写代码,但跑通、核对、对结果负责的是人。尤其涉及你的论文文件,建议先在几篇上试、确认没问题,再批量跑。
- **想要某个小工具?来提需求**:科研里有什么重复又烦人、"要是有个小工具就好了"的小事,欢迎来提——在 [GitHub Issue](https://github.com/HUIHUI59/openScientificTool/issues) 里说,或者直接**小红书私信我**。只要合适,我就用 Claude Code 试着做出来、并开源到这个仓库,一起把科研这点破事变简单点。
- **欢迎 issue / PR**:发现 bug、想加功能、有更顺手的写法,都欢迎开 issue 或提 PR。我也在学,咱们一起把它做得更好用。

## License

[Apache-2.0](./LICENSE)。随便用、随便改,记得保留版权声明就行。
