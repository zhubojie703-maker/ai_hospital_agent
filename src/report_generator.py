from __future__ import annotations

from .sql_agent import HospitalSQLAgent


class HospitalReportGenerator:
    def __init__(self, sql_agent: HospitalSQLAgent | None = None):
        self.sql_agent = sql_agent or HospitalSQLAgent()

    def generate_monthly_report(self, question: str = "生成本月医院运营简报") -> str:
        outpatient = self.sql_agent.ask("本月门诊量最高的5个科室", limit=5)
        income = self.sql_agent.ask("本月各科室收入排名", limit=5)
        drug = self.sql_agent.ask("本月药占比是多少", limit=5)
        beds = self.sql_agent.ask("最近7天床位使用率超过90%的科室", limit=10)
        surgery = self.sql_agent.ask("本月各科室手术量", limit=6)

        def fmt_rows(rows: list[dict], key: str, value: str, unit: str = "") -> str:
            if not rows:
                return "暂无数据"
            return "；".join(f"{row.get(key)} {row.get(value)}{unit}" for row in rows)

        risk_notes = beds.analysis + drug.analysis
        risk_text = "\n".join(f"- {note}" for note in risk_notes)

        return f"""# 医院运营月度简报（模拟数据）

## 一、总体运营概况
本月门诊量排名靠前科室：{fmt_rows(outpatient.rows, "department_name", "visit_count", "人次")}。
本月收入排名靠前科室：{fmt_rows(income.rows, "department_name", "total_income", "元")}。

## 二、科室表现分析
门诊端建议关注高流量科室的排班、候诊时间和诊室资源；收入端建议结合病种结构、医保支付规则和成本结构判断，不宜只按收入高低评价科室。

## 三、收入结构分析
药品收入占比较高科室：{fmt_rows(drug.rows, "department_name", "drug_ratio", "%")}。
该指标用于内部合理用药和费用结构监测，不应作为单一考核指标。

## 四、床位使用情况
最近 7 天床位紧张科室：{fmt_rows(beds.rows, "department_name", "avg_bed_occupancy_rate", "%")}。

## 五、手术工作量
本月手术工作量概览：{fmt_rows(surgery.rows, "department_name", "surgery_count", "台")}。

## 六、异常风险提示
{risk_text}

## 七、管理建议
- 对床位使用率持续超过 90% 的科室，优先评估出入院流程、床位周转和跨科调配。
- 对药品收入占比偏高科室，结合病种、诊疗路径和医保规则做二次核查。
- 对门诊量高峰科室，建议联动排班、预约号源和检查资源，降低患者等待时间。
- 后续可接入真实 HIS、财务和绩效系统，替换当前模拟明细数据。
"""
