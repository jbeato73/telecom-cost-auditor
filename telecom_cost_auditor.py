# =============================================================================
# telecom_cost_auditor.py
#
# Day 14 — AIOps → Toll Fraud Detection Pivot
# Author  : Jose M. Beato
# Created : March 9, 2026
# Built with the assistance of Claude (Anthropic) — claude.ai
#
# Description:
#   Evolved from infra-cost-auditor, this script pivots from cloud
#   infrastructure cost analysis to telecom call record auditing.
#   It ingests a CSV of branch call records, cleans and standardizes
#   the data, and produces a high-priority alert report identifying
#   calls that exceed cost and duration thresholds — the first line
#   of defense in a toll fraud detection pipeline.
#
# Forked from : infra-cost-auditor (github.com/jbeato73/infra-cost-auditor)
# Next script : telecom_cost_auditor_v2.py (Day 15 — threshold detection)
#
# Project Setup (run in terminal before opening VS Code):
# ─────────────────────────────────────────────────────
#   1. cd /Users/jmb/PythonProjects
#   2. uv init telecom-cost-auditor
#   3. cd telecom-cost-auditor
#   4. code .
#   5. python3 -m venv .venv
#   6. source .venv/bin/activate
#   # No extra packages — 100% Python standard library
#   # Create this file as: telecom_cost_auditor.py
#
# GitHub Commit (after completing):
# ──────────────────────────────────
#   git add telecom_cost_auditor.py sample_call_records.csv README.md
#   git commit -m "Day 14: Telecom Cost Auditor — csv ingestion, data cleaning, cost/duration alert thresholds, JSON report"
#   git push origin main
# =============================================================================

import csv  # Built-in: read and write CSV files
import json  # Built-in: save structured output as JSON
import os  # Built-in: file path handling
from datetime import datetime  # Built-in: timestamp generation


# =============================================================================
# SECTION 1 — CONFIGURATION
# Best Practice: Never hardcode values that might change. Keep them at the
# top of your script in one place so they're easy to find and update.
# =============================================================================

# Input/output file paths
INPUT_FILE = "sample_call_records.csv"  # Simulated branch call log
OUTPUT_CSV = "audited_call_records.csv"  # Cleaned, standardized output
OUTPUT_JSON = "audit_report.json"  # Structured summary report

# Column name mapping — maps raw CSV headers to clean internal names
# Best Practice: Define this explicitly so your code doesn't break if
# someone renames a column in the source file.
COLUMN_MAP = {
    "Branch ID": "branch_id",
    "Caller Extension": "caller_ext",
    "Destination Number": "destination",
    "Destination Country": "country",
    "Call Duration (min)": "duration_mins",
    "Call Cost (USD)": "cost_usd",
    "Timestamp": "timestamp",
}

# Audit thresholds — what we consider worth flagging at this stage
# (More sophisticated scoring rules come in Day 15)
ALERT_COST_THRESHOLD = 20.00  # Flag any single call costing more than $20
ALERT_DURATION_THRESHOLD = 10  # Flag any call longer than 10 minutes


# =============================================================================
# SECTION 2 — DATA LOADING
# Best Practice: Always separate the concern of loading data from processing
# it. If the file format changes, you only update this one function.
# =============================================================================


