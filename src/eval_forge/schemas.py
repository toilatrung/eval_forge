"""schemas.py — Pydantic schema cho test case + loader.

Mục đích: ép format test case ngay từ input, tránh lỗi ngầm khi JSON sai schema
(agent/AGENT.md §4-5). `runner.py` (Phase 3) và các module Phase 2 sẽ import từ đây.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

Category = Literal["factual", "rag", "safety"]
Difficulty = Literal["easy", "medium", "hard"]


class TestCase(BaseModel):
    """Một test case duy nhất trong test set."""

    id: str = Field(..., description="ID duy nhất, dùng để trace kết quả, ví dụ 'factual-01'.")
    category: Category
    difficulty: Difficulty = "medium"
    prompt: str = Field(..., min_length=1, description="Câu hỏi/lệnh gửi cho model cần eval.")
    context: str | None = Field(
        default=None,
        description="Đoạn context được retrieve — chỉ dùng cho category 'rag'.",
    )
    reference_answer: str | None = Field(
        default=None,
        description="Đáp án tham chiếu / hành vi mong đợi, dùng để evaluator và judge so sánh.",
    )
    rubric: list[str] = Field(
        default_factory=list,
        description="Tiêu chí cụ thể để judge chấm (ví dụ: 'phải từ chối', 'không hallucinate').",
    )
    notes: str | None = Field(
        default=None,
        description="Lý do case này được đưa vào test set — đặc biệt quan trọng với case khó.",
    )


class TestCaseLoadError(BaseModel):
    """Kết quả load lỗi của 1 file — không throw, để loader báo cáo đầy đủ 1 lần."""

    file: str
    error: str


class LoadResult(BaseModel):
    cases: list[TestCase]
    errors: list[TestCaseLoadError]


def load_test_cases(directory: str | Path = "test_cases") -> LoadResult:
    """Load + validate toàn bộ *.json trong `directory` qua schema `TestCase`.

    Không throw khi 1 file lỗi — thu thập lỗi vào `LoadResult.errors` để caller tự quyết
    (log, fail cứng, hay bỏ qua file lỗi và chạy tiếp phần còn lại), theo đúng nguyên tắc
    "không crash toàn run vì 1 lỗi nhỏ" áp dụng cho cả llm_judge.py (agent/AGENT.md §5).
    """

    directory = Path(directory)
    cases: list[TestCase] = []
    errors: list[TestCaseLoadError] = []
    seen_ids: set[str] = set()

    for file in sorted(directory.glob("*.json")):
        try:
            raw = json.loads(file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(TestCaseLoadError(file=str(file), error=f"invalid JSON: {exc}"))
            continue

        if not isinstance(raw, list):
            errors.append(
                TestCaseLoadError(file=str(file), error="top-level JSON phải là 1 list các test case")
            )
            continue

        for i, item in enumerate(raw):
            try:
                case = TestCase.model_validate(item)
            except ValidationError as exc:
                errors.append(
                    TestCaseLoadError(file=f"{file}[{i}]", error=str(exc))
                )
                continue

            if case.id in seen_ids:
                errors.append(
                    TestCaseLoadError(file=f"{file}[{i}]", error=f"id trùng lặp: '{case.id}'")
                )
                continue

            seen_ids.add(case.id)
            cases.append(case)

    return LoadResult(cases=cases, errors=errors)


if __name__ == "__main__":
    result = load_test_cases()
    print(f"Loaded {len(result.cases)} test case(s), {len(result.errors)} lỗi.")

    by_category: dict[str, int] = {}
    for c in result.cases:
        by_category[c.category] = by_category.get(c.category, 0) + 1
    for cat, count in sorted(by_category.items()):
        print(f"  - {cat}: {count}")

    if result.errors:
        print("\nLỗi:")
        for err in result.errors:
            print(f"  - {err.file}: {err.error}")
