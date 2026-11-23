#!/bin/sh
#  T18 배치를 옮겨 적는 차례 — 초안(JSON)이 서면 이 줄들을 그대로 쓴다.
#    apply_fixes 로 검토 결과를 붙인 뒤 render_batch 로 빌더를 만들고, lenplan 으로 길이를 재고,
#    모듈을 그대로 돌리면 저작 점검 → verify → 병합까지 한 번에 간다.
#  ★EXPECT_LEN 은 앞 배치가 병합된 뒤의 은행 크기★ — P1 2954 · P2 2964 · … · P5 2994.
S=/tmp/claude-0/-home-user-exam/5f2ecfac-9847-5091-89ed-a121f3b6410f/scratchpad
T=build_t16e_fin.py            # 꼬리(_ANON·local_checks)를 가져올 자리

python3 apply_fixes.py $S/t18p1_draft.json $S/t18p1_fix.json $S/t18p1.json
python3 render_batch.py $S/t18p1.json build_t18_p1.py M02955 2954 $T \
  "T18 P1 (M02955~M02964) — 전자점식에서 전자쌍 세기까지" \
  "T18 P1 — 점을 찍는 표기에서 전자쌍을 세는 셈으로 넘어간다." '분자의 구조' 18
python3 lenplan.py build_t18_p1 && python3 build_t18_p1.py && python3 link_t18_p1_concepts.py

python3 apply_fixes.py $S/t18p2_draft.json $S/t18p2_fix.json $S/t18p2.json
python3 render_batch.py $S/t18p2.json build_t18_p2.py M02965 2964 $T \
  "T18 P2 (M02965~M02974) — 결합각과 전자쌍 반발" \
  "T18 P2 — 전자쌍이 서로 밀치는 세기로 결합각을 가른다." '분자의 구조' 18
python3 lenplan.py build_t18_p2 && python3 build_t18_p2.py && python3 link_t18_p2_concepts.py

python3 apply_fixes.py $S/t18p3_draft.json $S/t18p3_fix.json $S/t18p3.json
python3 render_batch.py $S/t18p3.json build_t18_p3.py M02975 2974 $T \
  "T18 P3 (M02975~M02984) — 배열과 분자 모양을 갈라 부르기" \
  "T18 P3 — 전자쌍으로 센 배열과 원자만 보고 부르는 모양은 다른 것이다." '분자의 구조' 18
python3 lenplan.py build_t18_p3 && python3 build_t18_p3.py && python3 link_t18_p3_concepts.py

python3 apply_fixes.py $S/t18p4_draft.json $S/t18p4_fix.json $S/t18p4.json
python3 render_batch.py $S/t18p4.json build_t18_p4.py M02985 2984 $T \
  "T18 P4 (M02985~M02994) — 결합각을 견주는 차례" \
  "T18 P4 — 비공유 전자쌍이 늘수록 결합각이 좁아진다." '분자의 구조' 18
python3 lenplan.py build_t18_p4 && python3 build_t18_p4.py && python3 link_t18_p4_concepts.py

python3 apply_fixes.py $S/t18p5_draft.json $S/t18p5_fix.json $S/t18p5.json
python3 render_batch.py $S/t18p5.json build_t18_p5.py M02995 2994 $T \
  "T18 P5 (M02995~M03004) — 모양까지만 적고 멈추기" \
  "T18 P5 — 극성은 다음 테마다. 이 배치는 모양에서 멈춘다." '분자의 구조' 18
python3 lenplan.py build_t18_p5 && python3 build_t18_p5.py && python3 link_t18_p5_concepts.py

cd .. && python3 master/master_gate.py | tail -3