def load_call_records(filepath):
    """
    Reads the raw call records CSV and returns a list of row dictionaries.

    Args:
        filepath (str): Path to the input CSV file.

    Returns:
        list[dict]: Raw rows from the CSV, each as a dictionary.

    Best Practice: Docstrings on every function. They explain what the
    function does, what it expects, and what it returns — essential when
    others (or future you) read this code.
    """
    records = []

    # Best Practice: Always use 'with open()' for file handling.
    # It automatically closes the file even if an error occurs.
    try:
        with open(filepath, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                records.append(dict(row))
        print(f"[INFO] Loaded {len(records)} records from '{filepath}'")
    except FileNotFoundError:
        # Best Practice: Give meaningful error messages, not generic ones.
        print(f"[ERROR] File not found: '{filepath}'")
        print(f"        Make sure '{filepath}' is in the same folder as this script.")

    return records


# =============================================================================
# SECTION 3 — DATA CLEANING
# Best Practice: Clean data before you analyze it. Real-world data is messy —
# missing values, inconsistent formatting, extra spaces. Clean it once, early.
# =============================================================================


def clean_record(raw_row):
    """
    Takes one raw CSV row and returns a cleaned, standardized dictionary
    using the COLUMN_MAP defined above.

    Args:
        raw_row (dict): A single raw row from the CSV reader.

    Returns:
        dict | None: Cleaned record, or None if the row is invalid.
    """
    cleaned = {}

    try:
        # Remap column names using our COLUMN_MAP
        for raw_col, clean_col in COLUMN_MAP.items():
            value = raw_row.get(raw_col, "").strip()  # .strip() removes whitespace
            cleaned[clean_col] = value

        # Convert numeric fields from strings to proper types
        # Best Practice: Convert types as early as possible so downstream
        # code always gets the right type without re-converting.
        cleaned["duration_mins"] = (
            float(cleaned["duration_mins"]) if cleaned["duration_mins"] else 0.0
        )
        cleaned["cost_usd"] = float(cleaned["cost_usd"]) if cleaned["cost_usd"] else 0.0

        # Normalize country to title case (e.g., "SOMALIA" → "Somalia")
        cleaned["country"] = cleaned["country"].title()

    except (ValueError, KeyError) as e:
        # Best Practice: Log the problem and return None rather than crashing.
        # Your pipeline keeps running even if one record is malformed.
        print(f"[WARN] Skipping malformed record: {e} | Row: {raw_row}")
        return None

    return cleaned


def clean_all_records(raw_records):
    """
    Applies clean_record() to every row and filters out any that failed.

    Args:
        raw_records (list[dict]): All raw rows from the CSV.

    Returns:
        list[dict]: List of successfully cleaned records.
    """
    cleaned = []
    skipped = 0

    for row in raw_records:
        result = clean_record(row)
        if result:
            cleaned.append(result)
        else:
            skipped += 1

    print(f"[INFO] Cleaned {len(cleaned)} records. Skipped {skipped} malformed rows.")
    return cleaned


# =============================================================================
# SECTION 4 — AUDIT LOGIC
# Best Practice: Keep your business rules in dedicated functions, separate
# from data loading and output. If a rule changes, you update one function.
# =============================================================================


def flag_record(record):
    """
    Evaluates a cleaned call record against audit thresholds and adds
    an 'alert' field and 'alert_reason' field to the record.

    Args:
        record (dict): A cleaned call record.

    Returns:
        dict: The same record with 'alert' (bool) and 'alert_reason' (str) added.
    """
    reasons = []

    # Rule 1: Cost threshold
    if record["cost_usd"] > ALERT_COST_THRESHOLD:
        reasons.append(
            f"Cost ${record['cost_usd']:.2f} exceeds ${ALERT_COST_THRESHOLD:.2f} threshold"
        )

    # Rule 2: Duration threshold
    if record["duration_mins"] > ALERT_DURATION_THRESHOLD:
        reasons.append(
            f"Duration {record['duration_mins']:.1f} min exceeds {ALERT_DURATION_THRESHOLD} min threshold"
        )

    # Best Practice: Store both a boolean flag AND a human-readable reason.
    # The boolean is for filtering; the reason is for reporting and tickets.
    record["alert"] = len(reasons) > 0
    record["alert_reason"] = " | ".join(reasons) if reasons else "None"

    return record


def audit_all_records(cleaned_records):
    """
    Applies flag_record() to every cleaned record.

    Args:
        cleaned_records (list[dict]): All cleaned records.

    Returns:
        list[dict]: Records with alert flags applied.
    """
    return [flag_record(record) for record in cleaned_records]


# =============================================================================
# SECTION 5 — OUTPUT
# Best Practice: Separate your output logic from your processing logic.
# One function writes CSV, another writes JSON — each does one thing well.
# =============================================================================


def write_output_csv(records, filepath):
    """
    Writes all audited records (clean + alert columns) to a CSV file.

    Args:
        records (list[dict]): Audited call records.
        filepath (str): Output file path.
    """
    if not records:
        print("[WARN] No records to write.")
        return

    # Best Practice: Derive fieldnames from actual data so the output
    # always matches whatever columns exist in the records.
    fieldnames = list(records[0].keys())

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"[INFO] Output CSV written → '{filepath}'")


