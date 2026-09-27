# -*- coding: utf-8 -*-
"""T13 P7 (M02031~M02040) 층5 5차 조치 — 한 줄, 그러나 네 번째로 조치가 낳은 결함.

4차 순회: solver 마감 가능(F1 0) · factchecker ★마감 가능(확정 사실 오류 0)★ ·
student-sim 마감 가능(A 0 / B 0 / C 7 / D 10 · C·D 분기 3문항 · D 전항 정답) ·
defender ★마감 불가 — 변호 성공 1건, 심각도 높음/차단★

★같은 자리가 두 회차 연속으로 열렸다 — M02032 ③★
  3차: '그만큼 개수도 함께 늘어난다' → 지시 대상이 열려 껍질 오비탈 수(n²)로 읽으면 참.
  4차 조치: 숫자로 못 박았다 — '개수도 하나에서 셋으로 는다'.
  ▸ ★못이 빗나갔다.★ defender 가 지시 대상표를 만들어 확인했다.
      s 오비탈 개수      1·1·1  거짓
      껍질 속 총 오비탈  1·4·9  거짓
      오비탈 정원        2·2·2  거짓
      방사 마디 수       0·1·2  거짓
      ★껍질 속 부껍질 수  1·2·3  참★
    n = 1, 2, 3 의 부껍질 종류 수가 정확히 1 → 3 이다. ★내가 고른 숫자가 하필 살아
    있는 여섯 번째 독법의 값이었다.★
  ▸ defender 의 판정이 무겁다 — ★"3차 조치는 못 박기에 실패했을 뿐 아니라, 개수만
    말하던 이전 문면보다 위험해졌습니다."★ 열린 문면은 독자가 대상을 옮겨야 참이
    되지만, 숫자를 박은 문면은 ★그 숫자를 아는 학생이 곧바로 참으로 읽는다.★
  ▸ solver 도 같은 자리를 짚었다(다만 복수 정답으로는 보지 않음, [저]).
  ▸ ★student-sim 은 반대로 유지에 찬성했다★ — "주어가 앞절의 '오비탈' 로 고정돼 있어
    오비탈 개수 독법에서는 어느 쪽도 거짓이라 판정은 안전하다. 이 아슬함이 곧
    유인력이므로 그대로 두는 데 찬성한다."
    → ★중재 규칙대로 defender 를 따른다.★ defender 는 ★참 독법이 존재함★ 을 세웠고,
      복수 정답 판정은 언제나 매력도에 앞선다. 게다가 sim 이 적은 B 프로필의 착지
      논거가 ★"1껍질 s, 2껍질 s·p, 3껍질 s·p·d — 종류가 늘잖아"★ 다. 이것은
      오독이 아니라 ★바로 그 참 독법 자체★ 다. ★매력의 원천이 곧 결함이다.★

조치 — defender 수정안 A 를 다듬어 넣는다
──────────────────────────────────────────────────────────────────────────
  ③ ★'오비탈이 커지지만 한 껍질 속 s 오비탈 수도 는다'★ (28자)
  ▸ defender 문안('… s 오비탈 수도 하나에서 셋으로 는다', 30자)에서 ★숫자를 뺐다.★
    G3b 검산: 넣으면 폭 0.235 로 통과는 하나, ★이 결함이 두 번 다 숫자 근처에서
    났다.★ 숫자가 없으면 어떤 값과도 우연히 겹칠 수 없다. 25·24·28·26 → 폭 0.157.
  ▸ 다섯 독법이 모두 막힌다 — 's 오비탈' 이 대상을 이름으로 못 박아 부껍질·총
    오비탈·정원·마디 독법이 끊기고, '한 껍질 속' 이 누적 독법을 끊는다. s 부껍질의
    오비탈은 어느 껍질에서나 하나이므로 ★남는 유일한 독법에서 거짓★ 이다.
  ▸ 어미 '지만' 을 지켰다 — 4차에 배운 대로 ①③ : ②④ 의 어조 2 : 2 가 깨지면
    '완화 표현이 정답에만' 검사가 걸린다.
  ▸ 목표 오개념('껍질이 커지면 s 도 여러 개가 된다')은 그대로 살아 있고, sim 이 실측한
    B 착지 논거를 ★해설에서 정면으로 교정★ 한다 — 늘어나는 것은 부껍질의 종류와
    껍질 전체의 오비탈 수이지 s 오비탈의 수가 아니다.

★새로 넣는 검사 두 가지★
──────────────────────────────────────────────────────────────────────────
 (1) ★수량 진술은 대상을 이름으로 밝히거나 값을 밝혀야 한다★ — 3차 결함의 무늬.
     '개수·정원·수' 가 나오는데 한정어도 값도 없으면 지시 대상이 열린다.
 (2) ★값을 밝힌 수량 진술은 그것으로 안전해지지 않는다★ — 4차 결함의 무늬.
     값은 다른 지시 대상에서 참이 될 수 있다. 그래서 M02032 는 ★지시 대상표를
     코드로 세워★ 여섯 독법 전부에서 거짓임을 검산한다. ★손으로 센 것은 검사가
     아니다 — 표로 세워야 다음 회차에도 지켜진다.★

반려한 것 다섯 (근거를 남긴다)
──────────────────────────────────────────────────────────────────────────
 · ★M02031 의 mₗ 세 번 되풀이 (factchecker)★ — ★반려. factchecker 스스로 손대지 말
   것을 권했다★ — "이번 회차에 문면을 또 건드리는 위험이 이득보다 크다." 4차에 ④ 를
   (3, 1, −1)로 옮기며 생긴 결과이고, 그 이동은 교차 사슬을 끊기 위한 것이었다.
   ★이 배치에서 조치가 결함을 낳은 것이 네 번이다.★ 차단이 아닌 자리는 건드리지 않는다.
 · ★M02032 정답이 '변하지 않는 것' 을 말한다 (solver [저])★ — 반려. 발문이 "달라지는
   것" 을 묻는데 정답 ① 은 앞절에서 '커진다' 로 달라짐을 말하고 뒷절에서 무엇이
   그대로인지를 말한다. ★두 절 모두 필요한 것이 이 각도(누가 무엇을 정하는가)의
   핵심★ 이고, 네 선지가 모두 같은 두 절 구조라 표면 단서가 되지 않는다.
 · ★M02039 의 '훈트' 2회 노출 (solver [저])★ — 반려. 어긴 규칙이 셋 중 무엇인지를
   묻는 각도라 규칙 이름이 발문과 선지에 함께 나오는 것이 구조적 불가피다.
 · ★M02038 ③ 이 3d 를 이름으로 불러 M02037 ① 을 죽인다 (sim 경미)★ — 반려.
   4주기가 열여덟인 까닭을 묻는 각도에서 4s·3d·4p 를 부르지 않을 방법이 없다.
   4차에 M02031 ④ 의 d 를 걷어 ★확인 사슬 가운데 강한 쪽은 이미 끊었다.★
   남은 것은 '정답 해설을 읽은 뒤' 에만 성립하는 약한 잔여다.
 · ★sim 의 다음 개정 후보 목록★ — 반려(이번 회차 기준). 설계 문서에 적어 둔다.

★기록 — 검증자가 확인해 준 것★
 · factchecker: ★확정 사실 오류 0.★ 4차에 자신이 올렸던 △D 를 스스로 철회했다.
 · sim: D 전항 정답 · A 0 · B 0. ★C·D 분기 3문항(M02036·M02039·M02040) 유지.★
 · solver: 무정답·복수 정답 0. 무지식 경로 0.
 · defender: ★"수정안 A 를 반영하면 나머지 아홉 문항은 차단 결함이 없으므로 그 한 줄
   교체만으로 마감 가능합니다."★
"""
import json
import re
from collections import Counter

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']
IDS = ['M%05d' % n for n in range(2031, 2041)]
TOUCHED = {'M02032'}


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:40]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


