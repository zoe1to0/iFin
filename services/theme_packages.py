"""Centralized Theme Package configuration for Event Analysis.

Adding a new broad market theme should start here. Runtime services consume
these packages for routing, search expansion, suggested queries, logic-chain
templates, prompt rules, and market-data pack hints.
"""

from __future__ import annotations


def _suggested(items: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"label": label, "query": query} for label, query in items]


THEME_PACKAGES: dict[str, dict] = {
    "precious_metal": {
        "label": "贵金属 / 黄金",
        "keywords": ["黄金", "gold", "白银", "silver", "贵金属", "黄金股"],
        "data_pack": ["gold", "dxy", "us10y", "gld"],
        "search_expansion": [
            "黄金",
            "gold",
            "gold price",
            "precious metals",
            "gold miners",
            "safe haven",
            "real yield",
            "dollar",
            "central bank gold buying",
        ],
        "suggested_queries": _suggested(
            [
                ("黄金价格持续上涨", "黄金价格持续上涨 gold price safe haven real yield dollar"),
                ("黄金股与有色金属板块走强", "黄金股 有色金属板块走强 gold miners precious metals"),
                ("美元指数与实际利率变化", "美元指数 实际利率 美债收益率 gold real yield dollar"),
                ("央行购金与避险需求", "央行购金 黄金 避险需求 central bank gold buying safe haven"),
                ("黄金ETF资金流", "黄金ETF 资金流 GLD gold ETF flows"),
            ]
        ),
        "logic_chain_template": [
            {
                "title": "主题输入",
                "content": "黄金主题输入",
                "description": "黄金被识别为贵金属资产主题，而非单一新闻事件。",
            },
            {
                "title": "核心变量",
                "content": "实际利率 / 美元指数 / 央行购金 / 避险需求",
                "description": "主要观察实际利率、美元指数、央行购金、避险需求。",
            },
            {
                "title": "市场传导",
                "content": "利率与避险情绪影响黄金吸引力",
                "description": "实际利率下降或避险升温通常提升黄金吸引力。",
            },
            {
                "title": "资产影响",
                "content": "黄金价格 / 黄金ETF / 黄金股",
                "description": "黄金价格、黄金ETF、黄金股可能出现不同步反应。",
            },
        ],
        "prompt_rules": [
            "Analyze as asset trend + related sectors + macro drivers, not as a single event.",
            "Focus on gold price drivers, real yields, dollar, ETF/flow proxy, and safe-haven demand.",
            "Do not invent gold prices, yield levels, historical percentiles, or central-bank purchase data.",
        ],
    },
    "ai_sector": {
        "label": "AI 产业链",
        "keywords": ["AI", "人工智能", "算力", "大模型", "AIGC"],
        "data_pack": ["nvda", "qqq", "ai_etf", "amd"],
        "search_expansion": [
            "AI",
            "人工智能",
            "算力",
            "大模型",
            "AIGC",
            "AI infrastructure",
            "cloud capex",
        ],
        "suggested_queries": _suggested(
            [
                ("AI产业链估值变化", "AI产业链 估值变化 AI valuation"),
                ("算力需求与英伟达", "算力需求 英伟达 Nvidia AI demand"),
                ("AI应用商业化进展", "AI应用 商业化 monetization"),
                ("云厂商资本开支变化", "云厂商 资本开支 cloud capex AI infrastructure"),
            ]
        ),
        "logic_chain_template": [
            {"title": "主题输入", "content": "AI 产业链主题", "description": "将输入识别为 AI 产业链主题，而非单一新闻事件。"},
            {"title": "产业变量", "content": "算力需求 / 云厂商资本开支 / 商业化进展", "description": "产业变量决定市场是否继续相信 AI 需求扩张。"},
            {"title": "资金偏好", "content": "成长股估值与风险偏好", "description": "资金会在增长预期、估值压力和利率环境之间重新权衡。"},
            {"title": "板块表现", "content": "AI 应用 / 芯片 / 云基础设施", "description": "不同环节可能因盈利兑现节奏不同而表现分化。"},
        ],
        "prompt_rules": [
            "Analyze sector demand, valuation, cloud capex, supply chain, and commercialization progress.",
            "Use NVDA, QQQ, AI ETF, and AMD market data only when is_mock is false.",
            "Do not turn AI theme analysis into stock recommendation or price prediction.",
        ],
    },
    "semiconductor": {
        "label": "半导体 / 芯片",
        "keywords": ["芯片", "半导体", "Nvidia", "英伟达", "AMD", "TSM", "台积电", "ASML"],
        "data_pack": ["soxx", "nvda", "amd", "tsm"],
        "search_expansion": ["芯片", "半导体", "semiconductor", "Nvidia", "AMD", "TSM", "ASML", "export control"],
        "suggested_queries": _suggested(
            [
                ("半导体出口限制影响", "半导体 出口限制 export control semiconductor"),
                ("英伟达财报与AI需求", "英伟达 财报 AI需求 Nvidia earnings AI demand"),
                ("台积电先进制程", "台积电 先进制程 TSMC advanced node"),
                ("存储芯片周期变化", "存储芯片 周期变化 memory chip cycle"),
            ]
        ),
        "logic_chain_template": [
            {"title": "主题输入", "content": "半导体 / 芯片主题", "description": "将输入识别为半导体或芯片产业链主题。"},
            {"title": "产业变量", "content": "AI需求 / 先进制程 / 出口限制 / 库存周期", "description": "产业变量会影响市场对订单、利润率和供应链稳定性的判断。"},
            {"title": "资金偏好", "content": "龙头公司与周期环节的估值切换", "description": "资金可能在 AI 龙头、设备、代工和存储周期之间重新分配。"},
            {"title": "板块表现", "content": "芯片股 / 设备商 / 代工厂", "description": "板块内部可能因需求能见度和政策风险不同而出现分化。"},
        ],
        "prompt_rules": [
            "Analyze demand, advanced nodes, export controls, inventory cycle, margins, and supply-chain risk.",
            "Use SOXX, NVDA, AMD, and TSM market data only when is_mock is false.",
            "Separate industry logic from individual stock advice.",
        ],
    },
    "crypto": {
        "label": "加密资产",
        "keywords": ["比特币", "BTC", "crypto", "ETH", "以太坊"],
        "data_pack": ["btc", "eth"],
        "search_expansion": ["BTC", "Bitcoin", "ETH", "crypto", "spot ETF", "liquidity"],
        "suggested_queries": _suggested(
            [
                ("比特币价格波动", "比特币价格波动 BTC volatility"),
                ("现货ETF资金流", "比特币 现货ETF 资金流 spot ETF flows"),
                ("加密资产风险偏好", "加密资产 风险偏好 crypto risk appetite"),
                ("美元流动性与BTC", "美元流动性 BTC dollar liquidity"),
            ]
        ),
        "logic_chain_template": [
            {"title": "流动性/风险偏好", "content": "美元流动性与风险偏好", "description": "加密资产通常对流动性和风险偏好变化较敏感。"},
            {"title": "资金流", "content": "ETF资金 / 稳定币流动性 / 杠杆变化", "description": "资金流变化会影响市场对加密资产需求强弱的理解。"},
            {"title": "市场反应", "content": "波动率与风险资产联动", "description": "风险偏好变化可能放大加密资产价格波动。"},
            {"title": "资产影响", "content": "BTC / ETH / 相关概念资产", "description": "不同加密资产和相关股票可能因资金流与叙事不同而分化。"},
        ],
        "prompt_rules": [
            "Analyze liquidity, risk appetite, ETF flows, leverage, and regulatory context.",
            "Do not predict token prices or returns.",
        ],
    },
    "macro": {
        "label": "宏观事件",
        "keywords": ["美联储", "Fed", "FOMC", "CPI", "非农", "降息", "加息", "利率", "美债"],
        "data_pack": ["dxy", "us10y", "sp500", "vix"],
        "search_expansion": ["美联储", "Fed", "FOMC", "CPI", "非农", "rate cut", "interest rate", "treasury yield"],
        "suggested_queries": _suggested(
            [
                ("美联储利率决议", "美联储 利率决议 Fed FOMC interest rate"),
                ("美国CPI与降息预期", "美国CPI 降息预期 CPI rate cut expectation"),
                ("美债收益率变化", "美债收益率变化 Treasury yield"),
                ("风险偏好与美元指数", "风险偏好 美元指数 risk appetite DXY"),
            ]
        ),
        "logic_chain_template": [
            {"title": "事件触发", "content": "宏观事件或政策信号", "description": "先识别宏观事件或政策信号本身。"},
            {"title": "利率预期", "content": "未来利率路径重新定价", "description": "市场会重新评估降息、加息或维持利率的概率。"},
            {"title": "风险偏好", "content": "美元 / 美债 / 波动率变化", "description": "利率预期会传导到美元、美债收益率和风险偏好。"},
            {"title": "资产反应", "content": "股票 / 债券 / 黄金 / 新兴市场", "description": "不同资产会根据利率敏感度和流动性预期出现差异化反应。"},
        ],
        "prompt_rules": [
            "Analyze expectation changes, rates, dollar, yields, volatility, and risk appetite.",
            "Do not write deterministic conclusions about market direction.",
        ],
    },
    "commodity": {
        "label": "大宗商品",
        "keywords": ["原油", "oil", "WTI", "Brent", "OPEC", "天然气"],
        "data_pack": ["wti", "brent", "dxy"],
        "search_expansion": ["原油", "WTI", "Brent", "OPEC", "oil", "natural gas", "dollar"],
        "suggested_queries": _suggested(
            [
                ("原油价格波动", "原油价格波动 WTI Brent oil price"),
                ("OPEC减产政策", "OPEC 减产政策 oil production cut"),
                ("地缘风险与油价", "地缘风险 油价 geopolitical risk oil"),
                ("美元指数与大宗商品", "美元指数 大宗商品 dollar commodities"),
            ]
        ),
        "logic_chain_template": [
            {"title": "主题输入", "content": "大宗商品主题", "description": "将输入识别为商品价格与供需主题。"},
            {"title": "供需变量", "content": "产量 / 库存 / 需求 / 地缘风险", "description": "商品价格通常受供需和地缘扰动共同影响。"},
            {"title": "市场传导", "content": "通胀预期 / 美元 / 成本曲线", "description": "商品变化会传导到通胀、企业成本和风险偏好。"},
            {"title": "资产影响", "content": "商品期货 / 能源股 / 资源品板块", "description": "相关资产可能因供需和美元变化出现分化。"},
        ],
        "prompt_rules": [
            "Analyze supply-demand, inventory, production policy, dollar, and geopolitical risk.",
        ],
    },
    "real_estate": {
        "label": "房地产",
        "keywords": ["地产", "房地产", "楼市", "房企", "按揭", "mortgage"],
        "data_pack": ["real_estate_index", "mortgage_rate"],
        "search_expansion": ["地产", "房地产", "楼市", "房企", "按揭", "mortgage", "housing market"],
        "suggested_queries": _suggested(
            [
                ("中国地产刺激政策", "中国地产刺激政策 real estate stimulus"),
                ("房地产销售数据", "房地产销售数据 housing sales"),
                ("房企融资风险", "房企融资风险 developer debt"),
                ("按揭利率变化", "按揭利率变化 mortgage rate"),
            ]
        ),
        "logic_chain_template": [
            {"title": "政策/需求输入", "content": "房地产主题", "description": "将输入识别为地产政策、销售或融资主题。"},
            {"title": "核心变量", "content": "销售 / 融资 / 房价 / 按揭利率", "description": "地产链条需要同时观察需求端、资金端和价格预期。"},
            {"title": "市场传导", "content": "信用风险 / 地方财政 / 产业链需求", "description": "地产变化会传导到信用、财政和相关产业链。"},
            {"title": "资产影响", "content": "房企债 / 银行 / 建材 / 消费", "description": "不同资产受地产链条影响的路径不同。"},
        ],
        "prompt_rules": [
            "Analyze housing sales, financing risk, policy support, mortgage rates, and property-chain spillovers.",
        ],
    },
    "robotics": {
        "label": "机器人产业链",
        "keywords": ["机器人", "robot", "robotics", "humanoid robot"],
        "data_pack": [],
        "search_expansion": ["机器人", "robot", "robotics", "humanoid robot"],
        "suggested_queries": _suggested(
            [
                ("人形机器人进展", "人形机器人 humanoid robot"),
                ("机器人产业链", "机器人 产业链 robotics supply chain"),
                ("商业化与订单", "机器人 订单 商业化 robotics orders"),
            ]
        ),
        "logic_chain_template": [
            {"title": "主题输入", "content": "机器人产业链", "description": "将输入识别为机器人行业主题。"},
            {"title": "产业变量", "content": "技术 / 成本 / 订单 / 量产", "description": "技术成熟度和量产能力决定商业化节奏。"},
            {"title": "资金偏好", "content": "产业资本与主题资金", "description": "订单和资本开支变化影响市场关注度。"},
            {"title": "板块表现", "content": "本体 / 零部件 / 自动化", "description": "产业链环节可能因兑现节奏不同而分化。"},
        ],
        "prompt_rules": ["Analyze robotics commercialization, orders, costs, supply chain, and deployment evidence."],
    },
    "new_energy_vehicle": {
        "label": "新能源汽车",
        "keywords": ["新能源车", "电动车", "electric vehicle", "EV market"],
        "data_pack": [],
        "search_expansion": ["新能源车", "电动车", "electric vehicle", "EV sales"],
        "suggested_queries": _suggested(
            [
                ("新能源车销量", "新能源车 电动车 EV sales"),
                ("价格竞争", "新能源车 价格战 EV price competition"),
                ("电池与供应链", "EV battery supply chain 新能源车"),
            ]
        ),
        "logic_chain_template": [
            {"title": "主题输入", "content": "新能源汽车产业链", "description": "将输入识别为新能源汽车行业主题。"},
            {"title": "产业变量", "content": "销量 / 价格 / 电池 / 政策", "description": "销量、价格竞争和供应链共同影响经营预期。"},
            {"title": "资金偏好", "content": "整车与供应链估值", "description": "盈利兑现和竞争格局影响资金选择。"},
            {"title": "板块表现", "content": "整车 / 电池 / 零部件", "description": "不同环节可能因利润率与需求变化而分化。"},
        ],
        "prompt_rules": ["Analyze EV sales, pricing, battery supply chain, policy, exports, and margins."],
    },
    "company": {
        "label": "公司事件",
        "keywords": ["NVDA", "AAPL", "TSLA", "英伟达", "苹果", "特斯拉"],
        "data_pack": ["stock", "earnings", "news"],
        "search_expansion": ["earnings", "revenue", "profit", "guidance", "market reaction"],
        "suggested_queries": _suggested(
            [
                ("公司最新财报", "{query} 最新财报 earnings"),
                ("收入与利润变化", "{query} 收入 利润 revenue profit"),
                ("管理层指引", "{query} 管理层指引 guidance"),
                ("市场反应", "{query} 市场反应 market reaction"),
            ]
        ),
        "logic_chain_template": [
            {"title": "公司事件", "content": "公司层面的新闻、财报或管理层表述", "description": "先识别公司层面的新闻、财报或管理层表述。"},
            {"title": "业绩/指引", "content": "收入、利润、现金流与管理层展望", "description": "市场会检查本期经营变化和前期指引是否兑现。"},
            {"title": "估值变化", "content": "增长预期与风险折现", "description": "如果经营质量或指引变化，估值假设可能随之调整。"},
            {"title": "股价反应", "content": "短期情绪与长期基本面重新平衡", "description": "价格反应不等于结论，需要继续观察数据验证。"},
        ],
        "prompt_rules": [
            "Analyze company news, earnings, guidance, operating changes, and market reaction without giving advice.",
            "If a company market-data item exists, use it as context only, not as a trading signal.",
        ],
    },
    "general": {
        "label": "综合市场主题",
        "keywords": [],
        "data_pack": [],
        "search_expansion": [],
        "suggested_queries": _suggested(
            [
                ("相关市场事件", "{query} 市场事件"),
                ("影响路径分析", "{query} 影响路径"),
                ("风险观察", "{query} 风险"),
            ]
        ),
        "logic_chain_template": [
            {"title": "事件/主题", "content": "输入对应的事件或主题", "description": "先识别输入对应的事件、主题或市场问题。"},
            {"title": "关键变量", "content": "政策、数据、盈利或流动性变化", "description": "再判断哪些变量会改变市场预期。"},
            {"title": "市场反应", "content": "风险偏好与资金定价", "description": "变量变化可能传导到情绪、估值和流动性。"},
            {"title": "资产影响", "content": "相关资产与板块表现", "description": "最后观察哪些资产或板块最容易受到影响。"},
        ],
        "prompt_rules": [
            "Analyze the input as a market cognition question when the topic is unclear.",
            "State evidence gaps naturally and avoid deterministic conclusions.",
        ],
    },
}


