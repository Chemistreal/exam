"""T14 P13 6차 조치 — 마감. 자문이 두 번 짚은 한 자리

4차 순회 판정 — ★세 게이팅 동시 0건★(마감 조건 성립) · 5차에 선택 수정 둘 반영
  · solver      차단 0 · 열 문항 전부 '확실' · "닫아도 됩니다"
  · defender    교체 필수 0 · "3차 조치는 새 흠을 낳지 않았습니다" · "더 손대면 흔들림이 큽니다"
  · factchecker ✗ 0 · 차단 △ 0 · "이 배치는 닫아도 됩니다"
  · sim(자문)   ★D 오답 0 · C 가 열 문항에서 모두 흔들리고 다섯에서 오답 착지★ ·
                죽은 선지 2 · "한 자리만 고치고 닫으십시오"

■ ★★자문이 두 번 짚은 자리를 받는다 — M02258 ②★★
  sim 이 3차에 권고했고 내가 보류했다(그때 sim 안이 같은 문항 ③ 과 경로가 겹쳤고 defender 가
  현행 ② 를 '반발력이 실재 요인이라 유인이 크다' 고 했다). 4차에 sim 이 ★같은 자리를 다시,
  더 정확한 근거로★ 짚었다 — ★유인이 요인 쪽이 아니라 전제 쪽에서 끊긴다★. '전자 수가 줄어' 는
  발문이 스스로 적어 둔 세 숫자(바깥 전자 1·2·7)에 정면으로 어긋나므로 ★가장 값싼 재독★ 으로
  지워지고, 반발력을 믿는 학생조차 그 전제를 받아들일 수 없다. 실제로 네 프로필 누구도 집지
  않았다(B 는 ③ 으로, A 는 ① 로 흘렀다).
  ▸ ★새로 얻는다 — 오답의 유인은 결론이 아니라 전제에서 먼저 끊긴다. 오답을 쓸 때 앞절이
    발문의 값과 어긋나는지부터 센다.★
  ▸ ★같은 지적을 두 번 보류하지 않는다★ — 첫 보류의 근거(경로 겹침)는 대체 문면을 바꾸면
    풀리는 것이었는데, 나는 문면을 바꾸는 대신 지적 전체를 미뤘다.

■ 문면은 sim 안을 그대로 쓰지 않았다 — ★두 절이 모두 거짓이 되게★ 고쳤다
  sim 안('늘어난 전자끼리 밀치는 힘이 커져 더 촘촘히 뭉친다')은 ★앞절이 참★ 이다(전자가 늘면
  반발은 실제로 커진다). 그 꼴은 1차에 defender 가 교체 필수로 짚은 병('…는 맞지만' 꼴)이다.
  ★밀치는 힘의 방향을 거꾸로 두면 두 절이 모두 거짓이 되고, sim 이 노린 기제 오독(반발을 압축
  으로 읽기)도 그대로 남는다.★ 반박에는 전자 수를 세고 반발의 방향을 짚는 두 걸음이 필요하다.

■ 받지 않은 하나 — M02262 ①(부채로 적는다)
  sim 이 '입자 전체가 띠고 있는 전하의 양' 을 죽었다고 하며 ★'전자 사이에 서로 밀치는 힘'★ 을
  대안으로 냈는데, 그것은 ★sim 자신이 3차에 죽였던 문면★ 이다(왕복). 이 문항은 '달라지지 않는
  것' 을 묻는 쉬움 자리라 쓸 수 있는 오답이 다섯뿐이고(전자 수 · 바깥 껍질 전자 수 · 반발 ·
  끌림 · 전하) 그 가운데 셋을 회차마다 하나씩 죽였다 — ★같은 계열의 대체안이 되풀이되면 그
  계열이 막힌 것이다★(P12 규약). defender 4차는 '얇으나 4지선다에서 한 자리 얕은 것은 허용 폭
  안' 이라 판정했다. ★설계가 정한 한계로 남긴다.★
"""
import ast
import importlib
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'build_t14_p13.py')
body = open(SRC, encoding='utf-8').read()
BEFORE = body


def rep(old, new, n):
    global body
    c = body.count(old)
    assert c == n, f'{c}곳(기대 {n}) — {old[:40]!r}'
    body = body.replace(old, new)


print('T14 P13 6차 조치 — 한 자리')

rep('전자 수가 줄어 서로 밀치는 힘도 약해진다는 것',
    '전자끼리 밀치는 힘이 약해져 전자가 더 촘촘히 뭉친다는 것', 3)
rep("'전자 수가 늘어나는 것을 '\n               '세지 않고 줄어든다고 봄'",
    "'밀치는 힘의 방향을 거꾸로 보아 '\n               '반발이 크기를 줄인다고 봄'", 1)
