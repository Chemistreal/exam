# -*- coding: utf-8 -*-
"""T13 P7 (M02031~M02040) 층5 6차 조치 — 마감 조치. 네 검증자 전원 마감 가능.

5차 순회
  · solver      ★마감 가능 · F1 0건★ (열 문항 모두 정답이 정확히 하나)
  · defender    ★마감 가능★ — M02032 ③ 을 ★지시 대상표 8행★ 으로 재검산해 전부 거짓 확인.
                변호 성공 1건뿐이고 심각도 낮음/비차단(M02039 ②).
  · factchecker ★마감 가능 · 확정 사실 오류 0건★ · △ 여섯
  · student-sim ★마감 가능★ — D 전항 정답 · ★C·D 분기 3 → 4 문항★ · 죽은 선지 6

★P5·P6 선례대로 마감한다★ — 세 검증자가 동시에 0건이면, 남은 다듬기를 마지막 조치로
받아 넣고 또 한 바퀴 돌리지 않는다. 이 배치는 ★조치가 새 결함을 낳은 것이 네 번★ 이라
그 선례가 더욱 무겁다. 그래서 이번 조치는 ★차단 아닌 것 가운데 값이 확실한 것만★ 받는다.

받은 것 여섯
──────────────────────────────────────────────────────────────────────────
1. ★M02037 발문이 다른 두 문항의 열쇠를 인쇄한다 (solver F5 [고] 2건)★
   발문에 아르곤 배치를 `1s² 2s² 2p⁶ 3s² 3p⁶` 으로 통째로 찍어 두었다.
   ▸ M02033 → 그 `3p⁶` 이 ★3p 의 실재와 정원 6 을 동시에 알려 준다.★ 그러면 ③ 3p⁵
     (이내)과 ④ 3p⁷(초과)이 지식 없이 갈리고, ①1p·②2d 는 그 배치에 아예 없으니
     '실재' 조건에서 탈락 → ④ 확정.
   ▸ M02034 → 같은 문자열이 ★3s 를 둘까지 채운 뒤 3p 로 간다★ 는 차례를 그대로 보여
     준다. 접두가 일치하는 것은 ② 뿐이다.
   → 발문에서 ★완전 표기를 걷어내고 말로 서술한다★ — "3p 부껍질까지 전자가 모두 차
     있다". 3p 가 찼다는 것은 남되 ★그 수가 6 이라는 것은 스스로 세야★ 한다(2(2l+1)).
     M02034 로 가는 접두 일치도 사라진다.
   ▸ ★조판 순서로는 막히지 않는다★ (solver) — 뒤에 두어도 시험지는 전체가 동시에
     보인다. 문면을 고치는 수밖에 없다. P6 에서 배운 ㉳ 와 같은 무늬인데, 그때는
     ★정답 문자열★ 이 새어 나갔고 이번에는 ★판정 근거★ 가 새어 나갔다.
2. ★M02039 ② — 쌓음원리의 넓은 정의를 끌어오면 참이 된다 (defender 낮음/비차단)★
   교과서 정의는 "낮은 오비탈부터 차례로" 지만, 문제집 어법 가운데 "바닥상태는 에너지가
   가장 낮은 배치" 로 넓게 적는 것이 있다. ★그 독법에서는 이 들뜬 배치가 쌓음원리 위반★
   이 되어 ① 과 함께 참이 된다.
   → defender 수정안을 받되 ★어미를 지켜서★ 넣는다 —
     '쌓음원리를 어겨 ★낮은 자리를 건너뛰었지만★ 존재하는 배치다'.
     건너뛴 낮은 자리가 실제로 없으므로(1s·2s 는 모두 찼고 2p 셋은 등에너지)
     ★넓은 독법에서도 명백히 거짓★ 이다.
   ▸ ★defender 문안 그대로는 넣을 수 없다.★ '…건너뛴 배치다' 로 끝내면 완화 어미가
     ① 에만 남아 ★3차에 넣어 둔 '완화 표현이 정답에만' 검사가 걸린다.★ 4차에 똑같은
     자리에서 걸렸던 것이 이번에도 그대로 재현됐다 — ★검증자 문안은 어조까지 그대로
     받으면 안 된다.★
   ▸ 덤이 있다 — sim 이 ② 를 죽은 선지로 꼽았는데, '빈 오비탈을 남겼으니 건너뛴 것'
     이라는 실제 오독을 정면으로 겨누게 되어 ★죽은 선지 하나가 살아난다.★
3. ★M02032 ③ 해설 — 두 수를 이름과 함께 못 박는다 (factchecker △1·△2·△3)★
   '부껍질의 종류' 와 'n²' 가 한 문장에 나란히 놓여 ★n² 를 부껍질 종류 수로 붙여 읽을
   여지★ 가 있었다. 종류는 n 가지, 오비탈은 n² 개로 각각 이름을 달고, n² 가 1+3+5+…
   에서 나온다는 근거를 붙이고, ④ 의 2n² 과 두 배로 이어 준다.
4. ★M02038 ④ 해설 — f 정원 14 를 밝힌다 (factchecker △4)★ 스물여섯이 2+10+14 에서
   나오는데 14 가 본문에 없어 숫자 검증이 학생 몫으로 남았다.
5. ★M02034 ③ 해설 — 어긴 규칙의 이름을 단다 (factchecker △5)★ 같은 배치에 규칙 분류
   각도(M02039)가 들어 있으므로 두 해설의 어휘가 맞물려야 한다.
6. ★M02033 ① 해설 — 가정 표지를 넣는다 (factchecker △6)★ "위첨자가 일곱이라 여섯을
   넘은 것은 맞아" 는 ★없는 1p 에 p 정원 6 을 이미 가정★ 한 서술이다. '설령 있다
   치더라도' 를 붙이면 두 잣대를 따로 보라는 의도가 살아난다.

반려한 것 아홉 (근거를 남긴다)
──────────────────────────────────────────────────────────────────────────
 · ★defender 의 문체 지적 — '커지지만 … 도 는다' 를 '커지는 데다' 로★ — ★반려.★
   판정에는 영향이 없다고 스스로 적었고, 바꾸면 ★① 만 완화 어미를 갖게 되어 검사가
   걸린다.★ 이 배치에서 어조 균형 때문에 문안을 되돌린 것이 이번이 세 번째다.
 · ★sim — M02031 ① 을 (2, 2, 0)으로★ — 반려. ★l < n 은 금지 축이다★(P3). l ≥ n 인
   조합은 두 까닭으로 함께 지워져 이 각도가 재려는 것(mₗ 을 묶는 것은 l)을 흐린다.
 · ★sim — M02033 ③ 을 3d¹⁰ 으로★ — 반려. 같은 칸(실재·이내)의 값만 바꾸는 안인데,
   3d¹⁰ 은 아연이라 ★전이금속(심화)★ 이고, 3p⁵ = 염소는 2차에 사실 오류까지 치르고
   확정한 자리다. 다음 개정 후보로 적는다.
 · ★sim — M02034 ④ 를 3s³ 으로★ — 반려. ★같은 배치 안의 M02033 이 바로 '위첨자 정원
   초과' 각도★ 다. 문항 사이 겹침이 생기고, 이 각도가 재는 것(채움 차례)이 파울리
   위반 판정으로 바뀐다.
 · ★sim — M02035 를 C·N·O·F 로 재편★ — 반려(이번 회차 기준). 제안 자체는 좋다
   ('점유 칸 수 = 홀전자 수' 오류를 ④ 가 흡수한다). 그러나 ★네 선지와 해설을 통째로
   다시 쓰는 일★ 이고, 이 배치는 조치가 결함을 낳은 것이 네 번이다. ★마감 조치에서
   가장 큰 수술을 하지 않는다.★ 4차에 이어 다음 개정 후보로 옮긴다.
 · ★sim — M02038 ④ 를 '서른둘(2n²)' 로★ — ★반려. 검사로 확인했다.★ 8·12·18·32 가
   되면 ★8·12·32 가 모두 4 의 배수라 18 만 어긋나 정답이 이상치로 지워진다.★
   1차에 8·16·32 에서 같은 무늬로 뚫렸던 자리이고, 그때 12 를 후보에서 뺀 까닭도
   똑같았다. ★관계식은 하나만 보면 안 된다★ 는 규약이 정확히 이 안을 막는다.
 · ★sim — M02039 ② 를 '들뜬상태이므로 훈트는 적용되지 않는다' 로★ — 반려.
   ★그 문장은 참으로 읽힐 길이 있다★ — 훈트 규칙은 바닥상태의 배치를 정하는 규칙이니
   "들뜬 배치에는 적용 대상이 아니다" 는 독법이 선다(defender 경로 가). 죽은 선지를
   살리려다 ★복수 정답을 여는 것★ 이 이 배치에서 두 번 있었다. 대신 위 2 로 살린다.
 · ★sim — M02040 ② 를 '홀전자가 반드시 하나뿐이다' 로★ — 반려. ★세 번째 같은 제안★
   이다(1차 solver·4차 solver·5차 sim). 참이면 1 은 홀수라 ★정답을 함의하는 포함
   관계★ 가 된다. 대장에 못 박아 둔다.
 · ★solver [저] 셋★ — 모두 반려. (ㄱ) M02032 정답이 불변 진술을 말한다 → 네 선지가
   모두 같은 두 절 구조라 표면 단서가 되지 않는다(4차에 이미 반려). (ㄴ) M02040 ③ 의
   반례가 수소뿐 → factchecker 가 H·Li·B·N·F·Na·P·Mn·Cu 까지 훑어 확인했고 발문의
   '반드시' 가 전칭을 못 박는다(defender). (ㄷ) M02033 ② 의 이중 결함 → defender 가
   ★① 덕분에 이중으로 막힌다★ 고 확인한 자리다.

★기록 — 검증자가 확인해 준 것★
 · defender 지시 대상표 8행: s 오비탈 수(1·1·1) · 껍질 총 오비탈(1·4·9) · 부껍질 수
   (1·2·3) · 누적 s(1·2·3) · 원자 전체 s · 방사 마디(0·1·2) · s 부껍질 오비탈(1·1·1) ·
   오비탈 정원(2·2·2) → ★전부 거짓.★ 한정어 's' 와 '속' 이 각각을 막는다.
 · defender: M02032 ④ 도 재검산 — '둘에서 넷' 은 어느 독법에서도 거짓. ★구체 수치가
   방어를 봉쇄한다★ (③ 은 반대로 수치가 우연히 맞아 뚫렸던 자리다. 같은 도구가 한쪽
   에서는 자물쇠, 다른 쪽에서는 열쇠였다).
 · defender: M02036 의 괄호 '(홀전자의 mₛ 는 모두 +1/2 로 본다.)' 가 ★7·8·9 를 모두
   살릴 뻔한 자리를 봉쇄한다.★ 괄호가 없었으면 셋 다 참이 되는 독법이 있었다.
 · defender: M02037 ③ 은 ★스핀오비탈 독법(18)에서만 참★ 인데 그것은 범위 밖이다.
 · sim: M02040 발문의 '2 로 나누어떨어지지 않는다' 를 ★'홀수' 로 되돌리지 말 것★ —
   A 프로필이 낱말 매칭만으로 정답에 닿는다. (1차에 일부러 바꿔 둔 자리다.)
 · sim: 교체된 M02032 ③ 이 ★C 를 새로 끌어당겼다★ — C·D 분기가 3 에서 4 로 늘었다.
   ★죽은 선지를 살리는 정공법은 매력을 지어내는 것이 아니라 참에 아슬하게 붙이는 것★
   이라는 것을 실측이 보여 준 셈이다(다만 참이 되어서는 안 된다).
"""
import json
import re
from collections import Counter

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']
IDS = ['M%05d' % n for n in range(2031, 2041)]
TOUCHED = {'M02032', 'M02033', 'M02034', 'M02037', 'M02038', 'M02039'}
STEM_TOUCHED = {'M02037'}


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:40]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


