# -*- coding: utf-8 -*-
"""T12 마감 14제 — 9차 보정: 배치 경계를 넘어간 정답 차례 줄(G3f).

9차를 끝내고 마감 14제의 정답 차례를 이어 붙여 보니

    ④①④③①③③②④②④②①②
              ↑   ↑   ↑   ↑
              8   10  12  14

② 가 8 · 10 · 12 · 14 번으로 **간격 2 씩 네 번** 놓여 있었다. 여덟 번째
문항부터는 한 칸 건너 ② 라는 뜻이다.

왜 여덟 회차 동안 아무도 못 봤는가. G3d(주기)와 G3e(등간격)는 **한 배치
안에서만** 돈다. 이 14 제는 P16 열 문항과 마감 네 문항으로 나뉘어
만들어졌고,

    P16  (1~10번):  ④①④③①③③②④②   → ② 는 8·10 두 자리뿐
    마감 (11~14번): ④②①②             → ② 는 12·14 두 자리뿐

각 배치 안에서는 두 번씩이라 G3e 의 문턱(세 번)에 걸리지 않았다.
**두 배치 모두 결백한데 이어 붙인 자리에서만 샜다.** 검증 에이전트도
정답 차례를 보지 않는다 — solver 는 "정답 위치 분포 ①3②4③4④3, 편향
없음" 이라고 보고했다. 개수는 정말로 고르기 때문이다.

조치는 둘이다.

  ㉠ M01966 의 정답 자리를 ② → ① 로 옮긴다. ① 과 ② 의 문면·반박을
     통째로 맞바꾸는 것이라 내용은 한 글자도 달라지지 않는다.
     새 차례 ④①④③①③③②④①④②①② 에서 ② 는 8·12·14 번이 되어
     간격이 4·2 로 흩어진다. 다른 번호도 등차 줄이 남지 않는다.
     은행 정답 분포는 ①493 ②492 ③492 ④493 으로 편차 1 을 지킨다.
     길이순위도 2 위 그대로라 최근 100 제 분포가 흔들리지 않는다.

  ㉡ `batch_template.verify()` 에 **G3f 경계 검사**를 넣었다. 앞 배치
     꼬리 여덟 자리를 끌어와 이어 붙인 뒤 '같은 번호가 등차로 네 번
     이상' 을 본다. 배치 안 기준(세 번)보다 문턱을 올린 것은 창을 넓히면
     우연히 세 번 걸리는 일이 잦기 때문이다.

★교훈★ 도구가 보는 단위와 학생이 보는 단위가 다르면 그 틈으로 샌다.
도구는 '배치' 를 보고 학생은 '시험지' 를 본다. 배치를 쪼개어 만든 날은
쪼갠 자리가 곧 사각지대다.
"""
import json

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']

bank = json.load(open(BANK, encoding='utf-8'))
by = {x['id']: x for x in bank}


def swap_slots(it, i, j):
    """두 선지 자리를 문면·반박·오답메타까지 통째로 맞바꾼다.
    한쪽이 정답 자리여도 된다 — 정답 번호가 따라 옮겨 간다."""
    lines = it['solution'].split('\n')
    lead, diag = lines[0], [L for L in lines if L.startswith('자가진단:')][0]
    a = it['answer']
    head = f'[정답] {MK[a]} {it["choices"][a]} — '
    hit = [L for L in lines if L.startswith('[정답] ')]
    assert len(hit) == 1 and hit[0].startswith(head), it['id']
    cor = hit[0][len(head):]
    reb = {}
    for k in range(4):
        if k == a:
            continue
        pfx = f'{MK[k]} {it["choices"][k]}: '
        h = [L for L in lines if L.startswith(pfx)]
        assert len(h) == 1, (it['id'], k)
        reb[k] = h[0][len(pfx):]

    it['choices'][i], it['choices'][j] = it['choices'][j], it['choices'][i]
    reb[i], reb[j] = reb.get(j), reb.get(i)
    for k in (i, j):
        if reb[k] is None:
            del reb[k]
    if a == i:
        it['answer'] = j
    elif a == j:
        it['answer'] = i
    a = it['answer']
    for dd in it['distractors']:
        if dd['opt'] == i:
            dd['opt'] = j
        elif dd['opt'] == j:
            dd['opt'] = i
    it['distractors'].sort(key=lambda d: d['opt'])
    assert sorted(d['opt'] for d in it['distractors']) == sorted(set(range(4)) - {a}), it['id']
    body = [lead, '', f'[정답] {MK[a]} {it["choices"][a]} — {cor}', '']
    body += [f'{MK[k]} {it["choices"][k]}: {reb[k]}' for k in range(4) if k != a]
    body += ['', diag]
    it['solution'] = '\n'.join(body)


it = by['M01966']
assert it['answer'] == 1, it['id']
before = list(it['choices'])
swap_slots(it, 0, 1)
assert it['answer'] == 0 and it['choices'][0] == before[1] and it['choices'][1] == before[0]

seq = [by[f'M0{n}']['answer'] for n in range(1957, 1971)]
print('새 정답 차례:', ''.join(MK[v] for v in seq),
      '| 개수', {MK[v]: seq.count(v) for v in range(4)})

# 배치 안 등차 줄이 남지 않았는지 직접 확인한다(G3f 와 같은 규칙, 문턱 3).
bad = []
for d in (1, 2, 3, 4, 5):
    for i in range(len(seq)):
        if i - d >= 0 and seq[i - d] == seq[i]:
            continue
        L = 1
        while i + L * d < len(seq) and seq[i + L * d] == seq[i]:
            L += 1
        if L >= 3:
            bad.append((MK[seq[i]], d, [i + k * d + 1 for k in range(L)]))
print('등차 줄(3 이상):', bad if bad else '없음')
assert not bad

print('M01966 선지 길이', [len(c) for c in it['choices']], '정답', MK[it['answer']])
json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('9b 완료 — M01966 정답 자리 ② → ①')
