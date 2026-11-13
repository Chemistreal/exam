"""T12 P15 2차 조치 — 복수정답 1 · 발문 3 · 오답 교체 4 · 해설 2

■ ★복수정답 — M01952 (defender '지금 고쳐야')★
  발문이 "화살표를 15 개 표시해 두었다"고만 하고 ★어느 15 개인지 지정하지 않았다.★
  21 가지 가운데 임의의 6 개가 빠질 수 있고, n = 6·7 에서 출발하는 전이가 11 가지이므로
  ★빠진 여섯이 모두 출발 6 또는 7 인 배치가 실제로 가능하다★ — 그러면 ①('출발 준위가
  n = 5 보다 높다')도 참이 된다. 정답 ②는 '그려진 15 개가 도착 1·2·3 전부'라는
  ★말하지 않은 전제★ 에 기대고 있었다.
  발문에 ★'라이먼·발머·파셴 세 계열에 드는 전이만 빠짐없이 그렸다'★ 를 넣어 도형을 못 박는다.
  계열 이름으로 적었으므로 학생은 여전히 계열 → 도착 준위를 옮겨야 한다.
  ▸ 곁들여 ① 을 ★'모두 도착 준위가 n = 1 로 같은 전이다'★ 로 바꾼다. 이것도 정확히 여섯
    가지라, solver 가 재현한 ★'각 선지가 가리키는 집합의 크기만 세면 된다'★ 는 요령이 닫힌다
    (11 / 6 / 1 / 4 였다). 그리고 도착 1 = 라이먼 = 그려진 쪽이라 확실히 거짓이다.

■ 형태 단서 셋 (solver — 지난 회차 9/10 이 5/10 로 줄었고 남은 것을 마저 닫는다)
  ▸ M01951 ★발문의 '중성자를 예상하기까지' 가 마지막 칸을 그대로 알려 준다.★
    끝에 '전하 없는 입자'를 둔 선지가 ③ 하나뿐이라 위치 대응만으로 확정됐다.
    발문을 '헬륨과 수소의 질량을 견준 논증' 으로 바꿔 결론을 감춘다.
  ▸ M01949 발문이 '조심해야 할 것'을 물어 ★한계 진술인 ① 이 곧 정답★ 이었다.
    발문을 '이 표에 대한 설명으로 옳은 것은?' 으로 중립화한다.
    ▸ 남는 부채: ① 만 '알려 주지 않는다' 꼴이다. ②③④ 가 모두 표를 잘못 믿는 서로 다른
      방식이라 축이 셋으로 갈리므로 다수결은 서지 않는다. 감사에서 다시 볼 것.
  ▸ M01948 ①③ 이 ★서로 오른쪽 반쪽을 맞바꾼 교차 쌍★ 이라 함께 소거됐다.
    ③ 의 뒷짝을 '음극선은 관 속 기체에서 나온다' 로 바꿔 교차를 끊는다.
    ★factchecker 의 △ 도 같은 자리에서 풀린다★ — 지금 ③ 반박의 '휘었다는 것은 곧게 가지
    않았다는 뜻이잖아' 는 본문이 그림자 실험으로 세워 둔 참인 명제('곧게 나아간다')를
    조건 없이 부정하는 꼴이었다. 뒷짝이 실제로 거짓이 되면 그 부정이 필요 없어진다.

■ 죽은 선지 교체 둘 (sim — 네 관문을 통과한 것만)
  ▸ M01954 ② '전하가 절반' → '나온 전자의 개수가 절반이다'
    ②(전하 절반)와 ③(질량 두 배)이 ★'금속마다 전자의 고유 성질이 다르다'는 하나의 오개념을
    두 벌로 적은 쌍둥이★ 라 짝 소거를 열어 두고 있었다. 개수 오독으로 바꾸면
    ①② 가 '잰 쪽 의심', ③④ 가 '금속 의존'이 되어 ★2 : 2★ 가 서고,
    solver 가 짚은 '②③④ 가 한 축이고 ① 만 밖'이라는 3 대 1 분리도 함께 닫힌다.
    거짓 근거: 비전하는 ★알갱이 하나당★ 값이라 개수와 무관하다(교과서 정의 한 줄).
  ▸ M01949 ④ '어느 쪽이 쉬운지 알 수 있다' → '3 → 5 는 값이 양수이니 저절로 일어난다'
    앞엣것은 대응하는 실제 오개념이 없어 구조적으로 비어 있었다. 새 문면은 준위가 올라가는
    전이라 흡수가 필요하다는 교재 서술로 곧바로 거짓이 된다.

■ 해설 손질 (factchecker △)
  M01954 ★양극선 예시의 규모가 본문의 '절반'과 어긋난다★ — 양극선(무거운 이온)의 비전하는
       수소 이온 기준 1/1836 수준이라 2 분의 1 을 설명하지 못한다. 규모를 빼고 완화한다.

■ 반려
  ▸ solver — M01956 '지수 비교만으로 풀린다': 0.4 ~ 0.7 μm 를 10⁻⁶ 자릿수로 옮기는 한 걸음이
    든다. ★이 각도(C12-N04[7])가 재는 것이 지수 비교 그 자체★ 이고 쉬움 문항이다.
  ▸ solver — M01955 '발문이 앞 축(커진다)을 결정한다': 앞 축이 상식으로 정해지는 것은
    이 문항이 ★뒷 축(분포 불변)★ 에 무게를 싣기 때문이고, 그 뒷 축이 이 각도가 재려는 것이다.
    sim 표에서도 C 가 ① 로 갈려 변별이 살아 있다.
  ▸ sim — 죽은 선지 아홉 가운데 일곱은 sim 스스로 '표본 탓'으로 유지 권고했고,
    M01955 ④ 는 2 × 2 격자가 요구하는 칸이라 '죽은 채로 두는 것이 정상'이라 적었다.
  ▸ factchecker — M01949 ② 에 '값만으로는' 을 한 번 더 박자: ② 는 '값이 같으니'로 이미
    시작한다. 같은 말을 두 번 넣으면 문면만 길어진다.
  ▸ factchecker — M01955 ③ 반박이 경계면 방향만 다룬다: ①④ 가 분포 축을 각각 맡고 있어
    셋을 합치면 두 축이 모두 덮인다(factchecker 도 '감점 아님'으로 닫았다).

■ ★C = D 7/10 (1·2차 같음)★ — 갈린 셋(M01950·M01952·M01955)은 모두
  '그 사실이 어디까지를 보증하는가'를 묻는다. P14 의 8/10 보다 낫다.
"""
import json, os

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')
MK = '①②③④'


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


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:32]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


