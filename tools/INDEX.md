# tools 차례

`python3 tools/gen_tool_index.py --write` 가 자마다의 설명 첫 줄을 모아 적는다.
손으로 고치지 않는다.

- ✓ CI 에 걸려 있다 (`.github/workflows/tests.yml`)
- `--check` 를 받는 자는 어긋나면 종료 코드 1 을 낸다

## 재는 자 (63)

| | 자 | `--check` | 무엇을 |
|---|---|---|---|
| ✓ | `answer_sync.py` | ○ | 채점하는 정답과 **해설이 말하는 정답**이 같은지 본다. |
| ✓ | `area_tag.py` | ○ | 회차의 **영역 이름**이 성적표가 아는 이름인지 본다. |
| ✓ | `audit_pages.py` | ○ | 화면을 한 줄씩 재는 자. |
| ✓ | `blind_wait.py` | ○ | 검사가 "이쯤이면 됐겠지" 하고 재우는 시간을 잰다. |
|  | `build_wrongbook_assets.py` |  | Build and audit wrong-answer review assets for final.html. |
| ✓ | `ci_deps.py` | ○ | CI 가 부르는 자가 **거기서 실제로 돌 수 있는지** 본다. |
| ✓ | `cohort_cover.py` | ○ | **모든 시험에 기준 기록(연도누적 인원)이 들어 있는지** 본다. |
| ✓ | `concept_table.py` | ○ | 125 개념표가 **화면 스물넷에 따로** 적혀 있다 — 다 같은 말을 하는지 본다. |
| ✓ | `const_sync.py` | ○ | 한 회차 안에서 **문제지와 해설이 같은 상수**를 쓰는지 본다. |
| ✓ | `crop_align.py` | ○ | 문항 크롭이 **그 문항 자리에서** 잘렸는지 본다. |
|  | `crops_measure.py` |  | 문항 크롭 이미지를 다른 형식으로 바꾸면 얼마나 줄어드는지 실제로 재 본다. |
| ✓ | `cut_fit.py` | ○ | 시상 컷이 회차의 실제 난이도와 얼마나 맞는지 잰다. |
| ✓ | `cut_link.py` | ○ | 늦춘 기준이 **시험지**를 보고 늦춘 것인지, 그 회차 **사람들**을 보고 늦춘 것인지. |
|  | `dh_concept_scan.py` |  | 원 DB의 `concept` 라벨에서 오타 후보를 찾는다. |
| ✓ | `dh_dupe_scan.py` |  | 서로 같은 문항이 된 쌍을 찾는다. 한 시험 안에서도, 시험끼리도 본다. |
| ✓ | `dh_lint.py` |  | 동형문제 상시 검사. 사람이 볼 수 없는 규모(2400문항)를 기계가 매번 훑는다. |
|  | `dh_manifest.py` |  | 동형문제 재집필용 입력 매니페스트 생성. |
|  | `dh_merge.py` |  | 집필된 파트 JSON들을 합쳐 donghyung/<examId>.json 을 만든다. |
|  | `dh_normalize.py` |  | 재집필본의 ASCII 화학 표기를 유니코드로 바꾼다(원칙 9). |
| ✓ | `dh_number.py` | ○ | 기출동형 문항의 **셈이 고른 답과 맞는지** 본다. |
|  | `dh_rebalance.py` |  | 한 번호에 몰린 정답을 고르게 흩는다. |
|  | `dh_review.py` |  | 집필된 파트 JSON을 검수용 압축 형식으로 출력. |
| ✓ | `dh_validate.py` |  | 집필된 동형문제(schemaVersion 2, strategy=original-authored) 구조 검증. |
| ✓ | `dupe_pages.py` | ○ | 같은 화면이 두 이름으로 있는 것을 찾고, **한쪽만 고치는 것**을 막는다. |
| ✓ | `editor_note.py` | ○ | 선생님께 남긴 메모가 학생 화면으로 새어 나가지 않는지 본다. |
| ✓ | `font_block.py` | ○ | 바깥 글꼴이 **첫 화면을 인질로 잡는 것**을 푼다. |
| ✓ | `haeseol_index.py` | ○ | 해설 목차(`index_haeseol.html`)가 실제 회차와 맞는지 본다. |
| ✓ | `hub_audit.py` | ○ | 허브(`hub.html`)의 **0회차 표**를 다시 잰다 — 브라우저 없이. |
|  | `hwp_text.py` |  | HWP 5.0(바이너리) 문제지에서 글자를 뽑는다 — **수식까지 제자리에**. |
| ✓ | `input_labels.py` | ○ | 입력칸에 **이름**이 있는지 보고, placeholder 로 지을 수 있으면 지어 넣는다. |
| ✓ | `js_syntax.py` | ○ | 화면 안에 박아 넣은 자바스크립트가 **문법이 맞는지** 본다. |
| ✓ | `label_typo.py` |  | 개념·영역·유형 이름의 오타 후보를 뽑는다 (사람이 판단한다). |
| ✓ | `lec_audit.py` | ○ | 강의 125장을 전수로 훑는다 — **처음 보는 학생이 알아들을 수 있는가.** |
| ✓ | `lec_back.py` | ○ | 강의를 보고 나면 **왔던 자리로** 돌아가야 한다. |
| ✓ | `lec_content.py` | ○ | 강의 125장의 **내용**을 기계가 잴 수 있는 데까지 잰다. |
| ✓ | `lec_readtime.py` | ○ | 강의마다 **읽는 데 얼마나 걸리는지** 적는다. |
| ✓ | `lec_selfcheck.py` | ○ | 숙제에 **스스로 확인할 기준**이 붙어 있는지 본다. |
| ✓ | `lie_check.py` | ○ | **자가 거짓말을 하는지** 잰다 — 참·거짓 예시를 주고 맞히는지 본다. |
| ✓ | `mis_sync.py` | ○ | **오개념 카탈로그와 강의의 함정이 같은 말을 하는지** 본다. |
| ✓ | `msg_ledger.py` | ○ | 화면이 **사람에게 하는 말**을 한 대장에 모은다. |
| ✓ | `name_key.py` | ○ | 네 앱이 **학생 이름을 같은 방식으로 다듬는지** 본다. |
| ✓ | `noindex.py` | ○ | **한 학생의 성적이 뜨는 화면**은 검색에 잡히지 않게 한다. |
| ✓ | `om_cover.py` | ○ | 오답 카드의 **한 줄**이 비어 나가지 않는지 센다. |
| ✓ | `orphan_scan.py` |  | 아무도 읽지 않는 자산을 찾는다. |
| ✓ | `page_doors.py` | ○ | **문이 없는 화면**을 찾는다 — 아무 데서도 이름이 불리지 않는 장. |
| ✓ | `page_exams.py` | ○ | 분석 화면들이 저마다 품고 있는 회차 목록이 `exams.json` 과 맞는지 본다. |
| ✓ | `page_honesty.py` | ○ | R&D 화면이 **자기 상태를 말하는지** 본다. |
| ✓ | `pages_budget.py` | ○ | GitHub Pages 한도에 얼마나 가까운지 잰다. |
| ✓ | `pdf_answer_leak.py` | ○ | 문제지 PDF 에 **답이 실려 있는지** 본다. |
| ✓ | `print_styles.py` | ○ | 인쇄해서 쓰는 화면에 **인쇄 규칙**이 있는지 보고, 없으면 넣는다. |
| ✓ | `rate_check.py` | ○ | 문제지에 적혀 있던 **공식 정답률**이 성한지 본다 — `exams.json` 의 `rate`. |
|  | `regen_seed_cohort.py` |  | 동형 2종(kch1to3-b, kch1to2-b) 시드 코호트 영역벡터 재생성. |
|  | `regrade_kch1to3b_q11.py` |  | kch1to3-b Q11 재채점 스크립트 (2026-07-07) |
|  | `review_queue.py` |  | 사람이 검수할 것을 **급한 순서로** 줄 세운다. |
| ✓ | `sci_notation.py` | ○ | 학생이 읽는 글의 **과학 표기**가 한 벌인지 잰다 — 그리고 함부로 안 고친다. |
| ✓ | `seed_stats.py` | ○ | index.html 의 두 코호트가 서로 어긋나지 않는지 본다 — SEEDS 와 STATIC_STATS. |
| ✓ | `start_index.py` | ○ | `START_HERE_index.html` 이 실제 파일과 맞는지 본다. |
| ✓ | `store_ledger.py` | ○ | 이 브라우저에 **무엇을 남기는지** 적어 두고, 늘어나면 한 번 묻게 한다. |
| ✓ | `term_drift.py` | ○ | **본문**이 같은 말을 두 가지로 적고 있지 않은지 잰다. |
| ✓ | `theme.py` | ○ | 화면 261장에 **같은 옷**을 입힌다. |
| ✓ | `type_norm.py` | ○ | 같은 말을 두 가지로 적고 있지 않은지 본다. |
|  | `unit_unify.py` |  | DT 단원 표기 통일 패치 (같은 과목 내 드리프트 7건) |
| ✓ | `void_check.py` | ○ | 출제 뒤 **폐기된 문항**이 제대로 처리돼 있는지 본다 — `exams.json` 의 `voided`. |

