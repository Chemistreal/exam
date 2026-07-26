# kmchc/ — 화학 명작 10,000제 문항 은행

인수인계 아카이브(`kmchc_handoff.zip` 분할본)에서 **생산 정본만** 옮겨 온 작업 공간입니다.
저장소의 기존 파일과 **겹치지 않도록 이 디렉터리 안에서만** 작업합니다.

## 무엇이 들어 있나

| 경로 | 내용 |
|---|---|
| `HANDOFF.md` | 프로젝트 전체 인수인계 문서 — **먼저 읽을 것** |
| `master/master_bank.json` | 전 문항 단일 진실 소스 |
| `master/RESUME.md` | 턴 재개용 상태 요약 (매 배치 후 갱신) |
| `master/rejection_log.md` | 배치별 제작 기록·폐기 사유 (가장 중요한 맥락) |
| `master/master_gate.py` | 전수 품질 게이트 (형식+실체+세트) |
| `master/selfaudit.py` | 신규 배치 ↔ 기존 전체 구조 충돌 검사 (R1~R5) |
| `master/expr_assert.py` | 플레이스홀더·미완성 문자열 검출 |
| `master/batch_template.py` | 배치 생산 템플릿 |
| `master/build_t11_p16.py` | **최신 배치 실작업본(P16)** — 다음 배치는 이걸 복사해 쓰면 됨 |
| `master/calibrate.py` | 실측 코호트 앵커로 `esr_cohort_ref` 부여 (배치 병합 후 실행) |
| `master/retro_audit.py` | 은행 전체 소급 자기복제 감사 리포트 생성 |
| `master/briefs/` | 감사 리포트·테마별 착수/마감 문서 + 실측대조·소급감사 리포트 |

아카이브의 `outputs_kmchc/`(139MB 과거 산출물)·`textbook/`(교재 스캔)·`uploads_misc/`는
용량이 커서 옮기지 않았습니다. 교재 페이지가 필요하면 원본 아카이브의 `textbook/t.zip`을 다시 풉니다.

## 상태 확인

```bash
cd kmchc
python3 -c "import json;b=json.load(open('master/master_bank.json'));print(len(b), b[-1]['id'])"
python3 master/master_gate.py | tail -3
cat master/RESUME.md
```

## 다음 배치 만들기

```bash
cd kmchc
cp master/build_t11_p16.py master/build_t12_p1.py
# START_ID / EXPECT_LEN / BATCH_NOTE 를 고치고 build() 안 문항 10개를 교체
python3 master/build_t12_p1.py             # 검증만 — 파일을 건드리지 않음
python3 master/build_t12_p1.py --merge     # 안전 게이트 통과 시 병합 + housekeeping
```

`--merge` 는 저장 직전 안전 게이트(`len` 실측 + ID 충돌 확인)를 통과해야만 진행되고,
병합 후 `selfaudit` → `master_gate` → `rejection_log`·`scenario_index`·`production_plan`
갱신까지 자동으로 수행합니다. `RESUME.md` 만 손으로 갱신하면 됩니다.

> 주의: `merge_and_house(items, note=...)` 의 `note` 는 반드시 명시 전달해야 합니다
> (기본인자가 import 시점에 묶여 템플릿의 자리표시자가 기록됩니다).