rep("'②는 전자 수가 줄어든다고 보았어. 세 원소는 모두 중성 원자라 전자 수가 양성자 '\n"
    "          '수와 같고, 자료의 배치를 더하면 11 개·12 개·17 개로 오른쪽으로 갈수록 늘어. 전자 '\n"
    "          '수가 늘면 밀치는 힘도 세지니 두 절이 다 어긋나지. 다만 그 힘만 따르면 반지름이 '\n"
    "          '커져야 하는데 자료는 줄어든다고 했으니, 반대 방향으로 작용하는 두 요인을 만나면 '\n"
    "          '★어느 쪽이 더 크게 작용했는지★를 적어야 해. '",
    "'②는 밀치는 힘의 방향을 거꾸로 보았어. 세 원소는 모두 중성 원자라 전자 수가 양성자 '\n"
    "          '수와 같고, 자료의 배치를 더하면 11 개·12 개·17 개로 오른쪽으로 갈수록 늘어. 전자가 '\n"
    "          '늘면 밀치는 힘은 약해지는 것이 아니라 세지고, 밀치는 힘은 전자를 뭉치게 하는 것이 '\n"
    "          '아니라 퍼지게 하지. 두 절이 다 어긋나. 그 힘만 따르면 반지름이 커져야 하니, 반대 '\n"
    "          '방향으로 작용하는 두 요인을 만나면 ★어느 쪽이 더 크게 작용했는지★를 적어야 해. '", 1)
rep("'배치를 더하면 전자 수가 '\n                                           '늘어.'",
    "'밀치는 힘은 전자를 퍼지게 해.'", 1)

assert body != BEFORE
open(SRC, 'w', encoding='utf-8').write(body)

bad = []
try:
    ast.parse(body)
except SyntaxError as e:
    bad.append(f'치환 결과가 문법에 어긋난다 — {e.lineno}행: {e.msg}')

live = '\n'.join(l for l in body.split('def build()')[1].split('\n')
                 if not l.lstrip().startswith('#'))
flat = re.sub(r"'\s*\n\s*'", '', live)

GONE = [('M02258 ② 의 전제가 발문의 값과 어긋난 자리(sim)', '전자 수가 줄어 서로 밀치는 힘도')]
WANT = [
    ('M02258 ② 새 문면(두 절이 모두 거짓)', '전자끼리 밀치는 힘이 약해져 전자가 더 촘촘히 뭉친다는 것'),
    ('M02258 ② 해설의 두 걸음', '밀치는 힘은 전자를 뭉치게 하는 것이 아니라 퍼지게 하지'),
]
KEEP = [
    ('M02262 ① — 부채로 남긴 자리(sim 안은 자기가 3차에 죽인 문면이다)',
     '입자 전체가 띠고 있는 전하의 양'),
    ('M02258 ③ — 경로가 겹치지 않아야 하는 이웃', '안쪽 껍질 전자의 가림이 늘어난 양성자를 상쇄한다는 것'),
    ('M02258 의 우열 맺음(factchecker 가 세운 문면)', '어느 쪽이 더 크게 작용하는지를 적는다'),
    ('M02255 의 유일성을 지탱하는 한정어', '단일결합으로 이어진 자리에서'),
    ('M02263 ② 5차 문면', '전하의 부호가 같은 것끼리만 견주어야 한다'),
    ('M02264 ② 4차 문면', '3주기의 값이 2주기의 값보다 크다고 보게 된다'),
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
for m in re.finditer(r'★\s+([은는이가을를에의로]|이고|이다|이지|이야)\b', flat):
    bad.append(f'별표 뒤에 조사를 띄웠다 — {flat[max(0, m.start() - 16):m.end()]!r}')

sys.path.insert(0, BASE)
items = importlib.import_module('build_t14_p13').build()
if ''.join(str(x['answer'] + 1) for x in items) != '1324134231':
    bad.append('정답 자리가 설계와 다르다')
for x in items:
    if len({w['type'] for w in x['distractors']}) < 3:
        bad.append(f"{x['id']} 오답 유형이 겹친다")
    for w in x['distractors']:
        if x['choices'][w['opt']] not in x['solution']:
            bad.append(f"{x['id']} {w['opt']+1}번 오답 문면이 해설에 없다")
from choiceprobe import probe
for x in items:
    for b in probe(x['choices'], ans=x['answer'], mid=x['id'], verbose=False):
        bad.append(f"{x['id']} 선지 자에 걸림 — {b}")

if bad:
    print('  ❌ 불변 검사 실패')
    for b in bad:
        print('     ·', b)
    raise SystemExit(1)
print('  ✅ 불변 검사 통과 — 선지 한 자리 교체 · 선지 마흔 재측정 0건')
