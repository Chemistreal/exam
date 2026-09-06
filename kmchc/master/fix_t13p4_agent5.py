# -*- coding: utf-8 -*-
"""T13 P4 (M02001~M02010) 층5 5차 조치 — 마감 확인 순회의 지적을 받는다.

네 검증자가 모두 도착했다. solver 마감 가능, factchecker 마감 가능(경미 △ 둘),
defender 마감 불가(심각 하나), student-sim 마감 불가(사표 둘).

받은 것
 1) M02001 발문 (defender 심각 · 마감 보류 사유)
    4차에 넣은 잣대 문장 "단, 방향만 다른 오비탈도 따로 센다." 의 '방향' 이
    이 단원 안에서 두 뜻으로 다 쓰인다 — 궤도 방향(p_x·p_y·p_z)과 스핀 방향.
    둘째 독법을 택한 학생에게 발문은 "스핀 방향만 다른 것도 따로 세라" 는 지시가
    되어 2n² = 32 곧 ④ 를 발문이 승인해 버린다. ④ 를 막으려 넣은 문장이 도리어
    ④ 를 정당화한 꼴이다. 예시를 박아 낱말을 궤도 쪽으로 못 박는다.
 2) M02003 ③ (student-sim 구조적 사표 · 저작 규약 위반)
    ① [Ne] 3s² 3d³ 와 ③ [Ne] 3s² 4p³ 는 심지도 같고 위첨자 합도 같아
    ★어떤 셈을 하든 값이 언제나 같다★. 곧 둘은 같은 까닭으로 함께 지워진다
    (머리말의 '같은 까닭으로 함께 지워지는 쌍 금지'). 남은 유일한 변별면인
    '4p 라는 순서 이상' 은 발문이 직접 무력화했으니 표를 받을 통로가 없다.
    → [Ne] 3s⁴ 3p¹ 로 간다. 합은 그대로 15 라 정답 유일성은 지켜지고,
    훅이 산술이 아니라 ★규칙 위반★ 이라 ① 과 표를 나눠 먹지 않는다.
    같이, 발문의 면제 범위를 '바닥상태' 에서 '옳은지' 로 넓힌다 — 3s⁴ 는
    바닥상태가 아닌 것이 아니라 아예 성립하지 않는 표기이므로.
 3) M02009 ②·④ 기호 병기 (defender 권고)
    '부양자수' 와 '주양자수' 는 한 글자 차이다. ④ 를 주양자수로 잘못 읽으면
    까닭이 참이 되어 정답 ② 와 내용이 같아진다. 오독이지 정당한 독법은 아니나,
    결론을 공유하는 짝에서 굳이 감수할 위험이 아니다. 내용은 그대로 두고
    (n)·(l) 만 붙인다.
 4) factchecker 경미 △ 둘 — M02001 의 홀수합 진술에 '1 부터 차례로' 를 보강,
    M02004 의 '두 배나 세 배' 를 실제 배수(2배·3.6배)에 맞게 고친다.

반려한 것 (까닭을 적어 둔다)
 - M02002 ② 교체 (sim, 사표) — ★멈춤 규칙★ 에 해당한다. 죽은 선지가 하나이고
   D 가 정답을 맞히며 F2 가 없으면 쫓지 않는다. defender 는 이번 순회에서 ② 를
   따로 훑고 F2 후보로 세지 않았고, 중재 규칙은 F2 를 매력도 위에 둔다.
   제안된 '에너지가 서로 달라야 한다' 는 되레 제만 갈라짐이라는 범위 밖 독법을
   새로 연다. 다음 배치에서 같은 각도를 쓸 때 실측으로 다시 본다.
 - M02004 ① → '3 개' (sim) — sim 스스로 "지금도 마감 가능" 이라 적었고,
   ① 은 "양자수 셋을 정했으니 전자도 하나" 라는 실재 경로를 갖고 있다.
 - M02008 ④ → 비소(As) (sim) — 86~94 쪽 범위를 벗어날 수 있어 sim 도 보류를
   권했다. 황은 홀전자 오독의 착지점으로 살아 있다.
 - M02010 ③ → '크기가 작아' (defender, 선택 사항) — defender 가 같은 문단에서
   현행 유지 가능으로 판정했다. 반발 축은 상한 2 를 내놓지 못해 거짓으로 닫힌다.
 - M02001 에 '4f 까지 포함' 명시 (defender, 곁들임) — ② 9 개를 죽인다.
   ② 는 f 를 빠뜨린 학생의 자리로 살아 있어야 한다. 예시 한 줄로 '방향' 만 닫는다.
"""
import json
import sys
from collections import Counter

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']
IDS = ['M%05d' % n for n in range(2001, 2011)]


