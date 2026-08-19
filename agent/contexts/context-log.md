# Context Log

Snapshot trạng thái dự án. **Chỉ append 1 entry mới khi 1 phiên làm việc kết thúc ở trạng
thái `done`** (mục tiêu đề ra cho phiên đó hoàn thành trọn vẹn — xem `session-history.md`
để biết chi tiết phiên). Mục đích: phiên sau chỉ cần đọc entry **mới nhất** ở đây để resume
context, không cần đọc lại toàn bộ `session-history.md`.

Format 1 entry:
```
## Snapshot — Session N (YYYY-MM-DD)
- Phase hiện tại:
- Đã có (file/module/kết quả):
- Chưa có / còn thiếu:
- Quyết định cần nhớ: (link tới AGENT.md §... hoặc session-history.md nếu chi tiết)
- Bước tiếp theo:
```

---

## Snapshot — Session 1 (2026-08-19)
- **Phase hiện tại:** Chưa vào Phase 1 (coding). Vừa hoàn thành việc dựng bộ tài liệu điều
  hành agent (không tính là 1 trong 6 phase của dự án, là bước chuẩn bị trước Phase 1).
- **Đã có:**
  - `agent/AGENT.md` — tài liệu tham chiếu chính (mục tiêu, tech stack, cấu trúc module,
    quyết định thiết kế, risk register, DoD, quy trình phiên làm việc).
  - `agent/taskboard.html` — board 6 phase, có checklist task + lưu tiến độ qua localStorage.
  - `agent/contexts/session-history.md`, `agent/contexts/context-log.md` (file này).
- **Chưa có / còn thiếu:**
  - Chưa `git init` project code (repo hiện chỉ có `agent/`).
  - Chưa có bất kỳ file code nào: `llm_client.py`, `evaluator.py`, `llm_judge.py`,
    `runner.py`, `metrics.py`, `report.py`, `app.py`, `pages/*`.
  - Chưa có `.gitignore`, `.env.example`, `requirements.txt`.
  - Chưa có `test_cases/` (15–20 test case, 3 category `factual`/`rag`/`safety`).
  - Chưa có schema Pydantic cho test case.
- **Quyết định cần nhớ:** toàn bộ mục 5 (Quyết định thiết kế quan trọng) và mục 6
  (Risk register) trong `AGENT.md` — chưa có thay đổi nào so với kế hoạch gốc.
- **Bước tiếp theo:** Bắt đầu **Phase 1 — Nền tảng** theo `agent/taskboard.html`: init repo +
  cấu trúc folder → `.gitignore` (trước commit đầu tiên) → `.env.example` → `requirements.txt`
  pin version → schema Pydantic → viết 15–20 test case → verify load qua schema không lỗi.

---

## Snapshot — Session 2 (2026-08-19)
- **Phase hiện tại:** Phase 1 — Nền tảng, đã xong phần "cấu trúc file/folder", còn lại phần
  "nội dung" (schema Pydantic + test case thật).
- **Đã có:**
  - Toàn bộ khung dự án đã commit + push lên `origin/main`
    (`https://github.com/toilatrung/eval_forge`): `.gitignore`, `.env.example`,
    `requirements.txt` (version đã pin), stub `llm_client.py`, `evaluator.py`,
    `llm_judge.py`, `runner.py`, `metrics.py`, `report.py`, `app.py`, `pages/*.py`
    (mỗi file chỉ có docstring + TODO theo phase, chưa có logic thật).
  - `test_cases/`, `results/` — folder rỗng có `.gitkeep`, đã track trong git.
  - `agent/` (AGENT.md, taskboard.html, contexts/session-history.md, contexts/context-log.md)
    — không đổi so với Session 1.
- **Chưa có / còn thiếu:**
  - Chưa có schema Pydantic cho test case.
  - Chưa có test case thật nào trong `test_cases/` (mới chỉ có `.gitkeep`).
  - Toàn bộ logic trong `llm_client.py`, `evaluator.py`, `llm_judge.py`, `runner.py`,
    `metrics.py`, `report.py`, `app.py`, `pages/*.py` đều là TODO — chưa implement.
- **Quyết định cần nhớ:**
  - Không thêm `Co-Authored-By: Claude` vào commit message trong repo này (yêu cầu riêng
    của user, xem `session-history.md` Session 2).
  - Các quyết định thiết kế khác vẫn theo `AGENT.md` §5, không đổi.
- **Bước tiếp theo:** Viết schema Pydantic cho test case + viết 15–20 test case thật (3
  category `factual`/`rag`/`safety`, có case khó) vào `test_cases/`, verify load qua schema
  không lỗi → hoàn tất Phase 1, chuyển sang Phase 2.

---

## Snapshot — Session 4 (2026-08-19)
- **Phase hiện tại:** **Phase 1 hoàn thành**. Chuyển sang **Phase 2 — Core eval engine**.
- **Đã có:**
  - Mọi thứ ở Snapshot Session 2, cộng thêm:
  - `schemas.py` (root) — model `TestCase` (Pydantic v2) + `load_test_cases()` (loader
    không throw khi 1 file lỗi, gom lỗi riêng, check id trùng lặp).
  - `test_cases/factual.json`, `test_cases/rag.json`, `test_cases/safety.json` — 18 test
    case tiếng Anh (6/category), mỗi category có ≥2 case hard/adversarial.
  - `README.md` đã commit (`e9dbb79`, do user tự commit).
  - Git identity đúng: `toilatrung <trung.trinhquang.work2303@gmail.com>`.
  - Verify: `python3 schemas.py` load 18/18 case, 0 lỗi; đã test riêng đường lỗi (file JSON
    hỏng) — loader không crash, báo lỗi riêng.
- **Chưa có / còn thiếu:**
  - `llm_client.py`, `evaluator.py`, `llm_judge.py`, `runner.py`, `metrics.py`, `report.py`,
    `app.py`, `pages/*.py` — vẫn chỉ là stub (TODO), chưa có logic thật.
  - Chưa có `.env` thật với `OPENAI_API_KEY`/`ANTHROPIC_API_KEY` (chỉ có `.env.example`).
  - Các thay đổi ở Session 4 (`schemas.py`, `test_cases/*.json`, xóa `test_cases/.gitkeep`,
    cập nhật `taskboard.html`) **chưa commit/push**.
- **Quyết định cần nhớ:**
  - Test case viết bằng **tiếng Anh** (yêu cầu rõ từ user ở Session 4).
  - `schemas.py` đặt ở root, dùng chung cho Phase 2–3, không đặt trong `test_cases/`.
  - Các quyết định khác: xem `AGENT.md` §5 (không đổi).
- **Bước tiếp theo:** Commit các file mới của Session 4 (nếu user yêu cầu) → bắt đầu Phase 2:
  `llm_client.py` (OpenAI call + retry/backoff), `evaluator.py` (rule-based), `llm_judge.py`
  (Claude judge, ép JSON ổn định + xử lý parse failure). Cần API key thật để test gọi API.
