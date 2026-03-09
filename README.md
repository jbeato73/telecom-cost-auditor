# telecom-cost-auditor

> **Day 14 — AIOps → Toll Fraud Detection Pivot**  
> Evolved from [`infra-cost-auditor`](https://github.com/jbeato73/infra-cost-auditor) | Built by Jose M. Beato with Claude (Anthropic)

---

## What This Does

`telecom_cost_auditor.py` is the first script in the **Toll Fraud Detection Pipeline**. It ingests raw branch call records from a CSV, cleans and standardizes the data, applies cost and duration alert thresholds, and outputs:

- A cleaned, flagged CSV of all call records
- A structured JSON audit report highlighting suspicious calls
- A formatted console summary for quick review

This is the data foundation every subsequent fraud detection module will build on.

---

## Why It Exists

Toll fraud — specifically International Revenue Share Fraud (IRSF) — costs the telecom industry billions annually. In a retail banking environment with thousands of branch locations, unauthorized calls to premium-rate international numbers can go undetected for weeks. This script automates the first line of detection: identifying calls that exceed normal cost and duration thresholds across branch PBX infrastructure.

---

## Evolution from infra-cost-auditor

| Original (`infra-cost-auditor`) | This Script (`telecom-cost-auditor`) |
|---|---|
| Ingests messy JSON cloud cost exports | Ingests branch call record CSVs |
| Flags high-priority budget alerts | Flags suspicious call cost & duration |
| Outputs tax-adjusted CSV reports | Outputs fraud-alert CSV + JSON report |
| Cloud infrastructure context | Telecom/PBX context |

The core architecture — load, clean, flag, report — carries forward directly.

---

## Project Structure

```
telecom-cost-auditor/
├── telecom_cost_auditor.py    # Main script
├── sample_call_records.csv    # Sample input data (20 fake branch records)
├── audited_call_records.csv   # Generated output (after running)
├── audit_report.json          # Generated JSON report (after running)
└── README.md                  # This file
```

---

## Project Setup

Run these commands in your terminal **before** opening VS Code:

```bash
# ─────────────────────────────────────────────────────────────
#  PROJECT SETUP — Day 14
# ─────────────────────────────────────────────────────────────

1.  cd /Users/jmb/PythonProjects
2.  uv init telecom-cost-auditor
3.  cd telecom-cost-auditor
4.  code .
5.  python3 -m venv .venv
6.  source .venv/bin/activate

# No extra packages today — 100% Python standard library
# (csv, json, os, datetime are all built-in)

# Create your script as:
#   telecom_cost_auditor.py

# Copy sample_call_records.csv into the same folder before running.
```

---

## Usage

### Run the script
```bash
python telecom_cost_auditor.py
```

### Review outputs
```
audited_call_records.csv   ← All records with alert flags
audit_report.json          ← Structured summary of flagged calls
Console output             ← Formatted summary with flagged call details
```

---

## Sample Output

```
============================================================
  TELECOM CALL AUDIT — SUMMARY REPORT
  Jose M. Beato | Day 14 | March 9, 2026
============================================================
  Total records processed : 19
  Records flagged         : 8
  Clean records           : 11
  Flagged cost total      : $210.00
============================================================

  ⚠  FLAGGED CALLS:

  Branch : NYC-001  |  Ext: 1042
  Dest   : +25261234567 (Somalia)
  Cost   : $37.00  |  Duration: 18.5 min
  Reason : Cost $37.00 exceeds $20.00 threshold | Duration 18.5 min exceeds 10 min threshold
  Time   : 2026-03-09 02:14:33
  --------------------------------------------------------
```

---

## Configurable Thresholds

Edit these values at the top of `telecom_cost_auditor.py`:

```python
ALERT_COST_THRESHOLD     = 20.00   # Flag calls costing more than $20
ALERT_DURATION_THRESHOLD = 10      # Flag calls longer than 10 minutes
```

---

## Python Best Practices Applied

- **Docstrings on every function** — explains purpose, args, and return values
- **COLUMN_MAP configuration** — decouples column names from logic
- **`with open()` for file handling** — safe, automatic file closing
- **Graceful error handling** — malformed rows are skipped, not crashes
- **`if __name__ == "__main__"`** — pipeline runs only when script is executed directly
- **Separation of concerns** — loading, cleaning, flagging, and output are distinct functions
- **Human-readable console output** — always know what ran and what it found

---

## Roadmap

| Day | Script | What's Added |
|-----|--------|--------------|
| ✅ 14 | `telecom_cost_auditor.py` | Load, clean, flag, report |
| 🔜 15 | `telecom_cost_auditor_v2.py` | Per-country daily cost aggregation + stricter thresholds |
| 🔜 17 | `fraud_detector.py` | Off-hours detection + datetime parsing |
| 🔜 19 | `risk_scorer.py` | Multi-factor risk scoring (LOW / MEDIUM / HIGH / CRITICAL) |

---

## GitHub Commit

After completing and testing the script:

```bash
# ─────────────────────────────────────────────────────────────
#  GITHUB COMMIT — Day 14
# ─────────────────────────────────────────────────────────────

git add telecom_cost_auditor.py sample_call_records.csv README.md
git commit -m "Day 14: Telecom Cost Auditor — csv ingestion, data cleaning, cost/duration alert thresholds, JSON report"
git push origin main
```

---

## Author

**Jose M. Beato**  
AIOps & Telecom Fraud Detection | Product Owner | Financial Services  
📍 New York Metro Area  
🔗 [LinkedIn](https://www.linkedin.com/in/jose-beato-5820798/) | [GitHub](https://github.com/jbeato73)

*Built with the assistance of [Claude](https://claude.ai) (Anthropic) — March 9, 2026*
