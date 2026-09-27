"""감사39 조치 ① — ★은행의 해설은 평문이다★ · T14 96제에 새 들어간 ★ 를 걷고 게이트를 건다

■ ★★감사39 가 은행 전체 규약이 깨진 자리를 잡았다★★
  검사 B(★ 유출)가 T14 2차 84제에서 ★83건★ 을 냈다. 오탐인지 재어 보니 오탐이 아니었다 —
    · T1~T13 의 2,134제: `solution` 에 ★ 가 든 문항 ★0건★
    · T14 의 164제:      `solution` 에 ★ 가 든 문항 ★96건★
    · 다른 필드(stem·answer_proof·calc_check·objective·skill·scenario·device)는 ★T14 도 전부 0★
  구간을 세니 ★P7(M02195)에서 시작해 P10(M02225) 이후로는 전량★ 이다. 강조 표기를 해설에
  쓰기 시작한 회차가 그때고, 그 뒤로 한 번도 되돌아보지 않았다.

■ ★★왜 도구가 못 잡았나 — 검사의 사정거리가 곧 사각이다★★
  저작 점검 ⑨(평문)는 ★발문과 선지만★ 본다("발문·선지에 강조 표기 — 은행은 평문"). 그 검사가
  선 자리에서 ★해설은 사정거리 밖★ 이었다. T14 P13 2차에 같은 갈래를 겪고 주석에 적어 두었는데
  (★사정거리를 좁게 세운 검사는 그 좁음이 곧 사각★), ★그 교훈을 다른 필드로 옮기지 않았다.★
  ▸ ★★새로 얻는다 — 한 필드에 건 규약은 같은 규약이 걸려야 할 다른 필드를 함께 적는다.★★
    '은행은 평문' 이라는 규약의 대상은 ★학생이 읽는 모든 문면★ 이다. 발문·선지에만 걸어 두면
    해설이 새고, 해설에서 새면 열여섯 배치가 지나서야 감사가 잡는다.

■ 무엇을 되돌리나
  ㉠ T14 의 `solution` 에서 ★ 문자만 걷는다. ★낱말은 하나도 바꾸지 않는다★ — 강조를 없애는 것이
     목적이고 문장을 고치는 것이 아니다. 판정·근거·반박이 그대로 남는다.
  ㉡ 되돌린 뒤 자를 다시 댄다 — ★해설 300자 하한★ · ★오답 문면이 해설에 그대로 있는가★ ·
     ★★ 가 사라진 뒤 조사가 앞말에서 떨어지지 않았는가★(★ 를 걷으면 '★탄소의 몫★이고' 가
     '탄소의 몫이고' 로 붙으므로 이 갈래는 오히려 좋아진다. 반대로 '★ 이고' 처럼 별표 뒤에
     띄어 쓴 자리가 있었으면 걷은 뒤 ' 이고' 가 남는데, 그런 자리는 조치 스크립트가 매번
     불변 검사로 막아 왔으므로 없어야 한다 — 세어서 확인한다).
  ㉢ ★verify() 에 은행 공통 게이트를 신설한다★ — 학생이 읽는 네 필드(stem·choices·solution·
     answer_proof)에 ★ 가 있으면 배치가 통과하지 못한다. ★테마 지역 검사가 아니라 은행 공통
     자리에 건다★ — T15 는 자기 local_checks 를 새로 쓸 터이므로 지역에 걸면 또 새 나간다.
  ▸ `calc_check` 는 ★걸지 않는다★ — 그 필드는 출제자가 읽는 계산 줄이고 T1~T13 도 ★ 가 0 이나
    학생에게 나가는 문면이 아니다. ★게이트는 학생이 읽는 자리에만 건다.★

■ 되돌리지 않는 것
  · `verified.watch`(층5 기록)의 ★ — ★그대로 둔다.★ 출제자·검증자가 읽는 내부 주석이고
    T1~T13 도 ★ 를 쓴다. 학생 문면이 아니다.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(BASE, 'master_bank.json')
TPL = os.path.join(BASE, 'batch_template.py')

bank = json.load(open(BANK, encoding='utf-8'))
t14 = [x for x in bank if x['theme'] == '원자반지름']
assert len(t14) == 164, f'T14 {len(t14)}제'

JOSA_RE = ('를|을|은|의|으로|로|에서|에|과|보다|처럼|까지|부터|이고|이다|이야|이라|이지')

# ── ㉠ solution 에서 ★ 만 걷는다 ────────────────────────────────────────────
#   ★★그런데 별표가 조사 앞 빈칸을 가리고 있던 자리가 둘 있었다★★ — '전자가 하나뿐★ 이지' ·
#   '읽는 일★ 이야'. 별표를 그냥 걷으면 '하나뿐 이지' 가 되어 ★조사가 앞말에서 떨어진다.★
#   조치 스크립트마다 걸어 온 검사 ⑱(조사 앞 빈칸)은 ★'★ 조사' 꼴만★ 보았고 은행에 이미
#   들어간 '낱말★ 조사' 는 사정거리 밖이었다 — ★여기서도 검사의 좁음이 사각이었다.★
#   ▸ 그래서 ★닫는 별표 뒤에 띄어 쓴 조사는 별표와 빈칸을 함께 걷어 붙인다.★ 여는 별표는
#     뒤에 빈칸이 없으므로(★낱말) 이 갈래에 걸리지 않는다 — 빈칸을 필수로 요구해 가른다.
hit = [x for x in t14 if '★' in x['solution']]
print(f'T14 해설에 ★ 가 든 문항 {len(hit)}제')
bad = []
joined = 0
for x in hit:
    before = x['solution']
    after, n = re.subn(rf'★ (?=(?:{JOSA_RE})(?:[\s,.·)?!]|$))', '', before)
    joined += n
    after = after.replace('★', '')
    # ★낱말이 바뀌지 않았는지 센다★ — 걷힌 것이 별표와 (붙인 자리의) 빈칸뿐이어야 한다
    if len(before) - len(after) != before.count('★') + n:
        bad.append(f"{x['id']} 별표·빈칸 말고 다른 것이 걷혔다")
    if before.replace('★', '').replace(' ', '') != after.replace(' ', ''):
        bad.append(f"{x['id']} 낱말이 바뀌었다")
    x['solution'] = after
print(f'  ▸ 닫는 별표 뒤에 떨어져 있던 조사 {joined}자리를 붙였다')

# ── ㉡ ★★별표를 걷다가 은행에 이미 들어가 있던 조사 앞 빈칸이 드러났다★★ ─────────────
#   ★검사 ⑱(조사 앞 빈칸)을 T14 164제 전체에 처음 걸어 보고서야 보였다★ — 그 검사는 조치
#   스크립트가 ★고치는 배치의 빌드 파일만★ 보았고, 이미 병합된 은행은 아무도 다시 세지 않았다.
#   ▸ ★★그래서 은행 전체로 재었다 — 7건이 울고 그 가운데 넷이 오탐이었다★★:
#       · M01241 의 '보면 은' — ★'은' 이 조사가 아니라 원소 은(銀)★
#       · M01838 의 '을' 셋   — ★'을' 이 조사가 아니라 갑·을·병 라벨★
#     ★검사의 사정거리를 넓히면 오탐이 따라온다 — 넓히기 전에 오탐부터 센다★(이 은행이 여러 번
#     얻은 규약이고, 여기서도 그대로였다). 그래서 ★오탐을 이름으로 적어 두고 검사는 좁히지
#     않는다★ — 좁히면 진짜 '…을' 이 새 나간다.
#   ▸ 진짜는 셋이다. 둘은 T14(M02157·M02171), ★하나는 T12(M01822)★ 로 감사39 범위 밖이지만
#     한 글자 붙이는 일이라 함께 고친다(판정을 바꾸지 않는다). ★범위 밖이라고 아는 흠을 두지
#     않는다 — 다음 감사가 T12 를 다시 열 계획이 없다.★
JOSA = ('를|을|은|의|으로|로|에서|에|과|보다|처럼|까지|부터|이고|이다|이야|이라|이지')
JOIN = [('M01822', '파셴 이지', '파셴이지'),
        ('M02157', '하나뿐 이지', '하나뿐이지'),
        ('M02171', '읽는 일 이야', '읽는 일이야')]
OTAM = {('M01241', '보면 은'), ('M01838', '그러니 을'), ('M01838', '보면 을'),
        ('M01838', '이라 을')}
byid = {x['id']: x for x in bank}
for mid, old, new in JOIN:
    it = byid[mid]
    if it['solution'].count(old) != 1:
        bad.append(f'{mid} 조사 앞 빈칸 앵커가 {it["solution"].count(old)}곳')
        continue
    it['solution'] = it['solution'].replace(old, new)
print(f'  ▸ 은행에 이미 있던 조사 앞 빈칸 {len(JOIN)}곳을 붙였다 (오탐 {len(OTAM)}곳은 이름으로 남김)')

for x in t14:
    s = x['solution']
    if len(s) < 300:
        bad.append(f"{x['id']} 해설 {len(s)}자 — 300자 하한")
    for i, c in enumerate(x['choices']):
        if i != x['answer'] and c not in s:
            bad.append(f"{x['id']} {i + 1}번 오답 문면이 해설에 없다")

# ★은행 전체★ 로 다시 센다 — 오탐 넷만 남아야 한다
still = []
for x in bank:
    for m in re.finditer(rf'(?<=[가-힣]) ({JOSA})(?=[\s,.·)?!]|$)',
                         x['solution'].replace('★', '')):
        frag = x['solution'].replace('★', '')[max(0, m.start() - 6):m.end()].strip()
        if not any(x['id'] == oid and frag.endswith(otxt) for oid, otxt in OTAM):
            still.append(f"{x['id']} 조사 앞 빈칸 — {frag!r}")
if still:
    bad.extend(still)

if bad:
    print('  ❌ 되돌린 뒤 자에 걸렸다 — 은행을 쓰지 않았다')
    for b in bad[:20]:
        print('     ·', b)
    raise SystemExit(1)

left = sum('★' in x['solution'] for x in bank)
assert left == 0, f'아직 {left}제 남았다'
json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'  ✅ 해설 {len(hit)}제에서 ★ 를 걷었다 · 은행 전체 {len(bank)}제에 남은 것 0')

# ── ㉢ verify() 에 은행 공통 게이트를 신설한다 ──────────────────────────────
tpl = open(TPL, encoding='utf-8').read()
ANCHOR = """        if not it.get('objective'):
            issues.append((it['id'], 'objective 없음 — mk(..., obj=) 로 출제 의도를 적을 것', [], 0))