def stem(it, old, new):
    assert it['stem'].count(old) == 1, it['id']
    it['stem'] = it['stem'].replace(old, new)


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    d = {x['id']: x for x in bank}

    # ══ M01948 ─ ③ 뒷짝 교체(교차 쌍 끊기 + factchecker △) ═══════════════
    swap_choice(d['M01948'], 2, '전기장 속에서 (+)극 쪽으로 휜다 — 음극선은 관 속 기체에서 나온다',
                '휘어짐이 말해 주는 것은 전하의 부호야. 그리고 음극선은 관 속 기체가 아니라 '
                '음극에서 나와 — 이름이 그래서 음극선이지.',
                '뒷짝 자체가 거짓 — 음극선은 음극 금속에서 나온다', 'sign')

    # ══ M01949 ─ 발문 중립화 + ④ 교체 ════════════════════════════════════
    it = d['M01949']
    stem(it, '이 표를 읽을 때 조심해야 할 것으로 옳은 것은?', '이 표에 대한 설명으로 옳은 것은?')
    swap_choice(it, 3, '3 → 5 는 표의 값이 양수이니 저절로 일어나는 전이다',
                '3 → 5 는 준위가 올라가는 전이야. 저절로 일어나는 것이 아니라 그만큼을 '
                '흡수해야 하지. 값이 양수인 것은 차의 크기를 적었기 때문이고.',
                '표의 값이 양수인 것을 전이가 저절로 일어난다는 뜻으로 읽음', 'sign')

    # ══ M01951 ─ 발문에서 결론 낱말 감추기 ═══════════════════════════════
    stem(d['M01951'], '중성자를 예상하기까지는', '헬륨과 수소의 질량을 견준 논증은')

    # ══ M01952 ─ 발문에 도형을 못 박고 ① 을 같은 개수의 오답으로 ══════════
    it = d['M01952']
    stem(it, '일곱 준위를 그리고 아래로 향하는 화살표를 15 개 표시해 두었다',
         '일곱 준위를 그리고, 라이먼·발머·파셴 세 계열에 드는 방출 전이만 빠짐없이 화살표로 '
         '그려 15 개를 표시해 두었다')
    swap_choice(it, 0, '모두 도착 준위가 n = 1 로 같은 전이다',
                '도착이 1 인 전이는 곧 라이먼 계열이라 그림에 이미 다 그려져 있어. 개수는 '
                '여섯으로 맞지만 빠진 쪽이 아니라 그려진 쪽이지.',
                '개수만 맞춰 그려진 쪽(라이먼)을 빠진 쪽으로 봄', 'proc')
    sub(it, '나머지를 왜 못 쓰는지도 확인해 두자. 빠진 것에는 5 → 4 가 들어 있으니 출발이 '
            '5 보다 높다고 할 수 없어. 그 5 → 4 의 에너지 차는',
        '나머지를 왜 못 쓰는지도 확인해 두자. 도착이 1 인 것은 라이먼 계열이라 이미 그려진 '
        '쪽이고, 개수만 여섯으로 같을 뿐이야. 빠진 것 가운데 5 → 4 의 에너지 차는')

    # ══ M01954 ─ ② 교체 + 양극선 예시 완화 ═══════════════════════════════
    it = d['M01954']
    swap_choice(it, 1, '그 금속에서 나온 전자의 개수가 절반이다',
                '비전하는 알갱이 하나의 전하를 그 하나의 질량으로 나눈 값이야. 몇 개가 '
                '나왔는지는 값에 들어가지 않아 — 개수가 줄면 세기가 약해질 뿐이지.',
                '한 알갱이당 값인 비전하를 흐름의 세기와 뒤섞음', 'proc')
    sub(it, '실제로 이런 일이 있어. 방전관에서는 전자 말고 양극선이라는 무거운 이온의 흐름도 '
            '생기는데 그것을 재면 비전하가 훨씬 작게 나오거든.',
        '실제로 이런 일이 있어. 방전관에서는 전자 말고 이온의 흐름도 함께 생기는데, 전자가 '
        '아닌 것이 섞여 들면 잰 값이 달라지거든.')

    for x in bank:
        assert '**' not in x['stem'] and '**' not in x['solution'], x['id']
        assert '★' not in x['stem'] and '★' not in x['solution'], x['id']

    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('P15 2차 조치 완료 — 발문 3 · 오답 교체 4 · 해설 2')
    from collections import Counter
    ranks = []
    for i in range(1947, 1957):
        x = d[f'M0{i}']
        L = [len(c) for c in x['choices']]
        s = sorted(L)
        sp = (s[3] - s[0]) / ((s[1] + s[2]) / 2)
        rk = sorted(range(4), key=lambda j: -L[j]).index(x['answer']) + 1
        ranks.append(rk)
        flag = '' if (sp <= 0.25 or s[1] < 8) else '  ← G3b'
        if L[x['answer']] == s[3] and L.count(s[3]) == 1:
            flag += '  ← G3 최장'
        if L[x['answer']] == s[0] and L.count(s[0]) == 1:
            flag += '  ← G3 최단'
        print(f'  {x["id"]} {L} 산포{sp:.2f} 순위{rk}{flag}')
    print('  길이순위', dict(sorted(Counter(ranks).items())))


if __name__ == '__main__':
    main()
