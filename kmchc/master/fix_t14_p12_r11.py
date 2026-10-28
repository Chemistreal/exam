"""T14 P12 11차 조치 — 마감 직전 한 낱말

11차 순회 판정 — ★세 게이팅 동시 0건★
  · solver     차단 0 · 열 문항 전부 '확실' · ★편집 지적 없음★
               ("이번 순회에서 새로 눈에 걸리는 것은 없습니다")
  · defender   ★선지 교체 0건 · "열 문항 모두 닫아도 됩니다"★
  · factchecker ✗ 0 · ★차단 △ 0 · "닫아도 됩니다"★ · 선택 수정 1
  · sim(자문)  별도 기록

■ 받은 선택 수정 하나 (factchecker)
  M02251 ② 반박의 '★어떤 수의 차로도★ 족은 가려지지 않지' 가 문자 그대로는 지나치다 —
  정답 ③ 의 잣대('원자가전자 수가 같은지')는 곧 ★원자가전자 수의 차가 0★ 이므로 예민한
  학생은 "그럼 원자가전자 수 차이도 수의 차 아닌가" 라는 충돌을 느낀다. '번호로 잰 어떤
  차로도' 로 한정하면 자가진단('수가 아니라 종류를 본다')과도 더 잘 맞는다.

■ 받지 않은 선택 수정 하나 (defender)
  M02252 ④ '전자를 잃은 만큼 알갱이의 무게가 줄어들기 때문' 에 '크게' 를 넣어 사실 층위
  에서도 거짓이 되게 하라는 안. defender 스스로 "필수 아님, 현행 유지도 무리 없음" 이라
  했고, sim 이 10차에 "④ 는 발문의 '전자가 몇 개 줄었으니' 를 그대로 되받아 A 가 확실히
  물린다" 며 유지에 동의했다. '크게' 를 넣으면 그 되받기가 흐려진다.
  → ★게이팅이 '필수 아님' 으로 둔 선택 사항이 자문의 매력 근거와 부딪치면 자문을 따른다★.

■ defender 가 마지막에 남긴 '건드리지 말 것' 둘 — 대장에 박아 둔다
  ㄱ) M02251 ④ 의 ★앵커 무게는 H–F 갈래에 둔다★ — H–Li 갈래는 '수소를 1족으로 보느냐' 를
      걸고 오는 반박이 이론상 가능하지만, ★수소를 17족에 놓는 규약은 없으므로 H–F 는 어느
      배치에서도 반례★ 다.
  ㄴ) M02248 ① 의 ★'두 쌍에서' 를 건드리지 않는다★ — 이 한정어가 비교항 생략 독법
      ("[껍질 수 요인과] 서로 반대로" — ㄴ에서는 참)을 막고 있다. ㄱ 에서는 맞설 껍질
      요인이 없으므로 그 독법에서도 거짓이 된다.
"""
import ast, re, os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_t14_p12.py')
body = open(SRC, encoding='utf-8').read()
BEFORE = body

print('T14 P12 11차 조치 — 한 문항')

old = ("'가지 않아 — 리튬과 나트륨은 열여섯, 베릴륨과 마그네슘은 열다섯이야. 어떤 수의 '\n"
       "          '차로도 족은 가려지지 않지. '")
new = ("'가지 않아 — 리튬과 나트륨은 열여섯, 베릴륨과 마그네슘은 열다섯이야. 번호로 잰 '\n"
       "          '어떤 차로도 족은 가려지지 않지. '")
pat = re.compile(r'\s*\n\s*'.join(re.escape(t) for t in re.split(r'\s*\n\s*', old)))
body, c = pat.subn(lambda m: new, body)
assert c == 1, f'{c}곳(기대 1)'

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

if '어떤 수의 차로도' in flat:
    bad.append('M02251 ② 반박의 지나친 단정이 남아 있다')
if '번호로 잰 어떤 차로도 족은 가려지지 않지' not in flat:
    bad.append('새 한정이 들어가지 않았다')
#   ★건드리지 말라고 한 두 자리가 그대로 있는지 센다★
for keep, why in (('두 쌍에서 양성자 수 요인이 서로 반대로 작용한다',
                   "M02248 ① 의 '두 쌍에서' 한정어가 사라졌다"),
                  ('수소와 플루오린은 번호 차가 ★여덟★인데 같은 족이 아니고',
                   'M02251 ④ 의 H–F 앵커가 사라졌다'),
                  ('전자를 잃은 만큼 알갱이의 무게가 줄어들기 때문',
                   'M02252 ④ 가 바뀌었다 — 자문 판정에 따라 그대로 두기로 했다')):
    if keep not in flat:
        bad.append(why)

if bad:
    print('  ❌ 불변 검사 실패')
    for b in bad:
        print('     ·', b)
    raise SystemExit(1)
print('  ✅ 불변 검사 통과')
