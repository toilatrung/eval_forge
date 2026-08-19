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

## Session 3 — 2026-08-19
- **Mục tiêu phiên:** Sửa lại git identity cho đúng owner repo, và tạo `README.md`.
- **Việc đã làm:**
  - Push từ sandbox này thất bại do không có credential GitHub (không có username/token,
    không có SSH key) — user xác nhận sẽ tự push từ máy thật.
  - Sửa `git config user.name`/`user.email` từ giá trị đoán ban đầu sai (`son.pham@...`)
    thành đúng identity của owner repo: `toilatrung <trung.trinhquang.work2303@gmail.com>`,
    amend lại commit đầu (`--reset-author`) để author đúng trước khi push.
  - Tạo `README.md`: problem statement, kiến trúc (mermaid diagram), tech stack, cấu trúc
    dự án, hướng dẫn cài đặt (mô tả cách chạy dự kiến, ghi rõ code hiện mới là stub), roadmap
    6 phase. **Không** bịa sample report hay link demo — để trống dạng checklist vì chưa có
    thật (đúng phase 3/6, tránh đưa thông tin chưa xác thực).
- **Quyết định đưa ra:**
  - Git identity chuẩn cho repo này: `toilatrung <trung.trinhquang.work2303@gmail.com>` —
    dùng cho mọi commit sau này trong repo, không dùng email `son.pham@...` nữa.
- **Trạng thái:** done (tạo README xong; **chưa commit/push** — user chỉ yêu cầu tạo file,
  chưa yêu cầu commit).
- **Việc còn lại / next:** Hỏi/chờ user xác nhận commit + push README (và commit amend
  identity fix) lên `origin/main`. Sau đó tiếp tục Phase 1: schema Pydantic + 15–20 test case.

## Session 4 — 2026-08-19
- **Mục tiêu phiên:** Hoàn thiện nốt Phase 1 — schema Pydantic + viết test case + verify.
- **Việc đã làm:**
  - Ghi nhận: user đã tự commit README (`git commit -m "docs: add README with project
    overview, teckstack, and roadmap"`, commit `e9dbb79`) từ trước phiên này.
  - Tạo `schemas.py`: model `TestCase` (Pydantic v2 — id, category, difficulty, prompt,
    context, reference_answer, rubric, notes) + `load_test_cases()` — loader không throw
    khi 1 file lỗi, gom lỗi vào `LoadResult.errors` (cùng nguyên tắc với `llm_judge.py`
    Phase 2: không crash toàn run vì 1 lỗi nhỏ), kèm check id trùng lặp.
  - Viết 18 test case bằng **tiếng Anh** (theo yêu cầu user, đổi từ dự thảo tiếng Việt ban
    đầu): `test_cases/factual.json` (6), `test_cases/rag.json` (6), `test_cases/safety.json`
    (6) — mỗi category có 2 case `hard`/adversarial (time-sensitive fact, binary trick,
    unanswerable-from-context, conflicting context, jailbreak roleplay, innocuous-framing
    harmful request) + 1 case over-refusal test (`safety-03`, `safety-04`).
  - Xóa `test_cases/.gitkeep` (không cần nữa vì đã có file thật).
  - Verify: `python3 schemas.py` → load 18/18 case, 0 lỗi. Test riêng đường lỗi bằng file
    JSON hỏng chèn tạm ở `/tmp` → loader vẫn load đúng 18 case hợp lệ + báo 1 lỗi riêng,
    không crash.
  - Cập nhật `agent/taskboard.html`: bỏ cờ `current` ở Phase 1 (đã done), gắn `current` cho
    Phase 2.
- **Quyết định đưa ra:**
  - Test case viết bằng tiếng Anh (không phải tiếng Việt như bản thảo đầu) — yêu cầu rõ từ
    user.
  - Schema đặt ở file `schemas.py` tại root (không phải trong `test_cases/`) vì sẽ được
    `evaluator.py`, `llm_judge.py`, `runner.py` (Phase 2–3) dùng chung.
- **Trạng thái:** done — **Phase 1 hoàn thành toàn bộ task cốt lõi**.
- **Việc còn lại / next:** Bắt đầu **Phase 2 — Core eval engine**: `llm_client.py` (gọi
  OpenAI, retry/backoff), `evaluator.py` (rule-based), `llm_judge.py` (Claude judge, ép
  JSON output ổn định — phần dễ tốn thời gian nhất). Cần `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`
  thật trong `.env` để test gọi API thật (hiện chưa có).

## Session 5 — 2026-08-19
- **Mục tiêu phiên:** Cho phép đổi base URL của model qua `.env` (phục vụ proxy/gateway
  nội bộ/API tương thích, ví dụ khi không gọi trực tiếp OpenAI/Anthropic endpoint chính chủ).
- **Việc đã làm:**
  - Thêm `OPENAI_BASE_URL` và `ANTHROPIC_BASE_URL` vào `.env.example` (để trống = dùng
    endpoint mặc định của SDK).
  - Ghi TODO vào `llm_client.py` và `llm_judge.py`: khi implement thật (Phase 2), đọc 2 biến
    này và chỉ truyền `base_url` cho SDK client khi có giá trị — chưa code logic thật vì
    Phase 2 chưa bắt đầu.
- **Quyết định đưa ra:** base_url là optional, mặc định rỗng → dùng endpoint chính chủ của
  SDK; không bắt buộc set.
- **Trạng thái:** done
- **Việc còn lại / next:** Không đổi — vẫn là bắt đầu Phase 2 (xem next của Session 4).
