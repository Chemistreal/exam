# -*- coding: utf-8 -*-
"""T13 P7 (M02031~M02040) 층5 4차 조치 — 죽은 선지를 살리려다 연 문 하나와 교차 사슬 하나.

3차 순회: solver 마감 불가(보통 2) · defender ★마감 불가(변호 성공 1건)★ ·
factchecker 마감 가능(★확정 사실 오류 0★) · student-sim 마감 가능(A 0 / B 0 / C 7 / D 10 ·
★C·D 분기 2 → 3 문항으로 복원★ · 네 선지 모두 득표한 문항이 처음 나왔다)

★세 검증자가 한 자리로 모였다 — M02032 ③★
  3차 조치에서 죽은 선지를 살리려고 앞절을 참으로 바꿨다('크기는 그대로' → '커지지만').
  그런데 그 순간 ★뒷절의 지시 대상이 풀렸다.★ '개수' 가 무엇의 개수인지 문장이
  정하지 않으므로, 독자가 껍질 전체의 오비탈 수(n² = 1, 4, 9)로 옮겨 읽으면 ★참이
  된다.★ defender 가 변호 성공으로 확정했고 solver·sim 도 같은 자리를 짚었다.
  ▸ defender 의 진단이 가장 날카롭다 — ★"개별 오비탈 하나에는 '개수' 가 없다.
    문장이 뜻을 가지려면 독자가 지시 대상을 옮겨야 하고, 옮기는 순간 참이 된다."★
  ▸ 형제 선지와의 비대칭도 짚었다 — ② 는 떼어 읽어도 거짓, ④ 는 '둘에서 넷으로' 라는
    ★숫자가 지시 대상을 고정★ 해 거짓인데, ③ 만 숫자 없이 열려 있었다.
  ▸ 위험 방향이 나쁘다 — ★n² 을 아는 우수한 학생일수록 ③ 을 참으로 읽는다.★
  → defender 안 A 를 받는다. ③ → '오비탈이 커지지만 개수도 하나에서 셋으로 는다'.
    ▸ ★고치다가 또 하나 열 뻔했다★ — defender 문안 그대로('커지는 만큼')를 넣었더니
      ① 만 완화형('…지만')으로 남아 ★3차에 넣어 둔 '완화 표현이 정답에만' 검사가
      곧바로 걸렸다.★ '커지지만' 으로 어미만 되돌려 어조 2 : 2 를 지켰다.
      검사를 코드로 넣어 두지 않았으면 그대로 나갔을 자리다.
    ④ 와 형식이 나란해지고 숫자가 지시 대상을 못 박아 ★어느 독법에서도 거짓★ 이다
    (s 로 읽으면 1·1·1, 껍질로 읽으면 1·4·9 — 둘 다 '하나에서 셋' 이 아니다).
    목표 오개념('커지면 개수도 는다')은 그대로 보존된다.
  ▸ ★이번이 세 번째다 — 조치가 새 결함을 낳은 것이.★ P5 는 2차 조치가 더 강한 F5 를
    낳았고, P7 은 2차가 사실 오류 둘을, 3차가 이 복수 정답 소지를 낳았다.
    ★죽은 선지를 살리려 절을 손댈 때는 그 절의 지시 대상이 열리는지 먼저 볼 것.★

받은 것 다섯
──────────────────────────────────────────────────────────────────────────
1. ★M02032 ③ — 위 참조 (defender 변호 성공 · solver 보통 · sim 최우선)★
2. ★M02031 ④ → M02037 교차 사슬 (solver 보통)★
   M02037 은 ① '3d 오비탈은 없다' 와 ② '4s 오비탈은 있다' 가 ★빈 오비탈의 실재★ 라는
   한 축에서 모순이라 시험요령만으로 2지선다가 된다. 그런데 ★M02031 ④ (3, 2, −2)가
   '가능한 조합' 으로 제시되어 3d 의 실재를 확인해 준다★ → ① 탈락 → ②.
   아르곤 지식 없이 옆 문항만으로 도달한다.
   → ④ 를 ★(3, 1, −1)★ 로. d 가 사라져 사슬이 끊기고, 덤으로 정답 (3, 1, +2)와
     ★n·l 이 같고 mₗ 만 다른 짝★ 이 되어 대비가 날카로워진다. 오답 경로(음수 배제 ·
     끝값 배제)도 그대로다.
   ▸ M02037 ①② 모순쌍 자체는 그대로 둔다 — P6 M02027 에서 세운 선례대로 ★남은 둘을
     가르는 일이 곧 이 문항이 묻는 것★ 이고, defender 도 "마감을 막지 않는다" 로 적었다.
3. ★M02033 ② 해설의 부정확한 한 마디 (factchecker △A)★
   "두 조건을 다 만족하는 것처럼 보이지만" — 2d¹¹ 은 두 조건 가운데 ★초과 조건 하나만★
   만족한다. → '위첨자만 보면 조건에 맞는 것처럼 보이지만' 으로.
4. ★M02038 ④ 반박이 절반만 짚는다 (factchecker △B)★
   4f 가 6주기라는 것만 말하고 ★이 선지가 4p 를 빠뜨렸다는 점★ 은 짚지 않는다.
   → 한 마디를 붙여 완결한다.
5. ★M02039 ② 해설의 '비워 둔' (factchecker △C)★ — 2차에 M02034 에서 고친 것과 같은
   어감이 남아 있다. → '비어 있는 자리는' 으로 통일한다.

반려한 것 여섯 (근거를 남긴다)
──────────────────────────────────────────────────────────────────────────
 · ★M02032 ④ 의 '넷' → '여덟' (sim)★ — ★반려. defender 의 분석이 이 안을 무너뜨린다.★
   defender 는 ④ 가 닫혀 있는 까닭을 "어떤 오비탈도 정원이 4 가 아니고, ★껍질 정원으로
   읽어도 2 → 8★ 이라 '둘에서 넷으로' 가 거짓" 으로 적었다. 곧 '여덟' 으로 바꾸면
   ★껍질 정원 독법에서 2 → 8 이 참이 되어★ ④ 가 방어된다. sim 이 노린 2n²·옥텟 공명이
   바로 그 참 독법의 통로다. ★두 검증자의 지적을 교차해 보지 않았으면 그대로 넣을
   뻔했다.★
 · ★M02031 ② → (4, 3, −3) (sim)★ — 반려. f 오비탈은 defender 가 1차에 범위 리스크로
   짚어 걷어낸 자리다. 되돌릴 수 없다.
   ▸ M02031 은 ①② 가 둘 다 무득표로 남는다(sim 이 이번 회차 최다로 지목). ★구조적
     제약을 적어 둔다★ — d 와 f 를 뺀 유효 조합은 (n, 0, 0)과 (n, 1, mₗ) 뿐이고, 살아
     있는 오독 경로(음수 배제 · 끝값 배제 · 범위를 n 으로)가 모두 ③④ 에 몰린다.
     ①② 는 "완전히 합법인 대조군" 이라 이 각도에 반드시 필요하다. ★다음 개정에서
     M02037 을 다시 짜면 그때 d 조합을 되살릴 것.★
 · ★M02040 ①② 가 같은 패리티 논거로 죽는다 (solver 경미~보통)★ — 반려. 지적은
   맞으나 solver 가 낸 대안('홀전자가 반드시 하나뿐이다')은 ★자신이 1차에 잡은 포함
   관계★ 를 그대로 되살린다(참이면 1 은 홀수라 정답을 함의한다). 이 각도의 핵심이
   패리티 하나이므로 홀전자 수의 홀짝을 말하는 오답은 모두 그 하나로 죽는다 —
   M02033 의 l < n 과 같은 구조적 불가피다. ③ 이 다른 축(경계 사례)을 맡고 있다.
 · ★M02037 ① 을 모순쌍에서 빼기 (solver · defender 비차단 메모)★ — 반려.
   ① 은 sim 실측에서 ★B 의 착지점★ 이다('전자 없으면 오비탈도 없다'). 살아 있는
   착지점을 표면 단서와 맞바꾸지 않는다. 교차 사슬은 M02031 쪽에서 끊었다.
 · ★M02033 의 (없음·이내) 칸 메우기★ — ★defender 가 메우지 말라고 명시했다.★
   그 칸은 초과 검산에서 자동 탈락하는 죽은 칸이다(3f⁷ 이 죽어 있던 바로 그 까닭).
   현행 3 : 1 이 오히려 낫다 — "위첨자가 크다" 가 넷 중 셋에 해당해 ★표면 단서로서의
   값이 0 이 되고 판단이 존재 축(2 : 2)으로 강제된다.★
 · ★M02037 ④ 의 '전자가 둘 이상이면 서로 밀어내 준위가 갈라져' (factchecker △D)★ —
   반려. factchecker 스스로 범위 안이라 적었고, ★P6 M02030 이 같은 문면을 쓰면서
   교재 표준 문장으로 확인받은 자리★ 라 여기서만 바꾸면 은행 안에서 서술이 어긋난다.

★기록 — 검증자가 확인해 준 것★
 · defender: M02040 ③ 은 ★두 독법 모두에서 거짓★ 이다 — '짝지은 전자' 를 전자쌍 수로
   읽으면 리튬(1쌍 vs 홀전자 1, 초과 아님)·질소(2쌍 vs 3)가 반례로 늘어난다.
   ★경계 사례 하나에 기댄 선지를 안전하게 만드는 성질★ 이다.
 · factchecker: 전자 수가 홀수인 바닥상태 중성 원자를 H·Li·B·N·F·Na·P·Mn·Cu 까지 훑어
   ★반례가 수소 하나뿐★ 임을 확인했다(홀전자는 3d⁵·4f⁷ 로 상한이 있는데 짝지은 전자는
   원자 번호와 함께 급증한다).
 · defender: M02033 의 ② 를 2d¹¹ 로 바꾼 것이 ★① 의 존재 덕분에 이중으로 막힌다★ —
   "d 는 3d·4d 로 실재하니 '있다'" 는 느슨한 독법을 쓰면 ① 1p⁷ 도 같은 꼴로 함께
   참이 되어 ②를 단독으로 세우지 못한다.
 · sim: M02038 ④(스물여섯)는 무득표이나 ★나열 수·값 균형을 위한 의도된 채움 선지★ 로
   남기라고 판정했다. M02037 ④ 도 4인 표본의 한계로 보아 유지 권장.
"""
import json
import re
from collections import Counter

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']
IDS = ['M%05d' % n for n in range(2031, 2041)]
TOUCHED = {'M02031', 'M02032', 'M02033', 'M02038', 'M02039'}


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:40]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


