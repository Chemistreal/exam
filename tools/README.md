# 동형문제 재집필 파이프라인

## 왜 다시 만드는가

구 `donghyung` DB(schemaVersion 1)는 **동형문제가 아니었다.** 2400건 전부가
`sourceExamId`/`sourceQuestion` 을 달고 **다른 시험의 기존 문항을 개념 라벨로 매칭해
연결**한 것이었고, 해당 문항에서 파생 생성된 항목은 0건이었다.

- 매칭 수준: `exact_type` 1434(59.8%) / `exact_area` 947(39.5%) / 기타 19
- `concept` 필드는 **원 문항 값을 복사**해 넣은 라벨이라 항상 일치하는 것처럼 보였다.
  실제로는 `jmchc-3` 1번(돌턴의원자론)에 `hwol-2013` 14번(결합 길이)이 붙는 식.
- 원본 1417개를 2400 자리에 재사용(한 문항 최대 10회 중복).
- 도형·선택지 추출에 실패한 167건(7.0%)은 `(…렌더 누락)` 문구와 빈 선택지를
  학생에게 그대로 노출했다.

## 원칙

1. **기출 복제 금지.** 집필 입력에 원문 지문·선택지를 넣지 않는다. 각 문항의
   `개념 / 영역 / 학습 포인트 / 함정`만 전달하고, 그 개념을 묻는 **새로운 상황·수치의
   독자 문항**을 집필한다.
2. **화학적 정확성이 최우선.** 계산형은 집필자가 재계산하고, 별도 검수자가
   독립 검증한다. 틀린 화학은 없느니만 못하다.
3. **글자만으로 완결.** 그림·도표가 필요한 문항은 만들지 않는다.
4. 오답 3개는 원 문항의 함정과 **같은 종류의 오개념**을 유도해야 한다.
5. **고유명사로 지정된 개념은 대상 자체를 유지한다.** 오스왈트 공정·하버법·리비히
   장치처럼 개념 이름이 특정 공정·장치를 가리키면, 그 공정을 다른 공정으로 바꾸지
   말고 수치와 묻는 방식만 새로 설계한다. (jmchc-5 32번이 접촉법으로 바뀌어 재작성함)

## 사용법

```bash
# 1) 집필 입력 생성 (원문 미포함)
python3 tools/dh_manifest.py <examId> [시작번호] [끝번호]

# 2) 집필 → 파트 JSON 저장 (문항번호 → 엔트리 맵)

# 3) 파트 병합 → donghyung/<examId>.json (schemaVersion 2)
python3 tools/dh_merge.py <examId> part1.json part2.json ...

# 4) 구조 검증
python3 tools/dh_validate.py donghyung/<examId>.json

# 5) 회귀 테스트 (신·구 스키마 모두 검사)
python3 tests/wrongbook-assets.py
```

`dh_merge.py` 는 번호 누락·중복을 막고, 기출 참조 필드
(`sourceExamId`·`sourceQuestion`·`matchLevel`·`image` 등)를 병합 단계에서 제거한다.
`dh_validate.py` 는 그 필드가 남아 있으면 실패시킨다.

## 표시 계층

`final.html` 은 두 스키마를 함께 지원한다.

- `origin: "authored"` → **동형문제 · 같은 개념으로 새로 만든 문제**
- 구 DB 항목 → **같은 개념 유형 문제** + 출처(시험명·문항 번호) 표기
- `dhUsable()` 가드가 빈 선택지·플레이스홀더 항목을 화면·Word 양쪽에서 숨긴다.

## 검수 원칙

집필은 병렬 에이전트가 맡고, **화학적 정확성은 전량 직접 검산**한다.
문항마다 다음을 확인한다.

1. 정답이 실제로 맞는가 (계산형은 재계산)
2. 오답 3개가 확실히 틀리는가 (복수 정답 불가)
3. 지문이 조건 부족으로 모호하지 않은가
4. 해설의 수치·논리가 정답과 일치하는가

`tools/dh_review.py <examId> [시작] [끝] [--full]` 로 검수용 압축 출력을 얻는다.

## 진행 상황

전체 41개 시험 2400문항. 재집필 완료분은 `strategy: original-authored`.

| 시험 | 상태 |
|---|---|
| jmchc-3 | 완료 (60문항, 36문항 직접 검산) |
| jmchc-1 | 완료 (60문항, 60문항 전량 직접 검산 · 오류 0) |
| jmchc-2 | 완료 (60문항, 60문항 전량 직접 검산 · 오류 0) |
| jmchc-4 | 완료 (60문항, 60문항 전량 직접 검산 · 오류 0) |
| jmchc-5 | 완료 (60문항, 60문항 전량 직접 검산 · 32번은 개념 이탈로 직접 재작성) |
| jmchc-6 | 완료 (60문항, 60문항 전량 직접 검산 · 오류 0) |
| jmchc-7 | 완료 (60문항, 60문항 전량 직접 검산 · 오류 0) |
| jmchc-8 | 완료 (60문항, 60문항 전량 직접 검산 · 오류 0) |
| jmchc-9 | 완료 (60문항, 60문항 전량 직접 검산 · 오류 0) |
| 나머지 32개 | 순차 재집필 진행 중 |

남은 시험 목록은 다음으로 확인한다.

```bash
python3 - <<'PY'
import json,glob
exams=json.loads(open('final.html',encoding='utf-8').read()
    .split("const FINAL_EXAMS=",1)[1].split(";\n",1)[0])
done={json.load(open(f,encoding='utf-8')).get('examId')
      for f in glob.glob('donghyung/*.json')
      if json.load(open(f,encoding='utf-8')).get('strategy')=='original-authored'}
print([e['id'] for e in exams if e['id'] not in done])
PY
```