bank = json.load(open(BANK, encoding='utf-8'))
D = {i['id']: i for i in bank}
before = {k: json.loads(json.dumps(D[k])) for k in IDS}

# ── M02032 ③ — 대상을 이름으로 못 박고 숫자를 뺀다 ────────────────────────
it = D['M02032']
assert it['choices'][2] == '오비탈이 커지지만 개수도 하나에서 셋으로 는다', it['choices']
it['choices'][2] = '오비탈이 커지지만 한 껍질 속 s 오비탈 수도 는다'
for d in it['distractors']:
    if d['opt'] == 2:
        d['error'] = ('껍질이 커지면 s 오비탈도 여러 개가 된다고 봄 — 늘어나는 것은 '
                      '부껍질의 종류와 껍질 전체의 오비탈 수이지 s 오비탈의 수가 아니다')
sub(it, '③ 오비탈이 커지지만 개수도 하나에서 셋으로 는다: 커진다는 앞말은 맞아. 그런데 '
        's 부껍질의 오비탈은 어느 껍질에서나 하나뿐이라 1s 도 2s 도 3s 도 하나씩이야. '
        '껍질 전체로 넓혀 보아도 오비탈 수는 n² 이라 1, 4, 9 로 늘지 셋으로 가지 않아.',
        '③ 오비탈이 커지지만 한 껍질 속 s 오비탈 수도 는다: 커진다는 앞말은 맞아. '
        '그런데 s 부껍질에는 어느 껍질에서나 오비탈이 하나뿐이라 1s 도 2s 도 3s 도 '
        '하나씩이야. 껍질이 커질 때 늘어나는 것은 부껍질의 종류(1껍질은 s, 2껍질은 '
        's·p, 3껍질은 s·p·d)와 껍질 전체의 오비탈 수(n²)지 s 오비탈의 수가 아니야. '
        '무엇이 늘어나는지를 이름까지 붙여 말해 보면 이 헷갈림이 풀려.')

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

