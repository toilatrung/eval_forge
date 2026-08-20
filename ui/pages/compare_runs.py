"""ui/pages/compare_runs.py — so sánh pairwise A/B giữa 2 run đã chạy.

Lưu ý: dự án hiện tại chỉ test 1 model tại 1 thời điểm (`DEFAULT_MODEL` trong `llm_client.py`)
— "so sánh" ở đây nghĩa là so sánh 2 **run** (ví dụ trước/sau khi đổi model, đổi prompt, hoặc
đổi test case), không phải chạy song song 2 model trong cùng 1 request.
"""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from eval_forge.metrics import list_runs, load_and_compute

st.set_page_config(page_title="Compare Runs — eval_forge", page_icon="🧪", layout="wide")
st.title("Compare Runs")
st.caption(
    "So sánh pairwise A/B giữa 2 run đã chạy — ví dụ trước/sau khi đổi model, prompt, hoặc "
    "test case."
)


def _pct(x: float | None) -> str:
    return f"{x * 100:.1f}%" if x is not None else "n/a"


run_files = list(reversed(list_runs()))
if len(run_files) < 2:
    st.info(
        f"Cần ít nhất 2 run để so sánh (hiện có {len(run_files)}). Chạy thêm ở trang "
        "**Run Evaluation**."
    )
    st.stop()

col_a, col_b = st.columns(2)
with col_a:
    run_a_path = st.selectbox(
        "Run A (mốc so sánh)",
        run_files,
        index=min(1, len(run_files) - 1),
        format_func=lambda p: p.stem,
        key="run_a",
    )
with col_b:
    run_b_path = st.selectbox(
        "Run B (run mới)", run_files, index=0, format_func=lambda p: p.stem, key="run_b"
    )

if run_a_path == run_b_path:
    st.warning("Chọn 2 run khác nhau để so sánh.")
    st.stop()

metrics_a = load_and_compute(run_a_path)
metrics_b = load_and_compute(run_b_path)

label_a, label_b = f"A: {run_a_path.stem}", f"B: {run_b_path.stem}"

st.subheader("Tổng quan")
overview_df = pd.DataFrame(
    {
        "metric": ["Overall accuracy", "Parse failure rate", "Call error rate"],
        label_a: [
            _pct(metrics_a["overall_accuracy"]),
            _pct(metrics_a["parse_failure_rate"]),
            _pct(metrics_a["call_error_rate"]),
        ],
        label_b: [
            _pct(metrics_b["overall_accuracy"]),
            _pct(metrics_b["parse_failure_rate"]),
            _pct(metrics_b["call_error_rate"]),
        ],
    }
).set_index("metric")
st.dataframe(overview_df, use_container_width=True)

st.subheader("Theo category")
categories = sorted(set(metrics_a["by_category"]) | set(metrics_b["by_category"]))
cat_rows = [
    {
        "category": cat,
        f"accuracy ({label_a})": _pct(metrics_a["by_category"].get(cat, {}).get("accuracy")),
        f"accuracy ({label_b})": _pct(metrics_b["by_category"].get(cat, {}).get("accuracy")),
    }
    for cat in categories
]
st.dataframe(pd.DataFrame(cat_rows).set_index("category"), use_container_width=True)

st.subheader("Theo case — regression / improvement")
raw_a = json.loads(run_a_path.read_text(encoding="utf-8"))
raw_b = json.loads(run_b_path.read_text(encoding="utf-8"))
by_id_a = {r["test_case_id"]: r for r in raw_a["results"]}
by_id_b = {r["test_case_id"]: r for r in raw_b["results"]}
common_ids = sorted(set(by_id_a) & set(by_id_b))


def _classify(verdict_a: str | None, verdict_b: str | None) -> str:
    if verdict_a == verdict_b:
        return "= không đổi"
    if verdict_a == "pass" and verdict_b != "pass":
        return "⬇ regression"
    if verdict_a != "pass" and verdict_b == "pass":
        return "⬆ improvement"
    return "↔ thay đổi"


diff_rows = []
for cid in common_ids:
    a, b = by_id_a[cid], by_id_b[cid]
    diff_rows.append(
        {
            "id": cid,
            "category": a["category"],
            f"verdict ({label_a})": a.get("judge_verdict"),
            f"verdict ({label_b})": b.get("judge_verdict"),
            "change": _classify(a.get("judge_verdict"), b.get("judge_verdict")),
        }
    )

diff_df = pd.DataFrame(diff_rows)
only_diff = st.checkbox("Chỉ hiện case có thay đổi", value=False)
shown_df = diff_df[diff_df["change"] != "= không đổi"] if only_diff else diff_df
st.dataframe(shown_df, use_container_width=True, hide_index=True)

regressions = (diff_df["change"] == "⬇ regression").sum()
improvements = (diff_df["change"] == "⬆ improvement").sum()
r1, r2 = st.columns(2)
r1.metric("⬇ Regression", int(regressions))
r2.metric("⬆ Improvement", int(improvements))

only_in_b = sorted(set(by_id_b) - set(by_id_a))
only_in_a = sorted(set(by_id_a) - set(by_id_b))
if only_in_a or only_in_b:
    st.caption(
        "Test set khác nhau giữa 2 run — "
        f"chỉ có ở A: {only_in_a or 'không có'} · chỉ có ở B: {only_in_b or 'không có'}"
    )
