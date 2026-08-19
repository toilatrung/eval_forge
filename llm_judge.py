"""llm_judge.py — gọi Claude (Anthropic) làm judge, khác họ với model test để giảm
self-preference bias.

TODO (Phase 2 — xem agent/taskboard.html, phần dễ tốn thời gian nhất):
- Prompt ép judge trả JSON đúng schema (response_format/tool-use nếu API hỗ trợ).
- Strip markdown fences trước khi parse.
- try/except quanh JSON parse — không throw làm crash toàn run.
- Log riêng metric `parse_failure`, không lẫn với kết quả judge hợp lệ.
- Đọc ANTHROPIC_BASE_URL từ .env — chỉ truyền base_url cho Anthropic client khi biến này có
  giá trị (không set thì dùng endpoint mặc định của SDK), để hỗ trợ proxy/gateway/API tương thích.
"""