OPEN = re.compile(r'(그만큼|함께)\s*(개수|정원|수)')
for it in items:
    for i, c in enumerate(it['choices']):
        assert not OPEN.search(c), (it['id'], MK[i], '지시 대상이 열린 수량어', c)

# ── ★새 검사 (1) — 수량 진술은 대상을 이름으로 밝히거나 값을 밝혀야 한다★ ──
#   3차 결함의 무늬. '개수·정원·수' 가 나오는데 ★무엇의 그것인지★ 를 한정하는 말도
#   없고 값도 없으면, 독자가 지시 대상을 옮겨 참으로 읽을 여지가 열린다.
#   ▸ ★첫 판에 오탐이 났다★ — '있을 수는' 의 의존명사 '수' 를 수량어로 읽었다.
#     앞 어절이 관형형 어미 ㄹ 로 끝나면(있을·할·갈) 그것은 ★가능성의 '수'★ 다.
#     ★검사는 헛돌아도 안 되지만 엉뚱한 것을 잡아도 안 된다.★
QTY = re.compile(r'(개수|정원|(?:^|(?<=[ ]))수(?:도|가|는|를))')


def _qty_hits(c):
    out = []
    for m in QTY.finditer(c):
        if m.group().startswith('수') and m.start() >= 2:
            prev = c[m.start() - 2]           # 앞 어절의 끝 음절
            if '가' <= prev <= '힣' and (ord(prev) - 0xAC00) % 28 == 8:   # 받침 ㄹ
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

# ── ★새 검사 (2) — M02032 지시 대상표: 여섯 독법 전부에서 거짓인가★ ─────────
#   4차 결함의 무늬. ★값을 밝혔다고 안전해지지 않는다★ — 그 값이 다른 지시 대상에서
#   참일 수 있다. 손으로 세지 말고 표로 세운다. n = 1, 2, 3 (1s·2s·3s 를 견주는 발문).
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
    # 문면이 주장하는 것은 '는다'(단조 증가). 어느 독법에서 실제로 늘어나는가.
    grows = seq[0] < seq[1] < seq[2]
    named = 's 오비탈' in c3 and name != 's 오비탈 개수'
    assert (not grows) or named, \
        ('M02032 ③', f'「{name}」 독법에서 참이 된다', seq, c3)
    # 값을 적어 두었다면 그 값열과 겹치는 독법이 없어야 한다
    for a, b in (('하나에서 둘로', (1, 2)), ('하나에서 셋으로', (1, 3)),
                 ('둘에서 넷으로', (2, 4)), ('하나에서 넷으로', (1, 4))):
        if a in c3:
            assert (seq[0], seq[-1]) != b, ('M02032 ③', f'「{name}」 값이 겹친다', seq)
assert '한 껍질 속' in c3 and 's 오비탈' in c3, c3
assert not any(ch.isdigit() for ch in c3) and '하나' not in c3 and '셋' not in c3, c3

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P7 5차 조치 완료 — 1 문항')
print('  M02032 ③', D['M02032']['choices'][2], f"({len(D['M02032']['choices'][2])}자)")
print('  길이', [len(c) for c in D['M02032']['choices']])
