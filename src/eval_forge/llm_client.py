"""llm_client.py — gọi OpenAI API cho model cần eval (gpt-4o-mini).

Đọc OPENAI_BASE_URL từ .env — chỉ truyền base_url cho OpenAI client khi biến này có giá
trị (không set thì dùng endpoint mặc định của SDK), để hỗ trợ proxy/gateway/API tương thích.
"""

from __future__ import annotations

import os
import time

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_TOKENS = 512  # thấp để rẻ khi debug — runner.py có thể override khi cần
MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 1.0


class LLMClientError(RuntimeError):
    """Lỗi sau khi đã retry hết số lần cho phép, hoặc lỗi input không thể retry (4xx)."""


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMClientError("Thiếu OPENAI_API_KEY trong .env")

    kwargs: dict = {"api_key": api_key}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def call_model(
    prompt: str,
    *,
    context: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    client: OpenAI | None = None,
) -> str:
    """Gọi model cần eval, trả về text output.

    Retry với exponential backoff khi rate limit (429) hoặc lỗi kết nối/5xx tạm thời.
    Lỗi 4xx khác (auth sai, model không tồn tại...) fail ngay, không retry vô ích.
    """

    client = client or get_client()
    messages = []
    if context:
        messages.append(
            {
                "role": "system",
                "content": f"Use only the following context to answer the user's question:\n\n{context}",
            }
        )
    messages.append({"role": "user", "content": prompt})

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except RateLimitError as exc:
            last_error = exc
        except APIConnectionError as exc:
            last_error = exc
        except APIStatusError as exc:
            if exc.status_code and exc.status_code < 500:
                # lỗi input (auth, model sai tên...) — retry thêm cũng không giúp gì
                raise LLMClientError(f"OpenAI API lỗi không thể retry ({exc.status_code}): {exc}") from exc
            last_error = exc

        time.sleep(BASE_BACKOFF_SECONDS * (2**attempt))

    raise LLMClientError(f"Gọi OpenAI thất bại sau {MAX_RETRIES} lần retry: {last_error}") from last_error


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    out = call_model("Say 'ok' and nothing else.", max_tokens=16)
    print(repr(out))