bank = json.load(open(BANK, encoding='utf-8'))
D = {i['id']: i for i in bank}
before = {k: json.loads(json.dumps(D[k])) for k in IDS}

# ── 1. M02031 ④ — d 를 없애 교차 사슬을 끊는다 ────────────────────────────
it = D['M02031']
assert it['choices'][3] == '(3, 2, −2)', it['choices']
it['choices'][3] = '(3, 1, −1)'
for d in it['distractors']:
    if d['opt'] == 3:
        d['error'] = '음수 mₗ 이나 끝값 |mₗ| = l 은 빠진다고 봄 — 2p 의 mₗ 은 −1, 0, +1 이고 양 끝도 값이다'
sub(it, '(3, 2, −2)는 3d 라 mₗ 이 −2 부터 +2 까지인데 −2 는 그 양 끝의 하나지. '
        '끝값도 어엿한 값이야.',
        '(3, 1, −1)은 3p 라 mₗ 이 −1, 0, +1 인데 −1 은 그 양 끝의 하나지. '
        '음수도 끝값도 어엿한 값이야.')
sub(it, '④ (3, 2, −2): d 부껍질은 l 이 2 라 mₗ 이 −2 부터 +2 까지 다섯이야. −2 는 '
        '그 양 끝의 하나지 범위 밖이 아니야.',
        '④ (3, 1, −1): 정답과 n 도 l 도 같고 mₗ 만 달라. p 부껍질의 mₗ 은 −1, 0, +1 '
        '셋이니 −1 은 그 양 끝의 하나지 범위 밖이 아니야. 음수라는 것도, 끝값이라는 것도 '
        '배제할 까닭이 되지 못해.')

