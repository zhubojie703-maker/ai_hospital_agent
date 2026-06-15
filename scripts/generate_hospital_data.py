from __future__ import annotations

import json
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "hospital.db"
SCHEMA_PATH = DATA_DIR / "hospital_schema.json"
RANDOM_SEED = 20260607
START_DATE = date(2026, 3, 1)
END_DATE = date(2026, 6, 7)


DEPARTMENTS = [
    (1, "内科", "住院科室", "张主任", 58),
    (2, "外科", "住院科室", "李主任", 52),
    (3, "儿科", "门诊科室", "王主任", 32),
    (4, "妇产科", "住院科室", "赵主任", 45),
    (5, "ICU", "特殊科室", "周主任", 18),
    (6, "骨科", "住院科室", "陈主任", 50),
    (7, "心血管内科", "住院科室", "刘主任", 55),
    (8, "影像科", "医技科室", "孙主任", 0),
]

DOCTOR_TITLES = ["主任医师", "副主任医师", "主治医师", "住院医师"]
DIAGNOSES = {
    1: ["高血压", "糖尿病", "肺炎", "胃炎"],
    2: ["胆囊炎", "阑尾炎", "甲状腺结节"],
    3: ["上呼吸道感染", "支气管炎", "儿童发热"],
    4: ["妊娠管理", "妇科炎症", "产检"],
    5: ["重症肺炎", "休克", "多器官功能障碍"],
    6: ["骨折", "腰椎间盘突出", "关节炎"],
    7: ["冠心病", "心律失常", "心力衰竭"],
    8: ["影像检查", "CT 复查", "MRI 检查"],
}
ITEM_TYPES = ["药品", "检查", "检验", "治疗", "手术", "耗材", "挂号", "床位"]
SURGERY_NAMES = ["腹腔镜胆囊切除术", "阑尾切除术", "剖宫产术", "骨折内固定术", "冠脉介入术", "清创缝合术"]
SURGERY_LEVELS = ["一级", "二级", "三级", "四级"]

DRG_GROUPS = [
    ("IM01", "内科慢病综合治疗", "内科", 9800, 9000, 7.0, "中"),
    ("IM02", "肺炎及呼吸系统治疗", "内科", 11800, 10800, 8.0, "中"),
    ("GS01", "普外科腹腔镜手术", "外科", 16800, 15200, 7.0, "中"),
    ("GS02", "普外科复杂手术治疗", "外科", 23800, 21400, 10.0, "高"),
    ("PD01", "儿科呼吸道感染治疗", "儿科", 6200, 5600, 5.0, "低"),
    ("OB01", "妇产科分娩与围产管理", "妇产科", 12800, 11600, 6.0, "中"),
    ("IC01", "重症监护综合治疗", "ICU", 42000, 38500, 12.0, "高"),
    ("OR01", "骨科骨折内固定治疗", "骨科", 25800, 23100, 10.0, "高"),
    ("CV01", "心血管内科介入治疗", "心血管内科", 28800, 26200, 8.0, "高"),
    ("CV02", "心力衰竭内科治疗", "心血管内科", 18600, 17100, 9.0, "中"),
]

DRG_RISK_RULES = [
    (1, "费用超出模拟支付标准", "病例总费用高于模拟支付标准，提示经营亏损或费用结构需复核", 3),
    (2, "住院日偏长", "病例住院日超过模拟病组期望住院日 2 天以上，提示流程或病情复杂度需复核", 2),
    (3, "高风险病组亏损", "高风险病组同时出现模拟亏损，需联动医保办、病案室和临床科室复核", 3),
]


def daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def create_tables(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    for table in (
        "departments",
        "doctors",
        "outpatient_visits",
        "inpatient_records",
        "billing_records",
        "surgery_records",
        "bed_daily_stats",
        "drg_groups",
        "case_drg_records",
        "drg_risk_rules",
    ):
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    cursor.execute(
        """
        CREATE TABLE departments (
            department_id INTEGER PRIMARY KEY,
            department_name TEXT NOT NULL,
            department_type TEXT NOT NULL,
            director_name TEXT NOT NULL,
            open_beds INTEGER NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE doctors (
            doctor_id INTEGER PRIMARY KEY,
            doctor_name TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            FOREIGN KEY(department_id) REFERENCES departments(department_id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE outpatient_visits (
            visit_id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            visit_date TEXT NOT NULL,
            registration_fee REAL NOT NULL,
            diagnosis TEXT NOT NULL,
            FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id),
            FOREIGN KEY(department_id) REFERENCES departments(department_id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE inpatient_records (
            inpatient_id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            admission_date TEXT NOT NULL,
            discharge_date TEXT,
            bed_days INTEGER NOT NULL,
            total_cost REAL NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(department_id) REFERENCES departments(department_id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE billing_records (
            bill_id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            bill_date TEXT NOT NULL,
            item_type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY(department_id) REFERENCES departments(department_id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE surgery_records (
            surgery_id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            surgery_date TEXT NOT NULL,
            surgery_name TEXT NOT NULL,
            surgery_level TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            outcome TEXT NOT NULL,
            FOREIGN KEY(department_id) REFERENCES departments(department_id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE bed_daily_stats (
            stat_id INTEGER PRIMARY KEY,
            department_id INTEGER NOT NULL,
            stat_date TEXT NOT NULL,
            open_beds INTEGER NOT NULL,
            occupied_beds INTEGER NOT NULL,
            FOREIGN KEY(department_id) REFERENCES departments(department_id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE drg_groups (
            drg_code TEXT PRIMARY KEY,
            drg_name TEXT NOT NULL,
            department_name TEXT NOT NULL,
            standard_payment REAL NOT NULL,
            average_cost REAL NOT NULL,
            expected_los REAL NOT NULL,
            risk_level TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE case_drg_records (
            case_id INTEGER PRIMARY KEY,
            inpatient_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            drg_code TEXT NOT NULL,
            settlement_month TEXT NOT NULL,
            total_cost REAL NOT NULL,
            estimated_payment REAL NOT NULL,
            profit_loss REAL NOT NULL,
            length_of_stay INTEGER NOT NULL,
            cost_overrun_rate REAL NOT NULL,
            risk_flag TEXT NOT NULL,
            risk_reason TEXT NOT NULL,
            FOREIGN KEY(inpatient_id) REFERENCES inpatient_records(inpatient_id),
            FOREIGN KEY(department_id) REFERENCES departments(department_id),
            FOREIGN KEY(drg_code) REFERENCES drg_groups(drg_code)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE drg_risk_rules (
            rule_id INTEGER PRIMARY KEY,
            rule_name TEXT NOT NULL,
            condition_desc TEXT NOT NULL,
            risk_weight INTEGER NOT NULL
        )
        """
    )


def insert_drg_reference_data(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO drg_groups VALUES (?, ?, ?, ?, ?, ?, ?)", DRG_GROUPS)
    cursor.executemany("INSERT INTO drg_risk_rules VALUES (?, ?, ?, ?)", DRG_RISK_RULES)


def insert_departments_and_doctors(conn: sqlite3.Connection) -> list[tuple[int, str, int, str]]:
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO departments VALUES (?, ?, ?, ?, ?)", DEPARTMENTS)

    doctors = []
    doctor_id = 1
    surnames = ["张", "李", "王", "赵", "陈", "刘", "周", "孙", "郑", "黄", "吴", "何"]
    names = ["明", "华", "磊", "敏", "军", "芳", "强", "丽", "涛", "婷", "洋", "宁"]
    for dept_id, dept_name, _, _, _ in DEPARTMENTS:
        doctor_count = 3 if dept_name == "ICU" else 4
        for index in range(doctor_count):
            doctor_name = f"{random.choice(surnames)}{random.choice(names)}"
            title = DOCTOR_TITLES[index % len(DOCTOR_TITLES)]
            doctors.append((doctor_id, doctor_name, dept_id, title))
            doctor_id += 1
    cursor.executemany("INSERT INTO doctors VALUES (?, ?, ?, ?)", doctors)
    return doctors


def insert_outpatient_visits(conn: sqlite3.Connection, doctors: list[tuple[int, str, int, str]]) -> None:
    cursor = conn.cursor()
    doctors_by_department: dict[int, list[tuple[int, str, int, str]]] = {}
    for doctor in doctors:
        doctors_by_department.setdefault(doctor[2], []).append(doctor)

    visit_id = 1
    patient_id = 10000
    visit_rows = []
    bill_rows = []
    bill_id = 1
    for current in daterange(START_DATE, END_DATE):
        for dept_id, dept_name, _, _, open_beds in DEPARTMENTS:
            base = 26 if dept_name in {"内科", "儿科", "心血管内科"} else 18
            if dept_name == "影像科":
                base = 12
            if current.weekday() >= 5:
                base = int(base * 0.55)
            count = max(3, int(random.gauss(base, 6)))
            for _ in range(count):
                doctor = random.choice(doctors_by_department[dept_id])
                diagnosis = random.choice(DIAGNOSES[dept_id])
                fee = random.choice([20, 25, 30, 50])
                visit_rows.append(
                    (visit_id, patient_id, doctor[0], dept_id, current.isoformat(), fee, diagnosis)
                )
                bill_rows.append((bill_id, patient_id, dept_id, current.isoformat(), "挂号", "门诊挂号费", fee))
                bill_id += 1

                for item_type in random.sample(ITEM_TYPES[:4], random.randint(1, 3)):
                    amount_base = {
                        "药品": random.uniform(45, 360),
                        "检查": random.uniform(120, 900),
                        "检验": random.uniform(40, 260),
                        "治疗": random.uniform(80, 520),
                    }[item_type]
                    bill_rows.append(
                        (
                            bill_id,
                            patient_id,
                            dept_id,
                            current.isoformat(),
                            item_type,
                            f"{item_type}项目",
                            round(amount_base, 2),
                        )
                    )
                    bill_id += 1

                visit_id += 1
                patient_id += 1

    cursor.executemany("INSERT INTO outpatient_visits VALUES (?, ?, ?, ?, ?, ?, ?)", visit_rows)
    cursor.executemany("INSERT INTO billing_records VALUES (?, ?, ?, ?, ?, ?, ?)", bill_rows)


def get_next_bill_id(conn: sqlite3.Connection) -> int:
    cursor = conn.execute("SELECT COALESCE(MAX(bill_id), 0) + 1 FROM billing_records")
    return int(cursor.fetchone()[0])


def insert_inpatient_surgery_and_beds(conn: sqlite3.Connection, doctors: list[tuple[int, str, int, str]]) -> None:
    cursor = conn.cursor()
    doctors_by_department: dict[int, list[tuple[int, str, int, str]]] = {}
    for doctor in doctors:
        doctors_by_department.setdefault(doctor[2], []).append(doctor)
    drg_groups_by_department: dict[str, list[tuple[str, str, str, float, float, float, str]]] = {}
    for group in DRG_GROUPS:
        drg_groups_by_department.setdefault(group[2], []).append(group)

    bill_id = get_next_bill_id(conn)
    inpatient_id = 1
    surgery_id = 1
    case_id = 1
    patient_id = 50000
    inpatient_rows = []
    bill_rows = []
    surgery_rows = []
    bed_rows = []
    case_drg_rows = []
    bed_stat_id = 1

    for current in daterange(START_DATE, END_DATE):
        for dept_id, dept_name, dept_type, _, open_beds in DEPARTMENTS:
            if open_beds <= 0:
                continue

            pressure = 0.88 if dept_name in {"ICU", "心血管内科"} else 0.72
            weekday_boost = 0.04 if current.weekday() < 5 else -0.03
            if current >= date(2026, 6, 1) and dept_name in {"ICU", "心血管内科"}:
                occupied = min(open_beds, max(1, round(open_beds * random.uniform(0.93, 0.99))))
            else:
                occupied = min(open_beds, max(1, int(open_beds * random.uniform(pressure - 0.08, pressure + 0.1 + weekday_boost))))
            bed_rows.append((bed_stat_id, dept_id, current.isoformat(), open_beds, occupied))
            bed_stat_id += 1

            if random.random() < (0.32 if dept_name != "ICU" else 0.16):
                bed_days = random.randint(3, 13 if dept_name != "ICU" else 20)
                discharge = current + timedelta(days=bed_days)
                status = "已出院" if discharge <= END_DATE else "在院"
                total_cost = round(bed_days * random.uniform(550, 1800) + random.uniform(600, 6000), 2)
                inpatient_rows.append(
                    (
                        inpatient_id,
                        patient_id,
                        dept_id,
                        current.isoformat(),
                        discharge.isoformat() if status == "已出院" else None,
                        bed_days,
                        total_cost,
                        status,
                    )
                )
                drg_group = random.choice(drg_groups_by_department.get(dept_name, DRG_GROUPS[:2]))
                drg_code, _, _, standard_payment, _, expected_los, group_risk = drg_group
                estimated_payment = round(standard_payment * random.uniform(0.94, 1.06), 2)
                profit_loss = round(estimated_payment - total_cost, 2)
                cost_overrun_rate = round((total_cost - estimated_payment) * 100.0 / estimated_payment, 2)
                risk_reasons = []
                if profit_loss < 0:
                    risk_reasons.append("费用超出模拟支付标准")
                if bed_days > expected_los + 2:
                    risk_reasons.append("住院日偏长")
                if group_risk == "高" and profit_loss < 0:
                    risk_reasons.append("高风险病组亏损")
                if cost_overrun_rate > 10 or (group_risk == "高" and profit_loss < 0):
                    risk_flag = "高风险"
                elif risk_reasons:
                    risk_flag = "关注"
                else:
                    risk_flag = "正常"
                case_drg_rows.append(
                    (
                        case_id,
                        inpatient_id,
                        patient_id,
                        dept_id,
                        drg_code,
                        current.strftime("%Y-%m"),
                        total_cost,
                        estimated_payment,
                        profit_loss,
                        bed_days,
                        cost_overrun_rate,
                        risk_flag,
                        "；".join(risk_reasons) if risk_reasons else "未触发模拟控费风险",
                    )
                )
                case_id += 1

                for item_type in ["床位", "药品", "检查", "检验", "治疗", "耗材"]:
                    amount = {
                        "床位": bed_days * random.uniform(60, 220),
                        "药品": total_cost * random.uniform(0.16, 0.34),
                        "检查": total_cost * random.uniform(0.06, 0.2),
                        "检验": total_cost * random.uniform(0.04, 0.13),
                        "治疗": total_cost * random.uniform(0.08, 0.22),
                        "耗材": total_cost * random.uniform(0.03, 0.18),
                    }[item_type]
                    bill_rows.append(
                        (
                            bill_id,
                            patient_id,
                            dept_id,
                            current.isoformat(),
                            item_type,
                            f"住院{item_type}费",
                            round(amount, 2),
                        )
                    )
                    bill_id += 1

                if dept_name in {"外科", "妇产科", "骨科", "心血管内科"} and random.random() < 0.42:
                    doctor = random.choice(doctors_by_department[dept_id])
                    level = random.choices(SURGERY_LEVELS, weights=[1, 3, 4, 2], k=1)[0]
                    duration = random.randint(35, 230)
                    surgery_rows.append(
                        (
                            surgery_id,
                            patient_id,
                            dept_id,
                            doctor[0],
                            current.isoformat(),
                            random.choice(SURGERY_NAMES),
                            level,
                            duration,
                            random.choices(["成功", "好转", "并发症观察"], weights=[85, 12, 3], k=1)[0],
                        )
                    )
                    bill_rows.append(
                        (
                            bill_id,
                            patient_id,
                            dept_id,
                            current.isoformat(),
                            "手术",
                            "手术费",
                            round(random.uniform(1800, 22000), 2),
                        )
                    )
                    bill_id += 1
                    surgery_id += 1

                inpatient_id += 1
                patient_id += 1

    cursor.executemany("INSERT INTO inpatient_records VALUES (?, ?, ?, ?, ?, ?, ?, ?)", inpatient_rows)
    cursor.executemany("INSERT INTO billing_records VALUES (?, ?, ?, ?, ?, ?, ?)", bill_rows)
    cursor.executemany("INSERT INTO surgery_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", surgery_rows)
    cursor.executemany("INSERT INTO bed_daily_stats VALUES (?, ?, ?, ?, ?)", bed_rows)
    cursor.executemany(
        "INSERT INTO case_drg_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        case_drg_rows,
    )


def write_schema() -> None:
    schema = {
        "database": "hospital.db",
        "description": "医院运营管理模拟数据库，不含真实患者身份信息。",
        "date_range": {"start": START_DATE.isoformat(), "end": END_DATE.isoformat()},
        "tables": {
            "departments": {
                "description": "科室基础信息",
                "columns": {
                    "department_id": "科室ID，主键",
                    "department_name": "科室名称",
                    "department_type": "科室类型",
                    "director_name": "科主任姓名，模拟数据",
                    "open_beds": "开放床位数",
                },
            },
            "doctors": {
                "description": "医生基础信息，姓名为模拟数据",
                "columns": {
                    "doctor_id": "医生ID，主键",
                    "doctor_name": "医生姓名，模拟数据",
                    "department_id": "所属科室ID",
                    "title": "职称",
                },
            },
            "outpatient_visits": {
                "description": "门诊记录",
                "columns": {
                    "visit_id": "门诊记录ID",
                    "patient_id": "脱敏患者ID",
                    "doctor_id": "接诊医生ID",
                    "department_id": "接诊科室ID",
                    "visit_date": "就诊日期",
                    "registration_fee": "挂号费",
                    "diagnosis": "诊断类别，模拟标签",
                },
            },
            "inpatient_records": {
                "description": "住院记录",
                "columns": {
                    "inpatient_id": "住院记录ID",
                    "patient_id": "脱敏患者ID",
                    "department_id": "住院科室ID",
                    "admission_date": "入院日期",
                    "discharge_date": "出院日期",
                    "bed_days": "住院天数",
                    "total_cost": "住院总费用",
                    "status": "已出院/在院",
                },
            },
            "billing_records": {
                "description": "收费明细",
                "columns": {
                    "bill_id": "收费记录ID",
                    "patient_id": "脱敏患者ID",
                    "department_id": "计费科室ID",
                    "bill_date": "收费日期",
                    "item_type": "费用类别：药品、检查、检验、治疗、手术、耗材、挂号、床位",
                    "item_name": "收费项目名称",
                    "amount": "收费金额",
                },
            },
            "surgery_records": {
                "description": "手术记录",
                "columns": {
                    "surgery_id": "手术记录ID",
                    "patient_id": "脱敏患者ID",
                    "department_id": "手术科室ID",
                    "doctor_id": "主刀医生ID",
                    "surgery_date": "手术日期",
                    "surgery_name": "手术名称",
                    "surgery_level": "手术级别",
                    "duration_minutes": "手术时长",
                    "outcome": "转归，模拟标签",
                },
            },
            "bed_daily_stats": {
                "description": "床位日报",
                "columns": {
                    "stat_id": "日报ID",
                    "department_id": "科室ID",
                    "stat_date": "统计日期",
                    "open_beds": "开放床位数",
                    "occupied_beds": "占用床位数",
                },
            },
            "drg_groups": {
                "description": "模拟 DRG/DIP 病组参考表，用于展示医保控费观察，不代表正式医保分组规则",
                "columns": {
                    "drg_code": "模拟病组编码",
                    "drg_name": "模拟病组名称",
                    "department_name": "主要关联科室",
                    "standard_payment": "模拟支付标准",
                    "average_cost": "模拟平均成本",
                    "expected_los": "模拟期望住院日",
                    "risk_level": "病组经营风险等级",
                },
            },
            "case_drg_records": {
                "description": "模拟病例 DRG/DIP 观察记录，用于展示费用超支、住院日偏长和模拟亏损风险",
                "columns": {
                    "case_id": "模拟病例观察记录ID",
                    "inpatient_id": "关联住院记录ID",
                    "patient_id": "脱敏患者ID",
                    "department_id": "科室ID",
                    "drg_code": "模拟病组编码",
                    "settlement_month": "模拟结算月份",
                    "total_cost": "病例总费用",
                    "estimated_payment": "模拟医保支付金额",
                    "profit_loss": "模拟盈亏，支付金额减病例总费用",
                    "length_of_stay": "住院日",
                    "cost_overrun_rate": "费用超支率",
                    "risk_flag": "正常/关注/高风险",
                    "risk_reason": "模拟风险原因",
                },
            },
            "drg_risk_rules": {
                "description": "医保控费观察规则说明表，用于解释风险评分依据",
                "columns": {
                    "rule_id": "规则ID",
                    "rule_name": "规则名称",
                    "condition_desc": "触发条件说明",
                    "risk_weight": "风险权重",
                },
            },
        },
        "metrics": {
            "门诊量": "COUNT(outpatient_visits.visit_id)",
            "科室收入": "SUM(billing_records.amount) GROUP BY department_id",
            "药品收入占比": "SUM(item_type='药品' 的 amount) / SUM(amount)",
            "床位使用率": "occupied_beds / open_beds",
            "平均住院日": "AVG(inpatient_records.bed_days) WHERE status='已出院'",
            "手术量": "COUNT(surgery_records.surgery_id)",
            "模拟DRG/DIP亏损": "SUM(CASE WHEN case_drg_records.profit_loss < 0 THEN ABS(profit_loss) ELSE 0 END)",
            "模拟费用超支病例数": "COUNT(case_drg_records.case_id) WHERE profit_loss < 0",
        },
    }
    SCHEMA_PATH.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")


def create_database() -> None:
    random.seed(RANDOM_SEED)
    DATA_DIR.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        create_tables(conn)
        insert_drg_reference_data(conn)
        doctors = insert_departments_and_doctors(conn)
        insert_outpatient_visits(conn, doctors)
        insert_inpatient_surgery_and_beds(conn, doctors)
        conn.commit()
    write_schema()
    print(f"医院模拟数据库已生成：{DB_PATH}")
    print(f"Schema 已生成：{SCHEMA_PATH}")


if __name__ == "__main__":
    create_database()
