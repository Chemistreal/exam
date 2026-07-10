# DT(데일리테스트) 자산 상태 - 재확인 결과 (2026-07-07)

## 결론: 상태 변경됨. 자산이 이제 라이브로 접근 가능합니다.
감사 시점(2026-07-04)에는 "chemistreal.github.io/DT 404 · 자산 부재 · Eric 제공 필요"였으나,
오늘 재확인 결과 DT 앱과 회차 데이터가 모두 게시되어 직접 페치됩니다.

## 확인된 사실 (오늘 라이브 점검)
- 앱: https://chemistreal.github.io/DT/  -> HTTP 200 (단일 HTML 약 288KB, title "Chemistreal · 채점과 진단")
  - 토큰 게이팅 존재(dt_admgate, STUDENT/ADMIN), OX 누적 진단 앱.
  - 데이터 로드: `DATA_BASE='./appdata/'` + `fetch(DATA_BASE+file, {cache:'no-store'})`.
- 회차 데이터: https://chemistreal.github.io/DT/appdata/round_ch{1,2}_NN.json  -> HTTP 200 (표본 다수 200 확인)
  - 본문 참조 회차 파일 36종 확인(ch1 · ch2 계열). (메모리상 46회차와 차이가 있어, 전수 목록은 앱 최신본 기준 재집계 필요.)
  - 1회차 구조 예: {course, round, title, scoring{per,max,wrong,blank,pass}, jeongsi{n:60, items:[{n,u,mis,a:"O"/"X",s,f,w,...}]}, retakeC}
    -> 각 문항이 정답(a=O/X)·오개념(mis)·해설(s/f/w)까지 담은 정제 자산.

## 무엇이 남았나 (감사 관점)
- 감사에서 'DT 46회 키 대조'가 유일하게 자산 부재로 보류였음. 이제 자산이 있으니 대조가 가능합니다.
- 다만 이 작업(회차별 OX 정답을 공식/원자료와 전수 대조)은 이번 세션의 대상(exam app = index.html/final.html)과
  별개의 큰 작업이며, DT는 명시적으로 이번 범위 밖이었습니다. 따라서 상태만 정확히 갱신하고, 실행은 별도 지시를 권장합니다.

## 다음 단계 옵션 (원하시면 진행)
1. DT 회차 전수 인벤토리: appdata의 실제 회차 파일 목록·문항수·중복/결번을 라이브에서 수집해 정리.
2. DT 내부 정합성 감사: 각 회차 JSON의 정답(a)·통과선(pass)·배점(per*max) 일관성, 오개념(mis) 커버리지, retake 로직 검증.
3. DT 정답 외부 대조: 공식/원자료가 있으면 회차별 O/X 키를 전수 대조(단원평가 3중 대조와 동일 방법론).
4. exam app과의 연계는 하지 않음(별개 앱 · 별개 배포). 필요 시에만.

## 메모
- 이번에 만든 exam app 성장 리포트(2~10단계)와 final.html Q60 패치는 DT와 무관하게 독립적입니다.
- DT 착수를 원하시면 "DT 1번(인벤토리)부터" 같은 형태로 지시해 주세요.
