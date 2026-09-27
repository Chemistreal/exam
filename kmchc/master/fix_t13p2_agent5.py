# -*- coding: utf-8 -*-
"""T13 P2 — 5차 조치 (sim 3차의 구조 지적 넷).

3차 순회에서 **solver 지적 없음 · defender F2 승격 0건 · factchecker 사실 오류
1건(4차에 닫음)** 이었고, 남은 것은 sim 이 짚은 **오답의 착지점** 문제다.

★가장 값이 큰 지적 — M01982 는 가장 흔한 오개념의 착지점이 선지에 없었다★
설계는 3 단(배치 → 4s 우선 이온화 → 훈트 계수)인데, **2 단에서 무너진 학생**
— '나중에 채운 3d 부터 빠진다' 고 보는 다수 — 의 산출값은
    Co²⁺ = [Ar] 4s² 3d⁵ (홀 5) · Co³⁺ = [Ar] 4s² 3d⁴ (홀 4) → **3 · 5 · 4**
인데 그 값이 네 선지에 없었다. 갈 곳을 잃은 B 가 ④(3·4·5)로 흩어지고,
② (3·2·1)는 아무 경로와도 대응되지 않아 죽었다.
→ ② 를 **'차례로 3 · 5 · 4'** 로 바꾼다. 죽은 선지가 살아나고, 붕괴 지점이
  회수되며, ★solver 가 짚은 형태 단서(오답 셋이 모두 규칙적 수열이라 불규칙한
  정답이 지목됨)까지 함께 사라진다★ — 이제 불규칙한 것이 둘이다.
  ▸ ★교훈: 죽은 선지를 볼 때 '이 값이 매력적인가' 를 묻기 전에 **'이 문항의
    붕괴 지점마다 착지점이 있는가' 를 먼저 물을 것.★ 착지점 없는 붕괴는 오답을
    죽이고 학생을 무작위로 흩는다.

★M01989 — 정의 한 줄로 뚫리고 죽은 선지가 둘이었다 (sim 우선순위 1)★
"가장 바깥 껍질 = 주양자수가 가장 큰 껍질" 이라는 **정의**만 알면, 게다가 축약
배치의 **맨 끝 항을 읽는 것만으로** 답이 나왔다. 앞의 4f¹⁴ 5d¹⁰ 은 장식이었다.
→ 원소를 금(…6s¹)에서 **비스무트(… 6s² 6p³)** 로 옮긴다. 가장 바깥 껍질에
  부껍질이 둘이라 **두 항을 더해야** 하고, ★맨 끝 항만 읽는 우회로는 이제
  틀린 선지(전자 3 개)에 착지한다.★ 우회로를 막는 가장 좋은 방법은 그것을
  덫으로 바꾸는 것이다. 죽어 있던 ② 가 그 덫이 되고, ④(전자가 가장 많은
  부껍질 4f 의 14)는 4차에서 바로잡은 경로를 그대로 쓴다.
  각도(C13-009[4] 교재 실례에서 최외각 껍질의 n 찾기)는 그대로다.

★M01984 ① · M01987 ④ — 죽은 선지 둘★
· M01984 ①('세 오비탈의 에너지가 서로 달라지기 때문')은 sim 이 죽었다 했고,
  defender 는 **정답의 거친 판본**이라고 경계 표시를 했다(SCF 로 재면 실제로
  갈라지고, 갈라지는 원인이 곧 정답이 말하는 반발이다). 둘을 한꺼번에 닫는다 —
  **'낮은 자리를 비워 쌓음 원리를 어겼기 때문'**. 같은 2p 부껍질 안의 재배치라
  낮은 자리를 비운 것이 아니므로 명백히 거짓이고, ②(파울리)와 짝을 이루어
  **규칙 이름을 잘못 대는 두 자리**가 된다.
· M01987 ④('3py 와 4px')는 n 도 l 도 달라 아무도 고르지 않았다 →
  **'2pz 와 3pz'**. "모양이 같으면 에너지도 같다" 는 실재 오개념이 착지하고,
  n 이 달라 수소에서도 다르므로 발문의 앞 조건을 채우지 못한다.

받아들이지 않은 것 (마감 부채)
· M01986 ① 대안 '+1/2' — 2 차에 패리티로 죽어 뺀 값을 도로 넣자는 것이라 되풀이.
· M01985 ① 대안 '[Ar] 3d¹⁰ 4s² 4p³' — 17 자라 나머지 셋(12 자)과 G3b 산포가
  0.42 로 튄다.
· M01981 ② 대안 'He⁺ 가 He 로 되는 변화' — 15 자라 정답(17 자)이 유일최장이 된다.
  경로 자체는 좋다(변화의 시작 쪽을 보는 학생) — ★T13 뒤 배치에서 이 각도를 쓸 때
  길이를 맞춰 넣을 것.★
· M01988 ② 대안 '3d 오비탈은 M 껍질에 속하지 않기 때문에' — 3 차에 넣은 선지를
  또 가는 것이고, defender 가 "명백히 거짓" 으로 정상 판정했다. 하나 남는 죽은
  선지로 둔다.
· M01983 ③('18 개') 죽음 — defender 는 같은 선지를 "n = 3 껍질 정원, mₗ 조건
  무시" 라는 실재 경로로 보았다. 두 검증자가 어긋나고, 대안('3 개')을 넣으려면
  살아 있는 6 을 빼야 해서 더 나빠진다.
· M01983 과 M01990 이 둘 다 '오비탈 수 × 2 누락' 을 잰다(sim 두 회차) — 배치
  구성의 문제라 문항 하나를 고쳐 풀 일이 아니다. ★P3 설계의 검사 6 번(한 배치에
  같은 실패 지점을 두 번 두지 말 것)으로 옮겨 두었다.★
"""
import json
from collections import Counter

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']