def setc(it, choices, wrongs):
    assert len(choices) == 4 and len(set(choices)) == 4, it['id']
    it['choices'] = choices
    ds = [{'opt': choices.index(w[0]), 'error': w[1], 'type': w[2]} for w in wrongs]
    assert len(ds) == 3 and all(d['opt'] != it['answer'] for d in ds), it['id']
    it['distractors'] = sorted(ds, key=lambda d: d['opt'])


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:40]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


def retext(it, idx, new, error=None):
    old = it['choices'][idx]
    assert new not in it['choices'], (it['id'], new)
    it['choices'][idx] = new
    it['solution'] = it['solution'].replace(old, new)
    if error is not None:
        for d in it['distractors']:
            if d['opt'] == idx:
                d['error'] = error


bank = json.load(open(BANK, encoding='utf-8'))
D = {i['id']: i for i in bank}
before = {k: json.loads(json.dumps(D[k])) for k in IDS}

# ── 1. M02001 — '방향' 을 궤도 쪽으로 못 박는다 (defender 심각) ───────────
it = D['M02001']
old_stem = 'N 껍질(n = 4)에 있는 오비탈은 모두 몇 개인가? 단, 방향만 다른 오비탈도 따로 센다.'
assert it['stem'] == old_stem, it['stem']
it['stem'] = ('N 껍질(n = 4)에 있는 오비탈은 모두 몇 개인가? '
              '단, p_x·p_y·p_z 처럼 방향이 다른 오비탈도 각각 따로 센다.')
sub(it, '발문이 방향만 다른 것도 따로 세라고 했으니',
        '발문이 p_x·p_y·p_z 처럼 방향이 다른 것도 따로 세라고 했으니')
# factchecker △ — 홀수의 출발점을 못 박는다
sub(it, '1, 3, 5, 7 처럼 홀수를 n 개 더하면 n² 이 되거든.',
        '1 부터 차례로 홀수를 n 개 더하면 n² 이 되거든.')

# ── 2. M02003 — 함께 지워지는 쌍을 끊는다 (student-sim) ───────────────────
it = D['M02003']
old_stem = ('다음은 인(P, 원자 번호 15)의 전자배치를 축약 표기로 적어 본 것이다. '
            '배치가 바닥상태인지는 따지지 말고 전자의 총수만 셀 때, 15 가 되지 않는 것은?')
assert it['stem'] == old_stem, it['stem']
it['stem'] = ('다음은 인(P, 원자 번호 15)의 전자배치를 축약 표기로 적어 본 것이다. '
              '적힌 배치가 옳은지는 따지지 말고 전자의 총수만 셀 때, 15 가 되지 않는 것은?')
retext(it, 2, '[Ne] 3s⁴ 3p¹',
       error='3s 에 넷은 성립할 수 없는 표기라 골라 냄 — 총수만 물었고 10+5 = 15 로 맞다')
sub(it, '③ [Ne] 3s⁴ 3p¹: 4p 도 낮은 자리를 건너뛴 표기일 뿐이야. 총수는 10 더하기 5 로 열다섯이야.',
        '③ [Ne] 3s⁴ 3p¹: 한 오비탈에 전자가 넷일 수는 없으니 이 표기는 아예 성립하지 않아. '
        '그래도 적힌 대로 세라고 했으니 10 더하기 5 로 열다섯이야.')
sub(it, '넷 다 인의 바닥상태 배치는 아니지만 그것은 이 문제가 묻는 바가 아니야.',
        '넷 다 인의 바닥상태 배치가 아니고 ③ 은 아예 성립하지도 않는 표기이지만, '
        '그것은 이 문제가 묻는 바가 아니야.')

# ── 3. M02004 — 배수 표현을 실제 값에 맞춘다 (factchecker △) ──────────────
sub(D['M02004'], '값이 두 배나 세 배로 커져', '값이 두 배, 세 배 넘게 커져')

