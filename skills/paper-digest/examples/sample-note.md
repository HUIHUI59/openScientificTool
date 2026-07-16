# 真实产出样例（非虚构）

> 本卡是 paper-digest 对一篇**真实开放获取论文**（PLOS ONE, CC-BY 4.0）的完整产出：
> Klar et al. (2020), DOI: 10.1371/journal.pone.0229446（DOI 可在 CrossRef 自行核验）。
> 产出后全部 38 条锚点经逐页回读核对通过。**这不改变铁律 5：拿到任何一份笔记，
> 锚点都请你自己再抽查几条。**

---

# 精读笔记 ·《Using social media to promote academic research: Identifying the benefits of twitter for sharing academic work》

- **作者**: Samara Klar, Yanna Krupnikov, John Barry Ryan, Kathleen Searles, Yotam Shmargad
- **年份 / 期刊**: 2020 / PLOS ONE
- **DOI**: 10.1371/journal.pone.0229446
- **PDF 文件页数**: 15 页（读取工具口径）
- **论文类型**: 实证（观察数据：推文追踪＋文章人工编码＋引用数）
- **精读日期**: 2026-07-10
- **精读范围**: 全文（p.13–15 为参考文献与附录列表）

## ① 研究问题

- 核心问题 1：学者把论文"推"上 Twitter，到底有没有好处 —— [p.1]"we provide a broad empirical investigation of whether Twitter offers any advantage to academics who share their work via social media"
- 核心问题 2：这种"推"的好处是不是对所有学者均等——具体聚焦作者性别差异 —— [p.1]"we examine whether there are systematic differences in the types of scholars who most benefit from this push model"
- 核心问题 2 的展开：社交媒体是拉平学界层级，还是复制线下已有的偏差 —— [p.2]"We investigate whether social media serves as an equalizing force within academia by allowing academics to disseminate their work without the traditional gatekeeping of existing academic hierarchies"
- 研究缺口：既有性别差异研究基本都建立在"拉取"式传播上，"推送"场景没人系统查过 —— [p.3]"Yet much of the previous work on gender relies on the pull method: a scholarly audience finds research to cite, papers to include on syllabi, or speakers to invite to seminars"
- 研究假设：原文未提及明确假设（全文以上述研究问题驱动，未列 H1/H2）

## ② 理论框架

- 核心概念：科研传播的 pull（拉取）→ push（推送）模式转变，是全文分析框架 —— [p.2]"The benefit of Twitter (and other social media platforms) is that it shifts the dissemination of scientific research from a "pull" model to a "push" model"
- 两种模式的定义 —— [p.2]"A pull model requires people who are interested in ongoing scientific research to search through publications to obtain the information; a push model allows scholars to transmit the information more directly to potentially interested parties"
- 承接的学术争论：社交媒体复制还是消除结构性不平等 —— [p.2]"scholars debate whether social media replicate pre-existing structural inequalities"
- 作者对因果性的预先声明：推文与引用之间的因果联系在文献里尚有争议 —— [p.2]"While the causal connection between pushing research articles on Twitter and article citation rates is under debate"

## ③ 数据与方法

- 数据来源：2016 年发表在政治学＋传播学 6 本期刊上的全部文章 —— [p.3]"We began by creating a dataset of every article published in 2016 in the following academic journals"
- 期刊抽样方式：目的抽样，刻意覆盖不同影响因子层级 —— [p.3]"We selected journals based on a purposive sampling strategy: we deliberately chose a range of journals from two social science fields"
- 原始样本量：308 篇文章、576 位作者（去重后 552 位）—— [p.3]"these journals published a total of 308 articles, which were collectively written by 576 authors (or 552 unique authors)"
- 最终样本量：N=294 篇（剔除性别/职级无法识别的文章）—— [p.3]"This left us with a total of 294 articles in the final dataset"
- 样本构成：48% 的文章至少有一位女性作者 —— [p.3]"48 percent had at least one woman listed as an author"
- 编码方式：3 名研究助理对每篇文章编码作者数、性别、职级、院系排名、推特粉丝数、引用数、主题等 8 项 —— [p.3]"three different research assistants coded each article"
- 推文数据：检索到 191 条含文章链接的推文，覆盖 76 篇文章 —— [p.4]"we obtained 191 tweets that included a link to one of 76 unique articles"
- 转推者数据：549 个转推者中拿到 517 个的账号信息 —— [p.4]"we were able to obtain the handles of 517 out of the possible 549 retweeters"
- 核心自变量：% Women（女性作者占比）、作者数、两者交互项 —— [p.6]"(1) the percentage of the authors on an article who are women (% Women), (2) the total number of authors on an article (Number of Authors), and (3) the interaction of these two measures"
- 分析方法：因变量是计数且过度离散，改用负二项回归 —— [p.6]"A plot of the data, however, demonstrates an overdispersion problem"；[p.6]"Therefore, we estimate negative binomial models in Table 2"
- 引用数据：Web of Science，2018 年 8 月与 2019 年 7 月两个时点各取一次 —— [p.8]"we also collected the number of citations for each of the articles in our sample at two different points in time: August 2018 (soon after the tweets) and July 2019 (one year later)"
- 稳健性做法 1：用"第一作者是否女性"替换"% Women"重跑全部模型 —— [p.6]"we rerun all of these analyses but replace the percentage of women with a dummy indicator for whether the lead author is a woman"
- 稳健性做法 2：剔除极端影响点后重新分析 —— [p.9]"In S7 Appendix, we reanalyze our data excluding this outlying article"
- 分析软件：原文未提及

