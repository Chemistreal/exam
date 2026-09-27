"""T14 P16 8차 조치 — 발문에 '반지름' 이라는 낱말이 한 번도 없었다

7차 순회 판정
  · solver      ★차단 0 · 자족성 전부 ○★ · "닫아도 됩니다" (M02294 네 선지가 발문만으로 갈림)
  · factchecker ★✗ 0 · 차단 △ 0★ · "닫아도 됩니다" (M02294 ④ 반박이 발문만으로 도출됨)
  · defender    ★블로커 2★(M02287 ② 반박 · M02293 발문의 빈 척도)

■ ★★M02293 — 발문 전체에 '반지름' 이 한 번도 나오지 않았다★★
  '양성자 수는 차례로 15·16·17·19·20 이라 ★그 차례대로 작아진다★' — 무엇이 작아지는지 주어가 비어
  있고, 문면대로 직전 명사구를 주어로 삼으면 '양성자 수가 15 에서 20 으로 늘면서 작아진다' 는
  ★자기모순★ 이 된다. ▸ factchecker 7차도 같은 자리를 △ 로 짚었다(두 게이팅) — solver 도 4·6차에
  보완을 권했다. 네 번 지적된 자리다.
  ▸ 이 공백이 ④('전하가 없어 끼울 수 없다')에 ★실물 옹호★ 를 열어 준다 — 이온 반지름과 중성 원자
    반지름은 같은 척도로 잴 수 없고, 실제로 아르곤(공유 106 · 판데르발스 188 pm)은 Cl⁻ 181 과
    K⁺ 138 '사이' 에 오지 않는다. 막고 있는 것은 '잰 값이 아니라 그 순서 규칙만으로' 한 구절인데,
    그 '순서 규칙' 이 가리키는 것이 곧 ★미정의된 반지름 감소열★ 이라 자기 참조에 가까웠다.
  ▸ 고침은 둘이다 — ㉠주어를 채운다('이온 반지름은 그 차례대로 작아진다') ㉡봉인이 가리키는 잣대를
    이름으로 박는다('이 줄을 세운 ★양성자 수 순서★ 만으로').
  ▸ ★★새로 얻는다 — 자료의 순서를 규칙으로 봉인할 때는 그 규칙이 무엇의 순서인지 이름으로 적는다.
    '그 순서 규칙' 처럼 앞을 가리키는 말로 두면, 가리키는 대상이 정의되지 않은 채 자기 참조가
    되어 봉인이 새 나간다.★★

■ M02287 ② — 반박이 결정적 반박을 적지 않았다(defender)
  '②는 묶여 있는 요인도 다툰다고 보았어. 같은 주기에서는 껍질 수가 그대로라 ★다툴 것이 없어★.'
  — 이는 ②('껍질이 이긴다')의 ★전건이 성립하지 않는다★ 는 말이라 공허참 쪽으로 밀어 준다. ② 를
  실제로 죽이는 것은 '주기에서는 값이 ★줄어든다★' 인데 그 문장이 빠져 있었다.
  ▸ solver·factchecker 7차는 M02287 을 이상 없음으로 읽었고 factchecker 5차는 같은 어법을 △ 로
    두었다. ★정답 문면은 그대로 두고 반박에 결정적 문장을 넣는다★ — 세 회차에 걸쳐 두 게이팅이
    닿은 자리이므로 값을 치를 만하고, 정답을 고치면 다른 흠이 생긴다(네 조합의 완결 분할이 깨진다).
  ▸ ★★새로 얻는다 — '다툴 것이 없다' 는 전건을 비우는 반박이다. 승패를 말하는 오답은 ★결과의
    방향★ 으로 죽인다(무엇이 이기는지가 아니라 값이 어느 쪽으로 가는지).★★

■ 받지 않은 것 — M02287 정답의 '이긴다' 어법(defender 제안)
  defender 는 정답을 '주기에서는 껍질이 묶여 양성자 수만 남아 값이 줄고, 족에서는 껍질이 이겨 값이
  는다' 로 고치자고 했으나 ★받지 않는다★ — ㉠solver·factchecker 7차가 둘 다 이상 없음으로 읽었고
  ㉡네 선지가 {주기, 족} × {양성자, 껍질} 의 완결 분할이라 정답 문면을 늘리면 그 대칭이 깨지며
  ㉢선지 길이 산포가 자를 넘는다(defender 자신도 그 분할을 "좋은 설계" 라 적었다).
"""
import ast
import importlib
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'build_t14_p16.py')
body = open(SRC, encoding='utf-8').read()
BEFORE = body


def rep(old, new, n=1):
    global body
    c = body.count(old)
    assert c == n, f'{c}곳(기대 {n}) — {old[:46]!r}'
    body = body.replace(old, new)


print('T14 P16 8차 조치')

# ══ M02287 ② — 전건을 비우는 반박에 결과의 방향을 더한다(defender) ══
rep("          '②는 묶여 있는 요인도 다툰다고 보았어. 같은 주기에서는 껍질 수가 그대로라 다툴 것이 '\n"
    "          '없어. '",
    "          '②는 묶여 있는 요인도 다툰다고 보았어. 같은 주기에서는 껍질 수가 그대로여서 양성자 '\n"
    "          '몫만 남아 값이 줄어들지. '")

# ══ M02293 — ★발문에 '반지름' 이 한 번도 없었다★(defender 블로커 · factchecker △) ══
rep("             '계열이고, 양성자 수는 차례로 15·16·17·19·20 이라 그 차례대로 작아진다. 아르곤 '",
    "             '계열이고, 양성자 수는 차례로 15·16·17·19·20 이며 이온 반지름은 그 차례대로 '\n"
    "             '작아진다. 아르곤 '")
