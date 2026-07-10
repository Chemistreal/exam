# 배포/실행 체크리스트 (2026-07-07 세션)

이번 세션 산출물 중 "실제로 반영해야 끝나는" 항목만 정리. 감사 리포트는 참고용이라 배포 대상이 아니다.

## A. 지금 배포하면 되는 것

### A1. final.html (2021 Q60 제외 패치) [필수]
- 파일: backlog/final.html
- 무엇: FINAL_EXAMS 채점에서 2021 Q60(공식 삭제 문항)을 제외. JSON 의 "miss":[] -> "miss":[60] 한 줄.
- 반영: 라이브 final.html 을 이 파일로 교체 후 배포.
- 검증(브라우저): 2021 시험 열기 -> 총 문항 60 -> 59 로, Q60 오답 시 감점 0, 대상 award 반영, Q60 칸에 '제외' 표시.
- 근거: FINAL_Q60_PATCH_NOTES.md.

### A2. 성장 10단계(2~10) 최종 패키지 [필수, 직전 세션분]
- 파일: stage10/chemistreal_deploy_20260707_stage2-10_FINAL.zip
- 무엇: exam-app index.html 의 최종 리포트 18개 섹션(신규 7 + 보강 2) 완성본.
- 반영: zip 내 index.html 을 라이브에 반영(DEPLOY_NOTES.md 순서대로).
- 검증: stage10 스크린샷(proof/compete/depth desktop + mobile 390) 과 대조.

## B. 파일에 돌리는 작업(배포 아님)

### B1. kch1to3-b Q11 과거 기록 재채점 [선택]
- 파일: backlog/regrade_kch1to3b_q11.py
- 무엇: Q11 정답 4->1 정정은 이미 라이브. 과거 시트 기록만 소급 재채점.
- 실행: 시트 export(csv/tsv/xlsx) 를 스크립트에 입력. dry-run 으로 영향 행 확인 후 패치본 생성.
- 주의: 백분위/석차 재산정은 별도(스크립트가 플래그로 표시). 근거: KCH1TO3B_Q11_REGRADE_NOTES.md.

### B2. DT 단원 표기 통일 7건 [선택, 채점 무영향]
- 파일: backlog/dt/unit_unify.py
- 무엇: 같은 과목 내 단원 드리프트 7문항의 u 만 표준으로 통일(진술/정답 불변).
- 실행: `python3 unit_unify.py --appdata ./appdata` (미리보기) -> `--apply` (백업 .bak 생성).
- 동점 3건은 표준 권고값. 다른 단원 원하면 PLAN 의 to 만 수정. 적용 후 바뀐 round_*.json 재배포.
- 검증됨: 테스트 appdata 에서 7건 정확 적용, u 만 변경, 멱등 안전. 근거: DT_REMEDIATION.md.

## C. 반영할 것 없음(참고 자료)
- DT 감사 리포트(dt/DT_INVENTORY/CONSISTENCY/ANSWER_REVIEW) 및 DT_ASSET_STATUS: 결과 문서.
  DT 는 구조/정합성/정답 모두 클린으로 확인됐고 코드 수정 불필요.
- 고아 동형 4건: 무해한 대기 자산. 유지 권장(삭제/편입 불필요).

## 순서 제안
1) A1 final.html 배포 + 브라우저 검증
2) A2 성장 패키지 배포 + 스크린샷 대조
3) (원하면) B1 과거 기록 재채점
4) (원하면) B2 단원 통일 후 round 파일 재배포
