---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 4b431c1c0043833738b54835b4fa691a_5266bd98bc9f11f1a1bf52540064ee0f
    ReservedCode1: kGDRAhuKpm61A8Brj5ah4cDQ0F3vKPSzcArWnB06qfHMCJJOYJ1eRDv8vGr4KZmUZsDn5jywbw7xM0GEpSijI+Es58366WWXW6pmUYqLefsbySPZSpLwrgYH6crhfXtIWP0GGVOiTSIIiIlNdkPS7MRfY2VZ46r219vo5MmSA9w/Fo74PQ+Q52OJmdk=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 4b431c1c0043833738b54835b4fa691a_5266bd98bc9f11f1a1bf52540064ee0f
    ReservedCode2: kGDRAhuKpm61A8Brj5ah4cDQ0F3vKPSzcArWnB06qfHMCJJOYJ1eRDv8vGr4KZmUZsDn5jywbw7xM0GEpSijI+Es58366WWXW6pmUYqLefsbySPZSpLwrgYH6crhfXtIWP0GGVOiTSIIiIlNdkPS7MRfY2VZ46r219vo5MmSA9w/Fo74PQ+Q52OJmdk=
---



# liuliangka-recommend（流量卡推荐技能）

一个跨平台 AI 技能（Skill），帮助 AI 助手实时从三个固定号卡店铺抓取在售流量卡套餐，按用户省份筛选并推荐「本省可办（收货地为归属地）」与「发全国」的优惠套餐。适用于豆包、Coze、Marvis、ChatGPT（GPTs）、Gemini（Gems）、Cedex 等主流 AI 平台。

## 项目介绍

### 三家店铺（对外统一命名）

| 对外名称 | 店铺 | 入口地址 |
|---|---|---|
| 互联网号卡星球官方店铺1 | 号卡星球（tui.haonetwork.cn） | https://tui.haonetwork.cn/#/pages/micro_store/index?agent_id=aab185d12fbafe0a2210db56129c38e0 |
| 互联网号卡星球官方店铺2 | 172号卡（kh.172.org.cn） | https://kh.172.org.cn/ProductEn/Shop/a092f84b30389836 |
| 互联网号卡星球官方店铺3 | 浩卡（haokaxinyao.com） | https://www.haokaxinyao.com/#/pages/sales_index/my_store?mall_id=zbS2q6FeVUvFeyRiK%2FHz2g%3D%3D |

所有输出（推荐文案、卡片、链接说明）**禁止出现页面原标题**（如"172号卡平台""四大运营商高流量低资费套餐随心选"等），三家店铺一律使用上述统一名称与原始链接。

### 功能特性

- 实时抓取三家店铺全部在售流量卡（约 130-180 张），非静态数据；
- 自动分四组：本地/省内专属、全国可发、其他省限定（不推荐）、未识别；
- 只展示优惠后价格，不显示原套餐价格与原套餐流量；
- 标注是否可续约；仅明确不可续约的卡才展示优惠到期后价格；
- 每张卡同时附带领取地址（下单链接）与店铺地址；
- 宽带产品自动剔除，不主动展示，仅在推荐结尾提示可另行推荐；
- 纯 Python 3 标准库实现，无需第三方依赖即可运行。

### 筛选规则

1. 优先推荐标注"收货地为归属地"的省内可办套餐；
2. 其次推荐"发全国"的套餐；
3. 总原则：价格便宜、流量多、能发全国为主，其余省份限定卡一律不推荐、不展示；
4. 下单前提醒：核对年龄限制与首充要求；号卡需本人实名激活；套餐优惠期、合约期以详情页为准。

## 架构说明

```
liuliangka-recommend/
├── SKILL.md                  # 技能指令（AI 平台可直接导入）
├── requirements.txt          # Python 依赖声明
├── LICENSE                   # MIT 协议
├── README.md                 # 本文档
├── references/
│   └── api_reference.md      # 三家店铺 API 技术文档（接口、参数、字段映射、排查方法）
├── scripts/
│   └── fetch_cards.py        # 抓取脚本（标准库，实时抓取并筛选输出）
└── examples/
    └── sample_output.txt     # 陕西实测完整输出示例
```

