"""runner.py — nối pipeline: load test case -> llm_client -> evaluator -> llm_judge
-> lưu results/*.json.

Nguyên tắc: 1 test case lỗi (gọi model lỗi, judge lỗi) không được làm dừng cả run — ghi
nhận rõ trạng thái của case đó (`call_error` / `judge_parse_failure`) và tiếp tục chạy các
case còn lại, để `results/*.json` luôn phản ánh đúng toàn bộ test set, không chỉ phần chạy
suôn sẻ.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from evaluator import evaluate
from llm_client import DEFAULT_MODEL, LLMClientError, call_model
from llm_judge import DEFAULT_JUDGE_MODEL, JudgeCallError, JudgeParseError, judge
from schemas import TestCase, load_test_cases

DEFAULT_SLEEP_SECONDS = 1.0  # nghỉ giữa mỗi test case để tránh rate limit khi chạy full set


@dataclass
class CaseResult:
    test_case_id: str
    category: str
    difficulty: str
    status: str  # "ok" | "judge_parse_failure" | "call_error"
    # Ngữ cảnh gốc của case — lưu lại để trang Calibration (Phase 5) hiển thị đủ thông tin
    # cho người chấm, không chỉ output trần trụi.
    prompt: str = ""
    context: str | None = None
    reference_answer: str | None = None
    rubric: list[str] = field(default_factory=list)
    model_output: str | None = None
    rule_signals: dict = field(default_factory=dict)
    empty_output: bool | None = None
    judge_verdict: str | None = None
    judge_score: int | None = None
    judge_reasoning: str | None = None
    error: str | None = None


def _base_fields(tc: TestCase) -> dict:
    """Field chung cho mọi `CaseResult` của 1 test case, tránh lặp ở 4 nhánh return."""

    return {
        "test_case_id": tc.id,
        "category": tc.category,
        "difficulty": tc.difficulty,
        "prompt": tc.prompt,
        "context": tc.context,
        "reference_answer": tc.reference_answer,
        "rubric": tc.rubric,
    }


def run_test_case(tc: TestCase) -> CaseResult:
    """Chạy 1 test case qua toàn bộ chuỗi llm_client -> evaluator -> llm_judge.

    - Lỗi gọi model cần eval (`LLMClientError`) → status `call_error`, không có gì để judge.
    - Gọi model thành công nhưng judge lỗi parse (`JudgeParseError`) → status
      `judge_parse_failure`, vẫn giữ output + rule signal (evaluator không cần judge).
    - Gọi model thành công nhưng judge lỗi hệ thống (`JudgeCallError`) → status `call_error`,
      vẫn giữ output + rule signal.
    """

    base = _base_fields(tc)

    try:
        output = call_model(tc.prompt, context=tc.context)
    except LLMClientError as exc:
        return CaseResult(**base, status="call_error", error=f"llm_client: {exc}")

    ev = evaluate(tc, output)

    try:
        verdict = judge(tc, output)
        return CaseResult(
            **base,
            status="ok",
            model_output=output,
            rule_signals=ev.signals,
            empty_output=ev.empty_output,
            judge_verdict=verdict.verdict,
            judge_score=verdict.score,
            judge_reasoning=verdict.reasoning,
        )
    except JudgeParseError as exc:
        return CaseResult(
            **base,
            status="judge_parse_failure",
            model_output=output,
            rule_signals=ev.signals,
            empty_output=ev.empty_output,
            error=str(exc),
        )
    except JudgeCallError as exc:
        return CaseResult(
            **base,
            status="call_error",
            model_output=output,
            rule_signals=ev.signals,
            empty_output=ev.empty_output,
            error=f"llm_judge: {exc}",
        )


def run(
    *,
    test_cases_dir: str | Path = "test_cases",
    output_dir: str | Path = "results",
    sleep_seconds: float = DEFAULT_SLEEP_SECONDS,
    on_progress: Callable[[int, int, CaseResult], None] | None = None,
) -> dict:
    """Chạy toàn bộ test set.

    `on_progress(done, total, result)` (nếu có) được gọi sau mỗi case — dùng để UI
    (Streamlit, Phase 4) vẽ progress bar mà không phải parse output console. Không truyền gì
    thì chỉ in tiến trình ra console (dùng khi chạy `python3 runner.py` trực tiếp).
    """

    load_result = load_test_cases(test_cases_dir)
    if load_result.errors:
        print(f"CẢNH BÁO: {len(load_result.errors)} file/case load lỗi, bỏ qua:")
        for e in load_result.errors:
            print(f"  - {e.file}: {e.error}")

    total = len(load_result.cases)
    case_results: list[CaseResult] = []
    for i, tc in enumerate(load_result.cases, start=1):
        print(f"[{i}/{total}] {tc.id} ({tc.category})...", flush=True)
        result = run_test_case(tc)
        case_results.append(result)
        print(f"    -> {result.status}" + (f" — {result.error}" if result.error else ""), flush=True)
        if on_progress:
            on_progress(i, total, result)
        if i < total:
            time.sleep(sleep_seconds)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_under_test": DEFAULT_MODEL,
        "judge_model": DEFAULT_JUDGE_MODEL,
        "load_errors": [e.model_dump() for e in load_result.errors],
        "results": [asdict(r) for r in case_results],
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{run_id}.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nSaved {len(case_results)} result(s) to {out_path}")
    return output


if __name__ == "__main__":
    load_dotenv()
    run()
