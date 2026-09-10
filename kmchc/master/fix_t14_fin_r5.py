"""T14 마감 4차 조치 — ★내가 고쳤다고 적은 자리가 다른 필드였다★ (크기 귀속의 마지막 둘)

4차 확인 순회 판정 — ★★세 게이팅 동시 0건(최종 문면)★★
  · solver      ★차단 0★ — "네 문항 모두 닫아도 되겠습니다"
  · defender    ★블로커 0★ — "닫아도 되는 상태입니다" + ★미반영 확인 사항 1★
  · factchecker ★✗ 0 · 차단 △ 0★ — "네 건 다 닫아도 됩니다" + 비차단 △ 3

■ ★★defender 가 내 말을 믿지 않고 문면을 확인해 반쪽 미반영을 잡았다★★
  3차 조치에서 M02298 의 크기 귀속을 낮추면서 ★해설과 계산 줄★ 을 고쳤다. 그리고 4차 프롬프트에
  "근거 줄에 '두 값은 서로 다른 기준으로 잰 값이라…' 를 넣었다" 고 적었다. ★그것이 틀렸다★ —
  넣은 곳은 `calc_check`(계산 줄)이고 `answer_proof`(근거)는 그대로였다. defender 는 내 말을 받아
  적지 않고 파일을 세어 ★"근거 줄에는 들어가 있지 않습니다"★ 라고 되짚었다.
  ▸ ★★새로 얻는다 — 검증자마다 보는 필드가 다르다★★. `agent_pipeline.write_inputs()` 를 보면
    defender 의 파일은 ★근거(answer_proof)와 해설만★ 싣고, factchecker 의 파일은 ★근거와 계산
    줄(calc_check)을 함께★ 싣는다. 그래서 ★계산 줄에만 넣은 고침은 defender 에게 보이지 않는다.★
    한 흠을 여러 필드가 나눠 지고 있으면 ★고칠 필드를 필드 이름으로 세어야 한다.★
  ▸ ★★그리고 조치 보고를 검증자에게 사실로 넘기지 않는다★★ — 내가 "이렇게 고쳤다" 고 적은 것이
    실제 문면과 어긋날 수 있다. 이번에는 검증자가 잡았지만, ★잡아 주기를 기대할 자리가 아니다.★
    다음부터 확인 순회 프롬프트에는 ★고친 필드 이름★ 을 적는다.

■ 남은 크기 귀속 둘 — 세 게이팅이 함께 짚었다
  ㉠ ★M02298 발문의 '그만큼'★ — '이온이 ★그만큼★ 커진 원인' 은 61 pm 이라는 ★크기★ 를 묻는
     낱말이다. 해설이 이제 방향만 주장하므로 결이 어긋난다(defender·factchecker 가 같은 문면을
     같은 방향으로 짚었다 — factchecker: "'더 커진' 으로 바꾸면 완전 정합").
  ㉡ ★M02298 근거의 '그만큼'★ — '전자구름이 ★그만큼★ 넓어져 커졌다'(defender 가 짚은 자리).
     두 값의 측정 기준이 달라 크기를 이 몫에 돌릴 수 없으므로 낱말을 뺀다.
  ▸ ★크기를 묻지 않고 방향을 묻는다★ — 발문·근거·계산 줄·해설 넷이 이제 같은 것을 말한다.

■ 함께 받는 둘(factchecker 비차단 △)
  ㉢ ★M02296 ③ 단평에 조건을 붙인다★ — 해설 본문에는 '양성자도 함께 늘어나는 이 그림에서는' 을
     넣었으나 ★단평은 조건 없이 남아 있었다★('같은 껍질에 전자가 늘면 값은 오히려 줄어들어').
     단평은 해설의 축약 포인터지만 학생이 그것만 볼 수도 있다. 다섯 자를 앞에 붙인다.
     ★같은 주장을 두 자리에 적었으면 한정도 두 자리에 적는다.★
  ㉣ ★M02297 ② 반박의 '오르는'★ — '곡선이 오르는 모양' 은 A 곡선의 단조 상승을 살짝 전제한다
     (주기 경계에서는 유효 핵전하가 내려간다). 결론은 오르내림과 무관하므로 ★'곡선 모양'★ 으로
     줄인다. ★전제가 필요 없는 문장에 전제를 넣지 않는다.★

■ 받지 않는 것
  · factchecker: M02296 껍질 정의에 '주양자수' 명시 — 3차에 물렸고 4차에 factchecker 자신이
    "현 문면 유지가 맞습니다" 로 확인했다.
  · solver 4차 부기: M02296 의 '완만하게' 표기 — factchecker 가 통용 표기로 판정했다.
"""
import ast
import importlib
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'build_t14_fin.py')
body = open(SRC, encoding='utf-8').read()
BEFORE = body


