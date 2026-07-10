// openScientificTool · skills/slide-polish · scripts/demo.js — Apache-2.0(同仓库根 LICENSE)
//
// pptxgenjs 完整参考实现:deep-gold 深金主题 × 10 页,把 SKILL.md「页型库」9 种页型全走一遍
// (外加 1 页 addChart 柱状图页)。每段注释标注对应页型编号,照抄改内容即可。
// demo 素材:「社交媒体与青少年心理健康 · 研究现状汇报(组会分享)」,文献与数字真实可查:
//   - Twenge et al. (2018). Clinical Psychological Science, 6(1), 3-17.
//   - Orben & Przybylski (2019). Nature Human Behaviour, 3, 173-182.(0.4% 为该文真实结论)
//   - Orben, Dienlin & Przybylski (2019). PNAS, 116(21), 10226-10228.(UKHLS 面板)
//
// 跑法: npm install pptxgenjs && node demo.js  → 当前目录生成 demo-deck.pptx

const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 × 7.5 英寸宽屏
pres.title = "slide-polish demo · 研究现状汇报";

// ---------- 主题库 · deep-gold 深金(默认主题,hex 与 SKILL.md 主题库一致,勿改数值) ----------
const T = {
  bg:    "13140E", // 背景
  ink:   "F0EDE4", // 主字
  gold:  "C9A227", // 强调金 1
  gold2: "D9B33A", // 强调金 2(亮阶)
  muted: "928F80", // 次字
  line:  "3A392E", // 分隔线
  card:  "1C1D15", // 卡片底
};
// 字体:标题=思源宋体 / 正文=思源黑体;机器没装思源系时把两个值都换成 "Microsoft YaHei"
const F = { title: "Noto Serif SC", body: "Noto Sans SC" };

const W = 13.33, H = 7.5;

// 细节规范 · 页眉标签行:母题圆点 + 章节标签(字距拉开) + 细分隔线(全页唯一横线) + 大标题
function header(s, tag, title) {
  s.addShape(pres.shapes.OVAL, { x: 0.62, y: 0.66, w: 0.16, h: 0.16, fill: { color: T.gold } }); // 圆点母题
  s.addText(tag, { x: 0.9, y: 0.52, w: 8, h: 0.42, fontFace: F.body, fontSize: 12,
    bold: true, color: T.muted, charSpacing: 3, valign: "middle", margin: 0 });
  s.addShape(pres.shapes.LINE, { x: 0.62, y: 1.06, w: W - 1.24, h: 0, line: { color: T.line, width: 0.75 } });
  s.addText(title, { x: 0.6, y: 1.2, w: 12.1, h: 0.85, fontFace: F.title, fontSize: 30,
    bold: true, color: T.ink, valign: "middle", margin: 0 });
}
// 细节规范 · 右下页码:母题小圆 + 页码
function pageNum(s, n) {
  s.addShape(pres.shapes.OVAL, { x: W - 0.82, y: H - 0.6, w: 0.3, h: 0.3, fill: { color: T.card }, line: { color: T.line, width: 0.75 } });
  s.addText(String(n), { x: W - 0.82, y: H - 0.6, w: 0.3, h: 0.3, fontFace: F.body, fontSize: 10,
    bold: true, color: T.gold2, align: "center", valign: "middle", margin: 0 });
}
function newSlide() { const s = pres.addSlide(); s.background = { color: T.bg }; return s; }

