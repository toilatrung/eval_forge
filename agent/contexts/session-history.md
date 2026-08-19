# Session History

Lịch sử toàn bộ phiên làm việc + quyết định đưa ra trong từng phiên. **Append mỗi phiên**,
kể cả phiên chưa xong (`in-progress` / `blocked`) — khác với `context-log.md` (chỉ ghi khi
phiên `done`).

Format 1 entry:
```
## Session N — YYYY-MM-DD
- Mục tiêu phiên:
- Việc đã làm:
- Quyết định đưa ra: (nếu có — kèm lý do)
- Trạng thái: done | in-progress | blocked
- Việc còn lại / next:
```

---

## Session 1 — 2026-08-19
- **Mục tiêu phiên:** Chuẩn bị "bộ nhớ" điều hành cho agent (AGENT.md, session-history,
  context-log, taskboard) trước khi bắt đầu code, vì dự án sẽ code theo từng giai đoạn qua
  nhiều phiên khác nhau.
- **Việc đã làm:**
  - Nhận kế hoạch triển khai đầy đủ từ user (tech stack, timeline 6 giai đoạn, risk register,
    Definition of Done) cho dự án "LLM Evaluation Harness + Internal Platform".
  - Viết `agent/AGENT.md` — tài liệu tham chiếu chính: mục tiêu, tech stack, cấu trúc module,
    quyết định thiết kế quan trọng, risk register, DoD, quy trình phiên làm việc.
  - Viết `agent/taskboard.html` — board trực quan chia 6 phase, mỗi phase có checklist task
    cụ thể, tick được và lưu tiến độ qua `localStorage`.
  - Viết khung `agent/contexts/session-history.md` (file này) và
    `agent/contexts/context-log.md`.
- **Quyết định đưa ra:**
  - Phân định rõ 2 file trong `contexts/`: `session-history.md` = log mọi phiên (kể cả chưa
    xong) + quyết định phát sinh trong phiên; `context-log.md` = snapshot trạng thái dự án,
    **chỉ ghi khi phiên kết thúc ở trạng thái `done`**, dùng để phiên sau resume nhanh.
  - Giữ nguyên toàn bộ tech stack / phase breakdown / risk register do user đề ra ban đầu,
    không đổi — chỉ tổ chức lại thành tài liệu điều hành.
- **Trạng thái:** done (mục tiêu phiên là dựng xong bộ tài liệu điều hành — đã xong).
- **Việc còn lại / next:** Bắt đầu **Phase 1 — Nền tảng**: init repo, `.gitignore`,
  `.env.example`, `requirements.txt`, schema Pydantic cho test case, viết 15–20 test case
  (3 category: `factual`, `rag`, `safety`). Xem chi tiết task ở `../taskboard.html` Phase 1.

## Session 2 — 2026-08-19
- **Mục tiêu phiên:** Dựng xong khung cấu trúc dự án (folder + file stub theo đúng mục 3 của
  `AGENT.md`) và push lên remote GitHub đã cấu hình sẵn (`origin` →
  `https://github.com/toilatrung/eval_forge`).
- **Việc đã làm:**
  - Tạo `.gitignore` (loại `.env`, `__pycache__/`, `.venv/`, `results/*.json`, ...),
    `.env.example` (2 biến `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`), `requirements.txt`
    (pin version cụ thể).
  - Tạo stub cho toàn bộ file code cốt lõi: `llm_client.py`, `evaluator.py`,
    `llm_judge.py`, `runner.py`, `metrics.py`, `report.py`, `app.py`,
    `pages/{run_evaluation,results_explorer,compare_runs,calibration}.py` — mỗi file chỉ có
    docstring mô tả mục đích + TODO gắn với phase tương ứng, **chưa viết logic thật**
    (logic thật là việc của Phase 2–5, không làm ở phiên này để tránh nhảy cóc phase).
  - Tạo `test_cases/` và `results/` — folder rỗng, thêm `.gitkeep` để git track được.
  - `git add` toàn bộ, commit, push lên `origin/main`.
- **Quyết định đưa ra:**
  - Theo yêu cầu user: **không** thêm trailer `Co-Authored-By: Claude` vào commit message
    (khác với quy ước mặc định của harness) — đây là lựa chọn của user về repo của họ.
  - Các file `.py` chỉ là stub (docstring + TODO theo phase), không viết logic — giữ đúng
    nguyên tắc "code theo từng giai đoạn, không nhảy cóc" đã chốt ở `AGENT.md` §5.
- **Trạng thái:** done
- **Việc còn lại / next:** Bắt đầu code thật cho **Phase 1** phần còn lại: schema Pydantic
  cho test case + viết 15–20 test case (3 category `factual`/`rag`/`safety`, có case khó)
  vào `test_cases/`. Xem `agent/taskboard.html` Phase 1.
