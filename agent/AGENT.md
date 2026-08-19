# AGENT.md — LLM Evaluation Harness + Internal Platform

Đây là tài liệu tham chiếu chính cho agent (và người) khi làm việc trên dự án này.
Đọc file này **trước mỗi phiên làm việc**, cùng với 2 file trong `contexts/`:

- `contexts/session-history.md` — lịch sử toàn bộ phiên làm việc + quyết định đã đưa ra
  trong từng phiên (append mỗi phiên, kể cả phiên chưa xong).
- `contexts/context-log.md` — snapshot trạng thái dự án, **chỉ ghi khi 1 phiên kết thúc ở
  trạng thái "done"** (mục tiêu phiên đó hoàn thành trọn vẹn). Dùng để phiên sau resume
  context nhanh, không cần đọc lại toàn bộ session-history.
- `taskboard.html` — board trực quan theo phase/task, tick trực tiếp khi làm xong.

Quy tắc: không suy diễn lại các quyết định đã chốt ở mục 5 dưới đây — nếu có lý do muốn đổi,
ghi rõ lý do vào `session-history.md` trước khi đổi.

---

## 1. Mục tiêu
Xây một LLM evaluation harness + platform nội bộ (demo dạng dashboard) để:
- Chạy test case qua 1 model cần eval (OpenAI `gpt-4o-mini`)
- Judge kết quả bằng model khác họ (Anthropic Claude) để giảm self-preference bias
- Có UI (Streamlit) để chạy eval, xem kết quả, so sánh run, và calibrate judge với human label
- Deploy demo public (Streamlit Community Cloud) + dùng làm dẫn chứng trong CV

## 2. Tech stack đã chốt

| Layer | Công nghệ |
|---|---|
| Core logic | Python 3.11+ |
| LLM API (model test) | OpenAI API — `gpt-4o-mini` |
| LLM API (judge) | Anthropic API — Claude |
| Data validation | Pydantic (schema test case) |
| UI/Platform | Streamlit (multi-page) |
| Lưu kết quả | JSON file (`results/*.json`) — SQLite chỉ nếu cần nâng cấp sau |
| Phân tích | Pandas |
| Version control | Git + GitHub |
| Deploy demo | Streamlit Community Cloud |
| Secrets | `.env` + `python-dotenv` local; `st.secrets` khi deploy |
| Test code Python | `pytest` (optional, cho `evaluator.py`) |

`requirements.txt` pin version cụ thể (không dùng `>=` mở).

## 3. Cấu trúc module dự kiến
```
llm_client.py     # gọi OpenAI API cho model cần eval
evaluator.py      # rule-based evaluator, chạy độc lập, test được bằng tay
llm_judge.py      # gọi Claude làm judge, ép JSON output ổn định (phần khó nhất)
runner.py         # nối pipeline: load test case -> gọi model -> evaluate -> judge -> lưu results/*.json
metrics.py        # tính số liệu tổng hợp (accuracy, agreement rate, parse failure rate...)
report.py         # xuất báo cáo từ metrics
app.py            # Streamlit entrypoint (multi-page)
  pages/
    run_evaluation.py     # Trang chạy eval từ UI
    results_explorer.py   # Trang xem kết quả
    compare_runs.py        # Trang so sánh pairwise A/B (2 model)
    calibration.py          # Trang so sánh agreement rate judge vs human label
test_cases/         # 15-20 test case, chia 3 category
results/            # output run, không commit (trừ 1-2 mẫu demo)
agent/              # tài liệu điều hành agent (file này + contexts/ + taskboard.html)
```

## 4. Test case
- Tối thiểu 15–20 case, chia 3 category: `factual`, `rag`, `safety`
- Phải có case "khó" (ambiguous, adversarial), không chỉ case dễ — nếu không metrics vô nghĩa
- Schema Pydantic ép format ngay từ input, chặn lỗi ngầm khi JSON sai

## 5. Quyết định thiết kế quan trọng (không suy diễn lại)
- **Judge khác họ với model test** (Claude judge OpenAI) để giảm self-preference bias — nhưng
  không quảng cáo là "giải quyết hoàn toàn", chỉ "giảm thiểu", kèm agreement rate thực tế minh chứng.