## 만드는 자 (14)

| | 자 | `--check` | 무엇을 |
|---|---|---|---|
|  | `gen_cohort_baseline.py` |  | 성적표 엑셀(.xlsm)에서 **익명 통계**만 뽑아 `cohort/baseline.json` 을 만든다. |
| ✓ | `gen_cut_adj.py` | ○ | 어려웠던 회차의 시상 기준을 조금 늦춰 준다 → `exams.json` 의 `cutAdj` |
| ✓ | `gen_exam_fallback.py` |  | `exams.json` 을 `final.html`·`final-submit.html` 안에 예비본으로 심는다. |
| ✓ | `gen_exam_solflag.py` |  | `exams.json` 의 `solFull` 을 `answers/<id>.json` 에서 만든다. |
| ✓ | `gen_exam_titles.py` |  | `AppsScript-Code.gs` 의 EXAM_TITLES 를 `exams.json` + 옛 시험 목록에서 만든다. |
| ✓ | `gen_expl_html.py` | ○ | `explanation`(글) 에서 `explanationHtml`(해설지에 실릴 꼴) 을 만든다. |
| ✓ | `gen_gas_cohort.py` |  | `AppsScript-Code.gs` 의 EXAM_COHORT 를 `exams.json` + `cohort/baseline.json` 에서 만든다. |
| ✓ | `gen_gas_msgexams.py` |  | `AppsScript-Code.gs` 의 MSG_EXAMS 를 `exams.json` 의 영역 데이터로 만든다. |
| ✓ | `gen_omlib.py` | ○ | 오개념 라이브러리(OMLIB)를 **한 벌로** 맞춘다 — final.html 이 원본이다. |
| ✓ | `gen_pool_index.py` | ○ | 2400문항을 개념으로 찾을 수 있게 색인을 만든다 → `donghyung/index.json` |
| ✓ | `gen_qmatrix_tags.py` | ○ | `qmatrix-editor.html` 이 품고 있는 **유형 태그 표**를 exams.json 에서 다시 뽑는다. |
| ✓ | `gen_sol_page.py` | ○ | `sol-final-<id>.html` 해설지를 `answers/<id>.json` 에서 만든다. |
| ✓ | `gen_sw_version.py` | ○ | 서비스워커 캐시 이름을 **껍데기 파일의 내용**에서 짓는다. |
| ✓ | `gen_tool_index.py` | ○ | 자 예순 개의 **차례**를 만든다 — `tools/INDEX.md`. |

---

자 77개 · CI 에 걸린 것 63개 · `--check` 를 받는 것 53개
