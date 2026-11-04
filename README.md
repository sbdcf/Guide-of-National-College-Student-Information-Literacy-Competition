# AI+信息素养大赛备考站

面向本校同学（以及任何想了解这个比赛的人）的备考资料站。

**在线访问**：[AI+信息素养大赛备考站](https://sbdcf.github.io/Guide-of-National-College-Student-Information-Literacy-Competition/)

> 本站由学校AI+信息素养社整理，内容仅供参考，一切以官方通知为准。

---

## 这是什么比赛

- 母赛事：中国移动杯·浙江省大学生人工智能竞赛
- 本赛项：其中的「AI+信息素养」专项赛

本比赛每年都有，赛事名会随着主办方的变化而变化，但举办时间是相近的

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

见 [贡献指南](https://sbdcf.github.io/Guide-of-National-College-Student-Information-Literacy-Competition/contributing/)（或仓库内 [CONTRIBUTING.md](CONTRIBUTING.md) 速览版）。

- 报错、提问、建议 → 开 Issue（有模板）
- 交题 → 网页上传 `data/questions/q-tmp-*.json`，字段说明见贡献指南
- 改文字 → 网页编辑 Markdown，提交时选「新建分支 + Propose changes」，别直推 `main`

## 许可

内容以 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 发布；代码部分以 MIT 发布。
