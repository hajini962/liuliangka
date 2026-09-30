# -*- coding: utf-8 -*-
"""
流量卡店铺数据抓取与省份筛选脚本（纯标准库，无第三方依赖）

数据源1（好网/号卡星球，微店）：
  POST https://hyapi.haomifi.com/v11/micro_store_list/page_goods
  参数 agent_id 来自店铺链接 tui.haonetwork.cn/#/pages/micro_store/index?agent_id=XXX
  每个商品自带【发全国】/【只发XX】标签、copy 下单链接、place 收货地标注、
  settle_accounts_msg 续约/优惠说明、config.original_monthly 优惠到期后价格。

数据源2（172号卡店铺）：
  GET https://h5api.lot-ml.com/api/ProductEn/TyIndex?Id=XXX&page=1&limit=100
  返回该代理的"省内产品集合中心"全部卡片（含各省专属卡），
  下单链接 = https://kh.172.org.cn + tuiPath
  （店铺首页 Index2 接口通常为省内集合的入口，实测该代理为空，故以 TyIndex 为准）

数据源3（浩卡店铺）：
  POST https://api.haokavip.com/open/shop/default_card
  Content-Type: application/json
  参数 agent_id=1539225、page、tab_name=big_flow，按 pageInfo.totalPage 翻页抓全；
  宽带商品（bandwidth/broadband_type 非空或名称含"宽带"）自动剔除。

用法：
  python fetch_cards.py 陕西
  python fetch_cards.py 湖南省 --json
输出：分组后的本地专属卡 / 全国可发卡 / 其他城市限定卡（仅供参考）
每张卡输出字段：
  original_monthly  原价/优惠到期后价格（数据源2无原价字段时为空字符串）
  place             收货地/归属地标注（数据源1取 place 字段；数据源2取名称/套餐描述中
                    "收货地"字样，无则空字符串）
  renewable         是否可续约：可续约 / 续约情况以详情页为准
  discount_note     优惠/续约说明
  shop_url          所属店铺首页地址（调用入口固定店铺）
"""
import json
import re
import sys
import urllib.parse
import urllib.request

AGENT_ID_1 = "aab185d12fbafe0a2210db56129c38e0"   # 数据源1 agent_id
SHOP_TK_2 = "a092f84b30389836"                     # 数据源2 店铺 tk
AGENT_ID_3 = 1539225                               # 数据源3 agent_id

# 调用入口固定店铺地址（商品展示时作为"店铺地址"输出）
SHOP_URL_1 = "https://tui.haonetwork.cn/#/pages/micro_store/index?agent_id=aab185d12fbafe0a2210db56129c38e0"
SHOP_URL_2 = "https://kh.172.org.cn/ProductEn/Shop/a092f84b30389836"
SHOP_URL_3 = "https://www.haokaxinyao.com/#/pages/sales_index/my_store?mall_id=zbS2q6FeVUvFeyRiK%2FHz2g%3D%3D"

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"

# 省份名归一化：去掉后缀，得到短名（用于在产品名/发货标签中匹配）
PROVINCE_ALIASES = {
    "北京": "北京", "天津": "天津", "上海": "上海", "重庆": "重庆",
    "河北": "河北", "山西": "山西", "辽宁": "辽宁", "吉林": "吉林",
    "黑龙江": "黑龙江", "江苏": "江苏", "浙江": "浙江", "安徽": "安徽",
    "福建": "福建", "江西": "江西", "山东": "山东", "河南": "河南",
    "湖北": "湖北", "湖南": "湖南", "广东": "广东", "海南": "海南",
    "四川": "四川", "贵州": "贵州", "云南": "云南", "陕西": "陕西",
    "甘肃": "甘肃", "青海": "青海", "台湾": "台湾",
    "内蒙古": "内蒙古", "广西": "广西", "西藏": "西藏",
    "宁夏": "宁夏", "新疆": "新疆", "香港": "香港", "澳门": "澳门",
}


