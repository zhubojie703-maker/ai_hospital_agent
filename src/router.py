from dataclasses import dataclass


@dataclass
class RouteDecision:
    route: str
    reason: str


REPORT_KEYWORDS = ("报告", "简报", "月报", "周报", "日报", "运营分析")
DOC_KEYWORDS = ("是什么意思", "怎么计算", "指标", "制度", "政策", "医保", "绩效", "口径", "说明")
SQL_KEYWORDS = (
    "多少",
    "排名",
    "最高",
    "最低",
    "超过",
    "统计",
    "趋势",
    "收入",
    "门诊",
    "住院",
    "床位",
    "药占比",
    "耗材",
    "费用结构",
    "医疗服务收入",
    "床位周转",
    "出院",
    "手术",
    "医生",
    "科室",
)


def route_question(question: str) -> RouteDecision:
    text = question.strip()
    if any(word in text for word in REPORT_KEYWORDS):
        return RouteDecision("report", "用户需要生成管理报告。")
    if any(word in text for word in DOC_KEYWORDS) and any(word in text for word in SQL_KEYWORDS):
        return RouteDecision("hybrid", "问题同时涉及数据查询和指标解释。")
    if any(word in text for word in DOC_KEYWORDS):
        return RouteDecision("rag", "用户需要制度或指标口径解释。")
    if any(word in text for word in SQL_KEYWORDS):
        return RouteDecision("sql", "用户需要查询医院运营数据。")
    return RouteDecision("rag", "未识别到明确数据查询意图，优先按知识问答处理。")
