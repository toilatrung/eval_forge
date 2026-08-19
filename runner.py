"""runner.py — nối pipeline: load test case -> llm_client -> evaluator -> llm_judge
-> lưu results/*.json.

TODO (Phase 3 — xem agent/taskboard.html):
- time.sleep() nhỏ giữa các call khi chạy full test set (rate limit).
- Lưu kết quả ra results/<run_id>.json.
"""
