"""T14 P13 5차 조치 — 마감 직전 두 자리(선택 수정)

4차 순회 판정 — ★세 게이팅 동시 0건★
  · solver      ★차단 0 · 열 문항 전부 '확실' · 무정답·복수정답 0★ · "닫아도 됩니다"
  · defender    ★교체 필수 0 — "3차 조치는 새 흠을 낳지 않았습니다"★ · 닫아도 되는 문항 아홉
                · 선택 수정 1 · "더 손대면 이득보다 흔들림이 큽니다"
  · factchecker ★✗ 0 · 차단 △ 0★ · 선택 2 · "이 배치는 닫아도 됩니다"
  · sim(자문)   별도 기록

■ 받은 선택 둘
  ㄱ) ★M02263 ② — 한 독법에서 참(defender ㉢)★ 이라 받았다. 자료에서 부호를 먼저 따지면
     염소 이온이 음이온이고 나트륨 이온이 양이온이므로 ★학생의 결론이 그 한 걸음만으로 실제로
     깨진다★ — '결론을 내리기 전에 해야 할 일' 로서 참으로 작동한다. defender 는 이 자리를
     선택으로 두었으나 ★오답이 참이 되는 것은 이 은행에서 가장 무거운 결함★ 이라 받는다
     (P12 규약 가). 문면은 defender 안을 그대로 쓴다 — 부호라는 유혹이 남고, 정답의 '등전자
     계열' 을 품지 않으며, ④(같은 주기)와 경로가 갈린다.
  ㄴ) ★M02257 ① 단평 — 발문에 없는 '셋째 요인' 의 정체를 근거로 씀(factchecker)★. 진술은
     참이지만 학생이 자료에서 확인할 수 없고, ① 의 배제는 '괄호가 열린 자리가 둘째 요인 옆'
     이라는 발문 안의 근거로 이미 완결된다. ★선지는 건드리지 않고 해설만 자료 안으로 낮춘다.★

■ ★★세 번째로 기각한 안 — 근거를 문서로 못 박아 둔다★★
  factchecker 가 2차·3차·4차에 걸쳐 M02261 발문에 '비활성 기체의 점은 찍혀 있지 않고' 를
  넣으라고 했다. ★받지 않는다.★ 개념 대장이 그래프 A 를 ★3주기 11~18★ 로 적었고(C14-016),
  C14-012 는 그 구간을 ★'3주기 Na→Ar 단조 감소'★ 로 적었다. 즉 ★교재의 그래프 A 는 아르곤을
  포함하고 그 구간의 단조성도 아르곤까지 보증된다.★ 비활성 기체를 뺀 것은 그래프 B 뿐이다
  (C14-015·C14-016[6]).
  ▸ ★검증자의 지적이 옳은 자리도 있다★ — 이 단원의 규칙(이어진 두 원자의 핵 사이 거리)만으로는
    아르곤의 결합반지름을 정의할 수 없다는 것은 화학적으로 맞다. 그러나 ★이 은행의 근거는
    교재이고, 교재가 그 값을 그래프에 실었다.★ 자료를 교재와 어긋나게 고칠 수는 없다.
  ▸ ★새로 얻는다 — 같은 안이 세 회차 되풀이되면 내 근거를 대장에 문서로 박는다. 기각의 근거가
    회차마다 말로만 오가면 다음 회차에 같은 지적이 다시 온다.★

■ 마감 판정 근거
  ★세 게이팅이 4차에서 동시 0건★ 이 되었다. 이 회차의 조치는 ㉠선지 한 자리(참인 독법 제거)와
  ㉡해설 한 줄(자료 밖 근거 제거)뿐이고, 두 자리 모두 ★검증자가 문면까지 준 것★ 이다.
  P12 11차와 같은 자리다 — ★게이팅이 0건이 된 뒤의 선택 수정은 반영하고 마감한다.★
  다만 ㉠은 선지를 갈므로 ★choiceprobe 로 다시 재고★(0건) 게이트·국소검사를 다시 돌린다.
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
    """★앵커가 줄 가운데에서 시작하면 앞에 따옴표가 없다★ — 이 배치에서 다섯 번 걸렸다."""
    global body
    c = body.count(old)
    assert c == n, f'{c}곳(기대 {n}) — {old[:40]!r}'
    body = body.replace(old, new)


print('T14 P13 5차 조치 — 두 자리')

# ── M02263 ② 교체(defender 선택 — 한 독법에서 참) ──
rep('이온의 크기는 전하의 부호부터 따져야 한다', '전하의 부호가 같은 것끼리만 견주어야 한다', 3)
rep("'전하의 부호를 계열과 상관없이 '\n               '서는 잣대로 봄', 'sign')",
    "'부호가 다른 이온끼리는 견줄 수 '\n               '없다고 봄', 'sign')", 1)
rep("'②는 전하의 부호를 계열과 상관없이 서는 잣대로 보았어. 음이온이 양이온보다 크다는 '\n"
    "          '것도 등전자 계열 안에서 하는 말이야. 계열이 다른 이온끼리는 부호만으로 대소가 '\n"
    "          '정해지지 않아. '",
    "'②는 부호가 다른 이온끼리는 견줄 수 없다고 보았어. 자료는 산소 이온과 나트륨 '\n"
    "          '이온을 부호가 다른데도 전자 수가 같게 나란히 놓았고, 그 둘은 한 계열이라 견줄 수 '\n"
    "          '있어. 견주는 자리를 정하는 것은 부호가 아니라 계열이지. '", 1)
rep("'부호로 재는 것도 계열 안의 '\n                                       '말이야.'",
    "'부호가 달라도 한 계열이면 '\n                                       '견줘.'", 1)

# ── M02257 ① 단평의 자료 밖 근거를 낮춤(factchecker 선택 · 선지는 그대로) ──
rep("'①은 전하라는 낱말을 전자 수에 묶어 셋째 요인으로 보았어. 유효 핵전하는 핵이 '\n"
    "          '원자가전자를 당기는 세기를 말한 것이고, 셋째 요인은 전자끼리 밀치는 쪽을 말한 '\n"
    "          '것이야. 두 자리는 서로 다르고, 괄호가 열린 자리는 둘째 요인 옆이지. '",
    "'①은 전하라는 낱말을 전자 수에 묶어 셋째 요인으로 보았어. 셋째 요인이 무엇이든 '\n"
    "          '발문에서 괄호가 열린 자리는 둘째 요인 옆이야. 유효 핵전하는 핵이 원자가전자를 '\n"
    "          '당기는 세기를 더 정확히 말한 이름이니 그 자리가 맞지. '", 1)

assert body != BEFORE
open(SRC, 'w', encoding='utf-8').write(body)

# ─────────────────────────── 불변 검사 ───────────────────────────
bad = []
try:
    ast.parse(body)
except SyntaxError as e:
    bad.append(f'치환 결과가 문법에 어긋난다 — {e.lineno}행: {e.msg}')

live = '\n'.join(l for l in body.split('def build()')[1].split('\n')
                 if not l.lstrip().startswith('#'))
flat = re.sub(r"'\s*\n\s*'", '', live)

GONE = [
    ('M02263 ② 의 참인 독법(defender ㉢)', '이온의 크기는 전하의 부호부터 따져야 한다'),
    ('M02257 ① 단평의 자료 밖 근거(factchecker)', '셋째 요인은 전자끼리 밀치는 쪽'),
]
WANT = [
    ('M02263 ② 새 문면', '전하의 부호가 같은 것끼리만 견주어야 한다'),
    ('M02263 ② 해설의 새 까닭', '견주는 자리를 정하는 것은 부호가 아니라 계열이지'),
    ('M02257 ① 단평을 자료 안으로', '셋째 요인이 무엇이든 발문에서 괄호가 열린 자리는'),
]
KEEP = [
    ('M02255 의 유일성을 지탱하는 한정어(solver 가 지우지 말라고 했다)',
     '단일결합으로 이어진 자리에서'),
    ('M02261 발문 — 비활성 기체 줄은 세 번째로 기각했다(교재의 그래프 A 는 아르곤을 포함한다)',
     '3주기 원소만 담겨 있으며'),
    ('M02256 발문의 두 형용사(factchecker 의 보강안은 M02260 의 정답과 겹쳐 기각)',
     '값이 크게 오르는 자리와 완만하게 내려가는 자리'),
    ('M02258 ② (sim 권고를 받지 않은 자리)', '전자 수가 줄어 서로 밀치는 힘도 약해진다는 것'),
    ('M02264 ② (두 게이팅이 같은 문면을 낸 자리)', '3주기의 값이 2주기의 값보다 크다고 보게 된다'),
    ('M02263 ④ 의 계열 확인 대비쌍', '세 이온이 같은 주기에 있는지부터 확인해야 한다'),
    ('C14-020 의 못 — 껍질 수도 함께 묶인다', '전자 수와 껍질 수가 함께 묶여서'),
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
seq = ''.join(str(x['answer'] + 1) for x in items)
if seq != '1324134231':
    bad.append(f'정답 자리가 설계와 다르다 — {seq}')
diff = {d: sum(1 for x in items if x['difficulty'] == d) for d in ('쉬움', '중간', '어려움')}
if diff != {'쉬움': 2, '중간': 6, '어려움': 2}:
    bad.append(f'난이도 배분이 설계와 다르다 — {diff}')
if sum(1 for x in items if x['track'] == '일반') != 7:
    bad.append('일반 트랙이 7 이 아니다')
for x in items:
    ts = [w['type'] for w in x['distractors']]
    if len(set(ts)) < 3:
        bad.append(f"{x['id']} 오답 유형이 겹친다 — {ts}")
    for w in x['distractors']:
        if x['choices'][w['opt']] not in x['solution']:
            bad.append(f"{x['id']} {w['opt']+1}번 오답 문면이 해설에 없다")

#  ★선지를 갈았으니 choiceprobe 로 다시 센다★
sys.path.insert(0, BASE)
from choiceprobe import probe
for x in items:
    for b in probe(x['choices'], ans=x['answer'], mid=x['id'], verbose=False):
        bad.append(f"{x['id']} 선지 자에 걸림 — {b}")

if bad:
    print('  ❌ 불변 검사 실패')
    for b in bad:
        print('     ·', b)
    raise SystemExit(1)
print(f'  ✅ 불변 검사 통과 — 사라져야 할 문면 {len(GONE)} · 새 문면 {len(WANT)} · '
      f'지켜야 할 자리 {len(KEEP)} · 선지 마흔 재측정 0건')
