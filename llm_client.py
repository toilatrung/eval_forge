"""llm_client.py — gọi OpenAI API cho model cần eval (gpt-4o-mini).

TODO (Phase 2 — xem agent/taskboard.html):
- Wrapper gọi OpenAI chat completion, max_tokens thấp khi debug.
- Retry với exponential backoff khi gặp rate limit.
"""