## ④ 核心发现

- 总发现（正向）：文章被推文提及与引用数正相关 —— [p.1]"article citations are positively correlated with tweets about the article"
- 总发现（性别）：没有证据显示作者性别影响研究在推特上的传播 —— [p.1]"we find little evidence to suggest that author gender affects the transmission of research in this new media"
- 推文层面无性别偏差 —— [p.8]"we see no evidence of a gender bias in the number of tweets received by the women authors in the journals in our sample"
- 方向相反的细节：单一男性作者的文章平均比单一女性作者的文章少收到 0.6 条初始推文 —— [p.7]"articles authored by one male author receive, on average, 0.6 fewer initial tweets than articles authored by a solo female author"
- 系数记录：总推文模型（Model 2）中 % Woman 系数 2.846、SE 0.780、Z 3.65 —— [p.7]"% Woman 1.587 0.623 2.55 2.846 0.780 3.65"（Table 2 原行：前三个数为 Model 1 的系数/SE/Z，后三个为 Model 2）
- 推文内容也无性别差异（语气/性质编码）—— [p.8]"We see no evidence of differences in content"
- 引用（2018 时点）：有没有被推过是关键，后续转推没有线性增益 —— [p.9]"receiving an initial tweet had a positive effect on citations, but each additional re-tweet did not have a linear effect on citation counts"
- 引用（2019 时点）：推文越多引用增长越持续 —— [p.9]"which shows continued growth in citations as the number of tweets increases"
- 剔除离群点后的量化：被推过至少 1 次的文章比 0 推文的多约 4 次引用 —— [p.9]"Articles that received even one initial tweet received 4 more citations"
- 但推文数量边际收益极小：50 条推文只比 1 条多约 0.5 次引用 —— [p.10]"having 50 tweets results in only one half more citations than 1 tweet"
- 引用层面同样无性别化传播模式 —— [p.10]"when we consider citations–rather than just tweets–we do not find any evidence of gendered dissemination patterns"
- 条件性细节：控制推文数后，女性作者占比与引用的正向关系只在 ≥3 位作者的文章中出现 —— [p.10]"as the percentage of women authors increases, the number of citations increases but only for papers with at least 3 authors"
- 结论句：最不容易被分享的是单一男性作者的文章 —— [p.11]"we find that articles that are least likely to be shared on Twitter are authored by a solo man"

## ⑤ 局限与作者自述不足

- 作者自述 1：作者性别靠编码员根据姓名/照片判断，可能有误差 —— [p.11]"a team of coders determined the author of each gender to the best of their ability"
- 作者自述 2：选取的领域（传播学/政治传播）本身性别差距可能低于其他领域 —— [p.12]"it is possible that we have focused on research areas (e.g. communication and political communication) where gender disparities are lower"
- 作者自述 3：只追踪了正式见刊的文章，没算 First View 在线期的推文 —— [p.12]"Another limitation may be that we tracked already published articles, rather than beginning with articles that appear in First View"
- 【我的疑问·非原文】全文是观察数据，推文与引用的正相关也可能由"论文本身质量/话题热度"同时驱动；作者在引言承认了因果争议（见 ②），但结论仍用了"benefit"这类带因果味的表述——用这篇文章时要自己把住"相关≠因果"这条线。
- 【我的疑问·非原文】样本只覆盖 2016 年、两个学科、6 本英文期刊，且推文是发表约两年后（2018-06）才回溯检索的，删号删推会漏计——外推到其他学科或非英语学界要谨慎。

## ⑥ 中英术语表

| 英文原文 | 中文 | 一句大白话（≤30字） | 首现页 |
|---|---|---|---|
| push model / pull model | 推送模式／拉取模式 | 推送=作者把成果送到读者眼前；拉取=读者自己来翻 | p.1 |
| purposive sampling | 目的抽样 | 不抽签，按研究目的刻意挑样本 | p.3 |
| impact factor | 影响因子 | 一本期刊文章平均被引多少次的打分 | p.3 |
| quote tweet | 引用转推 | 转发时自己再添一句话的那种转推 | p.5 |
| interaction (term) | 交互项 | 检验"A 的效果是否随 B 大小而变" | p.6 |
| dummy variable | 虚拟变量 | 只取 0/1 的开关变量，如"是/否某期刊" | p.6 |
| Poisson distribution | 泊松分布 | 描述"数次数"类数据的常用概率分布 | p.6 |
| overdispersion | 过度离散 | 数据比泊松假设更"散"：方差明显大于均值 | p.6 |
| negative binomial model | 负二项模型 | 计数数据太"散"时替代泊松回归的模型 | p.6 |
| marginal effect | 边际效应 | 其他都不动，这个变量动一点，结果动多少 | p.6 |
| influence point | 影响点 | 一个极端观测就能把回归线整个拽歪 | p.9 |
| First View | 在线抢先版 | 论文正式排期见刊前先挂网的版本 | p.12 |

---
抽查锚点 38 条 / 通过 38 条 / 删改 0 条（工作流第 4 步记录：全部 38 条锚点逐页回读核对＋其中 3 条人工并排对照）

> 本笔记是个人学习卡：锚点请自行抽查核对，内容不可直接用于任何提交文本。
