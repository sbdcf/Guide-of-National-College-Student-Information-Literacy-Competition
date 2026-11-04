# AI+信息素养大赛备考站

面向本校同学（以及任何想了解这个比赛的人）的备考资料站。

**在线访问**：部署后填写实际地址

> 本站由学校信息素养部（学生社团）整理，内容仅供参考，一切以官方通知为准。

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

## 本地预览

```bash
python -m venv .venv
.venv/Scripts/activate      # Windows
pip install -r requirements.txt
mkdocs serve
```

打开 http://127.0.0.1:8000 。

## 部署

推送到 `main` 分支即由 GitHub Actions 自动构建并发布到 GitHub Pages。

首次部署前需要：

1. 把 `mkdocs.yml` 里的 `<你的GitHub用户名>` 全部替换成实际用户名（`site_url` 与 `repo_url` 两处）。
2. 在仓库 Settings → Pages → Source 里选择 **GitHub Actions**。

## 维护者交接

> 这一节是给下一任负责人看的。社团会换届，作者 2027 年毕业，务必按下面做。

- **权限**：仓库所有者把下一任负责人加为 Collaborator（Settings → Collaborators），确认对方能推代码后，再到 Settings → General 底部 **Transfer ownership** 把仓库转走。
- **每年要改的地方**（比赛约在赛年 6–7 月发通知）：
  1. 届次与年份（标题、`mkdocs.yml` 的 `site_name`、前言）
  2. 报名与各阶段时间节点
  3. 官方平台链接（高职 `cscgz.zhixinst.com`、本硕 `csc.xxsuyang.com`、省级官网 `zjcsc.nczxst.com`）
  4. 考点大纲变化
  5. 上一届真题入库
  6. 题库里过期题重新核验
- **数据都在文本里**：题目是 `data/questions/*.json`，不要把题库只留在 Word 里。

## 贡献

见 [贡献指南](https://sbdcf.github.io/Guide-of-National-College-Student-Information-Literacy-Competition/contributing/)（或仓库内 [CONTRIBUTING.md](CONTRIBUTING.md) 速览版）。

- 报错、提问、建议 → 开 Issue（有模板）
- 交题 → 网页上传 `data/questions/q-tmp-*.json`，字段说明见贡献指南
- 改文字 → 网页编辑 Markdown，提交时选「新建分支 + Propose changes」，别直推 `main`

## 许可

内容以 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 发布；代码部分以 MIT 发布。