bank = json.load(open(BANK, encoding='utf-8'))
by = {x['id']: x for x in bank}


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:40]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


def retext(it, idx, new):
    old = it['choices'][idx]
    assert new not in it['choices'], (it['id'], new)
    it['choices'][idx] = new
    if old in it['solution']:
        it['solution'] = it['solution'].replace(old, new)
    return old


def audit(it):
    a = it['answer']
    head = it['solution'].split('\n\n')[1]
    for k in range(4):
        if k == a:
            continue
        for tail in ('가 옳아', '이 옳아'):
            assert MK[k] + tail not in head, f"{it['id']}: 정답 본문에 {MK[k]}{tail}"
    assert (MK[a] + '가 옳아' in head) or (MK[a] + '이 옳아' in head), it['id']
    for k in range(4):
        assert (MK[k] + ' ' + it['choices'][k]) in it['solution'], \
            f"{it['id']}: 해설에 {MK[k]} 선지 본문이 없다"
    assert '★' not in it['stem'], it['id']
    assert '★' not in it['solution'], f"{it['id']}: G10 해설 강조 표기"


def g3(it):
    L, a = [len(c) for c in it['choices']], it['answer']
    assert not (L[a] == max(L) and L.count(max(L)) == 1), f"{it['id']}: G3 유일최장 {L}"
    assert not (L[a] == min(L) and L.count(min(L)) == 1), f"{it['id']}: G3 유일최단 {L}"
    s = sorted(L)
    if (s[1] + s[2]) / 2 >= 8:
        sp = (s[3] - s[0]) / ((s[1] + s[2]) / 2)
        assert sp <= 0.25, f"{it['id']}: G3b 산포 {sp:.2f} {L}"
    return L, sorted(range(4), key=lambda i: -L[i]).index(a) + 1


def rebuild(it, *, stem, choices, ans, lead, cor, reb, diag, wrongs,
            proof, calc, device, scenario, skill=None, objective=None, esr=None):
    assert len(choices) == 4 and len(set(choices)) == 4, it['id']
    it['stem'] = stem
    it['choices'] = list(choices)
    it['answer'] = ans
    it['distractors'] = sorted(
        [{'opt': choices.index(t), 'error': e, 'type': ty} for t, e, ty in wrongs],
        key=lambda d: d['opt'])
    assert [d['opt'] for d in it['distractors']] == sorted(set(range(4)) - {ans}), it['id']
    it['answer_proof'] = proof
    it['calc_check'] = calc
    it['device'] = device
    it['scenario'] = scenario
    for k, v in (('skill', skill), ('objective', objective), ('expected_solve_rate', esr)):
        if v is not None:
            it[k] = v
    body = [lead, '', f'[정답] {MK[ans]} {choices[ans]} — {cor}', '']
    body += [f'{MK[k]} {choices[k]}: {reb[k]}' for k in range(4) if k != ans]
    body += ['', diag]
    it['solution'] = '\n'.join(body)
    assert len(it['solution']) >= 300, (it['id'], len(it['solution']))