// ============ 第 1 页 · 页型 1 封面页 ============
(() => {
  const s = newSlide();
  // 右侧 1/3 留白区放母题圆装饰(不用图片、不用艺术字)
  s.addShape(pres.shapes.OVAL, { x: 10.2, y: -1.8, w: 5.4, h: 5.4, fill: { color: T.card } });
  s.addShape(pres.shapes.OVAL, { x: 11.3, y: 4.4, w: 2.6, h: 2.6, fill: { color: T.gold, transparency: 82 } });
  s.addShape(pres.shapes.OVAL, { x: 0.9, y: 1.02, w: 0.4, h: 0.4, fill: { color: T.gold } });
  // 左上标签行(13-15pt,字距拉开)
  s.addText("组会分享 · 研究现状汇报", { x: 1.45, y: 0.98, w: 8, h: 0.5, fontFace: F.body,
    fontSize: 14, bold: true, color: T.gold2, charSpacing: 4, valign: "middle", margin: 0 });
  // 主标题 44-54pt,落在纵向约 1/3 处;标题用思源宋体
  s.addText("社交媒体使用\n与青少年心理健康", { x: 0.85, y: 2.0, w: 9.6, h: 2.5, fontFace: F.title,
    fontSize: 48, bold: true, color: T.ink, valign: "middle", margin: 0, lineSpacingMultiple: 1.08 });
  // 副标题 18pt 次字色
  s.addText("——「小效应」还是「大警报」?一场仍在进行的学术争论", { x: 0.9, y: 4.6, w: 10.5, h: 0.6,
    fontFace: F.body, fontSize: 18, color: T.muted, valign: "middle", margin: 0 });
  // 左下细竖条 + 汇报人/日期占位(铁律 2:不编造,留 ___ 用户自己填)
  s.addShape(pres.shapes.RECTANGLE, { x: 0.9, y: 5.9, w: 0.06, h: 0.95, fill: { color: T.gold } });
  s.addText([
    { text: "汇报人  ", options: { color: T.muted, fontSize: 13 } },
    { text: "___(你的名字)", options: { color: T.ink, fontSize: 15, bold: true, breakLine: true } },
    { text: "___(院系 · 方向)     ___(日期)", options: { color: T.muted, fontSize: 12 } },
  ], { x: 1.15, y: 5.85, w: 9, h: 1.05, fontFace: F.body, valign: "middle", margin: 0, lineSpacingMultiple: 1.25 });
})();

// ============ 第 2 页 · 页型 2 章节隔页 ============
(() => {
  const s = newSlide();
  // 超大章节号压左侧,低存在感处理(卡片底色近似的暗金);其余全留白,整页元素 ≤3
  s.addText("01", { x: 0.5, y: 1.4, w: 6.5, h: 4.6, fontFace: F.title, fontSize: 190,
    bold: true, color: T.card, outline: { size: 1, color: T.gold }, valign: "middle", margin: 0 });
  s.addShape(pres.shapes.OVAL, { x: 6.9, y: 3.42, w: 0.2, h: 0.2, fill: { color: T.gold } }); // 母题圆点
  s.addText("争论从哪来", { x: 7.25, y: 2.9, w: 5.6, h: 1.2, fontFace: F.title, fontSize: 38,
    bold: true, color: T.ink, valign: "middle", margin: 0 });
  s.addText("同一批数据,两派结论", { x: 7.28, y: 4.05, w: 5.6, h: 0.5, fontFace: F.body,
    fontSize: 15, color: T.muted, valign: "middle", margin: 0 });
  pageNum(s, 2);
})();

// ============ 第 3 页 · 页型 3 两栏对比页 ============
(() => {
  const s = newSlide();
  header(s, "01  争论从哪来", "两派观点:警报派 vs 谨慎派");
  // 左右两张等宽卡片(各约 42% 版宽,中缝留沟槽),阵营名用两档强调色区分
  const cards = [
    { x: 0.62, name: "「大警报」派", who: "代表:Twenge et al. (2018)", color: T.gold2, pts: [
      "iGen 世代抑郁与自伤指标上升,时间上与智能手机普及同步",
      "屏幕时间越长,幸福感指标越差(横断面相关)",
      "主张:立即限制青少年屏幕时间",
    ]},
    { x: 7.11, name: "「小效应」派", who: "代表:Orben & Przybylski (2019)", color: T.gold, pts: [
      "效应量极小,仅解释幸福感变异的约 0.4%",
      "分析自由度太大:同一数据可跑出上万种规格",
      "主张:先把测量与因果做扎实,再谈干预",
    ]},
  ];
  cards.forEach((c) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: c.x, y: 2.3, w: 5.6, h: 4.35, rectRadius: 0.1,
      fill: { color: T.card }, line: { color: T.line, width: 1 } });
    s.addText(c.name, { x: c.x + 0.35, y: 2.6, w: 4.9, h: 0.55, fontFace: F.title, fontSize: 20,
      bold: true, color: c.color, valign: "middle", margin: 0 });
    s.addText(c.who, { x: c.x + 0.35, y: 3.15, w: 4.9, h: 0.4, fontFace: F.body, fontSize: 11.5,
      italic: true, color: T.muted, valign: "middle", margin: 0 });
    c.pts.forEach((p, i) => {
      const y = 3.75 + i * 0.92;
      s.addShape(pres.shapes.OVAL, { x: c.x + 0.38, y: y + 0.12, w: 0.12, h: 0.12, fill: { color: c.color } });
      s.addText(p, { x: c.x + 0.66, y, w: 4.7, h: 0.85, fontFace: F.body, fontSize: 13.5,
        color: T.ink, valign: "top", margin: 0, lineSpacingMultiple: 1.12 });
    });
  });
  // 中缝小「VS」圆
  s.addShape(pres.shapes.OVAL, { x: 6.31, y: 4.12, w: 0.7, h: 0.7, fill: { color: T.bg }, line: { color: T.gold, width: 1.25 } });
  s.addText("VS", { x: 6.31, y: 4.12, w: 0.7, h: 0.7, fontFace: F.body, fontSize: 14,
    bold: true, color: T.gold2, align: "center", valign: "middle", margin: 0 });
  pageNum(s, 3);
})();