def rep(old, new, n=1):
    global body
    c = body.count(old)
    assert c == n, f'{c}곳(기대 {n}) — {old[:46]!r}'
    body = body.replace(old, new)


print('T14 마감 4차 조치')

# ══ ㉠ M02298 발문 — 크기를 묻지 않고 방향을 묻는다 ═════════════════════════════════
rep("""             '다른 알갱이와의 작용은 생각하지 않을 때 이온이 그만큼 커진 원인으로 옳은 것은?',""",
    """             '다른 알갱이와의 작용은 생각하지 않을 때 이온이 더 커진 원인으로 옳은 것은?',""")

# ══ ㉡ M02298 근거 — defender 가 짚은 '그만큼'(계산 줄과 달리 여기는 그대로였다) ══════
rep("""             '늘어 서로 밀치는 몫이 커졌으므로, 전자구름이 그만큼 넓어져 커졌다',""",
    """             '늘어 서로 밀치는 몫이 커졌으므로, 전자구름이 넓어져 커졌다',""")

# ══ ㉢ M02296 ③ 단평 — 해설에만 붙였던 한정을 단평에도 붙인다 ═══════════════════════
rep("""           '전자 수가 늘어 급상승하고 핵전하가 커져 하강한다': '같은 껍질에 전자가 늘면 값은 '
                                          '오히려 줄어들어.'},""",
    """           '전자 수가 늘어 급상승하고 핵전하가 커져 하강한다': '양성자도 함께 늘면 같은 '
                                          '껍질에서는 값이 오히려 줄어들어.'},""")

# ══ ㉣ M02297 ② 반박 — 전제가 필요 없는 문장에 전제를 넣지 않는다 ═══════════════════
rep("""          '의 곡선이 오르는 모양에서 이미 읽히고, 그 축을 더해도 빠진 양은 그대로야. '""",
    """          '의 곡선 모양에서 이미 읽히고, 그 축을 더해도 빠진 양은 그대로야. '""")

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

if '그만큼' in flat:
    bad.append(f"★크기 귀속이 남아 있다★ — '그만큼' 이 아직 있다")