# ── 2. M02032 ③ — 숫자로 지시 대상을 못 박는다 ────────────────────────────
it = D['M02032']
assert it['choices'][2] == '오비탈이 커지지만 그만큼 개수도 함께 늘어난다', it['choices']
it['choices'][2] = '오비탈이 커지지만 개수도 하나에서 셋으로 는다'
for d in it['distractors']:
    if d['opt'] == 2:
        d['error'] = '껍질이 커지면 오비탈 개수도 는다고 봄 — s 부껍질의 오비탈은 어느 껍질에서나 하나다'
sub(it, '③ 오비탈이 커지지만 그만큼 개수도 함께 늘어난다: 커진다는 앞말은 맞아. 그런데 '
        's 부껍질의 오비탈은 어느 껍질에서나 하나뿐이야. 늘어나는 것은 껍질 전체의 오비탈 '
        '수(n²)지 s 오비탈의 개수가 아니지.',
        '③ 오비탈이 커지지만 개수도 하나에서 셋으로 는다: 커진다는 앞말은 맞아. 그런데 '
        's 부껍질의 오비탈은 어느 껍질에서나 하나뿐이라 1s 도 2s 도 3s 도 하나씩이야. '
        '껍질 전체로 넓혀 보아도 오비탈 수는 n² 이라 1, 4, 9 로 늘지 셋으로 가지 않아.')

