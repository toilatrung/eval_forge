"""report.py — xuất báo cáo tổng hợp (markdown) từ metrics.py."""

from __future__ import annotations

import sys
from pathlib import Path

from metrics import _latest_run, load_and_compute


def _pct(x: float | None) -> str:
    return f"{x * 100:.1f}%" if x is not None else "n/a"


def _fmt(x: float | None) -> str:
    return f"{x:.2f}" if x is not None else "n/a"


def format_report(run_path: Path, metrics: dict) -> str:
    lines = [
        f"# Eval report — {run_path.name}",
        "",
        f"- Tổng số test case: {metrics['total_cases']}",
        f"- Trạng thái: {metrics['status_counts']}",
        f"- Parse failure rate (judge trả JSON không hợp lệ): {_pct(metrics['parse_failure_rate'])}",
        f"- Call error rate (lỗi gọi API sau retry): {_pct(metrics['call_error_rate'])}",
        f"- Overall accuracy (theo judge, chỉ tính case chấm được): {_pct(metrics['overall_accuracy'])}",
        "",
        "## Theo category",
        "",
        "| Category | Total | Judged | Passed | Accuracy | Avg score |",
        "|---|---|---|---|---|---|",
    ]
    for cat, m in metrics["by_category"].items():
        lines.append(
            f"| {cat} | {m['total']} | {m['judged']} | {m['passed']} | "
            f"{_pct(m['accuracy'])} | {_fmt(m['avg_score'])} |"
        )
    lines.append("")
    lines.append(
        "> Agreement rate (judge vs human label): n/a — cần dữ liệu từ trang Calibration (Phase 5)."
    )
    return "\n".join(lines)


if __name__ == "__main__":
    run_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _latest_run()
    print(format_report(run_path, load_and_compute(run_path)))
