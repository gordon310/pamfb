# 螃蟹餐饮 · 酒店餐饮收益与投资回报分析

用于收集**餐饮行业专家**对「酒店餐饮收益分析与投资回报」平台的需求确认，并把结论沉淀为开发文档。

- 在线填写表单：`index.html`（也可直接打开本地文件）
- GitHub 在线提交：仓库 `Issues` → 选择「餐饮需求确认表 V1.0」
- 每条提交 = 一个 GitHub Issue（label `business-feedback`），永久留档、可导出
- 问卷唯一维护源：`questionnaire.md`

> 平台定位：螃蟹树聚协助酒店（集团）构筑实时云数据分析平台，0 成本搭建，仅收取单店每年不超过 999 元的年费。酒店上传数据后取得订阅报告，**上传什么数据，报告就呈现对应部分**。
>
> 本问卷在餐饮营收数据之外，新增**餐饮投资数据**（每个餐厅 / 宴会厅总投资额，**不含租金**），据此实现**投资回报分析**（回收期 / ROI / 年化回报率 / 单座投资额 / 坪效投资比 / 收入投资比），分析**不计算折旧**。

## 目录

```
pamfb/
├── README.md
├── index.html                              填写页（单按钮提交）
├── thanks.html                             提交成功后显示「感谢上传」
├── records.html                            答卷记录页（完成情况 / 明细 / CSV）
├── questionnaire.md                        问卷唯一维护源（52 题）
├── package.json                            测试脚本
├── .nojekyll                               GitHub Pages 原样发布
├── .github/ISSUE_TEMPLATE/
│   ├── hotel-fb-requirements.yml           GitHub Issue 表单（52 题结构化）
│   └── config.yml                          新增 issue 引导
├── relay/                                  Cloudflare Worker 中转（可选，实现「提交→谢谢」）
│   ├── worker.js
│   ├── wrangler.toml
│   └── README.md
├── scripts/
│   └── export_issues.py                    导出全部答卷为 CSV / Markdown 汇总
└── tests/
    ├── logic.test.mjs                      逻辑测试（只读）
    └── render.mjs                          无头 Chrome 渲染测试
```

## 仓库信息

- 仓库：https://github.com/gordon310/pamfb
- **填写页（单按钮提交）**：https://gordon310.github.io/pamfb/
- **答卷记录页（内部查看完成情况）**：https://gordon310.github.io/pamfb/records.html
- 提交入口（Issue 表单，备用）：https://github.com/gordon310/pamfb/issues/new/choose
- 建议在仓库 `Settings → Labels` 保持 `business-feedback` 标签存在，便于筛选导出。

> 记录页会展示每家酒店 / 每位填写人的提交次数、最近提交时间与状态，并支持按酒店 / 姓名过滤、导出 CSV。

### 提交方式

- **当前（已部署中转）**：填写页点「提交」→ Cloudflare Worker 中转写入 GitHub Issue → 页面显示「感谢上传」，填写人全程不接触 GitHub。中转地址 `https://pamfb-relay.zoubeacon.com/`，配置在 `index.html`（`RELAY_URL`、`FORM_KEY`）与 `records.html`（`RELAY_URL`）。
- **回退**：把 `RELAY_URL` 留空即回到「打开 GitHub 新建 Issue 页」流程，需登录 GitHub 点一次 Submit。详见 `relay/README.md`。

## 如何填写

1. 打开 `https://gordon310.github.io/pamfb/`（共 52 题，单按钮提交）。
2. 填写姓名、酒店名称、部门与日期，逐项作答，第 52 题可补充。
3. 点「提交」完成，可直接关闭浏览器。
4. 提交后请勿删除，作为需求留档。

> GitHub Issue 表单（`issues/new/choose`）无法强制"最多选 N 项"，第 50 / 51 题请在题干提示下自行控制；HTML 版会强制限制。

### 身份与多次提交

- **酒店名称 + 姓名必填**：每份答卷第一项要求填写，用于识别提交方。
- **可多次提交**：同一人可提交多份（如修订版），每份都是独立 Issue，全部留档。
- **建议**：提交时在 Issue 标题带上酒店与姓名（HTML 版已自动填充为 `[餐饮需求答卷] 酒店 / 姓名 / 日期`）。
- **取最新为准**：同名多次提交时，以导出表中 `创建时间` 最新的一条为准。

## 维护与回填

- 修改问卷：先改 `questionnaire.md`，再同步 `index.html` 的 `SECTIONS`、`records.html` 的 `QLABELS` 与 `hotel-fb-requirements.yml`、`scripts/export_issues.py` 的 `COLS`。
- 收到答卷后：将结论回填到对应开发需求文档，并标注来源与日期。

## 测试

只读测试，不会创建或修改任何记录。

```bash
npm test          # 逻辑（提交 URL / Markdown 往返 / 导出 / Worker）
npm run test:all  # 逻辑 + 无头浏览器渲染
```

详见 `tests/README.md`。

## 导出留档

```bash
# 需要已登录的 gh CLI
python3 scripts/export_issues.py --repo gordon310/pamfb --out ./exports
```

输出：

- `exports/business-feedback.csv`：每行一份答卷，列出题号答案
- `exports/business-feedback.md`：按填写人汇总的完整答卷

## 投资回报分析口径

> 本平台的分析口径，仅使用**总投资额 + 餐饮营收数据**，**不计算折旧**。

| 指标 | 口径 |
|---|---|
| 单座投资额 | 总投资额 ÷ 座位数 |
| 坪效投资比 | 总投资额 ÷ 营业面积 |
| 收入投资比 | 年度营收 ÷ 总投资额 |
| ROI | 年度营收（或净收益）÷ 总投资额 |
| 年化回报率 | ROI 按年折算 |
| 投资回收期 | 总投资额 ÷ 年度营收（或净收益） |

> 若酒店另行提供成本 / GOP 数据，可切换为净收益口径；否则默认按收入口径提示。
