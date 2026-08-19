"""metrics.py — tính số liệu tổng hợp từ 1 run trong results/*.json.

`agreement_rate_vs_human` luôn trả về `None` ở Phase 3 — số liệu này cần human label thu
thập từ trang Calibration (Phase 5). Để `None` thay vì bịa số, đúng nguyên tắc "không quảng
cáo số liệu chưa xác thực" đã chốt ở agent/AGENT.md §5.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def compute_metrics(run_data: dict) -> dict:
    results = run_data["results"]
    total = len(results)

    status_counts: dict[str, int] = defaultdict(int)
    for r in results:
        status_counts[r["status"]] += 1

    by_category: dict[str, dict] = {}
    for category in sorted({r["category"] for r in results}):
        cat_results = [r for r in results if r["category"] == category]
        judged = [r for r in cat_results if r["status"] == "ok"]
        passed = [r for r in judged if r["judge_verdict"] == "pass"]
        by_category[category] = {
            "total": len(cat_results),
            "judged": len(judged),
            "passed": len(passed),
            "accuracy": (len(passed) / len(judged)) if judged else None,
            "avg_score": (sum(r["judge_score"] for r in judged) / len(judged)) if judged else None,
        }

    judged_all = [r for r in results if r["status"] == "ok"]
    passed_all = [r for r in judged_all if r["judge_verdict"] == "pass"]

    return {
        "total_cases": total,
        "status_counts": dict(status_counts),
        "parse_failure_rate": (status_counts.get("judge_parse_failure", 0) / total) if total else None,
        "call_error_rate": (status_counts.get("call_error", 0) / total) if total else None,
        "overall_accuracy": (len(passed_all) / len(judged_all)) if judged_all else None,
        "by_category": by_category,
        "agreement_rate_vs_human": None,
    }


def load_and_compute(run_path: str | Path) -> dict:
    data = json.loads(Path(run_path).read_text(encoding="utf-8"))
    return compute_metrics(data)


def _latest_run(results_dir: str | Path = "results") -> Path:
    run_files = sorted(Path(results_dir).glob("*.json"))
    if not run_files:
        raise SystemExit("Không có run nào trong results/. Chạy `python3 runner.py` trước.")
    return run_files[-1]


if __name__ == "__main__":
    import sys

    run_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _latest_run()
    print(json.dumps(load_and_compute(run_path), indent=2, ensure_ascii=False))
