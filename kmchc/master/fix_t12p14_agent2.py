"""T12 P14 2차 조치 — 오답 교체 3 · 정답 자리 2 · 해설 다수

■ ★가장 큰 것 — M01942 의 둘째 축이 죽어 있었다 (solver)★
  1차에 defender·solver·sim 이 함께 요구해 발문에 '가시광선 400 ~ 700 nm' 를 못 박았다.
  그런데 그 순간 ★후보 파장 397 과 365 가 둘 다 400 미만★ 이 되어, ②④('가시광선 안')가
  ★계산을 하지 않고도 발문과 모순되어 소거★ 됐다. 경계를 못 박아 복수정답은 막았는데
  같은 손으로 판정 축을 죽인 것이다 — 조치가 만든 흠의 또 한 사례.
  ③④ 의 365 nm 를 ★410 nm★ 로 바꾼다. 410 은 발문의 표에 이미 실린 6 → 2 선이고
  (출발 준위를 하나 잘못 센 학생이 고를 값), ★400 ~ 700 안에 들어와 판정 축이 되살아난다.★
  이제 ① 은 값·판정 둘 다 맞고, ② 는 값만 맞고, ④ 는 판정만 맞고, ③ 은 둘 다 틀리다.
  ▸ 잃은 것: 365 nm(계열 한계)를 오답으로 쓰는 자리. 해설 본문에는 남겨 두었다.

■ ★사실 오류 하나 — M01941 정답 문단 (factchecker)★
  '전자가 하나뿐이면 헬륨 이온에도 ★그대로★ 통하고' 라고 적었는데, He⁺ 는 Z² = 4 배라
  Eₙ = −1312/n² 을 값까지 그대로 쓸 수는 없다(바닥 준위 −5248 kJ/mol).
  ① 반박은 '핵전하만 바꿔 넣으면' 이라 조건을 달아 두었으니 ★같은 해설 안에서 어긋났다.★
  1차에 내가 쓴 자리다. 정답 문단 쪽에 같은 조건을 넣어 맞춘다.

■ ★한 번호가 고른 간격으로만 나온다 — ① 이 2·6·10 (solver)★
  전체 차례는 주기가 없어 G3d 에 걸리지 않았지만, ★① 만 따로 보면 정확히 4 간격★ 이다.
  M01945 와 M01946 의 정답 자리를 각각 ①↔③ 으로 맞바꾼다 — ★둘 다 2 × 2 격자지만
  대각 맞바꿈이라 두 축의 2 : 2 가 그대로 보존된다.★
  차례가 3-1-4-3-2-1-2-4-1-3 이 되어 ① 은 2·6·9, ③ 은 1·4·10 으로 간격이 흩어진다.
  ▸ 같은 검사를 도구에 넣었다(G3e) — 한 번호가 세 번 이상 나오면서 간격이 모두 같으면 잡는다.

■ 형식 단서 둘 (solver)
  ▸ M01937 ★정답에만 극단어가 없어 극단어 배제만으로 100 % 뚫린다★
    ①'가장 작은' · ②'모두 똑같다' · ④'언제나 … 만' 대 ③ 평서. ② 에서 '모두'를 걷어
    극단어를 2 : 2 로 만든다('같은 원소의 원자는 서로 질량이 같고 성질도 같다').
    동위원소가 질량을 깨뜨리므로 문면은 그대로 거짓이다.
  ▸ M01940 ★두 절로 된 선지가 정답뿐★ — 1차에 ① 을 고쳤지만 겹주어 한 절이라 여전했다.
    '(+)전하가 고르게 퍼져 있고 질량도 함께 퍼져 있다' 로 실제 두 절로 만든다(①③ : ②④ = 2 : 2).

■ 해설 손질 (factchecker)
  M01937 ④ 반박이 ★'언제나 1 : 1' 을 돌턴의 주장으로 그대로 승인★ 했다 — 최대 단순성은
       '화합물이 하나만 알려진 두 원소' 에 건 조건부 가정이다. 한정을 넣는다.
       · 불가분성이 무엇에 깨졌는가를 본문(전자)과 ① 반박(전자·양성자·중성자)이 달리 적었다.
  M01938 ★'①이 옳아' 가 문단 안에서 자기부정으로 읽힌다★ — 선지 문면은 '부호는 (−)이다'
       인데 같은 문단이 '부호는 알 수 없어' 로 닫는다. 다른 아홉 문항은 'X 가 옳아 = X 는 참'
       으로 쓰므로 이 문항만 뜻이 뒤집힌다. '그래서 답이 ①이야' 로 바꾼다.
       · '전기적인 끌힘이 아니야' — 미는 힘과 대비하려면 인력만 들어서는 어긋난다.
  M01940 1/8000 이 '큰 휨'의 비율인지 '되튐'의 비율인지 M01939 와 나란히 읽으면 흐려진다.
  M01944 '새 상수가 드는 것' → '필요한 것'.

■ 반려
  ▸ solver — M01945 ④ 를 극단진술 아닌 것으로 교체
    ④ 는 (한쪽만 ①② : 둘 다 ③④) 격자의 '둘 다' 칸이다. 그리고 ③ 의 '~할수록' 은
    ★맞바꿈 관계를 서술하는 말 자체★ 라, 오답에 정도 표현을 넣으면 오히려 참이 되기 쉽다
    (solver 가 낸 예 '두 오차의 곱이 0 에 가까워진다'는 부호만 뒤집힌 참 문장에 가깝다).
    defender 는 ①②④ 를 모두 '중하 · 두어도 됨' 으로 닫았다.
  ▸ defender 2차 '지금 고쳐야: 없습니다' · solver F1 0 · F5 0 · factchecker ✗ 0
"""
import json, os

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')
MK = '①②③④'
PART = {0: '이', 1: '가', 2: '이', 3: '가'}


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