rep("             '세운 것이니, 잰 값이 아니라 그 순서 규칙만으로 아르곤의 자리를 정할 때 옳은 '",
    "             '세운 것이니, 잰 값이 아니라 이 줄을 세운 양성자 수 순서만으로 아르곤의 자리를 '\n"
    "             '정할 때 옳은 '")

assert body != BEFORE
try:
    ast.parse(body)
except SyntaxError as e:
    raise SystemExit(f'치환 결과가 문법에 어긋난다 — {e.lineno}행: {e.msg}')
open(SRC, 'w', encoding='utf-8').write(body)

bad = []
live = '\n'.join(l for l in body.split('def build()')[1].split('\n')
                 if not l.lstrip().startswith('#'))
flat = re.sub(r"'\s*\n\s*'", '', live)

GONE = [
    ('★M02293 발문의 빈 주어(두 게이팅)★', '15·16·17·19·20 이라 그 차례대로 작아진다'),
    ('★M02293 봉인의 자기 참조(defender)★', '잰 값이 아니라 그 순서 규칙만으로'),
    ('M02287 ② 반박이 전건을 비우던 문장(defender)', '껍질 수가 그대로라 다툴 것이 없어'),
]
WANT = [
    ('★M02293 발문에 반지름을 적음★', '이온 반지름은 그 차례대로 작아진다'),
    ('★M02293 봉인이 가리키는 잣대를 이름으로★', '잰 값이 아니라 이 줄을 세운 양성자 수 순서만으로'),
    ('M02287 ② 반박에 결과의 방향', '껍질 수가 그대로여서 양성자 몫만 남아 값이 줄어들지'),
]
KEEP = [
    ('M02285 정답', '두 말은 자료의 서로 다른 곳에서 각각 읽힌다'),
    ('M02286 정답', '봉우리마다 껍질이 하나씩 더 열리기 때문이다'),
    ('M02287 정답', '주기에서는 양성자가, 족에서는 껍질이 이긴다'),
    ('M02287 ③ 반박', '같은 족에서 아래로 갈수록 값이 커지는 것은'),
    ('M02288 정답', '한 그림에만 비활성 기체가 담겨 있다'),
    ('M02289 정답', '한 쌍만 두 요인이 같은 쪽을 가리킨다'),
    ('M02289 다툴 때의 승자(삭제 금지)', '두 가리킴이 어긋나는 쌍에서는 적힌 값이 승자를 말한다'),
    ('M02290 정답', '전자를 하나 잃었다는 표시다'),
    ('M02291 정답', '남은 전자가 같은데 셀레늄의 양성자가 적기 때문이다'),
    ('M02292 정답', '잃거나 얻은 전자 수까지 세어야 정해진다'),
    ('M02293 정답', '염화 이온과 칼륨 이온 사이에 놓인다'),
    ('M02293 계열의 전자 수', '전자가 모두 18 개인 한 계열'),
    ('M02294 정답', '값이 줄기만 하는 곡선이 이온선이다'),
    ('M02294 엇갈림 서술', '앞의 세 자리와 뒤의 세 자리에서 위아래가 서로 바뀐다'),
]
for why, txt in GONE:
    if txt in flat:
        bad.append(f'{why} — 문면이 남아 있다: {txt}')
for why, txt in WANT:
    if txt not in flat:
        bad.append(f'{why} — 문면이 들어가지 않았다: {txt}')
for why, txt in KEEP:
    if txt not in flat:
        bad.append(f'{why} — 지켜야 할 문면이 사라졌다: {txt}')
for m in re.finditer(r'★\s+(를|을|은|의|으로|로|에서|에|과|보다|처럼|까지|부터'
                     r'|이고|이다|이야|이라|이지)(?=[\s,.·)?!\'"]|$)', flat):
    bad.append(f'별표 뒤에 조사를 띄웠다 — {flat[max(0, m.start() - 16):m.end()]!r}')

sys.path.insert(0, BASE)
items = importlib.import_module('build_t14_p16').build()
if ''.join(str(x['answer'] + 1) for x in items) != '1342431321':
    bad.append(f"정답 자리가 설계와 다르다 — {''.join(str(x['answer'] + 1) for x in items)}")
for x in items:
    if len({w['type'] for w in x['distractors']}) < 3:
        bad.append(f"{x['id']} 오답 유형이 겹친다 — {[w['type'] for w in x['distractors']]}")
    for w in x['distractors']:
        if x['choices'][w['opt']] not in x['solution']:
            bad.append(f"{x['id']} {w['opt']+1}번 오답 문면이 해설에 없다")
from choiceprobe import probe
for x in items:
    for b in probe(x['choices'], ans=x['answer'], mid=x['id'], verbose=False):
        bad.append(f"{x['id']} 선지 자에 걸림 — {b}")
    ns = [len(c.replace(' ', '')) for c in x['choices']]
    s = (max(ns) - min(ns)) / (sum(ns) / 4)
    if s > 0.25:
        bad.append(f"{x['id']} 공백 뺀 산포 {s:.3f} > 0.25 — {ns}")

if bad:
    open(SRC, 'w', encoding='utf-8').write(BEFORE)
    print('  ❌ 불변 검사 실패 — 빌드 파일을 되돌렸다')
    for b in bad:
        print('     ·', b)
    raise SystemExit(1)
print('  ✅ 불변 검사 통과 — 두 문항 · 발문 둘 · 해설 하나 · 두 계수법 모두 자 안')
