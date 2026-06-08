from __future__ import annotations

import pandas as pd
import plotly.express as px


def make_chart(rows: list[dict], question: str):
    if not rows:
        return None
    df = pd.DataFrame(rows)
    text = question

    if "收入" in text and {"department_name", "total_income"}.issubset(df.columns):
        return px.bar(df, x="department_name", y="total_income", title="科室收入排名", labels={"department_name": "科室", "total_income": "总收入"})

    if "门诊" in text and {"department_name", "visit_count"}.issubset(df.columns):
        return px.bar(df, x="department_name", y="visit_count", title="科室门诊量排名", labels={"department_name": "科室", "visit_count": "门诊量"})

    if "床位周转" in text and {"department_name", "bed_turnover_times"}.issubset(df.columns):
        return px.bar(df, x="department_name", y="bed_turnover_times", title="床位周转次数", labels={"department_name": "科室", "bed_turnover_times": "床位周转次数"})

    if "床位" in text and {"department_name", "avg_bed_occupancy_rate"}.issubset(df.columns):
        return px.bar(df, x="department_name", y="avg_bed_occupancy_rate", title="平均床位使用率", labels={"department_name": "科室", "avg_bed_occupancy_rate": "平均床位使用率"})

    if ("平均住院日" in text or "住院日" in text) and {"department_name", "avg_length_of_stay"}.issubset(df.columns):
        return px.bar(df, x="department_name", y="avg_length_of_stay", title="平均住院日", labels={"department_name": "科室", "avg_length_of_stay": "平均住院日"})

    if "住院" in text and {"department_name", "inpatient_count"}.issubset(df.columns):
        return px.bar(df, x="department_name", y="inpatient_count", title="科室住院人数", labels={"department_name": "科室", "inpatient_count": "住院人数"})

    if "手术" in text and {"department_name", "surgery_count"}.issubset(df.columns):
        return px.bar(df, x="department_name", y="surgery_count", color="surgery_level", title="手术量按级别分布", labels={"department_name": "科室", "surgery_count": "手术量", "surgery_level": "手术级别"})

    if "医疗服务收入" in text and {"department_name", "medical_service_income_ratio"}.issubset(df.columns):
        return px.bar(df, x="department_name", y="medical_service_income_ratio", title="医疗服务收入占比", labels={"department_name": "科室", "medical_service_income_ratio": "医疗服务收入占比"})

    if "占比" in text and {"department_name", "item_ratio"}.issubset(df.columns):
        return px.bar(df, x="department_name", y="item_ratio", title="费用项目占比排名", labels={"department_name": "科室", "item_ratio": "项目占比"})

    if "药" in text and {"item_type", "amount"}.issubset(df.columns):
        return px.pie(df, names="item_type", values="amount", title="收入结构")

    date_col = next((col for col in ("stat_date", "visit_date", "bill_date") if col in df.columns), None)
    numeric_col = next((col for col in ("visit_count", "amount", "bed_occupancy_rate") if col in df.columns), None)
    if date_col and numeric_col:
        return px.line(df, x=date_col, y=numeric_col, title="趋势图")

    return None
