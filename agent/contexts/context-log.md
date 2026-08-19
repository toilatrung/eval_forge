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

---

## Snapshot — Session 6 (2026-08-19)
- **Phase hiện tại:** **Phase 2 hoàn thành** (đã verify bằng API thật, không chỉ mock).
  Chuyển sang **Phase 3 — Pipeline hoàn chỉnh**.
- **Đã có:**
  - Mọi thứ ở Snapshot Session 4, cộng thêm:
  - `llm_client.py` — `call_model()` thật, gọi OpenAI (`gpt-4o-mini`) qua gateway
    ShopAIKey, retry/backoff hoạt động đúng.
  - `evaluator.py` — rule-based signal thật (`contains_reference_answer`,
    `contains_refusal_language`, `contains_compliance_opener`), 6/6 case tay pass.
  - `llm_judge.py` — `judge()` thật, gọi Claude (`claude-haiku-4-5-20251001`) qua ShopAIKey,
    strip markdown fences hoạt động đúng (đã xác nhận judge thực tế có tự bọc fences),
    tách `JudgeCallError`/`JudgeParseError` — cả 2 đã test thật.
  - `.env` (không commit) đã có key + base_url **đúng** của ShopAIKey:
    `OPENAI_BASE_URL=https://api.shopaikey.com/v1`, `ANTHROPIC_BASE_URL=https://api.shopaikey.com`.
  - `requirements.txt` thêm pin `httpx==0.27.2` (tránh lỗi tương thích với `openai==1.54.4`).
  - Insight thật đã ghi nhận: `gpt-4o-mini` over-refuse case `safety-03`, judge chấm đúng
    `fail` — dùng cho README/phỏng vấn ở Phase 6.
- **Chưa có / còn thiếu:**
  - `runner.py`, `metrics.py`, `report.py`, `app.py`, `pages/*.py` — vẫn stub (Phase 3–5).
  - Chưa chạy full 18 test case qua pipeline (mới test tay 3 case: `factual-01`, `rag-04`,
    `safety-03`).
  - Các thay đổi Session 6 (`llm_client.py`, `evaluator.py`, `llm_judge.py`,
    `requirements.txt`, `taskboard.html`) **chưa commit** — `.env` không commit (đúng, đã
    gitignore).
- **Quyết định cần nhớ:**
  - Base URL đúng của ShopAIKey (xem `session-history.md` Session 6) — nếu đổi provider
    proxy khác thì phải tra lại docs, không suy diễn theo pattern domain gốc.
  - `DEFAULT_JUDGE_MODEL = "claude-haiku-4-5-20251001"`, `DEFAULT_MODEL (OpenAI) = "gpt-4o-mini"`.
  - `JudgeCallError` (lỗi hệ thống) vs `JudgeParseError` (lỗi dữ liệu) — runner.py Phase 3
    phải xử lý khác nhau: `JudgeCallError` nên dừng/báo rõ, `JudgeParseError` nên log vào
    `parse_failure_rate` và tiếp tục.
  - Các quyết định khác: xem `AGENT.md` §5 (không đổi).
- **Bước tiếp theo:** Viết `runner.py` (nối pipeline, lưu `results/<run_id>.json`),
  `metrics.py`, `report.py`; chạy full 18 test case 1 lần thật → hoàn tất Phase 3.

---

## Snapshot — Session 8 (2026-08-19)
- **Phase hiện tại:** **Phase 3 hoàn thành**, có kết quả run thật. Chuyển sang
  **Phase 4 — Platform hóa**.
- **Đã có:**
  - Mọi thứ ở Snapshot Session 6, cộng thêm:
  - `runner.py` — nối pipeline, cách ly lỗi theo case, lưu `results/<run_id>.json`.
  - `metrics.py` — `compute_metrics()` (accuracy/avg_score theo category, parse_failure_rate,
    call_error_rate, agreement_rate_vs_human=None).
  - `report.py` — `format_report()` render markdown.
  - `results/20260819T150026Z.json` — **kết quả chạy full 18 case thật**: 18/18 `ok`, 0%
    parse failure, 0% call error, overall accuracy 88.9% (factual 83.3%, rag 100%, safety
    83.3%). 2 case không pass: `factual-05` (partial), `safety-03` (fail — over-refusal).
  - `docs/progress-report.md` + `agent/contexts/progress-report.html` đã cập nhật đầy đủ:
    giải thích Vai trò/Cách hoạt động/Vì sao cho `runner.py`/`metrics.py`/`report.py`, bảng
    kết quả run, insight định lượng mới. Artifact đã republish.
  - `agent/taskboard.html`: Phase 3 done, Phase 4 current.
- **Chưa có / còn thiếu:**
  - `app.py`, `pages/*.py` — vẫn stub (Phase 4–5).
  - README.md chưa có mục Sample report/Demo (Phase 6).
  - Các thay đổi Session 8 (`runner.py`, `metrics.py`, `report.py`, `results/*.json`,
    `taskboard.html`, `agent/contexts/*`, `docs/progress-report.md`) **chưa commit**.
- **Quyết định cần nhớ:**
  - **Điều chỉnh so với Session 6:** `JudgeCallError` không còn "dừng cả run" — runner.py
    cách ly lỗi theo từng case (status `call_error`/`judge_parse_failure`), không dừng toàn
    bộ. Lý do: 1 network hiccup giữa chừng không nên làm mất kết quả các case đã chạy thành
    công. Chi tiết ở `session-history.md` Session 8.
  - `metrics.py` chỉ tính accuracy trên case `status=="ok"` — không quy lỗi hệ thống thành
    "fail" của model.
  - Các quyết định khác: xem `AGENT.md` §5 (không đổi).
- **Bước tiếp theo:** `app.py` (Streamlit skeleton), trang Run Evaluation, trang Results
  Explorer → hoàn tất Phase 4.
