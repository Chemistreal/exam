# -*- coding: utf-8 -*-
"""T12 마감 14제(M01957~M01970) 층5 순회 — 19차 조치 · 마감.

18차: **defender 0 건**(정답 붕괴 0 · 오답 승격 0). 17차에 갈아 끼운
M01961 ③ 을 파장·진동수·에너지·간격 네 축으로 각각 읽어 보고 어느
쪽으로도 참이 되지 않음을 확인했다. solver 도 정답 오류·복수정답·무정답·
계산 불일치 0 건이고, 포함 관계 쌍도 전 문항에서 사라졌다고 보고했다.

남은 둘만 닫는다. 하나는 17차 조치가 만든 것이고, 하나는 이 배치가
처음부터 안고 있던 문항 사이 모순이다.

────────────────────────────────────────────────────────────────
㉠ M01961 ③ — 주어를 생략해 '간격' 으로 읽으면 참이 된다 (solver 신규)
────────────────────────────────────────────────────────────────
17차판은 '선이 짧은 파장 쪽으로 끝없이 이어져 **0 에 다가간다**' 다.
주어가 '선' 이니 정상 독해는 '파장이 0 에 다가간다'(거짓)인데,
**선 사이 간격은 실제로 0 으로 수렴한다.** 생략된 주어를 '간격' 으로
잡으면 ③ 이 참이 되어 버린다.

→ '짧은 파장 쪽으로 선이 이어지며 **파장이** 0 에 다가간다' 로 주어를
박는다. 길이 30 이라 정답의 길이순위(1 위)도 그대로다.

★교훈★ 이 배치에서 오답이 참으로 읽힌 경로가 이제 넷이다 —
범위를 넓혀 읽기(M01966 ④) · 차 대신 비로 읽기(M01961 옛 ③) ·
교과서 관용으로 읽기(M01961 그다음 ③) · **주어를 바꿔 읽기(이번)**.
넷 다 '문장이 무엇을 주장하는지' 가 한 겹 열려 있어서 생겼다.
오답을 쓸 때 **주어와 잣대를 문장 안에서 닫아 둘 것.**

────────────────────────────────────────────────────────────────
㉡ M01970 발문이 M01961 의 정답과 어긋난다 (solver)
────────────────────────────────────────────────────────────────
M01970 발문은 "이 원자가 내는 발머 계열 선의 파장은 486 · 397 · 656 ·
410 · 434 nm 로 알려져 있다" 라고 적어 **계열을 다섯 개로 확정**한다.
그런데 M01961 의 정답은 "선이 무한히 많고 한 값에 모여든다" 이다.
두 발문이 같은 시험지에서 서로를 반증한다.

→ '발머 계열 선 가운데 다섯 개는 486 · 397 · 656 · 410 · 434 nm 다' 로
바꾼다. 397 nm 가 축 밖이라는 M01970 의 장치는 그대로 살아 있다.

★교훈★ 문항 사이 검사는 '정답이 새는가' 와 '함정이 새는가' 만 보아
왔는데, **한 문항의 발문이 다른 문항의 정답을 반증하는 경우**가 세 번째
유형으로 있었다. T13 저작 점검에 올린다.

────────────────────────────────────────────────────────────────
마감 부채로 넘기는 것
────────────────────────────────────────────────────────────────
· **발머 소재 4 중복**(M01961·M01963·M01967·M01970) — 한 테마의 마지막
  열네 자리에서 계열·파장을 네 번 다루면 서로가 서로의 발판이 된다.
  각도를 흩는 것은 배치 설계 단계의 일이라 여기서는 못 고친다.
  ★T13 부터: 한 배치에 같은 자료(같은 표·같은 축·같은 계열)를 세 번
  넘게 쓰지 말 것.★
· M01957 · M01959 의 '중복 도입절 쌍 안에 정답' — 짝짓기 문항에서 관찰이
  셋뿐일 때 구조적으로 생긴다. T13 짝짓기는 전제를 4 종으로 흩는다.
· M01962 ①·③ 의 '정확' 중복 — 7차 solver 는 ③ 에만 붙은 한정어를
  단서라 했고, 8차에 ① 에도 붙였더니 12·18차 solver 가 이번엔 겹친다고
  한다. 두 지적이 서로 반대 방향이라 어느 쪽으로 가도 한쪽이 남는다.
  defender 는 네 회차 내리 ○ 로 놓았다. 감사 몫으로 넘긴다.
· M01964 · M01965 의 낮은 변별 — 각각 상식 수준·연산 수준이다. T13 은
  개념 대장 단계에서 B(암기) 통과 각도를 27% 로 눌러 두었다.
"""
import json

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']

