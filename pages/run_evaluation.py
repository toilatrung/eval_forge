"""pages/run_evaluation.py — trang Streamlit chạy eval từ UI (gọi runner.py).

Chỉ chịu trách nhiệm: kiểm tra config, kích hoạt 1 run, hiển thị tiến trình + tóm tắt nhanh.
Xem chi tiết từng case ở trang Results Explorer — tách biệt trách nhiệm giữa 2 trang.
"""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from metrics import compute_metrics
from runner import DEFAULT_SLEEP_SECONDS, run
from schemas import load_test_cases

load_dotenv()

st.set_page_config(page_title="Run Evaluation — eval_forge", page_icon="🧪", layout="wide")
st.title("Run Evaluation")

missing_keys = [k for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY") if not os.getenv(k)]
if missing_keys:
    st.error(
        f"Thiếu {', '.join(missing_keys)} trong `.env` — copy từ `.env.example` và điền key "
        "trước khi chạy."
    )
    st.stop()

load_result = load_test_cases()
if load_result.errors:
    st.warning(f"{len(load_result.errors)} file/case load lỗi, sẽ bị bỏ qua khi chạy:")
    for e in load_result.errors:
        st.write(f"- `{e.file}`: {e.error}")

st.write(f"Sẵn sàng chạy **{len(load_result.cases)} test case**.")
sleep_seconds = st.slider(
    "Nghỉ giữa mỗi case (giây) — tăng nếu gặp rate limit",
    min_value=0.0,
    max_value=5.0,
    value=DEFAULT_SLEEP_SECONDS,
    step=0.5,
)

if st.button("▶ Chạy Evaluation", type="primary"):
    progress_bar = st.progress(0.0)
    status_line = st.empty()
    log_box = st.container(height=280)

    def on_progress(done: int, total: int, result) -> None:
        progress_bar.progress(done / total)
        status_line.write(f"{done}/{total} — `{result.test_case_id}` → **{result.status}**")
        with log_box:
            icon = "✅" if result.status == "ok" else "⚠️"
            st.write(f"{icon} `{result.test_case_id}` ({result.category}) — {result.status}")

    with st.spinner("Đang chạy... (mỗi case gọi 2 API — model test + judge)"):
        output = run(sleep_seconds=sleep_seconds, on_progress=on_progress)

    st.success(f"Xong! Đã lưu `results/{output['run_id']}.json`.")

    metrics = compute_metrics(output)
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Overall accuracy",
        f"{metrics['overall_accuracy'] * 100:.1f}%" if metrics["overall_accuracy"] is not None else "n/a",
    )
    c2.metric("Parse failure rate", f"{metrics['parse_failure_rate'] * 100:.1f}%")
    c3.metric("Call error rate", f"{metrics['call_error_rate'] * 100:.1f}%")

    st.caption("Xem chi tiết từng case ở trang **Results Explorer**.")