# ── ★M01982 : 붕괴 지점에 착지점을 놓는다 ───────────────────────────────
it = by['M01982']
retext(it, 1, '차례로 3 · 5 · 4')
sub(it, '② 차례로 3 · 5 · 4: 이온이 될 때마다 홀전자가 하나씩 준다고 본 값이야. '
        '4s 를 뺄 때는 3d 가 그대로라 홀전자도 변하지 않아.',
    '② 차례로 3 · 5 · 4: 나중에 채운 3d 부터 빠진다고 보았을 때 나오는 값이야. 그렇게 세면 '
    'Co²⁺ 은 [Ar] 4s² 3d⁵ 라 홀전자가 다섯, Co³⁺ 은 [Ar] 4s² 3d⁴ 라 넷이 되지. 산술은 '
    '맞지만 출발이 틀렸어 — 양이온이 될 때 먼저 빠지는 것은 3d 가 아니라 바깥 껍질인 4s 야.')
for d in it['distractors']:
    if d['opt'] == 1:
        d['error'] = '나중에 채운 3d 부터 빠진다고 봄 — 4s²3d⁵ 홀 5 · 4s²3d⁴ 홀 4'

# ── M01984 ① : 죽은 선지 + 정답의 거친 판본 (sim · defender) ────────────
it = by['M01984']
retext(it, 0, '낮은 자리를 비워 쌓음 원리를 어겼기 때문')
sub(it, '① 낮은 자리를 비워 쌓음 원리를 어겼기 때문: 전자가 여럿인 원자에서 준위가 갈라지는 것은 '
        '부양자수가 다를 때야. 2p 세 오비탈은 주양자수도 부양자수도 같아서, 홀로 있는 원자라면 '
        '전자를 어떻게 넣든 갈라지지 않아.',
    '① 낮은 자리를 비워 쌓음 원리를 어겼기 때문: 쌓음 원리는 에너지가 낮은 오비탈부터 채우라는 '
    '규칙이야. 그런데 이 배치는 2p 라는 한 부껍질 안에서 세 자리를 어떻게 나눠 쓰느냐를 바꾼 '
    '것뿐이고, 세 자리는 에너지가 서로 같아. 낮은 자리를 비워 둔 데가 없으니 쌓음 원리는 '
    '어기지 않았지. 어긴 것은 훈트 규칙이야.')
for d in it['distractors']:
    if d['opt'] == 0:
        d['error'] = '훈트 위반을 쌓음 위반으로 봄 — 같은 부껍질 안의 재배치라 빈 낮은 자리가 없다'

# ── M01987 ④ : 죽은 선지 → '모양이 같으면 같다' 오개념 (sim) ────────────
it = by['M01987']
retext(it, 3, '한 원자 안의 2pz 와 3pz')
sub(it, '④ 한 원자 안의 2pz 와 3pz: 같은 p 라도 주양자수가 3 과 4 로 달라. 껍질이 다르면 '
        '수소에서도 에너지가 다르니 발문의 앞 조건을 채우지 못해.',
    '④ 한 원자 안의 2pz 와 3pz: 모양이 같으니 에너지도 같겠다고 보기 쉬운 자리야. 그런데 '
    '주양자수가 2 와 3 으로 달라. 수소에서는 에너지가 주양자수만으로 정해지니 n 이 다르면 '
    '그것만으로 이미 달라지지. 발문의 앞 조건부터 채우지 못해.')
assert it['answer_proof'].count('2s 와 3px · 3py 와 4px') == 1
it['answer_proof'] = it['answer_proof'].replace('2s 와 3px · 3py 와 4px',
                                                '2s 와 3px · 2pz 와 3pz')
sub(it, '2s 와 3px, 3py 와 4px 는 주양자수부터 다르니 수소에서조차 같지 않지.',
    '2s 와 3px, 2pz 와 3pz 는 주양자수부터 다르니 수소에서조차 같지 않지.')
for d in it['distractors']:
    if d['opt'] == 3:
        d['error'] = '모양이 같으면 에너지도 같다고 봄 — 주양자수가 다르면 수소에서도 다르다'

# ── ★M01989 : 우회로를 덫으로 바꾼다 (sim 우선순위 1) ───────────────────
C89 = ['주양자수 6 · 전자 5 개', '주양자수 6 · 전자 3 개',
       '주양자수 5 · 전자 10 개', '주양자수 4 · 전자 14 개']
