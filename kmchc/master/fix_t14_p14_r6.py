"""T14 P14 6차 조치 — 단평 한 줄

5차 순회 판정
  · solver      ★차단 0★ · "닫아도 됩니다" · 갈린 네 자리가 모두 의도한 효과를 냈다고 확인
  · defender    ★교체 필수 0★ · "5차 순회 종결 권고" · M02270 ④ 는 "제 안보다 낫습니다"
  · factchecker ★✗ 1★ — M02268 ④ 단평 한 줄 · 차단 △ 0 · 나머지는 모두 참으로 확인

■ ★내가 5차에 저지른 것 — 해설을 고치고 단평을 따라 고치지 않았다★
  5차에 M02268 ④ 해설의 근거를 하나로 줄였다('주석의 주어는 원자가전자야'). 그런데 ★같은 자리의
  단평은 옛 근거를 그대로 두었다★ — '주석은 뒤따르는 것을 적었어' 는 방향 얘기이고, 게다가
  ★③ 단평('반지름은 그다음 고리야')이 이미 맡고 있는 자리★ 를 겹쳐 짚는다. 학생이 읽는 한 줄이
  그 선지가 틀린 까닭을 가리키지 못한다.
  ▸ ★새로 얻는다 — 해설의 근거를 바꾸면 그 자리의 단평도 함께 센다.★ 단평은 해설의 한 줄
    요약이므로 근거가 바뀌면 반드시 따라와야 하고, 짧아서 옛 문면이 남아도 눈에 띄지 않는다.
  ▸ 이 배치에서 ★단평이 문제가 된 것이 세 번째★ 다 — 3차(M02266 ④ 단평이 오답을 떠받침) ·
    5차(M02274 ① 단평의 한정 누락) · 6차(이번). ★단평은 짧아서 먼저 낡는다.★
"""
import ast
import importlib
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'build_t14_p14.py')
body = open(SRC, encoding='utf-8').read()
BEFORE = body


def rep(old, new, n=1):
    global body
    c = body.count(old)
    assert c == n, f'{c}곳(기대 {n}) — {old[:44]!r}'
    body = body.replace(old, new)


print('T14 P14 6차 조치 — 단평 한 줄')

rep("           '모든 전자를 두고 적은 한 방향의 고리': '주석은 뒤따르는 것을 '\n"
    "                                            '적었어.'},",
    "           '모든 전자를 두고 적은 한 방향의 고리': '주석의 주어는 '\n"
    "                                            '원자가전자야.'},")

assert body != BEFORE
open(SRC, 'w', encoding='utf-8').write(body)

bad = []
try:
    ast.parse(body)
except SyntaxError as e:
    raise SystemExit(f'치환 결과가 문법에 어긋난다 — {e.lineno}행: {e.msg}')

live = '\n'.join(l for l in body.split('def build()')[1].split('\n')
                 if not l.lstrip().startswith('#'))
flat = re.sub(r"'\s*\n\s*'", '', live)

GONE = [('M02268 ④ 단평의 옛 근거(factchecker ✗)', '주석은 뒤따르는 것을 적었어')]
WANT = [
    ('M02268 ④ 단평이 해설의 근거를 따라옴', "'모든 전자를 두고 적은 한 방향의 고리': '주석의 주어는 원자가전자야.'"),
    ('M02268 ④ 해설의 근거 하나', '주석의 주어는 ★원자가전자★야'),
]
KEEP = [
    ('M02268 ③ 단평 — 이 자리를 겹쳐 짚지 않아야 한다', '반지름은 그다음 고리야'),
    ('M02270 ④ 5차 문면(defender 가 승인)', '껍질 하나와 양성자 둘이 상쇄되어 비슷하다'),
    ('M02274 ② 5차 문면', '염소 이온까지 작아지다가 칼륨 이온에서 다시 커진다'),
    ('M02272 ② 5차 문면', '두 값은 자료가 달라 같은 자로 견줄 수 없다'),
    ('M02274 ① 단평의 한정', '계열 안에서는 양성자가 많을수록 작아져'),
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
items = importlib.import_module('build_t14_p14').build()
if ''.join(str(x['answer'] + 1) for x in items) != '3142312413':
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
print('  ✅ 불변 검사 통과 — 단평 한 줄 · 선지 마흔 재측정 0건')
