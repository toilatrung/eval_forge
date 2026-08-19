"""metrics.py — tính số liệu tổng hợp từ 1 run trong results/*.json, + human label
(Phase 5 — Calibration) để tính agreement_rate_vs_human thật.

Không truyền `labels` thì `agreement_rate_vs_human` trả về `None` — số liệu này cần human
label thu thập từ trang Calibration. Để `None` thay vì bịa số, đúng nguyên tắc "không quảng
cáo số liệu chưa xác thực" đã chốt ở agent/AGENT.md §5.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def list_runs(results_dir: str | Path = "results") -> list[Path]:
    """Liệt kê file run thật trong `results_dir`, KHÔNG bao gồm file `*.labels.json`
    (nhãn người, đi kèm 1 run — xem `_labels_path`)."""

    return sorted(
        p for p in Path(results_dir).glob("*.json") if not p.name.endswith(".labels.json")
    )


def _labels_path(run_path: str | Path) -> Path:
    run_path = Path(run_path)
    return run_path.with_name(run_path.stem + ".labels.json")


def load_labels(run_path: str | Path) -> dict:
    """Đọc nhãn người đã chấm cho 1 run — trả về `{}` nếu chưa chấm case nào."""

    path = _labels_path(run_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("labels", {})


def save_label(run_path: str | Path, test_case_id: str, human_verdict: str, note: str = "") -> None:
    """Lưu 1 nhãn người ra file **ngay lập tức** (không chỉ giữ trong `st.session_state`) —
    đúng nguyên tắc đã chốt để tránh mất dữ liệu khi Streamlit refresh (agent/AGENT.md §5,
    rủi ro #6)."""

    path = _labels_path(run_path)
    data = {"run_id": Path(run_path).stem, "labels": {}}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("labels", {})

    data["labels"][test_case_id] = {
        "human_verdict": human_verdict,
        "note": note,
        "labeled_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def compute_metrics(run_data: dict, labels: dict | None = None) -> dict:
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

    agreement_rate_vs_human = None
    labeled_count = 0
    if labels:
        matched = 0
        for r in judged_all:
            label = labels.get(r["test_case_id"])
            if label is None:
                continue
            labeled_count += 1
            if label["human_verdict"] == r["judge_verdict"]:
                matched += 1
        agreement_rate_vs_human = (matched / labeled_count) if labeled_count else None

    return {
        "total_cases": total,
        "status_counts": dict(status_counts),
        "parse_failure_rate": (status_counts.get("judge_parse_failure", 0) / total) if total else None,
        "call_error_rate": (status_counts.get("call_error", 0) / total) if total else None,
        "overall_accuracy": (len(passed_all) / len(judged_all)) if judged_all else None,
        "by_category": by_category,
        "agreement_rate_vs_human": agreement_rate_vs_human,
        "labeled_count": labeled_count,
    }


def load_and_compute(run_path: str | Path) -> dict:
    """Load 1 run + nhãn người đi kèm (nếu có) rồi tính metrics — nhờ vậy `agreement_rate_vs_human`
    tự động có số liệu thật ngay khi trang Calibration đã lưu ≥1 nhãn, không cần sửa lại
    app.py/results_explorer.py."""

    data = json.loads(Path(run_path).read_text(encoding="utf-8"))
    labels = load_labels(run_path)
    return compute_metrics(data, labels=labels or None)


def _latest_run(results_dir: str | Path = "results") -> Path:
    run_files = list_runs(results_dir)
    if not run_files:
        raise SystemExit("Không có run nào trong results/. Chạy `python3 runner.py` trước.")
    return run_files[-1]


if __name__ == "__main__":
    import sys

    run_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _latest_run()
    print(json.dumps(load_and_compute(run_path), indent=2, ensure_ascii=False))