bank = json.load(open(BANK, encoding='utf-8'))
by = {x['id']: x for x in bank}


def parts(it):
    lines = it['solution'].split('\n')
    lead = lines[0]
    diag = [L for L in lines if L.startswith('자가진단:')][0]
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
    return lead, cor, reb, diag


def emit(it, lead, cor, reb, diag):
    a = it['answer']
    body = [lead, '', f'[정답] {MK[a]} {it["choices"][a]} — {cor}', '']
    body += [f'{MK[k]} {it["choices"][k]}: {reb[k]}' for k in range(4) if k != a]
    body += ['', diag]
    it['solution'] = '\n'.join(body)


def field(it, key, old, new):
    assert it[key].count(old) == 1, (it['id'], key)
    it[key] = it[key].replace(old, new)


def dmeta(it, idx, error=None, typ=None):
    for dd in it['distractors']:
        if dd['opt'] == idx:
            if error:
                dd['error'] = error
            if typ:
                dd['type'] = typ
            return
    raise AssertionError(f"{it['id']}: distractor {idx} 없음")


def retext(it, idx, new_txt, new_reb=None):
    assert idx != it['answer'], it['id']
    lead, cor, reb, diag = parts(it)
    it['choices'][idx] = new_txt
    if new_reb is not None:
        reb[idx] = new_reb
    emit(it, lead, cor, reb, diag)


def audit(it):
    lead, cor, reb, diag = parts(it)
    a = it['answer']
    for k in range(4):
        if k == a:
            continue
        for tail in ('가 옳아', '이 옳아', '가 맞아', '이 맞아'):
            assert MK[k] + tail not in cor, f"{it['id']}: 정답 본문에 {MK[k]}{tail}"
    assert (MK[a] + '가 옳아' in cor) or (MK[a] + '이 옳아' in cor), f"{it['id']}: 정답 번호 미표시"


def g3(it):
    L, a = [len(c) for c in it['choices']], it['answer']
    assert not (L[a] == max(L) and L.count(max(L)) == 1), f"{it['id']}: G3 유일최장"
    assert not (L[a] == min(L) and L.count(min(L)) == 1), f"{it['id']}: G3 유일최단"
    s = sorted(L)
    if (s[1] + s[2]) / 2 >= 8:
        sp = (s[3] - s[0]) / ((s[1] + s[2]) / 2)
        assert sp <= 0.25, f"{it['id']}: G3b 산포 {sp:.2f}"
    return L, sorted(range(4), key=lambda i: -L[i]).index(a) + 1


# ── ㉠ M01961 ③ : 주어를 문장 안에 박는다 ────────────────────────────
it = by['M01961']
retext(it, 2, '짧은 파장 쪽으로 선이 이어지며 파장이 0 에 다가간다',
       '선이 무한히 많다는 데까지는 맞아. 그런데 출발이 아무리 높아도 전이 에너지가 k/4 를 '
       '넘지 못하니 파장은 0 이 아니라 계열 한계에서 멎어. 0 으로 가는 것은 파장이 아니라 '
       '이웃한 두 선의 간격이지 — 그 둘을 섞지 말아야 해.')
dmeta(it, 2, error='선이 무한히 많으니 파장도 0 까지 작아진다고 봄 — 0 으로 가는 것은 간격이다',
      typ='scale')

# ── ㉡ M01970 발문 : 계열을 다섯으로 확정하지 않는다 ─────────────────
it = by['M01970']
field(it, 'stem', '이 원자가 내는 발머 계열 선의 파장은 486 · 397 · 656 · 410 · 434 nm 로 알려져 있다',
      '발머 계열 선 가운데 다섯 개는 파장이 486 · 397 · 656 · 410 · 434 nm 다')

for n in range(1957, 1971):
    x = by[f'M0{n}']
    audit(x)
    L, r = g3(x)
    assert len(x['solution']) >= 300, x['id']

m = by['M01961']
print(f'  M01961 길이 {[len(c) for c in m["choices"]]} · 순위 {g3(m)[1]}')
for k, c in enumerate(m['choices']):
    print(f'   {MK[k]} {c}')
print('  M01970 발문:', by['M01970']['stem'][:70], '…')

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('19차 조치 완료 — 마감 14제 닫음')