GONE = [
    ('★M02298 발문의 크기 물음(두 게이팅)★', '이온이 그만큼 커진 원인'),
    ('★M02298 근거의 크기 귀속(defender)★', '전자구름이 그만큼 넓어져'),
    ('M02296 ③ 단평의 한정 없는 문면(factchecker)', "'같은 껍질에 전자가 늘면 값은 오히려 줄어들어.'"),
    ('M02297 ② 반박의 단조 상승 전제(factchecker)', '곡선이 오르는 모양에서'),
]
WANT = [
    ('★M02298 발문이 방향을 묻는다★', '이온이 더 커진 원인으로 옳은 것은?'),
    ('★M02298 근거가 방향만 말한다★', '전자구름이 넓어져 커졌다'),
    ('M02296 ③ 단평에 한정이 붙음', '양성자도 함께 늘면 같은 껍질에서는 값이 오히려 줄어들어'),
    ('M02297 ② 반박에서 전제가 빠짐', '곡선 모양에서 이미 읽히고'),
    ('★M02298 계산 줄의 기준 차이(3차에 넣은 것 — 지켜져야 한다)★',
     '서로 다른 기준으로 잰 값이라 늘어난 크기까지 이 몫에 돌리지 않는다'),
    ('★M02298 해설이 방향만 귀속(3차)★', '값이 커진 방향이 그 결과야'),
    ('★M02296 ③ 반박의 그림 조건(3차)★', '양성자도 함께 늘어나는 이 그림에서는'),
]
KEEP = [
    ('M02295 정답', '114 pm'),
    ('★M02295 의 가장 값진 오답★', "'77 pm'"),
    ('M02296 정답', '급상승은 껍질 때문이고 하강은 핵전하 때문이다'),
    ('★M02296 ①/④ 거울쌍★', '급상승은 핵전하 때문이고 하강은 껍질 때문이다'),
    ('★M02296 ② 두 항 짝 꼴(뒷항 2:2)★', '급상승도 껍질 때문이고 하강도 껍질 때문이다'),
    ('M02296 껍질·핵전하 정의', '껍질은 전자가 들어 있는 층을 뜻하고'),
    ('M02296 원자 번호 범위', '1~3주기 원소를 원자 번호 순으로'),
    ('M02297 정답', '원자가전자가 받는 끌림의 세기를 나타낸 축'),
    ('M02297 확인의 규정', '두 양이 한 그림에 함께 실려 있을 때에만 그 주석을 그림으로 확인했다고 하자'),
    ('M02297 더할 그림', '더 있어야 할 축은 그래프 A 에 함께 그린다고 할 때'),
    ('M02297 ② 반박의 결정 문장', '그 축을 더해도 빠진 양은 그대로야'),
    ('M02298 정답', '전자가 하나 늘어 밀침이 커졌기 때문이다'),
    ('M02298 ④ 의 방향 오류', '전자가 하나 늘어 유효 핵전하가 커졌기 때문이다'),
    ('★M02298 시야 한정★', '옆에 놓인 다른 알갱이와의 작용은 생각하지 않을 때'),
    ('★M02298 등전자가 아님을 세우는 발문★', '전자가 들어 있는 껍질 수도 둘로 같다'),
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
items = importlib.import_module('build_t14_fin').build()
if ''.join(str(x['answer'] + 1) for x in items) != '2413':
    bad.append(f"정답 자리가 설계와 다르다 — {''.join(str(x['answer'] + 1) for x in items)}")
for x in items:
    if len({w['type'] for w in x['distractors']}) < 3:
        bad.append(f"{x['id']} 오답 유형이 겹친다 — {[w['type'] for w in x['distractors']]}")
    for w in x['distractors']:
        if x['choices'][w['opt']] not in x['solution']:
            bad.append(f"{x['id']} {w['opt'] + 1}번 오답 문면이 해설에 없다")
from choiceprobe import probe
for x in items:
    for b in probe(x['choices'], ans=x['answer'], mid=x['id'], verbose=False):
        bad.append(f"{x['id']} 선지 자에 걸림 — {b}")
    ns = [len(c.replace(' ', '')) for c in x['choices']]
    s = (max(ns) - min(ns)) / (sum(ns) / 4)
    if s > 0.25:
        bad.append(f"{x['id']} 공백 뺀 산포 {s:.3f} > 0.25 — {ns}")

# ★네 필드가 같은 것을 말하는지 센다★ — 크기 귀속이 한 필드에만 남는 것이 이번 흠이었다
m98 = next(x for x in items if x['id'] == 'M02298')
for fld in ('stem', 'answer_proof', 'calc_check', 'solution'):
    if '그만큼' in m98.get(fld, ''):
        bad.append(f'M02298 {fld} 에 크기 귀속이 남아 있다')


def _tail_factor(c):
    for pat, f in (('하강은 껍질', '껍질'), ('하강도 껍질', '껍질'),
                   ('하강은 핵전하', '핵전하'), ('핵전하가 커져 하강', '핵전하')):
        if pat in c:
            return f
    return '?'


m96 = next(x for x in items if x['id'] == 'M02296')
kw = [_tail_factor(c) for c in m96['choices']]
if kw.count('껍질') != 2 or kw.count('핵전하') != 2:
    bad.append(f'M02296 뒷항이 2:2 가 아니다 — {kw}')

if bad:
    open(SRC, 'w', encoding='utf-8').write(BEFORE)
    print('  ❌ 불변 검사 실패 — 빌드 파일을 되돌렸다')
    for b in bad:
        print('     ·', b)
    raise SystemExit(1)
print('  ✅ 불변 검사 통과 — 발문 하나 · 근거 하나 · 단평 하나 · 반박 하나 · 네 필드 모두 방향만 말한다')
