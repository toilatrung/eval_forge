"""ui/pages/calibration.py — chấm human label cho từng case đã được judge chấm, lưu ra file
JSON ngay sau mỗi lần chấm (không chỉ giữ trong session_state), tính agreement rate thật
giữa judge và người.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from eval_forge.metrics import compute_metrics, list_runs, load_labels, save_label

st.set_page_config(page_title="Calibration — eval_forge", page_icon="🧪", layout="wide")
st.title("Calibration")
st.caption(
    "Chấm nhãn người (human label) cho case đã được judge chấm, để đo **agreement rate "
    "thật** giữa judge và người — không phải số giả định (xem agent/AGENT.md §5)."
)

run_files = list(reversed(list_runs()))
if not run_files:
    st.info("Chưa có run nào. Sang trang **Run Evaluation** để chạy lần đầu.")
    st.stop()

run_path = st.selectbox("Chọn run để chấm", run_files, format_func=lambda p: p.stem)
raw = json.loads(run_path.read_text(encoding="utf-8"))
judged = [r for r in raw["results"] if r["status"] == "ok"]

if not judged:
    st.warning("Run này không có case nào được judge chấm (toàn bộ lỗi call/parse).")
    st.stop()

labels = load_labels(run_path)
metrics = compute_metrics(raw, labels=labels or None)

c1, c2 = st.columns(2)
c1.metric("Đã chấm", f"{len(labels)}/{len(judged)}")
c2.metric(
    "Agreement rate (judge vs human)",
    f"{metrics['agreement_rate_vs_human'] * 100:.1f}%" if metrics["agreement_rate_vs_human"] is not None else "n/a",
)

st.divider()

case_ids = [r["test_case_id"] for r in judged]
selected_id = st.selectbox(
    "Chọn case để chấm",
    case_ids,
    format_func=lambda cid: f"{cid}  {'✅ đã chấm' if cid in labels else '— chưa chấm'}",
)
case = next(r for r in judged if r["test_case_id"] == selected_id)

if case.get("prompt"):
    st.write("**Prompt:**")
    st.text(case["prompt"])
else:
    st.info(
        "Run này được chạy trước khi `runner.py` lưu lại `prompt` — chạy 1 run mới ở trang "
        "Run Evaluation để chấm với đầy đủ ngữ cảnh."
    )

if case.get("context"):
    with st.expander("Context"):
        st.text(case["context"])
if case.get("reference_answer"):
    st.write("**Reference answer / expected behavior:**", case["reference_answer"])
if case.get("rubric"):
    st.write("**Rubric:**")
    for r in case["rubric"]:
        st.write(f"- {r}")

st.write("**Model output:**")
st.text(case["model_output"])

st.write(f"**Judge verdict:** `{case['judge_verdict']}` (score {case['judge_score']})")
st.caption(case["judge_reasoning"])

st.divider()
st.subheader("Nhãn của bạn")

existing = labels.get(selected_id)
verdict_options = ["pass", "fail", "partial"]
default_verdict = existing["human_verdict"] if existing else case["judge_verdict"]
default_index = verdict_options.index(default_verdict) if default_verdict in verdict_options else 0

human_verdict = st.radio(
    "Verdict theo bạn", verdict_options, index=default_index, horizontal=True, key=f"verdict-{selected_id}"
)
note = st.text_input(
    "Ghi chú (optional)", value=existing["note"] if existing else "", key=f"note-{selected_id}"
)

if st.button("💾 Lưu nhãn", type="primary"):
    save_label(run_path, selected_id, human_verdict, note)
    st.success(f"Đã lưu nhãn cho `{selected_id}` vào `{run_path.stem}.labels.json`.")
    st.rerun()