// ============ 第 4 页 · 页型 4 大数字页 ============
(() => {
  const s = newSlide();
  header(s, "02  关键证据", "把「效应量」摊开来看有多小");
  // 左侧:数字 80-120pt 当整页锚点,上方一行说明、下方一行来源
  s.addText("数字技术使用可解释的青少年幸福感变异", { x: 0.75, y: 2.45, w: 5.6, h: 0.5,
    fontFace: F.body, fontSize: 14, bold: true, color: T.gold2, valign: "middle", margin: 0 });
  s.addText([
    { text: "0.4", options: { fontFace: F.title, fontSize: 116, bold: true, color: T.ink } },
    { text: " %", options: { fontFace: F.title, fontSize: 54, bold: true, color: T.gold } },
  ], { x: 0.7, y: 3.0, w: 5.8, h: 2.3, valign: "middle", margin: 0 });
  s.addText("来源:Orben & Przybylski (2019). Nature Human Behaviour, 3, 173-182.",
    { x: 0.75, y: 5.5, w: 5.6, h: 0.4, fontFace: F.body, fontSize: 11, italic: true, color: T.muted, margin: 0 });
  // 右侧:配套要点收进小卡片(原文的日常类比)
  const anlg = [
    ["≈ 戴眼镜", "与幸福感的负关联,和屏幕使用体量相当"],
    ["≈ 吃土豆", "食用土豆与幸福感的关联也差不多大"],
    ["< 被欺凌 · 睡眠不足", "这些因素的影响远大于屏幕时间"],
  ];
  anlg.forEach((a, i) => {
    const y = 2.5 + i * 1.28;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.9, y, w: 5.75, h: 1.08, rectRadius: 0.1,
      fill: { color: T.card }, line: { color: T.line, width: 1 } });
    s.addShape(pres.shapes.OVAL, { x: 7.14, y: y + 0.47, w: 0.14, h: 0.14, fill: { color: T.gold } });
    s.addText([
      { text: a[0] + "\n", options: { fontSize: 15, bold: true, color: T.ink } },
      { text: a[1], options: { fontSize: 11.5, color: T.muted } },
    ], { x: 7.45, y, w: 5.05, h: 1.08, fontFace: F.body, valign: "middle", margin: 0, lineSpacingMultiple: 1.1 });
  });
  pageNum(s, 4);
})();

// ============ 第 5 页 · 页型 5 要点网格页(2×2) ============
(() => {
  const s = newSlide();
  header(s, "02  关键证据", "现有证据的四个局限");
  const grid = [
    ["横断面居多", "相关不等于因果:是社媒导致低落,还是低落的人更刷社媒?"],
    ["屏幕时间靠自报告", "自报告与手机日志实测相差可达数小时,测量误差巨大"],
    ["分析自由度太大", "同一数据换一种变量组合,能跑出方向相反的结论"],
    ["平均效应掩盖个体差异", "总体近零不代表对每个孩子都近零,高危亚群可能被平均掉"],
  ];
  grid.forEach((g, i) => {
    const x = 0.62 + (i % 2) * 6.2, y = 2.3 + Math.floor(i / 2) * 2.25;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.9, h: 1.95, rectRadius: 0.1,
      fill: { color: T.card }, line: { color: T.line, width: 1 } });
    // 角标序号 = 母题圆
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: y + 0.32, w: 0.46, h: 0.46, fill: { color: T.gold } });
    s.addText(String(i + 1), { x: x + 0.3, y: y + 0.32, w: 0.46, h: 0.46, fontFace: F.body,
      fontSize: 16, bold: true, color: T.bg, align: "center", valign: "middle", margin: 0 });
    s.addText(g[0], { x: x + 0.95, y: y + 0.26, w: 4.7, h: 0.55, fontFace: F.title, fontSize: 17,
      bold: true, color: T.ink, valign: "middle", margin: 0 });
    s.addText(g[1], { x: x + 0.95, y: y + 0.85, w: 4.7, h: 0.95, fontFace: F.body, fontSize: 12,
      color: T.muted, valign: "top", margin: 0, lineSpacingMultiple: 1.15 });
  });
  pageNum(s, 5);
})();

