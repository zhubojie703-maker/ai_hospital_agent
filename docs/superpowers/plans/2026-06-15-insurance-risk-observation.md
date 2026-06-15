# Insurance Risk Observation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a lightweight "医保控费观察" capability that demonstrates DRG/DIP-aware product thinking without building formal settlement prediction.

**Architecture:** Extend the existing simulated hospital database with DRG/DIP-style reference groups and case-level mock settlement records. Add a focused `src/risk_scoring.py` service that converts existing operation metrics and simulated settlement data into department risk scores, then surface that through Streamlit, monthly reports, and documentation.

**Tech Stack:** Python, SQLite, pandas, Streamlit, Plotly, unittest.

---

### File Structure

- Create `src/risk_scoring.py`: department risk scoring, summary metrics, and DRG group aggregation.
- Create `tests/test_risk_scoring.py`: unit tests for score calculation and empty-data behavior.
- Modify `scripts/generate_hospital_data.py`: generate three lightweight mock tables: `drg_groups`, `case_drg_records`, `drg_risk_rules`.
- Modify `app.py`: add "医保控费观察" page, navigation entry, labels, and charts.
- Modify `src/report_generator.py`: add monthly "医保控费与 DRG/DIP 观察" section.
- Create `hospital_docs/医保控费风险观察说明.md`: RAG-readable boundary and metric explanation.
- Create `docs/product_landing_plan.md`: product positioning, user flow, boundaries, and next step.
- Create `docs/product_review_checklist.md`: review checklist for business, data, technical, and risk alignment.
- Modify `README.md`, `docs/frontend_skeleton.md`, `docs/optimization_comparison.md`, `docs/ui_upgrade_change_log.md`: align project description and page registry.

### Task 1: Risk Scoring Core

**Files:**
- Create: `tests/test_risk_scoring.py`
- Create: `src/risk_scoring.py`

- [ ] **Step 1: Write the failing test**

```python
scores = MedicalInsuranceRiskScorer(db_path).get_department_risk_scores(
    "2026-06-01", "2026-07-01", "2026-06-01", "2026-06-08"
)
self.assertGreaterEqual(scores[0]["risk_score"], 8)
self.assertIn("DRG/DIP模拟亏损", scores[0]["triggered_risks"])
```

- [ ] **Step 2: Run the test and confirm RED**

Run: `python -m unittest discover -s tests -p test_risk_scoring.py`
Expected: FAIL because `src.risk_scoring` does not exist.

- [ ] **Step 3: Implement minimal production code**

Create `src/risk_scoring.py` with a SQLite-backed `MedicalInsuranceRiskScorer` class that computes ratios, simulated DRG/DIP loss, and text recommendations.

- [ ] **Step 4: Run the test and confirm GREEN**

Run: `python -m unittest discover -s tests -p test_risk_scoring.py`
Expected: PASS.

### Task 2: Mock DRG/DIP Data

**Files:**
- Modify: `scripts/generate_hospital_data.py`
- Modify: `data/hospital_schema.json`

- [ ] **Step 1: Extend table creation**

Add `drg_groups`, `case_drg_records`, and `drg_risk_rules` to the database generator.

- [ ] **Step 2: Generate deterministic mock records**

For each inpatient record, assign a department-appropriate DRG group, estimated payment, cost overrun rate, profit/loss, and risk reason.

- [ ] **Step 3: Regenerate database**

Run: `python scripts/generate_hospital_data.py`
Expected: prints regenerated database and schema paths.

### Task 3: App and Report Surface

**Files:**
- Modify: `app.py`
- Modify: `src/report_generator.py`

- [ ] **Step 1: Add page registry entry**

Add a "医保控费观察" page between "科室绩效" and "运营简报".

- [ ] **Step 2: Render risk observation**

Show KPI cards, risk ranking table, DRG group simulated loss chart, and a boundary note.

- [ ] **Step 3: Add report section**

Add a monthly report section summarizing top risk departments and simulated DRG/DIP loss.

### Task 4: Product Documentation

**Files:**
- Create: `docs/product_landing_plan.md`
- Create: `docs/product_review_checklist.md`
- Create: `hospital_docs/医保控费风险观察说明.md`
- Modify: `README.md`
- Modify: `docs/frontend_skeleton.md`
- Modify: `docs/optimization_comparison.md`
- Modify: `docs/ui_upgrade_change_log.md`

- [ ] **Step 1: Document product positioning**

Explain how the feature demonstrates需求理解、产品设计、数据建模和落地边界意识.

- [ ] **Step 2: Document review checklist**

Include business, data, technical, and compliance/risk review questions.

- [ ] **Step 3: Update public-facing README**

Keep the claim lightweight: "模拟 DRG/DIP 控费观察", not formal DRG/DIP settlement.

### Task 5: Verification and GitHub Sync

**Files:**
- All changed files.

- [ ] **Step 1: Run unit tests**

Run: `python -m unittest discover -s tests`
Expected: all tests pass.

- [ ] **Step 2: Smoke-check generated data**

Run a short Python script that instantiates `MedicalInsuranceRiskScorer` and prints summary values.

- [ ] **Step 3: Inspect git diff**

Run: `git diff --stat`
Expected: only planned files changed.

- [ ] **Step 4: Commit and push**

Run: `git add ... && git commit -m "feat: add insurance risk observation"` then `git push origin main`.

### Self-Review

- Spec coverage: the plan covers lightweight simulated data, risk scoring, page display, report section, boundary docs, and GitHub sync.
- Placeholder scan: no "TBD" or undefined future modules are required by the plan.
- Scope check: this avoids formal DRG/DIP settlement and keeps the feature focused on portfolio/product landing value.
