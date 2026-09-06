"""T12 P12 (M01917~M01926) 층5 5차 순회 조치

solver 10/10 확실 "확신도가 낮거나 자족성이 미흡한 문항: 없습니다" ·
defender "심각한 F2 실패 후보는 없습니다"(후보 4건 모두 하 이하) ·
factchecker ✗0 △2 · sim D 이탈 0 · 죽은 선지 8(전부 문항당 1개, 허용 범위).
다섯 회차 내리 D 이탈 0 이고, 이번 회차에는 ★사실 오류도 F2 도 없다.★
남은 넷은 모두 문면을 더 정확하게 만드는 손질이다.

★채택 4건★
  (1) solver: M01926 이 "에너지(k 단위)"라고만 적어 ★문항 안에서 k 가 정의되지 않는다.★
      비례관계만 쓰면 풀리므로 결함은 아니나 독립 문항으로 보면 미정의 기호다.
      → 발문 앞에 "수소 원자의 이온화 에너지를 k 라 하자"를 놓는다.
      준위식(−k/n²)을 주지 않으므로 ★불변량을 스스로 찾는다★ 는 이 문항의 축은 그대로다.
      (k = 1312 kJ/mol 이 곧 수소의 이온화 에너지이므로 M01925 의 k 정의와도 맞물린다.)
  (2) factchecker △1: M01923 ③ 반박의 "122 nm 보다 훨씬 짧아" — 라이먼 한계는 약 91 nm 로
      25% 짧을 뿐인데, 같은 문단이 122 nm ↔ 400~700 nm 라는 큰 격차를 다룬 직후라
      '훨씬'이 그 규모로 읽힌다. → ★"약 91 nm 라 122 nm 보다 더 짧아"★
      4차에 91.1 이라는 세 자리 수를 뺀 것은 은행 전역 상수(91.1)와 통용값(91.2)의 어긋남을
      피하기 위해서였는데, ★두 자리(약 91 nm)로 적으면 그 문제가 아예 생기지 않는다.★
  (3) factchecker △2: M01921 ③ 반박 "두 배로 오래 쬐면 전자가 두 배" — 앞 문단이
      "세기를 올리면 전자 수가 두 배"라고 말한 직후라 ★시간과 세기가 뭉뚱그려진다.★
      1초에 나오는 수는 그대로라는 점을 문면에 놓는다.
  (4) sim: M01923 ② '도로 흡수되어서 자리가 밀려났기 때문이다' 는 ★3·4·5차 내리 죽었다.★
      defender 도 3·4차에 ⑥ 유형(종속절이 참)으로 올렸던 자리다(5차엔 '확실히 틀림'으로 내렸다).
      sim 이 낸 대체안이 세 기준을 모두 통과한다 —
      → '그 선 하나만 내놓는 에너지가 가장 작은 전이이기 때문이다'
        ① 122 nm 는 다섯 가운데 ★에너지가 가장 큰★ 전이이므로 확실히 거짓
        ② ①(외부 오염)·③(출발 준위 혼동)과 오류 갈래가 겹치지 않는다
        ③ 32자로 ①33·③32·④32 와 정합
      게다가 ★에너지–파장 반비례를 뒤집어 아는 오개념★ 은 이 단원 최다 오개념의 하나다.

★반려★
  (1) solver: M01925 의 k = 1312 삭제 — ★다섯 회차 같은 제안.★ 선지가 k 단위라
      지우면 미정의 기호가 된다. 오히려 이번에 M01926 쪽에 k 정의를 넣어 둘을 맞춘다.
  (2) solver: M01925 의 분수를 M01926 처럼 기약분수로 — 분모 225 통일은 ★네 오답이
      25−9 · 25 · 2/15 · 25+9 라는 서로 다른 셈에서 나왔음을 견주게 하려는 것★ 이다.
      약분하면 둘만 약분되고 둘은 아니어서 약분 여부가 새 형식 단서가 된다(3차 sim 지적과 같다).
  (3) defender: M01918 ③ '빠르게 돌아 흐릿하게 보인다' 가 교과서 문구와 겹친다 —
      ★같은 자리·같은 논거로 네 회차 연속이고 심각도가 높음 → 하 → 확실히 틀림 → 중하로
      오르내렸다.★ 5차 자신도 "확실히 틀린 이유"를 적고 권고를 '(선택)'으로 달았다.
      제안한 대체("궤도가 눈에 안 보일 만큼 작아서")는 ★sim 이 이 단원 최다 오개념으로
      꼽은 자리를 더 드문 오개념으로 바꾸는 것★ 이라 순손실이다. 지침 (hh).
  (4) sim: M01922 ① 을 '밝은 곳에 전자가 더 많이 모여 쌓였기 때문이다' 로 —
      ★그 문장은 참이다.★ 회절 무늬에서 밝은 곳에 전자가 실제로 더 많이 쌓인다.
      sim 이 스스로 확인하라고 받은 기준 (1)을 통과하지 못한다. 현행 ① 은 defender 가
      다섯 회차 내리 '확실히 틀림'으로 분류했다.
  (5) sim 형식 요령 7: M01926 은 곱을 셈하지 않아도 E 의 간격이 매끄럽지 않아 셋째 줄이
      드러난다 — ★간격이 매끄럽게 벌어져야 한다는 것을 알려면 발머 계열의 구조를 알아야 한다.★
      그것은 형식이 아니라 물리 지식이고, 이 문항이 반기는 두 번째 풀이 길이다.
      아울러 간격의 단조성까지 지키려면 어긋뜨린 값이 0.175~0.198 안에 들어야 하는데,
      그러면 곱이 91.1 에서 4% 안쪽으로 붙어 ★② 반박이 기대는 반올림 폭과 구별되지 않는다.★
  (6) factchecker(참고): M01917 의 '원자가 수천 겹' 이 실제(약 1000~2000층)보다 넉넉하다 —
      factchecker 자신이 "국내 교과서 통용 범위 안이고 논증이 이 숫자에 의존하지 않아
      지적하지 않았다"고 적었다.
"""
import json, os

BJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')
MK = '①②③④'


def swap_choice(it, idx, new_txt, new_rebut, err, typ):
    mark = MK[idx]
    old = it['choices'][idx]
    assert idx != it['answer'], f"{it['id']}: 정답 자리는 이 헬퍼로 바꾸지 않는다"
    lines = it['solution'].split('\n')
    hit = [i for i, L in enumerate(lines) if L.startswith(f'{mark} {old}:')]
    assert len(hit) == 1, f"{it['id']}: 해설 {mark} 줄을 못 찾음"
    lines[hit[0]] = f'{mark} {new_txt}: {new_rebut}'
    it['solution'] = '\n'.join(lines)
    it['choices'][idx] = new_txt
    for dd in it['distractors']:
        if dd['opt'] == idx:
            dd['error'], dd['type'] = err, typ
            break
    else:
        raise AssertionError(f"{it['id']}: distractor {idx} 없음")


REPL = [
    # (1) M01926 — 문항 안에서 k 를 정의한다
    ('M01926', 'stem',
     '수소 발머 계열 네 선의 에너지(k 단위)와 파장(nm)을 옮겨 적었더니',
     '수소 원자의 이온화 에너지를 k 라 하자. 발머 계열 네 선의 에너지(k 단위)와 '
     '파장(nm)을 옮겨 적었더니'),

    # (2) M01923 ③ — '훨씬'을 두 자리 수치로 바꾼다 (은행 전역 상수와 부딪히지 않는다)
    ('M01923', 'solution',
     '출발이 n = ∞ 인 전이는 라이먼 계열의 한계라 122 nm 보다 훨씬 짧아. '
     '이 다섯 선에는 없지.',
     '출발이 n = ∞ 인 전이는 라이먼 계열의 한계로 약 91 nm 라 122 nm 보다 더 짧아. '
     '이 다섯 선에는 없지.'),

    # (3) M01921 ③ — 시간과 세기가 뭉뚱그려지지 않도록 초당 방출률을 적는다
    ('M01921', 'solution',
     '③ 빛을 쬐는 시간을 두 배로 한다: 두 배로 오래 쬐면 튀어나오는 전자가 두 배가 될 뿐이야. '
     '하나하나의 몫은 그대로지.',
     '③ 빛을 쬐는 시간을 두 배로 한다: 두 배로 오래 쬐면 그동안 나온 전자를 다 합쳐 두 배가 '
     '될 뿐이야. 1초에 나오는 수도, 하나하나의 몫도 그대로지.'),
]