rebuild(
    by['M01989'],
    stem=('어떤 원자의 바닥상태 전자 배치가 [Xe] 4f¹⁴ 5d¹⁰ 6s² 6p³ 이다. 이 원자에서 '
          '가장 바깥 껍질의 주양자수와 그 껍질에 든 전자 수를 옳게 짝지은 것은?'),
    choices=C89, ans=0,
    proof=('가장 바깥 껍질은 주양자수가 가장 큰 껍질이므로 4 · 5 · 6 가운데 6 이다. n = 6 인 '
           '오비탈은 6s 와 6p 둘이므로 두 항을 더해야 하고, 6s² 와 6p³ 을 합쳐 5 개다. '
           '맨 끝 항 6p³ 만 세면 3, 5d¹⁰ 을 바깥으로 보면 10, 전자가 가장 많은 4f¹⁴ 를 고르면 '
           '14 가 나오는데 모두 껍질을 잘못 잡았거나 한 항만 센 값이다'),
    calc='max n = 6 → 6s² + 6p³ = 5 / 끝 항만 3 · 5d 10 · 4f 14',
    device='축약 배치 한 줄', scenario='가장 바깥 껍질과 그 전자 수',
    wrongs=[(C89[1], '맨 끝 항 6p³ 만 세고 같은 껍질의 6s² 를 더하지 않음', 'proc'),
            (C89[2], '전자가 많은 5d 를 바깥으로 봄 — 바깥은 주양자수가 정한다', 'proc'),
            (C89[3], '전자가 가장 많은 부껍질(4f 의 14)을 고름 — 개수는 바깥과 무관하다', 'proc')],
    lead='"가장 바깥" 을 전자가 많은 쪽으로 읽는지 주양자수가 큰 쪽으로 읽는지가 갈리고, '
         '그다음 한 걸음이 더 남은 자리야.',
    cor=('가장 바깥 껍질이란 주양자수가 가장 큰 껍질을 말해. 적힌 네 항의 주양자수를 뽑아 보면 '
         '4f 는 4, 5d 는 5, 6s 와 6p 는 둘 다 6 이야. 그러니 가장 바깥은 n = 6 인 껍질이지. '
         '여기서 한 걸음이 더 남아. n = 6 인 오비탈이 6s 하나가 아니라 6s 와 6p 둘이거든. '
         '그 껍질에 든 전자를 다 세려면 두 항을 더해야 해. 6s 에 둘, 6p 에 셋이니 모두 5 개야 '
         '— ①이 옳아. 4f 에 열넷, 5d 에 열이 있어 수만 보면 훨씬 많지만 그것들은 안쪽 껍질이야. '
         '버릇을 하나 들여 두자. 축약 배치는 안쪽부터 바깥으로 적는 것이 관례라 마지막 항이 '
         '대개 가장 바깥이지만, 마지막 항 하나가 그 껍질의 전부는 아니야. 주양자수가 같은 '
         '항을 모두 찾아 더하는 것까지가 한 묶음이야.'),
    reb=[None,
         ('맨 끝 항 6p³ 만 세었을 때 나오는 값이야. 6s² 도 주양자수가 6 이라 같은 껍질에 '
          '들어가. 마지막 항만 보지 말고 n 이 같은 항을 모두 모아야 해.'),
         ('전자가 열이나 있는 5d 를 바깥으로 본 값이야. 바깥인지 안쪽인지는 개수가 아니라 '
          '주양자수로 정해지고 5 는 6 보다 작아. 전이금속에서 d 전자를 원자가전자처럼 다루는 '
          '습관이 여기서 걸리지.'),
         ('전자가 가장 많은 부껍질을 고른 값이야. 4f 에 열넷이 들어 있어 넷 가운데 가장 많지. '
          '그런데 바깥인지는 개수가 아니라 주양자수로 정해져. 게다가 이 항은 적힌 차례의 첫 '
          '항이라 오히려 가장 안쪽 가까이에 있어.')],
    diag='자가진단: 바깥은 n 이 큰 쪽 — n = 6 인 항을 모두 모아 6s² + 6p³ = 5.')

# ── 마무리 검사 ─────────────────────────────────────────────────────────
seq = [by[f'M0{i}']['answer'] for i in range(1981, 1991)]
assert Counter(seq) == Counter({0: 2, 1: 2, 2: 3, 3: 3}), dict(Counter(seq))
for p in (2, 3, 4, 5):
    assert not (len(seq) >= 2 * p and all(seq[k] == seq[k % p] for k in range(len(seq)))), p
for v in set(seq):
    pos = [k for k, a in enumerate(seq) if a == v]
    assert not (len(pos) >= 3 and len({pos[k + 1] - pos[k] for k in range(len(pos) - 1)}) == 1), v

for i in range(1981, 1991):
    x = by[f'M0{i}']
    audit(x)
    L, rk = g3(x)
    assert len(x['solution']) >= 300, (i, len(x['solution']))
    assert len(set(x['choices'])) == 4, i
    print(f"  M0{i} 정답 {MK[x['answer']]} · 길이 {L} · 순위 {rk} · 해설 {len(x['solution'])}자")

print('정답 차례', '-'.join(str(a + 1) for a in seq))
json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('5차 조치 완료 — M01982 착지점 · M01989 우회로를 덫으로 · M01984/M01987 죽은 선지')
