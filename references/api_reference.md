---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 4b431c1c0043833738b54835b4fa691a_55abafaabc9f11f1a1bf52540064ee0f
    ReservedCode1: vqRiGp28EN6Gf9utS14akcFhRfADAfX0z+JtGGyVXYfsJG2RZGQJwKvieG9L24xwe0jlBRmn6kXhwmg2k+aUYR2aUZpuzwpWQHKK/v1zaQngsaZjKJqnK6NRrBeASVyZuV6XQ45Tn6n5Srey0Vm0+bxHKgEkJq4P9Yvb/ZruRYOTmYXV5y5rVfKgnfQ=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 4b431c1c0043833738b54835b4fa691a_55abafaabc9f11f1a1bf52540064ee0f
    ReservedCode2: vqRiGp28EN6Gf9utS14akcFhRfADAfX0z+JtGGyVXYfsJG2RZGQJwKvieG9L24xwe0jlBRmn6kXhwmg2k+aUYR2aUZpuzwpWQHKK/v1zaQngsaZjKJqnK6NRrBeASVyZuV6XQ45Tn6n5Srey0Vm0+bxHKgEkJq4P9Yvb/ZruRYOTmYXV5y5rVfKgnfQ=
---



# 数据源 API 参考（2026-09-22 逆向自前端 JS，可能随改版失效）

## 数据源 1：号卡星球微店（tui.haonetwork.cn）

店铺页：`https://tui.haonetwork.cn/#/pages/micro_store/index?agent_id=<AGENT_ID>`
当前 agent_id：`aab185d12fbafe0a2210db56129c38e0`

前端为 uni-app，API 基础域名为 `https://hyapi.haomifi.com`，版本前缀 `/v11/`。

### 商品列表（店铺前台实际调用）

```
POST https://hyapi.haomifi.com/v11/micro_store_list/page_goods
content-type: application/x-www-form-urlencoded
Header 建议带: User-Agent(手机UA), Referer: https://tui.haonetwork.cn/, appchannel: self_1.0.365

参数:
  agent_id   店铺 agent_id（必填）
  page       页码，每页固定 10 条，按响应 last_page 翻页
  type/status/category_id/searchVal   筛选项，传空字符串即可
```

响应关键字段（data 数组每项）：
| 字段 | 含义 |
|---|---|
| p_goods_name | 卡名，含【发全国】【只发XX】等发货标签 |
| config.current_monthly | **优惠后**当前月租（元），对外展示只使用此价格 |
| config.original_monthly | **原价/优惠到期后价格（元）**。与 current_monthly 不同即存在优惠；优惠到期后不可续约/无法确认可续约时，需额外展示此价格 |
| config.current | 优惠期内通用流量（G） |
| config.directional | 定向流量（G） |
| config.telephone | 通话分钟 |
| config.charge_description | 首充/激活说明 |
| config.goods_subtitle | 副标题，常同发货标签（可能与名称标签冲突，以名称标签为准） |
| place | 收货地/归属地标注："收货地"=收货地即归属地（省内可办，优先推荐）；"随机"=归属地随机 |
| settle_accounts_msg | 续约/优惠/激活说明（数组），如"可续约""长期套餐""1年29""补贴1年""收货地及归属地""先激活后发货"。脚本据此解析 renewable（是否可续约）与 discount_note（优惠/续约说明） |
| age_min / age_max | 年龄限制 |
| copy | 领取/下单地址完整链接（tui.haonetwork.cn/#/pages/goods/details?goods_id=...&share_id=...） |
| shipAreas | 地区名单（语义不稳定：对"发全国"卡是禁发区，对"只发X省"卡反而是可发区，**不要使用**） |

注意：列表同时包含宽带产品（名称含"宽带"），流量卡推荐时应剔除。

## 数据源 2：172 号卡平台店铺（kh.172.org.cn）

店铺海报页（固定店铺入口）：`https://kh.172.org.cn/ProductEn/Shop/<TK>`
店铺首页：`https://kh.172.org.cn/shop/<TK>`
当前 tk：`a092f84b30389836`

前端为 Vue SPA，API 基础域名为 `https://h5api.lot-ml.com/api/`。

### 省内产品集合中心（本店铺商品全在这里）

```
GET https://h5api.lot-ml.com/api/ProductEn/TyIndex?Id=<TK>&page=1&limit=100
Header 建议带: User-Agent(手机UA), Referer: https://kh.172.org.cn/
```

- 返回该代理"省内产品集合中心"的全部卡片（约 14 张，覆盖多省），Province/City 参数服务端不生效，需按卡名中的省份关键字（如"陕西专属""仅发山东""仅发合肥"）在客户端筛选。
- 领取/下单链接 = `https://kh.172.org.cn` + 响应字段 `tuiPath`（形如 `/product?tk=...&pro=...`）。

响应关键字段：`name`（卡名）、`nowPrice`（**优惠后**月租）、`tyLiuliang`（通用流量G）、`dxLiuliang`（定向流量G）、`tonghua`（通话分钟）、`taocan`（套餐描述，含套餐/优惠/续约信息，如"首年XX""N年优惠""长期"；脚本据此解析 renewable 是否可续约与 discount_note 优惠说明）、`age1/age2`（年龄限制）、`isp`（运营商）、`sales`（销量）。

注意：数据源2 **无原价字段**（无 original_monthly），优惠到期后价格统一标注"以详情页为准"；`place` 字段由脚本从卡名与 taocan 中的"收货地"字样解析，无标注时为空。

### 其他已探明接口（备用）