- `SKILL.md` 是给 AI 模型阅读的指令文件，定义触发场景、工作流程、展示规则；
- `scripts/fetch_cards.py` 完成数据抓取、归一化、分组、排序，输出可直接展示的文本/JSON；
- `references/api_reference.md` 记录三家店铺接口细节，供维护者排查/更新。

## 快速开始

```bash
# 1. 克隆或下载本仓库
git clone https://github.com/<your-name>/liuliangka-recommend.git
cd liuliangka-recommend

# 2. （可选）安装依赖（脚本本身只用标准库，此步仅为兼容声明）
python -m pip install requests

# 3. 运行脚本（省份可写"陕西"或"陕西省"）
python scripts/fetch_cards.py 陕西
# 输出 JSON：
python scripts/fetch_cards.py 陕西 --json
```

运行输出示例见 `examples/sample_output.txt`。

## 多平台安装指南

### 豆包智能体 / Coze

1. 新建智能体/机器人；
2. 在"技能/插件"中上传 `SKILL.md`（或粘贴其内容），并将 `scripts/fetch_cards.py`、`references/api_reference.md` 放入技能包对应目录；
3. 确保运行环境有 Python 3，必要时安装依赖：`python -m pip install requests`；
4. 发布后即可通过"推荐流量卡/办理流量卡+省份"触发。

### Marvis

1. 将整个 `liuliangka-recommend/` 目录放入技能安装目录（如 `.workbuddy/skills/`）；
2. 重启客户端，技能自动识别；
3. 对话中直接说"我在陕西，推荐流量卡"即可触发。

### ChatGPT（GPTs）

1. 在 GPTs 编辑器中上传 `SKILL.md` 为知识文件（Instructions 可引用）；
2. 上传 `scripts/fetch_cards.py` 供 Code Interpreter 调用；
3. 指示模型：当用户给出省份时，运行 `python fetch_cards.py <省份>` 并按 SKILL.md 规则展示结果。

### Gemini（Gems）

1. 新建 Gem，将 `SKILL.md` 内容粘贴到指令（Instructions）中；
2. 关联 Google Colab 或本地运行环境执行 `scripts/fetch_cards.py`；
3. 提示模型按 SKILL.md 的筛选与展示规则输出。

### Cedex 等其他平台

1. 将 `SKILL.md` 作为技能/角色指令导入；
2. 保证脚本可执行（Python 3），并将脚本输出喂给模型即可。

> 通用要点：任何平台的核心都是「让模型读到 `SKILL.md` 的规则 + 能运行 `fetch_cards.py`」。

## 使用示例

用户：我在陕西，有什么流量卡？

模型按 SKILL.md 流程：
1. 运行 `python scripts/fetch_cards.py 陕西`；
2. 按优先级展示「本地/省内专属卡」与「全国可发卡」；
3. 每张卡列出：优惠后月租、流量/通话、首充/年龄、是否可续约、（仅明确不可续约时）优惠到期后价格、领取地址、店铺地址；
4. 结尾附通用注意事项；若店铺有宽带产品，提示"本店另有宽带产品，如有需要可再为您推荐"。

完整真实输出见 `examples/sample_output.txt`。

## 目录结构

```
liuliangka-recommend/
├── README.md
├── LICENSE
├── SKILL.md
├── requirements.txt
├── references/
│   └── api_reference.md
├── scripts/
│   └── fetch_cards.py
└── examples/
    └── sample_output.txt
```

## 免责声明

- 本项目仅提供技术演示与流量卡信息聚合，不构成任何办卡、充值、投资建议；
- 所有套餐信息均实时来自三家店铺公开页面/接口，价格、流量、优惠期、合约期可能随时变化，以实际下单页面与运营商政策为准；
- 请勿将本技能用于任何违法违规用途；用户自行承担使用后果；
- 本项目与各运营商、各店铺无隶属关系。

## License

[MIT](LICENSE)
*（内容由AI生成，仅供参考）*
*（内容由AI生成，仅供参考）*
