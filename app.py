"""app.py — Streamlit entrypoint (multi-page, tự động lấy page từ pages/).

Trang chủ chỉ tóm tắt: số test case hiện có, và (nếu đã từng chạy) số liệu của run gần nhất
— chi tiết chạy eval / xem kết quả nằm ở pages/run_evaluation.py và pages/results_explorer.py.
Giữ trang chủ tối giản theo đúng nguyên tắc "UI chỉ cần đủ dùng" (agent/AGENT.md §5).
"""

from __future__ import annotations

import streamlit as st

from metrics import list_runs, load_and_compute
from schemas import load_test_cases

st.set_page_config(page_title="eval_forge", page_icon="🧪", layout="wide")

st.title("🧪 eval_forge")
st.caption("LLM Evaluation Harness + Internal Platform")

st.markdown(
    """
Đánh giá output của model bằng **rule-based evaluator** + **LLM-as-judge** (Claude — khác
họ với model test để giảm self-preference bias). Dùng menu bên trái để chạy eval hoặc xem
kết quả.
"""
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Test set hiện có")
    load_result = load_test_cases()
    if load_result.errors:
        st.warning(f"{len(load_result.errors)} file/case load lỗi — xem log console.")
    by_category: dict[str, int] = {}
    for c in load_result.cases:
        by_category[c.category] = by_category.get(c.category, 0) + 1
    st.metric("Tổng số test case", len(load_result.cases))
    for cat, count in sorted(by_category.items()):
        st.write(f"- **{cat}**: {count} case")

with col2:
    st.subheader("Run gần nhất")
    run_files = list_runs()
    if not run_files:
        st.info("Chưa có run nào. Sang trang **Run Evaluation** để chạy lần đầu.")
    else:
        latest = run_files[-1]
        metrics = load_and_compute(latest)
        st.caption(f"`{latest.name}`")
        st.metric("Overall accuracy", f"{metrics['overall_accuracy'] * 100:.1f}%" if metrics["overall_accuracy"] is not None else "n/a")
        m1, m2 = st.columns(2)
        m1.metric("Parse failure rate", f"{metrics['parse_failure_rate'] * 100:.1f}%")
        m2.metric("Call error rate", f"{metrics['call_error_rate'] * 100:.1f}%")