// ============ 第 6 页 · 页型 6 时间线页 ============
(() => {
  const s = newSlide();
  header(s, "03  下一步", "后续工作计划(供组会讨论)");
  // 一条水平细线贯穿版心中部 + 4 个母题圆节点等距分布
  const steps = [
    ["文献补齐", "把两派近三年新证据读完建档", false],
    ["数据申请", "申请 UKHLS 面板数据使用权限", true], // 当前节点:强调色放大
    ["模型与预注册", "固定效应模型,分析方案先预注册", false],
    ["组会汇报结果", "带初步结果回组会讨论", false],
  ];
  const lineY = 4.3, x0 = 1.3, gap = (W - 2.6) / 3;
  s.addShape(pres.shapes.LINE, { x: x0, y: lineY, w: W - 2.6, h: 0, line: { color: T.line, width: 1.5 } });
  steps.forEach((st, i) => {
    const cx = x0 + i * gap, r = st[2] ? 0.34 : 0.22;
    s.addShape(pres.shapes.OVAL, { x: cx - r / 2, y: lineY - r / 2, w: r, h: r,
      fill: { color: st[2] ? T.gold : T.card }, line: { color: st[2] ? T.gold2 : T.line, width: 1.25 } });
    s.addText(st[0], { x: cx - 1.5, y: lineY - 1.15, w: 3, h: 0.5, fontFace: F.body, fontSize: 15,
      bold: true, color: st[2] ? T.gold2 : T.ink, align: "center", valign: "bottom", margin: 0 });
    s.addText(st[1], { x: cx - 1.5, y: lineY + 0.35, w: 3, h: 0.85, fontFace: F.body, fontSize: 11.5,
      color: T.muted, align: "center", valign: "top", margin: 0, lineSpacingMultiple: 1.12 });
  });
  s.addText("时间节点:___(待与导师确认后填写)", { x: 0.62, y: 6.35, w: 8, h: 0.4,
    fontFace: F.body, fontSize: 11, italic: true, color: T.muted, margin: 0 }); // 铁律 2:不编造日期
  pageNum(s, 6);
})();

// ============ 第 7 页 · 页型 7 金句引用页 ============
(() => {
  const s = newSlide();
  // 左上超大引号(强调色,纯装饰);整页只有金句 + 出处
  s.addText("“", { x: 0.7, y: 0.4, w: 3, h: 2.4, fontFace: F.title, fontSize: 160,
    bold: true, color: T.gold, valign: "top", margin: 0 });
  s.addText("以现有证据的体量,数字技术使用对青少年幸福感的解释力,\n还不足以支撑当下的政策恐慌。",
    { x: 1.6, y: 2.5, w: 10.1, h: 2.4, fontFace: F.title, fontSize: 28, bold: true,
      color: T.ink, align: "center", valign: "middle", margin: 0, lineSpacingMultiple: 1.3 });
  s.addText("—— 据 Orben & Przybylski (2019) 结论意译,原文见 Nature Human Behaviour, 3, 173-182.",
    { x: 1.6, y: 5.2, w: 10.1, h: 0.5, fontFace: F.body, fontSize: 13, italic: true,
      color: T.muted, align: "center", valign: "middle", margin: 0 });
  pageNum(s, 7);
})();

