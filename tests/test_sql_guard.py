import unittest

from src.sql_guard import add_default_limit, validate_select_sql


class TestSQLGuard(unittest.TestCase):
    def test_validate_select_sql_allows_simple_select(self):
        self.assertEqual(
            validate_select_sql("SELECT department_name FROM departments"),
            "SELECT department_name FROM departments",
        )

    def test_validate_select_sql_blocks_update(self):
        with self.assertRaises(ValueError):
            validate_select_sql("UPDATE departments SET open_beds = 0")

    def test_validate_select_sql_allows_readonly_cte(self):
        sql = "WITH beds AS (SELECT department_id FROM bed_daily_stats) SELECT department_id FROM beds"
        self.assertEqual(validate_select_sql(sql), sql)

    def test_add_default_limit(self):
        self.assertTrue(add_default_limit("SELECT department_name FROM departments", limit=5).endswith("LIMIT 5"))


if __name__ == "__main__":
    unittest.main()