def main():
    bank = json.load(open(BJ, encoding='utf-8'))
    x = {i['id']: i for i in bank}
    ids = [f'M0{i}' for i in range(1917, 1927)]

    # (4) M01923 ② — 세 회차 내리 죽은 자리를 에너지·파장 반비례 역전 오개념으로 갈아 끼운다
    swap_choice(x['M01923'], 1, '그 선 하나만 내놓는 에너지가 가장 작은 전이이기 때문이다',
                '파장이 가장 짧은 선이 에너지는 가장 커. 122 nm 는 다섯 가운데 '
                '내놓는 에너지가 가장 큰 전이야.',
                '에너지와 파장을 반비례가 아니라 비례로 읽음 — 122 nm 가 에너지 최대다', 'sign')

    miss = [(f, k, a[:30]) for f, k, a, _ in REPL if a not in x[f][k]]
    assert not miss, f'치환 대상 없음: {miss}'
    for f, k, a, b in REPL:
        x[f][k] = x[f][k].replace(a, b, 1)

    # ── 자기 검사 ────────────────────────────────────────────────
    from collections import Counter
    for fid in ids:
        it = x[fid]
        sol = it['solution']
        for k, c in enumerate(it['choices']):
            if k == it['answer']:
                assert f'[정답] {MK[k]} {c} —' in sol, f'{fid}: [정답] 줄 어긋남'
            else:
                assert f'{MK[k]} {c}:' in sol, f'{fid}: {k + 1} 번 줄 어긋남'
        assert sorted(d['opt'] for d in it['distractors']) == \
            sorted(k for k in range(4) if k != it['answer']), f'{fid}: 오답 자리 어긋남'
        assert '★' not in it['stem'] and '★' not in sol, f'{fid}: 강조 기호 잔존'
        assert '**' not in sol, f'{fid}: 굵게 기호 잔존'
        assert len(sol) >= 300, f'{fid}: 해설이 300자 미만'
    assert Counter(x[f]['answer'] + 1 for f in ids) == Counter({1: 3, 2: 2, 3: 3, 4: 2})
    assert 'k 라 하자' in x['M01926']['stem'], 'M01926: k 정의가 들어가지 않았다'
    assert '훨씬 짧아' not in x['M01923']['solution'], 'M01923: 옛 문면 잔존'

    json.dump(bank, open(BJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('P12 5차 조치 완료 — 오답 교체 1 · 발문/본문 치환 3')
    for fid in ids:
        L = [len(c) for c in x[fid]['choices']]
        s = sorted(L)
        sp = (s[3] - s[0]) / ((s[1] + s[2]) / 2)
        r = sorted(range(4), key=lambda i: -L[i]).index(x[fid]['answer']) + 1
        flag = ''
        if L[x[fid]['answer']] == max(L) and L.count(max(L)) == 1:
            flag = ' G3-최장'
        if L[x[fid]['answer']] == min(L) and L.count(min(L)) == 1:
            flag = ' G3-최단'
        if sp > 0.25 and s[1] >= 8:
            flag += ' G3b'
        print(f'  {fid} {L} 산포{sp:.2f} 순위{r}{flag}')


if __name__ == '__main__':
    main()
