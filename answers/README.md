# 오답정리 원문 정답·해설 데이터

`answers/<시험ID>.json`은 `FINAL_EXAMS`의 정답표와 기존 장문 해설 페이지를 결합한 파일입니다.

- `answer`, `acceptableAnswers`: `final.html`의 검증된 정답 데이터
- `explanationHtml`, `misconception`: 기존 `sol-final-*.html`의 장문 해설
- `verificationStatus`: `verified_long_form` 또는 `answer_key_and_concept_only`

장문 해설 원본이 없는 문항에는 내용을 만들어 넣지 않습니다. 화면에는 정답·개념과 준비 중 안내만 표시되며, 해당 목록과 개수는 `reports/wrongbook-asset-audit.json`에 기록됩니다.