DATA_PACK_EXPLANATIONS = {
    "gold": "黄金价格是贵金属主题的核心观察对象，用于理解黄金资产的市场位置。",
    "dxy": "美元变化会影响黄金和风险资产的相对吸引力，是重要传导变量。",
    "us10y": "10年期美债收益率代表资金成本和利率预期，对风险资产估值有影响。",
    "gld": "黄金 ETF 可作为黄金资产资金偏好的代理观察。",
    "nvda": "英伟达是 AI 与半导体主题中的核心龙头之一，可作为产业链风险偏好的观察变量。",
    "qqq": "纳斯达克100 ETF 可作为大型科技成长资产风险偏好的观察变量。",
    "ai_etf": "AI 相关 ETF 可作为 AI 产业链整体资金偏好的代理变量。",
    "amd": "AMD 是 AI 与半导体算力链条的重要观察对象。",
    "soxx": "半导体 ETF 可作为芯片板块整体表现的代理变量。",
    "tsm": "台积电是先进制程和半导体供应链的重要观察对象。",
    "sp500": "标普500可作为美国风险资产整体风险偏好的观察变量。",
    "vix": "VIX 可作为市场波动预期和风险偏好的观察变量。",
    "btc": "BTC 可作为加密资产风险偏好的观察变量。",
    "eth": "ETH 可作为加密生态风险偏好和资金流的观察变量。",
    "wti": "WTI 原油可作为能源价格和供需变化的观察变量。",
    "brent": "Brent 原油可作为全球能源价格的观察变量。",
}


THEME_MATCH_ORDER = [
    "precious_metal",
    "semiconductor",
    "ai_sector",
    "crypto",
    "macro",
    "commodity",
    "real_estate",
    "robotics",
    "new_energy_vehicle",
]


def get_theme_package(topic_type: str) -> dict:
    """Return a theme package with general fallback."""
    return THEME_PACKAGES.get(topic_type) or THEME_PACKAGES["general"]
