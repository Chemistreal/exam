# -*- coding: utf-8 -*-
"""T14 P9 5차 조치 — 단평은 단독으로 회수되는 줄이라 그 줄만으로 규칙이 되지 않아야 한다.

5차 보고. factchecker ★✗ 0 · △ 1★(1차 ✗4△12 → 2차 ✗0△5 → 3차 ✗1△3 → 4차 ✗0△1 →
5차 ✗0△1). 다른 셋은 이미 0 이다. 이번 조치는 ★단평 한 줄★ 뿐이다.

★① 단평은 단독으로 회수되는 줄이라 그 줄만으로 규칙이 되지 않는지 따로 센다.★
  4차에 M02220 ② 단평을 '두 칸만 벌어져도 오히려 작기도 해.' 로 적었다. 해설 본문과
  나란히 읽으면 맞지만, ★단평은 학생에게 그 한 줄만 돌아가는 자리★ 다. 떼어 놓으면
  ㉠ ★주어가 없고★('무엇이' 작은지 — 껍질이 더 많은 쪽이라는 말이 빠졌다)
  ㉡ '두 칸' 의 단위가 없어 ★'두 칸 벌어지면 껍질이 진다' 는 새 규칙★ 으로 읽힌다.
  실제로는 같은 두 칸에서 Be–Si 는 껍질이 이기므로 ★규칙으로 읽히면 거짓★ 이다.
  ㉢ 해설 본문은 ②③ 이 모두 '리튬과 알루미늄' 으로 쌍을 부르는데 ★단평에서는 ③ 만
     그 이름을 부른다★ — 4차에 내가 맞추려 한 바로 그 맞물림이 단평에서는 안 맞았다.
  ▸ '리튬과 알루미늄처럼 껍질이 더 많은 쪽이 오히려 작기도 해.' 로 간다(factchecker 안).
    한 줄로 ㉠㉡㉢ 이 함께 닫힌다 — 주어가 돌아오고, 두 칸이 규칙으로 굳지 않으며,
    ②③ 단평이 같은 쌍을 같은 이름으로 부른다.

★② 되묻기가 값을 했다 — 검증자가 자기 문면의 잘못을 확인했다.★
  4차에 factchecker 가 해설 쪽에 '두 칸 ★넘게★', 단평 쪽에 '두 칸★만★' 을 주어 둘이
  어긋났고, 나는 양쪽을 '두 칸만' 으로 맞추고 되물었다. 그가 답했다 — ★'두 칸 넘게' 로
  적으면 자신이 든 유일한 반례가 문장이 말하는 범위 밖으로 빠져 문장이 자기 근거를
  잃는다★ 며 자기 실수임을 확인하고 내 판단이 옳다고 적었다. 아울러 교육과정 범위 안의
  한 칸 대각 쌍 일곱(Li→Mg · Be→Al · B→Si · C→P · N→S · O→Cl · Na→Ca)이 ★모두 껍질
  쪽 승리★ 라 '확실한' 이라는 단어도 성립한다고 검산해 주었다.

이번 조치도 ★선지 문면을 하나도 건드리지 않는다★ — solver·defender·sim 의 입력은
바뀌지 않으므로 6차도 factchecker 만 돈다.
"""
import re

P = 'build_t14_p9.py'
src = open(P, encoding='utf-8').read()

CHOICES_RE = re.compile(r"\['(.+?)'\], (\d)", re.S)
BEFORE = CHOICES_RE.findall(src)
assert len(BEFORE) == 10
CH_BEFORE = [re.findall(r"'([^']+)'", f"'{b}'") for b, _ in BEFORE]
ANS_BEFORE = [a for _, a in BEFORE]


def sub(old, new, n=1):
    global src
    c = src.count(old)
    assert c == n, f'{c}곳(기대 {n}): {old[:56]!r}'
    src = src.replace(old, new)


# ══ M02220 ② 단평 ── 주어를 되돌리고 쌍을 이름으로 부른다 ═══════════════════
sub("': '두 칸만 벌어져도 오히려 '", "': '리튬과 알루미늄처럼 껍질이 더 많은 쪽이 오히려 '")

open(P, 'w', encoding='utf-8').write(src)


# ── ★기계로 센다★ ─────────────────────────────────────────────────────────────
body = '\n'.join(l for l in src.split('\n') if not l.strip().startswith('#'))
body = body[body.index('def build('):]
flat = re.sub(r"'\s*\n\s*'", '', body)

assert not re.search(r'[가-힣]★\s(를|을|은|의|으로|로|에서|에|과|보다|처럼|까지|부터'
                     r'|이고|이다|이야|이라|이지|인|야|다)(?=[\s,.·)?!\'"])', flat), \
    '★ 뒤에서 조사를 뗐다'
assert not re.search(r'[가-힣]\s(를|을|로)(?=[\s,.·)?!])', flat), '조사를 앞말에서 뗐다'
assert not re.search(r'\d+\s*pm', flat), '이 배치는 pm 값을 싣지 않는다'

AFTER = CHOICES_RE.findall(src)
assert len(AFTER) == 10
assert [a for _, a in AFTER] == ANS_BEFORE, '정답 자리가 바뀌었다'
CH = [re.findall(r"'([^']+)'", f"'{blk}'") for blk, _ in AFTER]
assert CH == CH_BEFORE, '선지 문면이 바뀌었다 — 이번 조치는 단평 한 줄이다'

# ★단평 둘이 같은 쌍을 같은 이름으로 부르는가★ — M02220 ②③
s20 = flat[flat.index("T.mk('M02220'"):flat.index("T.mk('M02221'")]
assert s20.count('리튬과 알루미늄') == 4, 'M02220 의 ②③ 단평이 쌍을 맞물지 않는다'

# ★그 한 줄만으로 규칙이 되지 않는가★ — 단평에서 '두 칸' 이 사라져야 한다
wm = s20[s20.index("{'같은 쪽을 가리키는"):]
assert '두 칸' not in wm, '단평에 두 칸이 규칙으로 남았다'
assert '껍질이 더 많은 쪽이' in wm, '단평의 주어가 돌아오지 않았다'

print('fix_t14_p9_r5 적용 완료 — 선지 문면 불변, M02220 ② 단평 한 줄')
