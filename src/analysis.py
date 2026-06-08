from __future__ import annotations

from statistics import mean


def analyze_metric_rows(rows: list[dict], question: str) -> list[str]:
    if not rows:
        return ["未查询到符合条件的数据，建议放宽时间范围或检查科室名称。"]

    notes: list[str] = []
    text = question

    if "床位" in text or any("bed_occupancy_rate" in row for row in rows):
        high = [
            row
            for row in rows
            if float(row.get("bed_occupancy_rate", row.get("avg_bed_occupancy_rate", 0)) or 0) >= 90
        ]
        if high:
            names = "、".join(str(row.get("department_name", "未知科室")) for row in high[:5])
            notes.append(f"{names} 床位使用率达到或超过 90%，提示住院资源较紧张。")

    if "药" in text or any("drug_ratio" in row for row in rows):
        values = [float(row.get("drug_ratio", 0) or 0) for row in rows if "drug_ratio" in row]
        if values and max(values) >= 30:
            notes.append("药品收入占比超过 30% 的科室需要结合病种结构、医保控费和合理用药规则进一步核查。")

    if "收入" in text:
        amount_fields = ("total_income", "department_income", "amount", "medical_service_income", "item_income")
        for field in amount_fields:
            values = [float(row.get(field, 0) or 0) for row in rows if field in row]
            if values:
                notes.append(f"本次结果中最高收入为 {max(values):,.2f} 元，平均值为 {mean(values):,.2f} 元。")
                break

    if "占比" in text:
        ratio_fields = ("item_ratio", "medical_service_income_ratio", "drug_ratio")
        for field in ratio_fields:
            values = [float(row.get(field, 0) or 0) for row in rows if field in row]
            if values:
                notes.append(f"本次结果中最高占比为 {max(values):.2f}%，建议结合病种结构和医保支付规则判断是否异常。")
                break

    if "平均住院日" in text or "住院日" in text:
        values = [float(row.get("avg_length_of_stay", 0) or 0) for row in rows if "avg_length_of_stay" in row]
        if values:
            notes.append(f"平均住院日最高为 {max(values):.2f} 天，需结合病种复杂度、出院流程和再入院风险综合判断。")

    if "床位周转" in text or "病床周转" in text:
        values = [float(row.get("bed_turnover_times", 0) or 0) for row in rows if "bed_turnover_times" in row]
        if values:
            notes.append(f"病床周转次数最高为 {max(values):.2f} 次，可结合床位使用率和平均住院日分析床位效率。")

    if "住院" in text:
        values = [int(row.get("inpatient_count", 0) or 0) for row in rows if "inpatient_count" in row]
        if values:
            notes.append(f"住院人数最高为 {max(values)} 人，建议联动床位、护理和出院计划管理。")

    if "手术" in text:
        values = [int(row.get("surgery_count", 0) or 0) for row in rows if "surgery_count" in row]
        if values:
            notes.append(f"手术量最高分组为 {max(values)} 台，应结合手术级别、耗材和术后床位资源评估压力。")

    if "门诊" in text or any("visit_count" in row for row in rows):
        values = [int(row.get("visit_count", 0) or 0) for row in rows if "visit_count" in row]
        if values:
            notes.append(f"门诊量最高值为 {max(values)} 人次，可优先关注排班、候诊和诊室资源配置。")

    if not notes:
        notes.append("结果已按医院运营管理口径汇总，可结合趋势、排名和异常阈值进一步分析。")
    return notes
