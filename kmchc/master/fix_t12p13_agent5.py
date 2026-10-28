"""T12 P13 (M01927~M01936) 층5 5차 순회 조치

solver 10/10 확실·"지금 고쳐야 하는 것 없음"(기록 5, 전부 조치 불필요) ·
defender "지금 고쳐야" 1건 · 구조 기록 5 ·
factchecker ✗0 · "지금 고치는 편이 나은 것" 3건 ·
sim D 이탈 0 · 죽은 선지 6.
★사실 오류는 세 회차 내리 0 이다.★

★채택 — defender '지금 고쳐야' 1건 (★4차 조치가 만든 자리★)★
  M01927 ② '전자는 두 준위 사이를 옮겨 가며 빛을 조금씩 내놓는다'
  ★"전자가 두 준위 사이를 옮겨 갈 때 빛을 내놓는다"는 보어의 둘째 가정 그 자체★ 라
  거짓이 부사 '조금씩' 하나에만 걸려 있다. 더 나쁜 것은 발문이 요구한 두 축 가운데
  ★'선스펙트럼' 쪽을 ② 가 가리킨다★ 는 점이다 — 잘 배운 학생일수록
  "선스펙트럼 = 준위 사이 전이"라는 도식으로 ② 에 끌린다(전형적 음변별).
  → '전자는 두 준위 사이를 옮길 때 빛을 ★이어진 띠로★ 내놓는다'
    이러면 ② 가 오히려 ★선스펙트럼을 부정★ 하게 되어, 발문의 두 축 가운데 어느 쪽도
    설명하지 못한다. solver 가 두 회차 짚은 "① 이 선스펙트럼을 절반만 설명한다"도 함께 닫힌다.

★채택 — factchecker 2건★
  (1) M01936 본문 "★두 자리는★ 세 칸에서 네 칸 떨어져 있지" — 같은 문단에서 '자리'가
      ★자릿수(서너 자리·한 자리)와 위치 두 뜻★ 으로 쓰인다. 자릿수를 세는 문항이라 읽기를 막는다.
      → '둘은'. 한 낱말 교체이고 현행보다 명확하다.
  (2) M01929 머리글 "두 실험이 ★곱해져야★ 비로소 질량이 나오는" — 이 문항의 오답 ③ 이
      정확히 '두 값을 곱한 것'이고 해설도 "질량은 나누어 얻지"라고 못 박는다.
      비유라도 ★하필 틀린 연산과 같은 낱말★ 이다. → '맞물려야'(본문의 '둘이 만나야'와도 맞는다).

★반려★
  (1) factchecker: M01928 본문이 '실제는 4 배'를 세우지 않은 채 오답 ③④ 가 그것을 쓴다 —
      ★4 배는 발문이 준다.★ factchecker 의 입력(items_solution.md)에는 발문이 들어 있지 않아
      생긴 착시다(3차에도 스스로 "발문을 못 봤으므로 문면 확정은 보류"라 적었다).
      ◆defender·solver 는 해설을 못 보고, factchecker 는 발문을 못 본다 —
        ★각 검증자의 '없다' 판정은 그 검증자가 보지 못하는 쪽에 대해서는 근거가 되지 않는다.★◆
  (2) sim: M01932 가 죽은 선지 둘(①④)이라 '유일한 위험 문항'이다 —
      ★같은 보고의 응답표가 A → ① 로 적혀 있다.★ ① 은 살아 있고 죽은 것은 ④ 하나뿐이라
      문항당 1개 허용 범위다. 게다가 제안한 교체(④ → 라이먼 > 파셴 > 발머)는
      ★sim 3차가 직접 경고한 첫 자리 다수결 누수★ 를 만든다(라이먼 선두 2표 → 정답 방향).
      쓸 수 있는 나머지 순열은 '파셴 > 라이먼 > 발머' 하나인데 그것은 ② 와 '파셴 최상위'가
      겹쳐 같은 병을 옮길 뿐이다.
  (3) sim: M01935 ③ · M01936 ① 이 죽었다 — ★2 × 2 격자를 지탱하는 자리★ 이고
      sim 4차 스스로 "채워 넣는 순간 다수결 축이 생긴다"고 적었다.
  (4) sim: M01929 가수 다수결 · M01934 되튐 칸만 검사 · 역순 쌍 규칙 —
      세 회차 내리 같은 지적이고, 앞선 회차에 각각 근거를 밝혀 반려했다.
  (5) factchecker: M01932 의 '발머는 가시광선' · M01930 의 '한계보다 짧은 파장은 없다' ·
      M01933 ④ 의 '아예 빛이 없어' · M01931 ② 의 '1, 2, 1' —
      factchecker 스스로 전부 '굳이 고칠 필요 없는 것'으로 갈랐다.
  (6) defender: M01929 ① · M01928 ④ · M01934 앞 요소 · M01935 ④ · M01936 ③ · M01933 ④ —
      defender 스스로 전부 '구조상 기록만'으로 갈랐다. 특히 ★M01934 에 '거짓 요소가 하나도 없는
      선지'는 이제 없다★ 고 확인했다(4차 조치가 먹혔다).
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
    ('M01936', 'solution', '두 자리는 세 칸에서 네 칸 떨어져 있지', '둘은 세 칸에서 네 칸 떨어져 있지'),
    ('M01929', 'solution', '두 실험이 곱해져야 비로소 질량이 나오는', '두 실험이 맞물려야 비로소 질량이 나오는'),
]


def main():
    bank = json.load(open(BJ, encoding='utf-8'))
    x = {i['id']: i for i in bank}
    ids = [f'M0{i}' for i in range(1927, 1937)]

    swap_choice(x['M01927'], 1, '전자는 두 준위 사이를 옮길 때 빛을 이어진 띠로 내놓는다',
                '그렇게 내놓으면 나오는 빛이 이어진 띠가 돼. 발문이 말한 띄엄띄엄한 '
                '선스펙트럼과 정면으로 어긋나지.',
                '전이 방출을 연속으로 봄 — 준위 차만큼을 한 번에 내놓는다', 'proc')

    miss = [(f, k, a[:26]) for f, k, a, _ in REPL if a not in x[f][k]]
    assert not miss, f'치환 대상 없음: {miss}'
    for f, k, a, b in REPL:
        x[f][k] = x[f][k].replace(a, b, 1)

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
        assert len(sol) >= 300, f'{fid}: 해설이 300자 미만 ({len(sol)})'
    assert Counter(x[f]['answer'] + 1 for f in ids) == Counter({1: 2, 2: 3, 3: 2, 4: 3})
    assert '조금씩' not in ' '.join(x['M01927']['choices']), 'M01927: 옛 문면 잔존'
    assert '곱해져야' not in x['M01929']['solution'], 'M01929: 옛 문면 잔존'

    json.dump(bank, open(BJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('P13 5차 조치 완료 — 오답 교체 1 · 본문 치환 2')
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
