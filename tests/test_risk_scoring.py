import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.risk_scoring import MedicalInsuranceRiskScorer


class TestMedicalInsuranceRiskScorer(unittest.TestCase):
    def test_scores_department_with_drg_loss_and_cost_risks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "risk.db"
            conn = sqlite3.connect(db_path)
            conn.executescript(
                """
                CREATE TABLE departments (
                    department_id INTEGER,
                    department_name TEXT,
                    department_type TEXT,
                    director_name TEXT,
                    open_beds INTEGER
                );
                CREATE TABLE billing_records (
                    bill_id INTEGER,
                    patient_id INTEGER,
                    department_id INTEGER,
                    bill_date TEXT,
                    item_type TEXT,
                    item_name TEXT,
                    amount REAL
                );
                CREATE TABLE bed_daily_stats (
                    stat_id INTEGER,
                    department_id INTEGER,
                    stat_date TEXT,
                    open_beds INTEGER,
                    occupied_beds INTEGER
                );
                CREATE TABLE inpatient_records (
                    inpatient_id INTEGER,
                    patient_id INTEGER,
                    department_id INTEGER,
                    admission_date TEXT,
                    discharge_date TEXT,
                    bed_days INTEGER,
                    total_cost REAL,
                    status TEXT
                );
                CREATE TABLE drg_groups (
                    drg_code TEXT,
                    drg_name TEXT,
                    department_name TEXT,
                    standard_payment REAL,
                    average_cost REAL,
                    expected_los REAL,
                    risk_level TEXT
                );
                CREATE TABLE case_drg_records (
                    case_id INTEGER,
                    inpatient_id INTEGER,
                    patient_id INTEGER,
                    department_id INTEGER,
                    drg_code TEXT,
                    settlement_month TEXT,
                    total_cost REAL,
                    estimated_payment REAL,
                    profit_loss REAL,
                    length_of_stay INTEGER,
                    cost_overrun_rate REAL,
                    risk_flag TEXT,
                    risk_reason TEXT
                );
                """
            )
            conn.execute("INSERT INTO departments VALUES (1, '心血管内科', '住院科室', '刘主任', 55)")
            conn.executemany(
                "INSERT INTO billing_records VALUES (?, ?, 1, '2026-06-03', ?, ?, ?)",
                [
                    (1, 1001, "药品", "药品项目", 4200.0),
                    (2, 1001, "耗材", "耗材项目", 2600.0),
                    (3, 1001, "治疗", "治疗项目", 3200.0),
                ],
            )
            conn.execute("INSERT INTO bed_daily_stats VALUES (1, 1, '2026-06-03', 55, 53)")
            conn.execute(
                "INSERT INTO inpatient_records VALUES (1, 1001, 1, '2026-06-01', '2026-06-10', 10, 21000.0, '已出院')"
            )
            conn.execute("INSERT INTO drg_groups VALUES ('CV01', '循环系统介入治疗', '心血管内科', 17000.0, 15500.0, 7.0, '高')")
            conn.execute(
                """
                INSERT INTO case_drg_records VALUES (
                    1, 1, 1001, 1, 'CV01', '2026-06', 21000.0, 17000.0,
                    -4000.0, 10, 23.53, '高风险', '费用超出模拟支付标准；住院日偏长'
                )
                """
            )
            conn.commit()
            conn.close()

            scores = MedicalInsuranceRiskScorer(db_path).get_department_risk_scores(
                "2026-06-01", "2026-07-01", "2026-06-01", "2026-06-08"
            )

        self.assertEqual(scores[0]["department_name"], "心血管内科")
        self.assertGreaterEqual(scores[0]["risk_score"], 8)
        self.assertEqual(scores[0]["risk_level"], "高")
        self.assertIn("DRG/DIP模拟亏损", scores[0]["triggered_risks"])
        self.assertIn("医保办", scores[0]["suggested_action"])

    def test_summary_handles_no_departments(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "empty.db"
            conn = sqlite3.connect(db_path)
            conn.executescript(
                """
                CREATE TABLE departments (
                    department_id INTEGER,
                    department_name TEXT,
                    department_type TEXT,
                    director_name TEXT,
                    open_beds INTEGER
                );
                CREATE TABLE billing_records (
                    bill_id INTEGER,
                    patient_id INTEGER,
                    department_id INTEGER,
                    bill_date TEXT,
                    item_type TEXT,
                    item_name TEXT,
                    amount REAL
                );
                CREATE TABLE bed_daily_stats (
                    stat_id INTEGER,
                    department_id INTEGER,
                    stat_date TEXT,
                    open_beds INTEGER,
                    occupied_beds INTEGER
                );
                CREATE TABLE inpatient_records (
                    inpatient_id INTEGER,
                    patient_id INTEGER,
                    department_id INTEGER,
                    admission_date TEXT,
                    discharge_date TEXT,
                    bed_days INTEGER,
                    total_cost REAL,
                    status TEXT
                );
                CREATE TABLE case_drg_records (
                    case_id INTEGER,
                    inpatient_id INTEGER,
                    patient_id INTEGER,
                    department_id INTEGER,
                    drg_code TEXT,
                    settlement_month TEXT,
                    total_cost REAL,
                    estimated_payment REAL,
                    profit_loss REAL,
                    length_of_stay INTEGER,
                    cost_overrun_rate REAL,
                    risk_flag TEXT,
                    risk_reason TEXT
                );
                """
            )
            conn.commit()
            conn.close()

            summary = MedicalInsuranceRiskScorer(db_path).get_risk_summary(
                "2026-06-01", "2026-07-01", "2026-06-01", "2026-06-08"
            )

        self.assertEqual(summary["department_count"], 0)
        self.assertEqual(summary["high_risk_department_count"], 0)
        self.assertEqual(summary["simulated_drg_loss"], 0)


if __name__ == "__main__":
    unittest.main()
