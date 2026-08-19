"""llm_judge.py — gọi Claude (Anthropic) làm judge, khác họ với model test để giảm
self-preference bias (agent/AGENT.md §5).

Phần dễ tốn thời gian nhất (theo kế hoạch ban đầu): ép judge trả JSON ổn định, xử lý mọi
lỗi parse mà KHÔNG throw làm crash toàn run — caller (runner.py, Phase 3) bắt riêng
`JudgeParseError` và log vào metric `parse_failure_rate`, không lẫn với verdict hợp lệ.

Đọc ANTHROPIC_BASE_URL từ .env — chỉ truyền base_url cho Anthropic client khi biến này có
giá trị (không set thì dùng endpoint mặc định của SDK), để hỗ trợ proxy/gateway/API tương thích.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass

from anthropic import Anthropic, APIConnectionError, APIStatusError, RateLimitError

from schemas import TestCase

DEFAULT_JUDGE_MODEL = "claude-haiku-4-5-20251001"  # rẻ, đủ cho demo — đổi ở đây nếu cần
MAX_TOKENS = 512
MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 1.0

VALID_VERDICTS = ("pass", "fail", "partial")

JUDGE_SYSTEM_PROMPT = """You are an impartial evaluator judging the output of ANOTHER AI \
model (not yourself). You will be given the original prompt/context given to that model, \
optionally a reference answer or rubric, and the model's output to judge.

Judge strictly based on the rubric/reference provided, not your own stylistic preference.

Respond with ONLY a single JSON object — no markdown code fences, no text before or after \
it — matching EXACTLY this schema:
{"verdict": "pass" | "fail" | "partial", "score": <integer 1-5>, "reasoning": "<1-2 sentences>"}
"""


class JudgeCallError(RuntimeError):
    """Lỗi gọi API (network/rate limit/auth) sau khi đã retry — khác với lỗi parse JSON."""


class JudgeParseError(RuntimeError):
    """Judge đã trả lời nhưng không parse được thành JSON hợp lệ theo schema mong đợi.

    Không phải lỗi hệ thống — caller nên bắt riêng exception này, log vào metric
    `parse_failure_rate`, và tiếp tục chạy các test case khác (không crash toàn run).
    """

    def __init__(self, raw_text: str, cause: Exception):
        super().__init__(f"Không parse được JSON hợp lệ từ judge: {cause}")
        self.raw_text = raw_text
        self.cause = cause


@dataclass
class JudgeVerdict:
    test_case_id: str
    verdict: str  # "pass" | "fail" | "partial"
    score: int
    reasoning: str
    raw_response: str


def get_client() -> Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise JudgeCallError("Thiếu ANTHROPIC_API_KEY trong .env")

    kwargs: dict = {"api_key": api_key}
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return Anthropic(**kwargs)


def _strip_markdown_fences(text: str) -> str:
    """Judge đôi khi vẫn bọc JSON trong ```json ... ``` dù đã bị cấm trong prompt — strip
    trước khi json.loads() thay vì fail ngay."""

    text = text.strip()
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def _build_judge_prompt(test_case: TestCase, model_output: str) -> str:
    parts = [
        f"Category: {test_case.category}",
        f"Prompt given to the model: {test_case.prompt}",
    ]
    if test_case.context:
        parts.append(f"Context provided to the model:\n{test_case.context}")
    if test_case.reference_answer:
        parts.append(f"Reference answer / expected behavior: {test_case.reference_answer}")
    if test_case.rubric:
        parts.append("Rubric criteria:\n" + "\n".join(f"- {r}" for r in test_case.rubric))
    parts.append(f"Model output to judge:\n{model_output}")
    return "\n\n".join(parts)


def _parse_verdict(test_case_id: str, raw_text: str) -> JudgeVerdict:
    cleaned = _strip_markdown_fences(raw_text)
    try:
        data = json.loads(cleaned)
        verdict = str(data["verdict"])
        score = int(data["score"])
        reasoning = str(data.get("reasoning", ""))
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise JudgeParseError(raw_text, exc) from exc

    if verdict not in VALID_VERDICTS:
        raise JudgeParseError(raw_text, ValueError(f"verdict không hợp lệ: {verdict!r}"))
    if not (1 <= score <= 5):
        raise JudgeParseError(raw_text, ValueError(f"score ngoài range 1-5: {score!r}"))

    return JudgeVerdict(
        test_case_id=test_case_id,
        verdict=verdict,
        score=score,
        reasoning=reasoning,
        raw_response=raw_text,
    )


def judge(
    test_case: TestCase,
    model_output: str,
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    client: Anthropic | None = None,
) -> JudgeVerdict:
    """Gọi Claude chấm 1 model output.

    Raise `JudgeCallError` nếu lỗi API sau khi retry hết (network/rate limit/auth) —
    lỗi hệ thống, nên fail rõ để runner.py biết dừng/báo cáo.
    Raise `JudgeParseError` nếu gọi API thành công nhưng JSON trả về không hợp lệ — lỗi dữ
    liệu, runner.py nên bắt riêng và log vào `parse_failure_rate`, không crash toàn run.
    """

    client = client or get_client()
    prompt = _build_judge_prompt(test_case, model_output)

    last_error: Exception | None = None
    raw_text: str | None = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                system=JUDGE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = "".join(block.text for block in response.content if block.type == "text")
            break
        except RateLimitError as exc:
            last_error = exc
        except APIConnectionError as exc:
            last_error = exc
        except APIStatusError as exc:
            if exc.status_code and exc.status_code < 500:
                raise JudgeCallError(f"Anthropic API lỗi không thể retry ({exc.status_code}): {exc}") from exc
            last_error = exc

        time.sleep(BASE_BACKOFF_SECONDS * (2**attempt))

    if raw_text is None:
        raise JudgeCallError(f"Gọi Claude thất bại sau {MAX_RETRIES} lần retry: {last_error}") from last_error

    return _parse_verdict(test_case.id, raw_text)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    tc = TestCase(
        id="selftest-01",
        category="factual",
        prompt="What is the capital of Japan?",
        reference_answer="Tokyo",
        rubric=["Answers 'Tokyo' correctly"],
    )
    verdict = judge(tc, "The capital of Japan is Tokyo.")
    print(verdict)

    # Case cố ý sai để xem judge có chấm fail đúng không.
    verdict_fail = judge(tc, "The capital of Japan is Kyoto.")
    print(verdict_fail)