# ── 4. M02009 — 기호 병기로 한 글자 차이를 끊는다 (defender 권고) ─────────
it = D['M02009']
retext(it, 1, '에너지가 주양자수(n)로만 정해지므로 3d 쪽이 더 낮다')
retext(it, 3, '부양자수(l)가 3d 쪽이 더 작으므로 3d 가 더 낮아진다')
sub(it, '부양자수는 3d 가 2, 4s 가 0 이라 오히려 3d 쪽이 커.',
        '부양자수 l 은 3d 가 2, 4s 가 0 이라 오히려 3d 쪽이 커.')

# ── 검사 ──────────────────────────────────────────────────────────────────
items = [D[k] for k in IDS]

assert Counter(i['answer'] for i in items) == {2: 3, 3: 3, 0: 2, 1: 2}, \
    Counter(i['answer'] for i in items)
for k in IDS:
    assert D[k]['answer'] == before[k]['answer'], k

touched = {'M02001', 'M02003', 'M02004', 'M02009'}
for k in IDS:
    if k not in touched:
        assert D[k]['choices'] == before[k]['choices'], k
        assert D[k]['solution'] == before[k]['solution'], k
        assert D[k]['stem'] == before[k]['stem'], k

for it in items:
    cs = it['choices']
    assert len(cs) == 4 and len(set(cs)) == 4, it['id']
    opts = sorted(d['opt'] for d in it['distractors'])
    assert opts == sorted(set(range(4)) - {it['answer']}), (it['id'], opts)
    assert len(it['solution']) >= 300, (it['id'], len(it['solution']))
    assert '★' not in it['solution'] and '★' not in it['stem'], it['id']
    assert it['objective'], it['id']
    L = sorted(len(c) for c in cs)
    a = len(cs[it['answer']])
    assert not (a == L[3] and L[2] < L[3]), (it['id'], 'G3 최장 단독', cs)
    assert not (a == L[0] and L[0] < L[1]), (it['id'], 'G3 최단 단독', cs)
    mid = (L[1] + L[2]) / 2
    if mid >= 8:
        sp = (L[3] - L[0]) / mid
        assert sp <= 0.25, (it['id'], 'G3b', round(sp, 3), cs)
    head = it['solution'].split('\n')[2] if len(it['solution'].split('\n')) > 2 else it['solution']
    assert MK[it['answer']] + ' ' in it['solution'], it['id']
    assert '가 옳아' in it['solution'] or '이 옳아' in it['solution'], it['id']
    for k in range(4):
        assert MK[k] + ' ' + cs[k] in it['solution'], (it['id'], MK[k])

# 이번 회차 문면 검사
s1 = D['M02001']
assert 'p_x·p_y·p_z' in s1['stem'] and '스핀' not in s1['stem'], s1['stem']
assert '1 부터 차례로 홀수를' in s1['solution']
s3 = D['M02003']
assert s3['choices'] == ['[Ne] 3s² 3d³', '[He] 2p⁶ 3d⁷', '[Ne] 3s⁴ 3p¹', '[Ar] 3s² 3p³'], s3['choices']
assert len(set(s3['choices'])) == 4 and len({len(c) for c in s3['choices']}) == 1
assert '적힌 배치가 옳은지는' in s3['stem'] and '바닥상태인지는 따지지' not in s3['stem']
assert '성립하지 않아' in s3['solution']
s4 = D['M02004']
assert '두 배, 세 배 넘게 커져' in s4['solution']
s9 = D['M02009']
assert s9['choices'][1] == '에너지가 주양자수(n)로만 정해지므로 3d 쪽이 더 낮다'
assert s9['choices'][3] == '부양자수(l)가 3d 쪽이 더 작으므로 3d 가 더 낮아진다'

# ① 과 ③ 이 더는 같은 셈으로 지워지지 않는지 — 심지와 위첨자를 나란히 적어 본다
core = {'[He]': 2, '[Ne]': 10, '[Ar]': 18}
sup = {'⁰': 0, '¹': 1, '²': 2, '³': 3, '⁴': 4, '⁵': 5, '⁶': 6, '⁷': 7, '⁸': 8, '⁹': 9}
tot = []
for c in s3['choices']:
    parts = c.split()
    n = core[parts[0]]
    for p in parts[1:]:
        n += sup[p[-1]]
    tot.append(n)
assert tot == [15, 15, 15, 23], tot
assert s3['answer'] == 3

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P4 5차 조치 완료 — M02001 발문 · M02003 ③ + 발문 · M02004 · M02009 ②④')
print('  총수 검산:', tot, '(①②③ 15 · ④ 23)')
for k in ['M02001', 'M02003', 'M02009']:
    print(' ', k, '|', D[k]['stem'][:60])
