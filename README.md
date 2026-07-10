# CHEMISTREAL 최종 산출물 패키지 (2026-07-07)

이번 및 직전 세션의 완료 산출물을 업로드/보관용으로 한데 모은 것. 실제 반영 순서와 검증은
DEPLOY_CHECKLIST.md 를 따르면 된다.

## 폴더 구조
- deploy/ : 사이트에 반영하는 파일(라이브)
  - final.html          FINAL_EXAMS 페이지. 2021 Q60(공식 삭제 문항) 제외 패치 반영본. 라이브 final.html 을 이걸로 교체.
  - index.html          exam-app 리포트 페이지. 성장 10단계(2~10) 최종본(리포트 18섹션: 신규 7 + 보강 2). 라이브 index.html 을 이걸로 교체.
  - DEPLOY_NOTES_growth.md   성장 패키지 반영 순서/주의.
- tools/ : 로컬에서 돌리는 스크립트(배포 아님)
  - regrade_kch1to3b_q11.py   kch1to3-b Q11(정답 4->1) 과거 시트 기록 소급 재채점. 시트 export 입력, dry-run 후 패치본 생성.
  - unit_unify.py             DT 단원 표기 통일 7건(진술/정답 불변, u 만). appdata 대상, --apply 시 .bak 백업.
  - unit_unify_changes.csv    통일 대상 7건 변경표.
- docs/ : 참고 문서/감사 리포트(반영 대상 아님)
  - FINAL_Q60_PATCH_NOTES.md, KCH1TO3B_Q11_REGRADE_NOTES.md, DT_ASSET_STATUS.md
  - dt/ : DT 전면 감사 결과(INVENTORY, CONSISTENCY, ANSWER_REVIEW, REMEDIATION, README + 근거 CSV/JSON)

## 우선순위 요약(자세한 건 DEPLOY_CHECKLIST.md)
1) 필수 배포: deploy/final.html, deploy/index.html
2) 선택 실행: tools/regrade_kch1to3b_q11.py(과거 기록 재채점), tools/unit_unify.py(단원 통일, 채점 무영향)
3) 참고: docs/ (DT 는 구조/정합성/정답 모두 클린 확인, 코드 수정 불필요)

## 무결성 확인(이 패키지 생성 시점)
- final.html: 전체 miss 40개 빈 값 + 2021 시험만 [60], 2021 key 길이 60 / key[59]=1 보존. 정상.
- index.html: 876,551 bytes(성장 최종본).
- tools 스크립트: em-dash 0, CJK-Han 0, 문법 OK, unit_unify.py 는 테스트 appdata 에서 7건 정확 적용 검증.

## 이 패키지에서 뺀 것
- 성장 중간 단계 zip(stage2~9): stage10 최종본으로 대체됨(중복).
- 검증용 스크린샷 PNG: 반영 대상이 아니라 제외. 필요하면 별도 제공 가능.