bank = json.load(open(BANK, encoding='utf-8'))
D = {i['id']: i for i in bank}
before = {k: json.loads(json.dumps(D[k])) for k in IDS}

# ── 1. M02037 발문 — 완전 표기를 걷어낸다 ─────────────────────────────────
it = D['M02037']
assert it['stem'] == ('아르곤(Ar, 원자 번호 18)의 바닥상태는 1s² 2s² 2p⁶ 3s² 3p⁶ 이다. '
                      '이 원자에 대한 설명으로 옳은 것은?'), it['stem']
it['stem'] = ('아르곤(Ar, 원자 번호 18)의 바닥상태에서는 3p 부껍질까지 전자가 모두 차 있다. '
              '이 원자에 대한 설명으로 옳은 것은?')

# ── 2. M02039 ② — 넓은 독법을 닫고 죽은 선지를 살린다 ────────────────────
it = D['M02039']
assert it['choices'][1] == '쌓음원리를 어겼지만 존재할 수는 있는 배치다', it['choices']
it['choices'][1] = '쌓음원리를 어겨 낮은 자리를 건너뛰었지만 존재하는 배치다'
for d in it['distractors']:
    if d['opt'] == 1:
        d['error'] = ('빈 오비탈을 남긴 것을 낮은 자리를 건너뛴 것으로 봄 — 2p 세 오비탈은 '
                      '에너지가 같아 건너뛸 낮은 자리가 없다')