| 接口 | 说明 |
|---|---|
| GET ProductEn/Index?id=<TK> | 店铺信息（店名、logo、h5url） |
| GET ProductEn/Index2 | 店铺首页商品（参数 Id/Province/City/Operator/PriceTime/LiuLiang/Tonghua/page/limit，省份不带"省"字；本店铺实测为空） |
| GET ProductEn/Shop?id=<TK> | 海报页店铺信息 |
| GET ProductEn/GetCitys | 全国省市列表（省份不带"省"字，如"陕西"） |
| GET ProductEn/GetLocation | IP 定位 |

## 数据源 3：浩卡店铺（haokaxinyao.com，对外统一名"互联网号卡星球官方店铺3"）

店铺页（固定店铺入口，mall_id）：`https://www.haokaxinyao.com/#/pages/sales_index/my_store?mall_id=<MALL_ID>`
当前 mall_id：`zbS2q6FeVUvFeyRiK%2FHz2g%3D%3D`（URL 编码，实际为 `zbS2q6FeVUvFeyRiK/Hz2g==`）

前端为 uni-app（h5），API 基础域名为 `https://api.haokavip.com`。

### 店铺信息接口（mall_id 换 agent_id）

```
POST https://api.haokavip.com/open/mall/page_index
Content-Type: application/json
Body: {"mall_id": "zbS2q6FeVUvFeyRiK/Hz2g=="}
```

返回 `data.agent.shop.agent_id = 1539225`（脚本所需 agent_id）。店铺签名文案（如"四大运营商授权 官方正品保障"）属于页面原标题，**禁止对外输出**。

### 商品列表接口（分页抓全）

```
POST https://api.haokavip.com/open/shop/default_card
Content-Type: application/json
Body: {"agent_id": 1539225, "page": 1, "tab_name": "big_flow", "keyword_name": "", "send_address": "", "local_address": "", "product_type": ""}
```

- `tab_name` 用 `"big_flow"`（流量卡主列表），实测 total=28、totalPage=2（每页 20 条），需按 `data.pageInfo.totalPage` 翻页抓全；`"recommend"`/`"local_card"` 与其他未知值会兜底返回精选列表，可抓取后按 link 去重。
- 响应：`data.items`（商品数组）+ `data.pageInfo{total, totalPage, currentPage}`。

商品字段（与店铺1/2输出字段同名映射）：
| 接口字段 | 含义 | 映射到输出 |
|---|---|---|
| name | 商品名（含【发全国】【只发XX】【可发全国N个省份】等标签） | name |
| gsd | 归属地标注（"收货地即归属地"/"归属地：随机归属地"） | place（含"收货地"→"收货地"，否则空） |
| current_monthly | 优惠后现价 | monthly |
| original_monthly | 原价/优惠到期后价格 | original_monthly |
| current | 通用流量（G） | data_gb |
| directional | 定向流量（G） | data_directed_gb |
| telephone | 通话分钟 | call_min |
| charge_description | 首充要求 | first_charge |
| setage | 年龄区间（如"18-65"） | age |
| link | 商品下单链接（完整 URL） | order_url |
| subtitle | 副标题（含首月免费、优惠/续约卖点） | discount_note / shipping |
| product_type | "haoka" 表示号卡 | - |
| bandwidth / broadband_type | 宽带字段，两者都为空/0 时才是普通号卡；非空即宽带，**脚本剔除，不推荐** | - |

注意：数据源3 有 `original_monthly` 原价字段，与数据源1 相同；宽带产品（bandwidth/broadband_type 非空或名称含"宽带"）从主推荐剔除，仅在推荐结尾提示"本店另有宽带产品，如有需要可再为您推荐"。

## 展示字段映射（新增）

| 输出字段 | 数据源1 | 数据源2 | 数据源3 |
|---|---|---|---|
| original_monthly | config.original_monthly（原价/优惠到期后价格） | 无，置空字符串 | original_monthly（原价/优惠到期后价格） |
| place | place（"收货地"=收货地即归属地，"随机"=归属地随机） | 从 name/taocan 中"收货地"字样解析，无则空 | gsd 含"收货地"→"收货地"，否则空 |
| renewable | 由 settle_accounts_msg 解析：含"可续约/长期套餐/长期/自动续约"或"数字年/补贴数字"（如 1年29、补贴1年、4年优惠）→"可续约"，否则"续约情况以详情页为准" | 由 taocan 解析，规则同左 | 由 subtitle+name 解析，规则同左 |
| discount_note | settle_accounts_msg 中优惠/续约相关片段 | taocan 全文 | subtitle |
| shop_url | 店铺1固定地址 | 店铺2固定地址 | 店铺3固定地址 |

## 失效后的排查方法

1. 先用 curl 直接请求上述 API 确认是否返回 JSON（而非 HTML 错误页）。
2. 若接口改版：用浏览器打开店铺页渲染，或重新下载前端 JS 逆向：
   - 数据源1：`https://tui.haonetwork.cn/` → `static/js/index.<hash>.js` → 搜 `micro_store_list` / `apiUrl`
   - 数据源2：`https://kh.172.org.cn/js/app.<hash>.js` 找 chunk 映射 → 对应 chunk 里搜 `ProductEn/`；基础域名在 chunk 82 里搜 `baseURL`
   - 数据源3：`https://www.haokaxinyao.com/` → 前端 JS 里搜 `open/shop/default_card` / `api.haokavip.com`
*（内容由AI生成，仅供参考）*
*（内容由AI生成，仅供参考）*