# ── 3. M02033 ② 해설 — 조건 하나만 만족한다 ───────────────────────────────
sub(D['M02033'], '두 조건을 다 만족하는 것처럼 보이지만 앞 조건에서 이미 걸려.',
                 '위첨자만 보면 조건에 맞는 것처럼 보이지만 앞 조건에서 이미 걸려.')

# ── 4. M02038 ④ 반박 — 4p 누락까지 짚는다 ─────────────────────────────────
sub(D['M02038'],
    '④ 4s·3d·4f 를 채우는 동안이라 스물여섯 개다: 4f 는 껍질 번호만 4 일 뿐 6주기에서 '
    '채워져. 껍질 번호로 주기를 가르면 안 돼 — 3d 가 4주기인 것이 바로 그 반례지.',
    '④ 4s·3d·4f 를 채우는 동안이라 스물여섯 개다: 4f 는 껍질 번호만 4 일 뿐 6주기에서 '
    '채워져. 껍질 번호로 주기를 가르면 안 돼 — 3d 가 4주기인 것이 바로 그 반례지. '
    '게다가 정작 4주기를 닫는 4p 가 빠졌어.')

# ── 5. M02039 ② 해설 — '비워 둔' 을 통일한다 ──────────────────────────────
sub(D['M02039'], '비워 둔 자리는 2p 오비탈 하나인데 셋은 에너지가 서로 같아.',
                 '비어 있는 자리는 2p 오비탈 하나인데 셋은 에너지가 서로 같아.')

# ── 검사 ──────────────────────────────────────────────────────────────────
items = [D[k] for k in IDS]
assert Counter(i['answer'] for i in items) == {2: 3, 0: 2, 3: 3, 1: 2}
for k in IDS:
    assert D[k]['answer'] == before[k]['answer'], (k, '정답 자리는 바뀌지 않는다')
    assert D[k]['stem'] == before[k]['stem'], (k, '발문은 건드리지 않는다')
for k in set(IDS) - TOUCHED:
    assert D[k] == before[k], k

for it in items:
    cs = it['choices']
    assert len(cs) == 4 and len(set(cs)) == 4, it['id']
    assert sorted(d['opt'] for d in it['distractors']) == sorted(set(range(4)) - {it['answer']}), it['id']
    assert len(it['solution']) >= 300, (it['id'], len(it['solution']))
    assert '★' not in it['stem'] and '★' not in it['solution'], it['id']
    assert it['objective'], it['id']
    L = sorted(len(c) for c in cs)
    a = len(cs[it['answer']])
    assert not (a == L[3] and L[2] < L[3]), (it['id'], 'G3 최장 단독', cs)
    assert not (a == L[0] and L[0] < L[1]), (it['id'], 'G3 최단 단독', cs)
    mid = (L[1] + L[2]) / 2
    if mid >= 8:
        assert (L[3] - L[0]) / mid <= 0.25, (it['id'], 'G3b', cs, L)
    assert '가 옳아' in it['solution'] or '이 옳아' in it['solution'], it['id']
    for k in range(4):
        assert MK[k] + ' ' + cs[k] in it['solution'], (it['id'], MK[k], cs[k])

# ── 앞 회차에 넣은 검사를 그대로 다시 돌린다 ──────────────────────────────
for x in items:
    ans = x['choices'][x['answer']]
    if len(ans) >= 6:
        for y in items:
            if y['id'] == x['id']:
                continue
            assert ans not in y['stem'], (x['id'], '정답이 발문에 노출', y['id'])
            assert ans not in ' '.join(y['choices']), (x['id'], '정답이 선지에 노출', y['id'])

NUMW = {'여덟': 8, '열': 10, '열두': 12, '열둘': 12, '열넷': 14, '열여섯': 16,
        '열여덟': 18, '스물여섯': 26, '서른둘': 32}


def vals(it):
    out = []
    for c in it['choices']:
        m = re.fullmatch(r'\s*(\d+)\s*개?\s*', c)
        if m:
            out.append(int(m.group(1)))
            continue
        hit = [v for w, v in NUMW.items() if w + ' 개' in c]
        out.append(max(hit) if hit else None)
    return out


REL = [('2의 거듭제곱', lambda v: v > 0 and (v & (v - 1)) == 0),
       ('4의 배수', lambda v: v % 4 == 0),
       ('홀수', lambda v: v % 2 == 1)]
