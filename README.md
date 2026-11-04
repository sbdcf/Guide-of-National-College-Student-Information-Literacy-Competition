# AI+信息素养大赛备考站

面向本校同学（以及任何想了解这个比赛的人）的备考资料站。

**在线访问**：[AI+信息素养大赛备考站](https://sbdcf.github.io/Guide-of-National-College-Student-Information-Literacy-Competition/)

> 本站由学校AI+信息素养社整理，内容仅供参考，一切以官方通知为准。

---

## 这是什么比赛

- 母赛事：中国移动杯·浙江省大学生人工智能竞赛
- 本赛项：其中的「AI+信息素养」专项赛
- 同时是全国「大学生“AI+信息素养”大赛」的浙江赛区

详细的事实底座（主办、赛制、时间线、考点范围、平台）见 [`design/赛事事实底稿.md`](../design/赛事事实底稿.md)。

## 仓库结构

```
docs/            站点内容（Markdown）
  index.md       首页
  about/         比赛概况
  guide/         参赛指南（待迁移）
  bank/          题库页面（待建）
  assets/        图片
data/
  taxonomy.json  受控词表（考点、数据库、题型）
  questions/     题库源数据，一题一个 JSON
source/          Word 原件留档
tools/
  builder.html   离线出题器
  validate.py    CI 校验
```

## 贡献

- 发现内容错误 → 开 Issue
- 想加题目 → 见「题库 → 贡献题目」页

## 许可

内容以 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 发布；代码部分以 MIT 发布。