def normalize_province(raw):
    """把用户输入（如 湖南省 / 湖南 / 陕）归一化为标准短名。"""
    s = raw.strip()
    for suffix in ("省", "市", "壮族自治区", "回族自治区", "维吾尔自治区", "自治区"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
    for name in PROVINCE_ALIASES:
        if s == name or s == name[:1] or (len(s) >= 2 and s in name):
            return name
    return s


def http_post_form(url, data, referer):
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "User-Agent": UA,
        "Referer": referer,
        "appchannel": "self_1.0.365",
        "content-type": "application/x-www-form-urlencoded",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def http_get_json(url, params, referer):
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(url + "?" + qs, headers={
        "User-Agent": UA, "Referer": referer,
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def http_post_json(url, payload, referer):
    """以 application/json 方式 POST，供数据源3使用。"""
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "User-Agent": UA,
        "Referer": referer,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def extract_tag(name):
    """提取卡名中的【...】标签，返回 (标签列表, 去标签后的名称)。"""
    tags = re.findall(r"【([^】]*)】", name)
    clean = re.sub(r"【[^】]*】", "", name).strip()
    return tags, clean


def classify_shipping(text, province):
    """
    根据发货范围文本分类：
    返回 (category, note)
    category: nationwide / local / other_province / unknown
    注意：「只发/仅发 X」优先级高于「发全国」，避免商品副标题与名称标签冲突时误判。
    """
    t = text or ""
    m = re.search(r"(?:只发|仅发|限发)([一-龥]{2,4}(?:省|市|自治区)?)", t)
    m2 = re.search(r"可发全国\s*(\d+)\s*(?:个)?省", t)
    if not m and m2:
        return "unknown", "仅发%s省" % m2.group(1)
    if not m and any(k in t for k in ("发全国", "全国发", "全国可发", "全国通用")):
        return "nationwide", ""
    if m:
        region = m.group(1)
        for suffix in ("省", "市", "自治区"):
            if region.endswith(suffix):
                region = region[: -len(suffix)]
        if province in region or region in province:
            return "local", ""
        return "other_province", "仅发" + region
    return "unknown", ""


def settle_text(settle):
    """把 settle_accounts_msg（可能是 list 或 str）拼成文本。"""
    if isinstance(settle, list):
        return " ".join(str(x) for x in settle)
    return str(settle or "")


def parse_renewable(settle):
    """解析是否可续约/长期套餐。

    命中"可续约/长期套餐/长期/自动续约"或"数字年/补贴数字"（如 1年29、补贴1年、
    4年优惠、首年180元）视为可续约；否则返回"续约情况以详情页为准"。
    """
    text = settle_text(settle)
    if not text.strip():
        return "续约情况以详情页为准"
    for kw in ("可续约", "长期套餐", "长期", "自动续约"):
        if kw in text:
            return "可续约"
    for kw in ("不可续约", "不能续约", "到期恢复原价", "到期恢复", "优惠期后恢复原价", "仅首年优惠"):
        if kw in text:
            return "不可续约"
    if re.search(r"\d+\s*年", text) or re.search(r"补贴\s*\d+", text):
        return "可续约"
    return "续约情况以详情页为准"


def build_discount_note(settle):
    """从 settle_accounts_msg 中提取优惠/续约相关说明片段。"""
    items = settle if isinstance(settle, list) else [settle_text(settle)]
    hits = []
    for x in items:
        s = str(x or "").strip()
        if s and any(k in s for k in ("续约", "长期", "优惠", "年", "补贴", "首年", "免租", "到期", "首月")):
            hits.append(s)
    return " ".join(hits)


def parse_place(text):
    """从文本中识别"收货地/归属地"标注，返回标注或空字符串。"""
    return "收货地" if "收货地" in (text or "") else ""


def _to_float(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _sort_local(c):
    # 收货地为归属地的省内卡排最前，其次流量大、价格便宜
    place_ok = 1 if ("收货地" in (c.get("place") or "") or "收货地及归属地" in (c.get("discount_note") or "")) else 0
    return (-place_ok, -_to_float(c.get("data_gb")), _to_float(c.get("monthly")))


def _sort_nationwide(c):
    # 全国卡按价格低→高、流量大→小排序
    return (_to_float(c.get("monthly")), -_to_float(c.get("data_gb")))


def fetch_source1(province):
    """抓取数据源1全部商品并分类。"""
    url = "https://hyapi.haomifi.com/v11/micro_store_list/page_goods"
    referer = "https://tui.haonetwork.cn/"
    cards = []
    page, last_page = 1, 1
    while page <= last_page and page <= 30:
        resp = http_post_form(url, {
            "agent_id": AGENT_ID_1, "page": page,
            "type": "", "status": "", "category_id": "", "searchVal": "",
        }, referer)
        data = resp.get("data") or []
        last_page = int(resp.get("last_page") or 1)
        for it in data:
            name = it.get("p_goods_name", "")
            if "宽带" in name:
                continue  # 本技能只推荐流量卡，跳过宽带产品
            cfg = it.get("config") or {}
            tags, _ = extract_tag(name)
            subtitle = cfg.get("goods_subtitle", "")
            ship_text = " ".join(tags) + " " + subtitle
            cat, note = classify_shipping(ship_text, province)
            settle = it.get("settle_accounts_msg")
            cards.append({
                "source": "店铺1",
                "name": name,
                "category": cat,
                "note": note,
                "monthly": cfg.get("current_monthly", ""),
                "original_monthly": cfg.get("original_monthly", ""),
                "place": it.get("place", ""),
                "renewable": parse_renewable(settle),
                "discount_note": build_discount_note(settle),
                "shop_url": SHOP_URL_1,
                "data_gb": cfg.get("current", ""),
                "data_directed_gb": cfg.get("directional", ""),
                "call_min": cfg.get("telephone", ""),
                "first_charge": cfg.get("charge_description", ""),
                "age": "%s-%s岁" % (it.get("age_min", ""), it.get("age_max", "")),
                "shipping": subtitle or " ".join(tags),
                "order_url": (it.get("copy") or "").replace("\\/", "/"),
            })
        page += 1
    return cards


def fetch_source2(province):
    """抓取数据源2（172平台）省内集合全部卡片并分类。"""
    url = "https://h5api.lot-ml.com/api/ProductEn/TyIndex"
    referer = "https://kh.172.org.cn/"
    resp = http_get_json(url, {"Id": SHOP_TK_2, "page": 1, "limit": 100}, referer)
    cards = []
    for it in resp.get("data") or []:
        name = it.get("name", "")
        cat, note = classify_shipping(name, province)
        if cat == "unknown":
            # 省内集合中心里未标注省份的卡，按名称中的省份关键字再判一次
            if province in name:
                cat = "local"
            else:
                m = re.search(r"(北京|天津|上海|重庆|河北|山西|辽宁|吉林|黑龙江|江苏|浙江|安徽|"
                              r"福建|江西|山东|河南|湖北|湖南|广东|海南|四川|贵州|云南|陕西|"
                              r"甘肃|青海|内蒙古|广西|西藏|宁夏|新疆)", name)
                cat = "other_province" if m else "unknown"
                if m:
                    note = "疑似限" + m.group(1)
        order = it.get("tuiPath", "")
        if order.startswith("/"):
            order = "https://kh.172.org.cn" + order
        taocan = it.get("taocan", "")
        cards.append({
            "source": "店铺2",
            "name": name,
            "category": cat,
            "note": note,
            "monthly": it.get("nowPrice", ""),
            "original_monthly": "",   # 数据源2无原价字段，到期后价格以详情页为准
            "place": parse_place(str(name) + " " + str(taocan)),
            "renewable": parse_renewable(taocan),
            "discount_note": str(taocan or ""),
            "shop_url": SHOP_URL_2,
            "data_gb": it.get("tyLiuliang", ""),
            "data_directed_gb": it.get("dxLiuliang", ""),
            "call_min": it.get("tonghua", ""),
            "first_charge": str(taocan or ""),
            "age": "%s-%s岁" % (it.get("age1", ""), it.get("age2", "")),
            "shipping": "省内专属" if cat == "local" else "",
            "order_url": order,
        })
    return cards


def fetch_source3(province):
    """抓取数据源3（浩卡店铺）big_flow 全部商品并分类。

    字段映射：gsd→place、current_monthly→monthly、original_monthly→original_monthly、
    current→data_gb、directional→data_directed_gb、telephone→call_min、
    charge_description→first_charge、setage→age、link→order_url。
    宽带商品（bandwidth/broadband_type 非空或名称含"宽带"）自动剔除。
    """
    url = "https://api.haokavip.com/open/shop/default_card"
    referer = "https://www.haokaxinyao.com/"
    cards = []
    page, total_page = 1, 1
    seen = set()
    while page <= total_page and page <= 30:
        resp = http_post_json(url, {
            "agent_id": AGENT_ID_3, "page": page, "tab_name": "big_flow",
            "keyword_name": "", "send_address": "", "local_address": "",
            "product_type": "",
        }, referer)
        data = resp.get("data") or {}
        pinfo = data.get("pageInfo") or {}
        total_page = int(pinfo.get("totalPage") or 1)
        for it in data.get("items") or []:
            name = it.get("name", "")
            link = it.get("link", "")
            key = link or name
            if key in seen:
                continue
            seen.add(key)
            if "宽带" in name:
                continue
            if (it.get("bandwidth") not in (None, "", 0)) or \
                    (it.get("broadband_type") not in (None, "", 0)):
                continue  # 宽带产品不在流量卡推荐范围内
            tags, _ = extract_tag(name)
            subtitle = it.get("subtitle", "")
            ship_text = " ".join(tags) + " " + subtitle + " " + name
            cat, note = classify_shipping(ship_text, province)
            gsd = it.get("gsd", "")
            cards.append({
                "source": "店铺3",
                "name": name,
                "category": cat,
                "note": note,
                "monthly": it.get("current_monthly", ""),
                "original_monthly": it.get("original_monthly", ""),
                "place": "收货地" if "收货地" in (gsd or "") else "",
                "renewable": parse_renewable((subtitle or "") + " " + name),
                "discount_note": str(subtitle or ""),
                "shop_url": SHOP_URL_3,
                "data_gb": it.get("current", ""),
                "data_directed_gb": it.get("directional", ""),
                "call_min": it.get("telephone", ""),
                "first_charge": it.get("charge_description", ""),
                "age": "%s岁" % (it.get("setage", "") or ""),
                "shipping": subtitle or " ".join(tags),
                "order_url": link,
            })
        page += 1
    return cards


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print("用法: python fetch_cards.py <省份> [--json]", file=sys.stderr)
        sys.exit(1)
    province = normalize_province(args[0])

    errors = []
    cards1, cards2, cards3 = [], [], []
    try:
        cards1 = fetch_source1(province)
    except Exception as e:
        errors.append("数据源1抓取失败: %s" % e)
    try:
        cards2 = fetch_source2(province)
    except Exception as e:
        errors.append("数据源2抓取失败: %s" % e)
    try:
        cards3 = fetch_source3(province)
    except Exception as e:
        errors.append("数据源3抓取失败: %s" % e)

    all_cards = cards1 + cards2 + cards3
    result = {
        "province": province,
        "local": [c for c in all_cards if c["category"] == "local"],
        "nationwide": [c for c in all_cards if c["category"] == "nationwide"],
        "other_province": [c for c in all_cards if c["category"] == "other_province"],
        "unknown": [c for c in all_cards if c["category"] == "unknown"],
        "errors": errors,
    }
    # 排序：收货地为归属地的省内卡优先，全国卡按价格低→高、流量大→小
    result["local"].sort(key=_sort_local)
    result["nationwide"].sort(key=_sort_nationwide)

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    def show(title, items):
        print("\n===== %s（%d 张）=====" % (title, len(items)))
        for c in items:
            directed = c["data_directed_gb"]
            call_min = c["call_min"]
            flow = str(c["data_gb"]) + "G"
            if directed not in ("", 0, "0"):
                flow += "通用+" + str(directed) + "G定向"
            call = ("+" + str(call_min) + "分钟") if call_min not in ("", 0, "0") else ""
            print("- %s" % c["name"])
            print("  优惠后月租 %s 元 | %s%s | 年龄%s | %s" % (
                c["monthly"], flow, call, c["age"], c["first_charge"]))
            if c.get("place"):
                print("  归属地/收货地: %s" % c["place"])
            print("  是否可续约: %s" % c["renewable"])
            if c.get("discount_note"):
                print("  优惠/续约说明: %s" % c["discount_note"])
            if c["renewable"] == "不可续约":
                if c.get("original_monthly"):
                    print("  优惠到期后价格: %s 元" % c["original_monthly"])
                else:
                    print("  优惠到期后价格: 以详情页为准")
            if c["note"]:
                print("  备注: %s" % c["note"])
            print("  领取地址: %s" % c["order_url"])
            print("  店铺地址: %s" % c["shop_url"])

    print("用户省份: %s" % province)
    show("本地/省内专属卡", result["local"])
    show("全国可发卡", result["nationwide"])
    show("其他城市/省份限定卡（不推荐，仅供参考）", result["other_province"])
    if result["unknown"]:
        show("发货范围未识别（需人工确认）", result["unknown"])
    for e in errors:
        print("!! " + e)


if __name__ == "__main__":
    main()
