#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
retro_audit.py — 은행 전체 소급 자기복제 감사 리포트 생성기

selfaudit 의 prior 가 (id < lo) 였던 동안에는 ①배치 내부 10제끼리 ②이미 등재된 구간을
소급으로 — 이 두 가지를 대조할 수 없었다. prior 를 '자기 자신 제외 전체'로 고친 뒤
처음으로 전 구간을 대조한 결과를 사람이 판정할 수 있는 형태로 정리한다.

R1/R2 는 대칭이라 한 쌍이 두 번 보고된다 → 쌍으로 접어서 실제 건수를 낸다.
R3/R5 는 도구 설계상 '△ 후보'이지 확정 결함이 아니다(hostile-reviewer 기본값).

사용: python3 master/retro_audit.py > master/briefs/소급감사_리포트.md
"""
import sys, os, json
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from selfaudit import audit, skeleton, ans_val

bank = {x['id']: x for x in json.load(
    open(os.path.join(HERE, 'master_bank.json'), encoding='utf-8'))}
flags, n = audit('M00001', 'M99999')

# 규칙별 수집 — R1/R2 는 무순 쌍으로 접는다
pairs = defaultdict(set)      # rule -> {frozenset({a,b})}
for fid, sk, hits in flags:
    for rule, ids in hits:
        code = rule.split()[0]
        if code == 'R4':
            continue
        for other in ids:
            pairs[code].add(frozenset((fid, other)))

theme_of = lambda i: bank[i]['textbook_theme']

print("# 소급 자기복제 감사 리포트 — selfaudit 사각지대 해소 후 첫 전수 대조\n")
print("`selfaudit.py` 의 대조 대상이 `id < lo`(이전 문항만)에서 "
      "**자기 자신을 뺀 은행 전체**로 바뀌면서 처음으로 가능해진 감사입니다.\n")
print("> R1/R2 는 대칭이라 원 출력에서 한 쌍이 두 번 세어집니다. 아래는 쌍으로 접은 실제 건수입니다.\n"
      "> R3/R5 는 도구 설계상 **△ 후보**(기계적 신호)이지 확정 결함이 아닙니다 — "
      "판정에는 근거가 필요합니다.\n")

print("## 요약\n")
print(f"- 대조 문항 **{n}제** (은행 전체)")
print("- 쌍으로 접은 충돌 건수\n")
print("| 규칙 | 뜻 | 실제 쌍 |")
print("|---|---|---|")
MEAN = {'R1': '동일 scenario 키', 'R2': '동일 skill 이름',
        'R3': '동일 계산 골격 + 동일 linked + **동일 정답값**',
        'R5': '동일 골격 + 두 정답값의 합이 10·100 (보완값 짝)'}
for code in ('R1', 'R2', 'R3', 'R5'):
    print(f"| {code} | {MEAN[code]} | {len(pairs[code])} |")

allids = set()
for s in pairs.values():
    for p in s:
        allids |= set(p)
tc = Counter(theme_of(i) for i in allids)
print(f"\n- 관련 문항 **{len(allids)}제**, 테마 분포: "
      + " · ".join(f"T{k} {v}" for k, v in sorted(tc.items())))
print("- 편중 테마는 **T5 몰·T6 PV=nRT·T9 양적관계** — 계산 비중이 높아 "
      "골격·정답값이 겹칠 여지가 큰 구간입니다.")
print("\n**전부 이미 봉인된 테마(T1~T10)입니다.** 봉인 구간을 소급 수정할지는 "
      "Eric 판단 사항이라, 이 리포트는 판정 자료까지만 제공합니다.\n")

for code in ('R1', 'R2', 'R3', 'R5'):
    ps = sorted(tuple(sorted(p)) for p in pairs[code])
    if not ps:
        continue
    print(f"\n## {code} — {MEAN[code]} ({len(ps)}쌍)\n")
    print("| 테마 | 문항 A | 문항 B | 대조 키 |")
    print("|---|---|---|---|")
    for a, bb in ps:
        A, B = bank[a], bank[bb]
        if code == 'R1':
            key = f"scenario `{A['scenario']}`"
        elif code == 'R2':
            key = f"skill `{A['skill']}`"
        else:
            key = f"골격 `{skeleton(A)}` · 정답값 {ans_val(A)} / {ans_val(B)}"
        print(f"| T{A['textbook_theme']} | {a} {A['skill'][:22]} | "
              f"{bb} {B['skill'][:22]} | {key} |")

print("\n## 권고 처리 순서\n")
print("1. **R1·R2 우선** — scenario·skill 은 중복 검색의 색인 키라 값이 겹치면 "
   "이후 쌍대조가 그 문항을 놓칩니다. 문항 내용이 정당해도 **키만은 세분화**해 두는 편이 좋습니다.")
print("2. **R5(보완값)** — 판례②가 명시적으로 금지하는 유형이라 실물 확인 우선순위가 높습니다.")
print("3. **R3** — 물질·맥락이 다르면 정당한 경우가 많습니다(판례④의 '정답 지식 상반' 예외). "
   "다만 같은 정답값이 반복되면 학생에게는 같은 문제로 보이므로 표본 점검을 권합니다.")
print("\n앞으로 신규 배치는 강화된 selfaudit 를 그대로 통과하므로 이 부채는 늘지 않습니다.")