sub(it, '② 쌓음원리를 어겼지만 존재할 수는 있는 배치다: 비어 있는 자리는 2p 오비탈 '
        '하나인데 셋은 에너지가 서로 같아. 높낮이가 없으니 쌓음원리로는 가릴 수 없지. '
        '존재한다는 뒷말은 맞지만 앞말이 틀렸어.',
        '② 쌓음원리를 어겨 낮은 자리를 건너뛰었지만 존재하는 배치다: 비어 있는 자리는 '
        '2p 오비탈 하나인데 셋은 에너지가 서로 같아. 높낮이가 없으니 건너뛸 만큼 낮은 '
        '자리가 애초에 없었지. 1s 와 2s 도 모두 찼고. 존재한다는 뒷말은 맞지만 앞말이 '
        '틀렸어.')

# ── 3. M02032 ③ 해설 — 두 수에 각각 이름을 단다 ──────────────────────────
sub(D['M02032'],
    '껍질이 커질 때 늘어나는 것은 부껍질의 종류(1껍질은 s, 2껍질은 s·p, 3껍질은 s·p·d)와 '
    '껍질 전체의 오비탈 수(n²)지 s 오비탈의 수가 아니야. 무엇이 늘어나는지를 이름까지 '
    '붙여 말해 보면 이 헷갈림이 풀려.',
    '껍질이 커질 때 늘어나는 것은 따로 있어. 하나는 부껍질의 종류로 n 껍질에 n 가지야'
    '(1껍질은 s, 2껍질은 s·p, 3껍질은 s·p·d). 다른 하나는 껍질 전체의 오비탈 수인데 '
    '부껍질마다 2l+1 개씩이라 1 + 3 + 5 + … 를 더해 n² 개가 되지. 종류는 n 가지, '
    '오비탈은 n² 개 — 이름을 달아 두면 섞이지 않아. 그 n² 에 둘을 곱한 2n² 이 아래 '
    '④에서 말하는 껍질 정원이고. 어느 쪽도 s 오비탈의 수는 아니야.')

