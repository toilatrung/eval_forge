"""pages/results_explorer.py — trang Streamlit xem kết quả (load results/*.json,
bảng Pandas + filter theo category).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from metrics import list_runs, load_and_compute

st.set_page_config(page_title="Results Explorer — eval_forge", page_icon="🧪", layout="wide")
st.title("Results Explorer")

run_files = list(reversed(list_runs()))
if not run_files:
    st.info("Chưa có run nào. Sang trang **Run Evaluation** để chạy lần đầu.")
    st.stop()

run_path = st.selectbox("Chọn run", run_files, format_func=lambda p: p.stem)
metrics = load_and_compute(run_path)

st.subheader("Tổng quan")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Tổng số case", metrics["total_cases"])
c2.metric(
    "Overall accuracy",
    f"{metrics['overall_accuracy'] * 100:.1f}%" if metrics["overall_accuracy"] is not None else "n/a",
)
c3.metric("Parse failure rate", f"{metrics['parse_failure_rate'] * 100:.1f}%")
c4.metric("Call error rate", f"{metrics['call_error_rate'] * 100:.1f}%")

if metrics["agreement_rate_vs_human"] is not None:
    st.caption(
        f"Agreement rate (judge vs human label): **{metrics['agreement_rate_vs_human'] * 100:.1f}%** "
        f"(trên {metrics['labeled_count']} case đã chấm ở trang Calibration)."
    )
else:
    st.caption(
        "Agreement rate (judge vs human label): n/a — chưa có nhãn nào, sang trang "
        "**Calibration** để chấm."
    )

st.subheader("Theo category")
cat_df = pd.DataFrame(
    [{"category": cat, **m} for cat, m in metrics["by_category"].items()]
).set_index("category")
st.dataframe(cat_df, use_container_width=True)

st.subheader("Chi tiết từng case")
raw = json.loads(Path(run_path).read_text(encoding="utf-8"))
results = raw["results"]

categories = sorted({r["category"] for r in results})
selected_categories = st.multiselect("Filter theo category", categories, default=categories)
filtered = [r for r in results if r["category"] in selected_categories]

table_df = pd.DataFrame(
    [
        {
            "id": r["test_case_id"],
            "category": r["category"],
            "difficulty": r["difficulty"],
            "status": r["status"],
            "verdict": r.get("judge_verdict"),
            "score": r.get("judge_score"),
        }
        for r in filtered
    ]
)
st.dataframe(table_df, use_container_width=True, hide_index=True)

case_ids = [r["test_case_id"] for r in filtered]
if case_ids:
    selected_id = st.selectbox("Xem chi tiết case", case_ids)
    case = next(r for r in filtered if r["test_case_id"] == selected_id)
    if case.get("prompt"):
        st.write("**Prompt:**")
        st.text(case["prompt"])
    st.write("**Model output:**")
    st.text(case.get("model_output") or "(không có output — call_error)")
    st.write("**Rule-based signals:**", case["rule_signals"])
    if case.get("judge_reasoning"):
        st.write(f"**Judge:** {case['judge_verdict']} (score {case['judge_score']})")
        st.write(case["judge_reasoning"])
    if case.get("error"):
        st.error(case["error"])