def swap_choice(it, idx, new_txt, new_reb, err=None, typ=None):
    assert idx != it['answer'], it['id']
    lead, cor, reb, diag = parts(it)
    it['choices'][idx] = new_txt
    reb[idx] = new_reb
    emit(it, lead, cor, reb, diag)
    for dd in it['distractors']:
        if dd['opt'] == idx:
            if err:
                dd['error'] = err
            if typ:
                dd['type'] = typ
            break
    else:
        raise AssertionError(f"{it['id']}: distractor {idx} 없음")


def swap_positions(it, i, j):
    old_a = it['answer']
    assert old_a in (i, j), it['id']
    lead, cor, reb, diag = parts(it)
    it['choices'][i], it['choices'][j] = it['choices'][j], it['choices'][i]
    new_a = j if old_a == i else i
    reb[old_a] = reb.pop(new_a)
    it['answer'] = new_a
    old_tok, new_tok = f'{MK[old_a]}{PART[old_a]} 옳아', f'{MK[new_a]}{PART[new_a]} 옳아'
    assert cor.count(old_tok) == 1, (it['id'], cor[-40:])
    cor = cor.replace(old_tok, new_tok)
    for dd in it['distractors']:
        dd['opt'] = j if dd['opt'] == i else (i if dd['opt'] == j else dd['opt'])
    it['distractors'].sort(key=lambda d: d['opt'])
    emit(it, lead, cor, reb, diag)


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:30]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    d = {x['id']: x for x in bank}

    # ══ M01937 ══════════════════════════════════════════════════════════
    it = d['M01937']
    swap_choice(it, 1, '같은 원소의 원자는 서로 질량이 같고 성질도 같다',
                '동위원소가 이 문장을 깼어. 양성자 수는 같아도 중성자 수가 다르면 질량이 달라.')
    swap_choice(it, 3, '두 원소가 언제나 1 : 1 의 개수비로만 짝지어진다',
                '돌턴은 화합물이 하나만 알려진 두 원소를 1 : 1 로 두었어 — 가장 단순한 쪽으로 '
                '어림한 거지. 그 어림은 폐기됐고, 선지처럼 "언제나"로 넓히면 더욱 거짓이야. '
                '물은 H 둘에 O 하나, 암모니아는 H 셋에 N 하나거든.')
    sub(it, '원자를 더 쪼갤 수 없다는 말은 톰슨이 전자를 찾아내면서 무너졌어.',
        '원자를 더 쪼갤 수 없다는 말은 전자와 원자핵이 잇달아 발견되면서 무너졌어.')

    # ══ M01938 ══════════════════════════════════════════════════════════
    it = d['M01938']
    sub(it, '그러니 부호는 이 실험으로 알 수 없어 — ①이 옳아.',
        '그러니 부호는 이 실험으로 알 수 없어 — 그래서 답이 ①이야.')
    sub(it, '밀어내는 힘은 부딪혀서 생긴 것이지 전기적인 끌힘이 아니야.',
        '바람개비를 민 힘은 부딪혀서 생긴 것이지 전기력이 당기거나 밀어서 생긴 것이 아니야.')

    # ══ M01940 ══════════════════════════════════════════════════════════
    it = d['M01940']
    swap_choice(it, 0, '알파 입자가 거의 다 지나갔으니 원자에는 무거운 것이 없다',
                '통과 쪽만 읽고 내린 결론이야. 8000 개에 1 개꼴로 되튄 것이 바로 알파 입자보다 '
                '무거운 것이 원자 속에 있다는 증거지.',
                '두 결과 가운데 통과 쪽만 읽어 되튐을 셈에 넣지 않음', 'proc')
    sub(it, '다음으로 8000 개에 1 개꼴로 크게 튕겼어.',
        '다음으로 8000 개에 1 개꼴로 크게 되튀어 나왔어.')

    # ══ M01941 ══════════════════════════════════════════════════════════
    it = d['M01941']
    swap_choice(it, 0, '헬륨 이온 He⁺ 에는 이 모형의 준위 식이 전혀 맞지 않는다',
                'He⁺ 는 전자가 하나뿐인 수소꼴 이온이야. 핵전하가 두 배인 만큼 준위가 네 배 '
                '깊어질 뿐 식의 꼴은 그대로지 — 가르는 것은 원소 이름이 아니라 전자의 개수야.',
                '한정을 원소 이름으로 읽어 전자 하나짜리 이온까지 배제함', 'overgen')
    sub(it, '전자가 하나뿐이면 헬륨 이온에도 그대로 통하고',
        '전자가 하나뿐이면 헬륨 이온에도 핵전하만 바꿔 넣으면 그대로 통하고')

    # ══ M01942 ─ ③④ 의 365 → 410 ═══════════════════════════════════════
    it = d['M01942']
    swap_choice(it, 2, '약 410 nm 이고, 발머 계열이지만 가시광선 영역에는 들지 않는다',
                '410 nm 는 발문의 표에 이미 실려 있는 6 → 2 짜리야. 출발을 7 이 아니라 6 으로 '
                '센 값이지. 게다가 410 은 400 보다 기니 가시광선 안이고 — 값도 판정도 어긋났어.',
                '출발 준위를 하나 잘못 세어 표에 실린 6 → 2 값을 답으로 삼음', 'proc')
    swap_choice(it, 3, '약 410 nm 이고, 발머 계열이므로 가시광선 영역 안에 놓여 있다',
                '판정은 맞았어 — 410 nm 는 가시광선 안이 맞지. 다만 그 값은 표에 실린 6 → 2 '
                '선이고, 7 → 2 는 그보다 짧은 397 nm 야.',
                '값은 표의 6 → 2 를 가져오고 판정만 그 값에 맞게 함', 'proc')
    it['answer_proof'] = it['answer_proof'].replace(
        '365 nm 는 ∞ → 2, 곧 발머 계열의 한계 파장이다',
        '410 nm 는 표에 이미 실린 6 → 2 선이고, 발머 계열의 한계 파장은 ∞ → 2 의 365 nm 다')
    sub(it, '365 nm 쪽으로 촘촘히 모여들고', '한계인 365 nm 쪽으로 촘촘히 모여들고')

    # ══ M01943 ─ ④ 극한 오답을 발문 수치로 즉사하지 않게 ═══════════════
    swap_choice(d['M01943'], 3,
                'm 이 아주 커지면 두 값 가운데 하나가 0 에 한없이 가까워지기 때문이다',
                '합이 k 인 것은 극한과 상관이 없어. m = 2 에서 두 값은 3/4 k 와 1/4 k 로 '
                '어느 쪽도 0 이 아닌데 합은 이미 k 야. 모든 m 에서 그대로 성립하지.',
                '모든 m 에서 성립하는 항등식을 극한 현상으로 읽음', 'proc')

    # ══ M01944 ══════════════════════════════════════════════════════════
    sub(d['M01944'], '할 일은 둘인데 새 상수가 드는 것은 하나야.',
        '할 일은 둘인데 새 상수가 필요한 것은 하나야.')

    # ══ M01945 · M01946 ─ ① 의 4 간격 깨기 (대각 맞바꿈, 격자 보존) ═══════
    swap_positions(d['M01945'], 0, 2)
    swap_positions(d['M01946'], 0, 2)

    for x in bank:
        assert '**' not in x['stem'] and '**' not in x['solution'], x['id']
        assert '★' not in x['stem'] and '★' not in x['solution'], x['id']

    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('P14 2차 조치 완료 — 오답 교체 3 · 정답 자리 2 · 해설 다수')
    seq, ranks = [], []
    for i in range(1937, 1947):
        x = d[f'M0{i}']
        L = [len(c) for c in x['choices']]
        s = sorted(L)
        sp = (s[3] - s[0]) / ((s[1] + s[2]) / 2)
        rk = sorted(range(4), key=lambda j: -L[j]).index(x['answer']) + 1
        seq.append(x['answer'] + 1)
        ranks.append(rk)
        flag = '' if (sp <= 0.25 or s[1] < 8) else '  ← G3b'
        if L[x['answer']] == s[3] and L.count(s[3]) == 1:
            flag += '  ← G3 최장'
        if L[x['answer']] == s[0] and L.count(s[0]) == 1:
            flag += '  ← G3 최단'
        print(f'  {x["id"]} 정답{MK[x["answer"]]} {L} 산포{sp:.2f} 순위{rk}{flag}')
    from collections import Counter
    print('  정답 차례', '-'.join(map(str, seq)))
    for v in set(seq):
        pos = [k for k, a in enumerate(seq) if a == v]
        gaps = {pos[k + 1] - pos[k] for k in range(len(pos) - 1)}
        print(f'   {MK[v-1]} 자리 {[p+1 for p in pos]} 간격 {sorted(gaps)}'
              + ('  ← 고른 간격' if len(pos) >= 3 and len(gaps) == 1 else ''))
    print('  길이순위 분포', dict(sorted(Counter(ranks).items())))


if __name__ == '__main__':
    main()