# ── 4. M02038 ④ 해설 — f 정원 14 를 밝힌다 ───────────────────────────────
sub(D['M02038'], '게다가 정작 4주기를 닫는 4p 가 빠졌어.',
                 '게다가 정작 4주기를 닫는 4p 가 빠졌어. f 부껍질의 정원이 열넷이라 '
                 '2 + 10 + 14 로 스물여섯이 나온 셈인데, 더한 자리들이 한 주기에 모여 '
                 '있지를 않아.')

# ── 5. M02034 ③ 해설 — 어긴 규칙의 이름을 단다 ───────────────────────────
sub(D['M02034'], '더 낮은 3s 에 빈자리를 남긴 채 3p 를 채웠으니 바닥상태가 아니라 들뜬 상태지.',
                 '더 낮은 3s 에 빈자리를 남긴 채 3p 를 채웠으니 바닥상태가 아니라 들뜬 '
                 '상태지. 낮은 자리부터 채우라는 쌓음원리를 어긴 거야.')

# ── 6. M02033 ① 해설 — 가정 표지를 넣는다 ────────────────────────────────
sub(D['M02033'], '① 1p⁷: 위첨자가 일곱이라 여섯을 넘은 것은 맞아.',
                 '① 1p⁷: 설령 1p 가 있다 치더라도 위첨자가 일곱이라 p 의 정원 여섯을 '
                 '넘긴 셈이야.')