for it in items:
    v = vals(it)
    if any(x is None for x in v) or len(set(v)) < 4:
        continue
    for name, f in REL:
        ok = [i for i in range(4) if f(v[i])]
        if len(ok) == 3 and it['answer'] not in ok:
            raise AssertionError(f"{it['id']}: 「{name}」 을 어기는 선지가 정답 하나뿐 {v}")
        if len(ok) == 1 and it['answer'] in ok:
            raise AssertionError(f"{it['id']}: 「{name}」 을 만족하는 선지가 정답 하나뿐 {v}")
    if not all(re.fullmatch(r'\s*\d+\s*개?\s*', c) for c in it['choices']):
        assert v[it['answer']] not in (max(v), min(v)), (it['id'], '정답이 최대 또는 최소', v)

NEG = ('않', '없', '아니', '못')
for it in items:
    neg = [i for i in range(4) if any(t in it['choices'][i] for t in NEG)]
    if len(neg) == 1:
        assert neg[0] != it['answer'], (it['id'], '정답만 부정형', it['choices'])
    if len(neg) == 3:
        pos = (set(range(4)) - set(neg)).pop()
        assert pos != it['answer'], (it['id'], '정답만 긍정형', it['choices'])

for it in items:
    for w in ('홀수', '짝수'):
        if w in it['stem']:
            hit = [i for i in range(4) if w in it['choices'][i]]
            assert hit != [it['answer']], (it['id'], f'어휘 메아리 {w}', it['choices'])

HEDGE = ('지만', '어도', '으나', '다만', '뿐')
for it in items:
    hg = [i for i in range(4) if any(t in it['choices'][i] for t in HEDGE)]
    if len(hg) == 1:
        assert hg[0] != it['answer'], (it['id'], '완화 표현이 정답에만', it['choices'])

for it in items:
    cnt = [len(re.findall(r'[1-9][spdf]', c)) for c in it['choices']]
    if max(cnt) >= 2 and cnt.count(max(cnt)) == 1:
        assert cnt.index(max(cnt)) != it['answer'], (it['id'], '정답만 최다 나열', cnt)

# ── ★새 검사 — 지시 대상이 열린 수식어가 정답 아닌 자리에만 있는가★ ────────
#   3차 조치가 만든 결함의 무늬 — '그만큼 개수도' 처럼 ★무엇의 개수인지 문장이 정하지
#   않으면★ 독자가 지시 대상을 옮겨 참으로 읽을 수 있다. 수를 밝히거나 대상을 밝힌
#   선지에는 그 여지가 없다. 선지에 '개수·정원·수' 가 나오면 ★그 앞에 대상이나 값이
#   붙어 있는지★ 를 본다.
OPEN = re.compile(r'(그만큼|함께)\s*(개수|정원|수)')
for it in items:
    for i, c in enumerate(it['choices']):
        assert not OPEN.search(c), (it['id'], MK[i], '지시 대상이 열린 수량어', c)

# ── 문항 전용 ─────────────────────────────────────────────────────────────
assert not any('2' in c and 'd' in c for c in D['M02031']['choices']), D['M02031']['choices']
assert D['M02031']['choices'] == ['(2, 1, 0)', '(4, 0, 0)', '(3, 1, +2)', '(3, 1, −1)']
# 정답과 ④ 가 n·l 을 공유하고 mₗ 만 다른가
q = [tuple(c.strip('()').split(', ')) for c in D['M02031']['choices']]
assert q[2][:2] == q[3][:2] and q[2][2] != q[3][2]
# M02032 ③ 이 어느 독법에서도 거짓인가 — s 는 1·1·1, 껍질은 1·4·9
assert '하나에서 셋으로' in D['M02032']['choices'][2]
assert [1, 1, 1] != [1, 3] and [1, 4, 9][:3] != [1, 2, 3]
assert '2 → 8' not in D['M02032']['choices'][3] and '여덟' not in D['M02032']['choices'][3]
assert '위첨자만 보면' in D['M02033']['solution']
assert '4주기를 닫는 4p 가 빠졌어' in D['M02038']['solution']
assert '비워 둔' not in D['M02039']['solution']

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P7 4차 조치 완료 — 5 문항')
print('  M02031', D['M02031']['choices'], '(d 제거 · 정답과 n·l 공유)')
print('  M02032 ③', D['M02032']['choices'][2])
print('  M02032 ④ 그대로 —', D['M02032']['choices'][3], "('여덟' 으로 바꾸면 껍질 정원 독법에서 참이 된다)")
