# 样例：一份盲审意见 → 拆解产出

> ⚠️ 素材说明：下面这份「审稿意见」是**为演示构造的模拟语料**——参考公开开放评审平台（OpenReview／PeerJ 等）上常见的意见结构与措辞、改写为社科问卷研究场景，**不对应任何真实论文、真实作者或真实审稿人**。
> 用途：让你看到 review-decoder 的输入长什么样、输出长什么样，以及「一条长意见拆成多个原子任务」的效果。

---

## 输入：用户粘贴的意见全文（模拟）

```text
Reviewer 1

1. The sample was drawn from a single university (N=312), which raises
serious concerns about generalizability. The authors must either collect
additional data from more diverse sites, or substantially temper their
claims. In addition, the response rate (38%) is not discussed at all, and
Table 2 reports 297 cases while the text says 312 — please check.

2. The choice of OLS is not justified. Given the nested structure of the
data (students within classes), why not a multilevel model? Please explain
this choice or re-estimate.

3. Minor: several typos in Section 3 ("questionaire", "regresion"); Figure 1
axis labels are too small to read.

Reviewer 2

1. The literature discussion overlooks recent work on survey fatigue
(2021-2024). This gap weakens the framing of Hypothesis 2.

2. The reliability of the adapted scale is not reported. Cronbach's alpha
for each subscale should be provided.
```

---

## 输出：review-decoder 产出的任务表

# 审稿意见拆解清单 · 问卷研究稿（演示）

> 拆解时间：2026-07-10 ｜ 意见来源：模拟盲审（演示语料）
> 🔒 本清单只做拆解整理，不含任何可直接提交的回复文字。

## 一、总览

- 审稿人：2 位（R1 / R2）；原始意见 5 条，拆出原子任务 **8** 条（R1 第 1 条一拆为三、第 3 条一拆为二）。
- 类别 × 优先级矩阵：

| | P0 不改就拒 | P1 重要 | P2 锦上添花 | 小计 |
|---|---|---|---|---|
| 数据 | 1 | 2 | 0 | 3 |
| 方法 | 1 | 0 | 0 | 1 |
| 写作 | 0 | 1 | 2 | 3 |
| 补充说明 | 0 | 1 | 0 | 1 |
| **合计** | **2** | **4** | **2** | **8** |

- ⚠️ 特别注意：R1-01（样本代表性）被审稿人用 must／serious 措辞点名，是全清单最重一条；R1-03 与 R2-02 都指向「数据报告不完整」，改的时候一起过。

## 二、任务清单（按 P0 → P1 → P2 排）

| 勾 | 编号 | 优先级 | 类别 | 工作量(预估) | 任务（一句话动作） | 备注 |
|---|---|---|---|---|---|---|
| [ ] | R1-01 | P0 | 数据 | 周级 | 决定补采多站点数据、或收窄结论适用范围（二选一，先与导师定方向） | must＋serious 措辞 |
| [ ] | R1-04 | P0 | 方法 | 天级 | 论证 OLS 的适用性；论证不成立则改用多层模型重新估计 | 见 taxonomy 判例 2，可能只需说明 |
| [ ] | R1-03 | P1 | 数据 | 小时级 | 核对表 2 的 297 与正文 312 的口径差异并统一 | 先核数据再定是不是笔误 |
| [ ] | R1-02 | P1 | 补充说明 | 小时级 | 准备回收率 38% 的处理依据与无应答分析材料 | |
| [ ] | R2-01 | P1 | 写作 | 天级 | 补充 2021-2024 年调查疲劳相关研究的讨论，重新支撑假设 2 的框架 | |
| [ ] | R2-02 | P1 | 数据 | 小时级 | 补报各分量表的 Cronbach's α | 见 taxonomy 判例 5：基于数据补算指标，数据在手时工作量小 |
| [ ] | R1-05 | P2 | 写作 | 小时级 | 修正第 3 节拼写错误（questionaire → questionnaire 等） | |
| [ ] | R1-06 | P2 | 写作 | 小时级 | 放大图 1 坐标轴标签字号 | |

### 原文锚点（编号对照，一字不差引用）

- **R1-01** ｜ 原文：
  > The sample was drawn from a single university (N=312), which raises serious concerns about generalizability. The authors must either collect additional data from more diverse sites, or substantially temper their claims.
- **R1-02** ｜ 原文：
  > In addition, the response rate (38%) is not discussed at all
- **R1-03** ｜ 原文：
  > Table 2 reports 297 cases while the text says 312 — please check.
- **R1-04** ｜ 原文：
  > The choice of OLS is not justified. Given the nested structure of the data (students within classes), why not a multilevel model? Please explain this choice or re-estimate.
- **R1-05** ｜ 原文：
  > Minor: several typos in Section 3 ("questionaire", "regresion")
- **R1-06** ｜ 原文：
  > Figure 1 axis labels are too small to read.
- **R2-01** ｜ 原文：
  > The literature discussion overlooks recent work on survey fatigue (2021-2024). This gap weakens the framing of Hypothesis 2.
- **R2-02** ｜ 原文：
  > The reliability of the adapted scale is not reported. Cronbach's alpha for each subscale should be provided.

## 三、依赖关系

- R1-01 定方向（补数据 or 收窄结论）→ R1-04 的模型重估是否需要新数据 → R2-02 的 α 若补了新数据要重算。
- R1-03 核对口径 → 决定它最终是数据修正还是笔误修正。

## 四、尾注（固定两句）

- 以上分类／优先级／工作量为拆解建议，请与导师或合作者确认后再执行。
- 本清单只做拆解整理，不含任何可直接提交的回复文字——回复怎么写，由你自己完成。

---

## 这个样例展示了什么

1. **一条拆多条**：R1 第 1 条一段话被拆成 R1-01（补样／收窄）、R1-02（回收率说明）、R1-03（数字核对）三个独立动作——这是本 skill 的核心能力。
2. **类别 ≠ 优先级**：R2-02 归数据类（taxonomy 判例 5）却只有小时级工作量；R1-01 同为数据类却是周级 P0。
3. **边界条目的处理**：R1-04 落在「补充说明 ↔ 方法」边界上，按 taxonomy 判例 2 归方法（最重动作），备注里留了降级可能。