- **Judge output phải robust**: ép `response_format` nếu API hỗ trợ, strip markdown fences,
  try/except, log riêng metric `parse_failure_rate` — không throw lỗi làm crash toàn run.
- **Human labels lưu ra file JSON ngay sau mỗi lần chấm** ở trang Calibration — không chỉ giữ
  trong `session_state` (Streamlit refresh sẽ mất).
- **80% effort vào evaluator/judge/metrics, không phải UI** — UI chỉ cần "đủ dùng". Tránh scope
  creep sang làm UI đẹp.
- API key: `.env` trong `.gitignore` **từ commit đầu tiên**. Kiểm tra lại bằng `git log -p`
  hoặc `gitleaks` trước khi push.
- Rate limit / cost control: `max_tokens` thấp khi debug, retry với exponential backoff,
  `time.sleep()` nhỏ giữa các call khi chạy full set.
- **Code theo từng giai đoạn (phase), không nhảy cóc** — xem `taskboard.html`. Một phase chỉ
  coi là xong khi các task cốt lõi (không đánh dấu "optional") đều hoàn thành.

## 6. Rủi ro chính cần nhớ khi code
| # | Rủi ro | Cách giảm thiểu | Theo dõi ở phase |
|---|---|---|---|
| 1 | Judge trả JSON sai format | strip fences + try/except + log `parse_failure` riêng | 2 |
| 2 | Tốn tiền API ngoài dự tính | model rẻ, `max_tokens` thấp khi debug | 2–3 |
| 3 | Rate limit API | retry + exponential backoff, `sleep()` nhỏ | 2–3 |
| 4 | API key leak lên GitHub | `.gitignore` từ đầu, check `git log -p`/`gitleaks` | 1, 6 |
| 5 | Self-preference bias vẫn còn dù đổi model | không quảng cáo quá mức, nêu agreement rate thật | 5 |
| 6 | Streamlit `session_state` mất dữ liệu | lưu file JSON ngay sau mỗi hành động | 5 |
| 7 | Test case quá ít/không đa dạng | tối thiểu 15–20, có case khó | 1 |
| 8 | Deploy thiếu secrets | dùng `st.secrets`, test deploy sớm | 6 |
| 9 | Scope creep sang UI đẹp | giữ tỷ lệ effort 80/20 | Toàn bộ |
| 10 | Không có thời gian viết README | chốt cứng 1 khoảng thời gian riêng cuối | 6 |

## 7. Definition of Done (tổng thể dự án)
- [ ] Ít nhất 15 test case, chia 3 category rõ ràng
- [ ] Rule-based evaluator chạy không lỗi trên toàn bộ test set
- [ ] LLM judge có xử lý lỗi parse, có log riêng tỷ lệ fail
- [ ] Có ít nhất 1 lần so sánh pairwise (2 model) qua UI
- [ ] Có số liệu calibration thực tế (không phải số giả định)
- [ ] README có: problem statement, architecture diagram, sample report, link demo
- [ ] Deploy thành công, link demo chạy được không cần setup local
- [ ] `.env`/API key không có trong git history

## 8. Quy trình phiên làm việc (bắt buộc)
1. **Đầu phiên:** đọc `AGENT.md` (file này) → đọc entry mới nhất trong
   `contexts/context-log.md` (nếu có) để biết trạng thái resume → lướt
   `contexts/session-history.md` nếu cần thêm chi tiết quyết định gần đây → xem
   `taskboard.html` để biết phase/task hiện tại.
2. **Trong phiên:** mỗi quyết định mới (đổi thiết kế, chọn giải pháp giữa nhiều phương án,
   phát hiện rủi ro mới...) → append ngay vào `contexts/session-history.md`.
3. **Cuối phiên:**
   - Cập nhật checkbox trong `taskboard.html` cho task đã xong.
   - Append 1 entry vào `contexts/session-history.md` tổng kết phiên (làm gì, quyết định gì,
     trạng thái: `done` / `in-progress` / `blocked`).
   - **Chỉ khi** trạng thái phiên là `done` (mục tiêu đề ra cho phiên đó hoàn thành trọn vẹn):
     append thêm 1 snapshot vào `contexts/context-log.md` mô tả trạng thái dự án tại thời điểm
     đó (phase nào, file nào đã có, còn thiếu gì) để phiên sau đọc nhanh mà không cần lục lại
     toàn bộ lịch sử.