# ── 검사 ──────────────────────────────────────────────────────────────────
items = [D[k] for k in IDS]
assert Counter(i['answer'] for i in items) == {2: 3, 0: 2, 3: 3, 1: 2}
for k in IDS:
    assert D[k]['answer'] == before[k]['answer'], (k, '정답 자리는 바뀌지 않는다')
    if k not in STEM_TOUCHED:
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

OPEN = re.compile(r'(그만큼|함께)\s*(개수|정원|수)')
for it in items:
    for i, c in enumerate(it['choices']):
        assert not OPEN.search(c), (it['id'], MK[i], '지시 대상이 열린 수량어', c)

QTY = re.compile(r'(개수|정원|(?:^|(?<=[ ]))수(?:도|가|는|를))')


def _qty_hits(c):
    out = []
    for m in QTY.finditer(c):
        if m.group().startswith('수') and m.start() >= 2:
            prev = c[m.start() - 2]
            if '가' <= prev <= '힣' and (ord(prev) - 0xAC00) % 28 == 8:
                continue
        out.append(m.group())
    return out


SCOPE = ('한 껍질 속', '껍질 전체', '오비탈 하나', '한 부껍질', '한 오비탈',
         's 오비탈', 'p 오비탈', 'd 오비탈', '홀전자', '부껍질', '전자')
VALW = tuple('하나 둘 셋 넷 다섯 여섯 일곱 여덟 아홉 열'.split()) + tuple('0123456789')
for it in items:
    for i, c in enumerate(it['choices']):
        if not _qty_hits(c):
            continue
        assert any(s in c for s in SCOPE) or any(v in c for v in VALW), \
            (it['id'], MK[i], '수량 진술에 한정어도 값도 없다', c)

NS = [1, 2, 3]
REFERENT = {
    's 오비탈 개수':      [1 for n in NS],
    '껍질 속 총 오비탈':  [n * n for n in NS],
    '오비탈 하나의 정원': [2 for n in NS],
    '껍질 전체의 정원':   [2 * n * n for n in NS],
    '방사 마디 수':       [n - 1 for n in NS],
    '껍질 속 부껍질 수':  [n for n in NS],
}
c3 = D['M02032']['choices'][2]
for name, seq in REFERENT.items():
    grows = seq[0] < seq[1] < seq[2]
    named = 's 오비탈' in c3 and name != 's 오비탈 개수'
    assert (not grows) or named, ('M02032 ③', f'「{name}」 독법에서 참이 된다', seq, c3)
    for a, b in (('하나에서 둘로', (1, 2)), ('하나에서 셋으로', (1, 3)),
                 ('둘에서 넷으로', (2, 4)), ('하나에서 넷으로', (1, 4))):
        if a in c3:
            assert (seq[0], seq[-1]) != b, ('M02032 ③', f'「{name}」 값이 겹친다', seq)