"""
assert tpl.count(ANCHOR) == 1, '앵커를 못 찾았다'
NEW = ANCHOR + """        # ★감사39 신설 — 은행이 읽히는 문면은 평문이다★
        #   T14 가 P7(M02195)부터 해설에 강조 표기를 쓰기 시작해 ★96제★ 가 그대로 병합됐다.
        #   저작 점검의 평문 항은 ★발문·선지만★ 보았고 해설은 사정거리 밖이었다 — 열여섯
        #   배치가 지나서야 감사39 의 검사 B 가 잡았다.
        #   ▸ ★한 필드에 건 규약은 같은 규약이 걸려야 할 다른 필드를 함께 적는다★ — 그래서
        #     ★학생이 읽는 네 자리★ 를 한꺼번에 본다(테마 지역 검사가 아니라 은행 공통 자리에
        #     건다 — 지역에 걸면 다음 테마가 새 local_checks 를 쓰면서 또 샌다).
        #   ▸ `calc_check` 와 `verified.watch` 는 ★걸지 않는다★ — 출제자·검증자가 읽는 내부
        #     주석이고 학생에게 나가는 문면이 아니다.
        for _f in ('stem', 'solution', 'answer_proof'):
            if '★' in (it.get(_f) or ''):
                issues.append((it['id'], f'{_f} 에 강조 표기 — 은행이 읽히는 문면은 평문', [], 0))
        for _i, _c in enumerate(it['choices']):
            if '★' in _c:
                issues.append((it['id'], f'{_i + 1}번 선지에 강조 표기 — 은행은 평문', [], 0))
"""
open(TPL, 'w', encoding='utf-8').write(tpl.replace(ANCHOR, NEW))
import ast
ast.parse(open(TPL, encoding='utf-8').read())
print('  ✅ batch_template.verify() 에 평문 게이트 신설 — stem·choices·solution·answer_proof')