def write_audit_report(records, filepath):
    """
    Generates a structured JSON audit report summarizing:
    - Total records processed
    - Total flagged records
    - Total cost of flagged calls
    - List of flagged records for review

    Args:
        records (list[dict]): All audited records.
        filepath (str): Output JSON file path.
    """
    flagged = [r for r in records if r["alert"]]
    total_cost = sum(r["cost_usd"] for r in flagged)

    report = {
        "report_title": "Telecom Call Cost Audit Report",
        "generated_by": "Jose M. Beato — telecom_cost_auditor.py",
        "generated_with": "Built with Claude (Anthropic) — claude.ai",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "audit_day": "Day 14 — AIOps → Toll Fraud Pivot",
        "total_records": len(records),
        "total_flagged": len(flagged),
        "flagged_total_cost": round(total_cost, 2),
        "thresholds_applied": {
            "cost_usd_threshold": ALERT_COST_THRESHOLD,
            "duration_mins_threshold": ALERT_DURATION_THRESHOLD,
        },
        "flagged_records": flagged,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        # Best Practice: indent=2 makes JSON human-readable.
        # Without it, the file is one long unreadable line.
        json.dump(report, f, indent=2)

    print(f"[INFO] Audit report written  → '{filepath}'")


# =============================================================================
# SECTION 6 — SUMMARY PRINT
# Best Practice: Always print a human-readable summary to the console
# so you know what happened when you run the script.
# =============================================================================


def print_summary(records):
    """
    Prints a formatted audit summary to the console.

    Args:
        records (list[dict]): All audited records.
    """
    flagged = [r for r in records if r["alert"]]

    print()
    print("=" * 60)
    print("  TELECOM CALL AUDIT — SUMMARY REPORT")
    print("  Jose M. Beato | Day 14 | March 9, 2026")
    print("=" * 60)
    print(f"  Total records processed : {len(records)}")
    print(f"  Records flagged         : {len(flagged)}")
    print(f"  Clean records           : {len(records) - len(flagged)}")
    print(f"  Flagged cost total      : ${sum(r['cost_usd'] for r in flagged):.2f}")
    print("=" * 60)

    if flagged:
        print("\n  ⚠  FLAGGED CALLS:\n")
        for r in flagged:
            print(f"  Branch : {r['branch_id']}  |  Ext: {r['caller_ext']}")
            print(f"  Dest   : {r['destination']} ({r['country']})")
            print(
                f"  Cost   : ${r['cost_usd']:.2f}  |  Duration: {r['duration_mins']:.1f} min"
            )
            print(f"  Reason : {r['alert_reason']}")
            print(f"  Time   : {r['timestamp']}")
            print("  " + "-" * 56)
    else:
        print("\n  ✅  No records exceeded alert thresholds.\n")

    print()


# =============================================================================
# SECTION 7 — MAIN ENTRY POINT
# Best Practice: Always use `if __name__ == "__main__"` to protect your
# main logic. This allows other scripts to import your functions without
# automatically running the whole pipeline.
# =============================================================================


def main():
    """
    Orchestrates the full audit pipeline:
    Load → Clean → Flag → Write CSV → Write JSON → Print Summary
    """
    print()
    print("=" * 60)
    print("  telecom_cost_auditor.py — Starting...")
    print("  Forked from: infra-cost-auditor")
    print("  Day 14 | AIOps → Toll Fraud Detection Pivot")
    print("=" * 60)
    print()

    # Step 1: Load raw records from CSV
    raw_records = load_call_records(INPUT_FILE)
    if not raw_records:
        print("[ERROR] No records loaded. Exiting.")
        return

    # Step 2: Clean and standardize
    cleaned_records = clean_all_records(raw_records)
    if not cleaned_records:
        print("[ERROR] No valid records after cleaning. Exiting.")
        return

    # Step 3: Apply audit flags
    audited_records = audit_all_records(cleaned_records)

    # Step 4: Write outputs
    write_output_csv(audited_records, OUTPUT_CSV)
    write_audit_report(audited_records, OUTPUT_JSON)

    # Step 5: Print summary to console
    print_summary(audited_records)


if __name__ == "__main__":
    main()