// ============ 第 8 页 · 页型 8 表格页 ============
(() => {
  const s = newSlide();
  header(s, "04  证据地图", "三项关键研究横向比较");
  const th = { fontFace: F.body, fontSize: 12.5, bold: true, color: T.gold2, fill: { color: T.card }, valign: "middle" };
  const td = { fontFace: F.body, fontSize: 11, color: T.ink, valign: "middle" };
  const tdm = { ...td, color: T.muted };
  s.addTable([
    [{ text: "研究", options: th }, { text: "数据", options: th }, { text: "方法", options: th }, { text: "核心结论", options: th }],
    [{ text: "Twenge et al. 2018", options: td }, { text: "MtF + YRBSS(横断面)", options: tdm },
     { text: "相关分析", options: tdm }, { text: "屏幕时间与抑郁指标正相关", options: td }],
    [{ text: "Orben & Przybylski 2019", options: td }, { text: "三大数据集,N≈35.5 万", options: tdm },
     { text: "规格曲线分析", options: tdm }, { text: "仅解释幸福感变异约 0.4%", options: { ...td, bold: true, color: T.gold2 } }],
    [{ text: "Orben, Dienlin & Przybylski 2019", options: td }, { text: "UKHLS 面板,N≈1.2 万", options: tdm },
     { text: "纵向交叉滞后", options: tdm }, { text: "双向效应皆极小", options: td }],
  ], {
    x: 0.9, y: 2.35, w: 11.5, rowH: 0.72, // 版心约 85% 宽,行高 ≥0.4in
    border: { type: "solid", color: T.line, pt: 0.75 },
    fill: { color: T.bg }, align: "left", margin: 0.12,
  });
  s.addText("缩写:MtF=Monitoring the Future;YRBSS=Youth Risk Behavior Surveillance System;UKHLS=UK Household Longitudinal Study(英国家庭纵向研究)。",
    { x: 0.9, y: 5.75, w: 11.5, h: 0.4, fontFace: F.body, fontSize: 10, italic: true, color: T.muted, margin: 0 });
  pageNum(s, 8);
})();

// ============ 第 9 页 · 图表页(pptxgenjs addChart 柱状图;版式沿用大数字页思路:一页一图一结论) ============
(() => {
  const s = newSlide();
  header(s, "04  证据地图", "和日常因素放在同一把尺上比");
  s.addChart(pres.charts.BAR, [{
    name: "可解释的幸福感变异(%)",
    labels: ["戴眼镜", "吃土豆", "数字技术使用", "遭受欺凌"],
    values: [0.3, 0.4, 0.4, 4.3],
  }], {
    x: 0.9, y: 2.2, w: 11.5, h: 4.1,
    barDir: "col", barGapWidthPct: 80,
    chartColors: [T.muted, T.muted, T.gold, T.gold2], chartColorsOpacity: 100,
    catAxisLabelColor: T.ink, catAxisLabelFontFace: F.body, catAxisLabelFontSize: 13,
    valAxisLabelColor: T.muted, valAxisLabelFontFace: F.body, valAxisLabelFontSize: 10,
    valGridLine: { color: T.line, style: "solid", size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelColor: T.ink, dataLabelFontFace: F.body, dataLabelFontSize: 12, dataLabelFormatCode: "0.0",
    showLegend: false, showTitle: false,
  });
  s.addText("注:据 Orben & Przybylski (2019) 的效应对比示意重绘,精确数值以原文为准。",
    { x: 0.9, y: 6.45, w: 11.5, h: 0.4, fontFace: F.body, fontSize: 10.5, italic: true, color: T.muted, margin: 0 });
  pageNum(s, 9);
})();

// ============ 第 10 页 · 页型 9 结尾页 ============
(() => {
  const s = newSlide();
  // 呼应封面的装饰与底色
  s.addShape(pres.shapes.OVAL, { x: -2.2, y: 4.6, w: 5.4, h: 5.4, fill: { color: T.card } });
  s.addShape(pres.shapes.OVAL, { x: W / 2 - 0.11, y: 1.75, w: 0.22, h: 0.22, fill: { color: T.gold } }); // 母题圆点收尾
  // 居中收束语(从上文结论提炼,不造新观点)
  s.addText("效应是小的,争论是真的\n——测量先行,再谈干预", { x: 1.5, y: 2.4, w: 10.3, h: 2.2,
    fontFace: F.title, fontSize: 36, bold: true, color: T.ink, align: "center", valign: "middle",
    margin: 0, lineSpacingMultiple: 1.25 });
  s.addText("欢迎各位老师同学讨论指正 · 联系方式:___", { x: 1.5, y: 5.0, w: 10.3, h: 0.55,
    fontFace: F.body, fontSize: 15, color: T.muted, align: "center", valign: "middle", margin: 0 });
  pageNum(s, 10);
})();

pres.writeFile({ fileName: "demo-deck.pptx" })
  .then((fn) => console.log("PPTX_WRITTEN:", fn))
  .catch((e) => { console.error("ERR", e); process.exit(1); });