# ── ★새 검사 — 한 문항의 발문이 다른 문항의 판정 근거를 인쇄하지 않는가★ ──
#   P6 은 ★정답 문자열★ 이 다른 발문에 실린 것을 잡았다. 이번에 샌 것은 ★판정 근거★ 다.
#   전자배치 완전 표기는 그 자체가 ★부껍질의 실재와 정원을 동시에 알려 주는 표★ 이므로,
#   같은 배치에 '정원 초과 판정' 이나 '채움 차례' 를 묻는 문항이 있으면 발문에 실을 수 없다.
#   ▸ ★첫 판이 너무 굵었다★ — "발문에 완전 표기를 실었는가" 로 잡았더니 ★배치를
#     인쇄하는 것이 곧 자기 각도인 문항★ 둘(배치 교정 · 홀전자 짝짓기)이 함께 걸렸다.
#     ★검사는 결함의 무늬를 그려야지 재료를 금지해서는 안 된다.★ 두 갈래로 좁힌다.
SUP = '⁰¹²³⁴⁵⁶⁷⁸⁹'
CAP = {'s': 2, 'p': 6, 'd': 10, 'f': 14}


def _cfg_tokens(s):
    out = []
    for m in re.finditer(r'(\d)([spdf])([' + SUP + r']+)', s):
        n = int(''.join(str(SUP.index(ch)) for ch in m.group(3)))
        out.append((m.group(1) + m.group(2), n))
    return out


# (ㄱ) 정원 초과 여부로 판정하는 부껍질이, 다른 발문에 ★정원까지 찬 채로★ 인쇄돼 있으면
#      그 발문이 정원을 알려 준다. 3p⁷ 을 묻는데 옆 발문에 3p⁶ 이 찍혀 있던 것이 그것이다.
judged_sub = set()
for x in items:
    if '최대 전자 수를 넘어선' in x['stem']:
        judged_sub |= {t for t, _ in _cfg_tokens(' '.join(x['choices']))}
for x in items:
    for t, n in _cfg_tokens(x['stem']):
        assert not (t in judged_sub and n == CAP[t[1]]), \
            (x['id'], f'발문이 {t}{n} 으로 정원을 알려 준다', sorted(judged_sub))

# (ㄴ) 배치를 고쳐 쓰게 하는 문항의 ★정답 접두★ 가 다른 발문에 통째로 있으면
#      그 발문이 채움 차례를 알려 준다.
for x in items:
    if '바닥상태 전자배치로 옳은' not in x['stem']:
        continue
    ans = x['choices'][x['answer']]
    pre = ans.rsplit(' ', 1)[0]
    assert len(pre) >= 10, (x['id'], pre)
    for y in items:
        if y['id'] != x['id']:
            assert pre not in y['stem'], (x['id'], '정답 접두가 발문에 노출', y['id'], pre)

# ── 문항 전용 ─────────────────────────────────────────────────────────────
assert '3p⁶' not in D['M02037']['stem'] and '1s²' not in D['M02037']['stem']
assert '3p 부껍질까지' in D['M02037']['stem']
assert '건너뛰었지만' in D['M02039']['choices'][1]
assert D['M02039']['choices'][1].count('지만') == 1
assert '종류는 n 가지, 오비탈은 n² 개' in D['M02032']['solution']
assert '1 + 3 + 5' in D['M02032']['solution']
assert 'f 부껍질의 정원이 열넷' in D['M02038']['solution']
assert '쌓음원리를 어긴 거야' in D['M02034']['solution']
assert '설령 1p 가 있다 치더라도' in D['M02033']['solution']

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P7 6차 조치 완료 — 6 문항')
print('  M02037 발문', D['M02037']['stem'][:44], '…')
print('  M02039 ②', D['M02039']['choices'][1], f"({len(D['M02039']['choices'][1])}자)")
print('  M02039 길이', [len(c) for c in D['M02039']['choices']])
