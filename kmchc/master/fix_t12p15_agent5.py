"""T12 P15 5차 조치 — 내용은 닫혔고 남은 것은 형태 3 : 1 둘과 내가 쓴 엉터리 판별 기준 하나

★5차 성적표★ defender 조치 0건 · factchecker 지금 고쳐야 0 · 두고 볼 것 0 · 참고 1건 ·
solver 내용 결함(복수정답·무정답·미정의 기호) 0건. ★실체는 닫혔다.★
남은 것은 solver 의 형태 단서 넷(두고 볼 것 2 · 참고 2)과 factchecker 의 참고 하나뿐이다.

■ ★M01956 — 4차에 내가 써 넣은 판별 기준이 실제로는 갈라 주지 않는다 (factchecker 참고)★
  '4 × 10⁻⁷ 도 자릿수로 재면 10⁻⁷ 보다 10⁻⁶ 쪽이 가까워 — ★열 배 안에 드는지로 가르면
  되거든★' 이라고 적었는데, 4 × 10⁻⁷ 은 10⁻⁶ 과도 10⁻⁷ 과도 ★둘 다 열 배 안★ 이라
  이 기준으로는 아무것도 갈리지 않는다. 결론은 맞고 근거만 헛돈다.
  ★학생이 그대로 외우면 다른 문항에서 오판한다★ — 참고 등급이지만 고친다.
  실제 판별은 배수 견줌이다: 10⁻⁶ 까지 2.5 배, 10⁻⁷ 까지 4 배.
  ◆규칙: 해설에 ★판별 기준★ 을 새로 만들어 붙일 때는 그 기준을 문제의 값에 실제로 넣어
    갈라지는지 해 볼 것. 결론이 맞으면 근거도 맞다고 여기기 쉽다.◆

■ M01954 — ★정답만 숫자가 없다★ (solver 2 회차 연속, 4차엔 다른 갈래로 같은 3 : 1)
  ②(개수 절반) ③(질량 두 배) ④(속도 절반)은 모두 수치 변형 가설인데 ① 만 숫자 없는
  정성 진술이라, 화학 없이 ★홀로 튀는 ①★ 이 뽑힌다.
  ▸ ★정답과 ③ 은 건드리지 않는다.★ ① 은 4차에 이미 한 번 손댔고(G3 최단 보정),
    ③ 은 defender 가 두 회차 연속 '산술적으로 정합한 최강 경쟁자'로 평가했다.
  ▸ ④ 의 '절반' 만 걷어 ★①④ 정성 · ②③ 수치의 2 : 2★ 로 만든다. ④ 가 겨누는 오개념은
    '속도가 비전하 값에 들어간다'이지 '정확히 절반'이 아니므로 매력은 그대로다.

■ M01949 — ★어미 3 : 1 이 세 회차째 축을 바꿔 되살아난다★ (solver 3·4·5 회차 연속)
  3차: ① 만 유보형 → ① 을 단정형으로. 4차: ②③④ 가 "X이니 Y다" → ③④ 어미를 흩음.
  5차: ②③④ 가 여전히 "…이므로/이니 …이다" 과잉추론형이고 ① 만 담백한 서술이다.
  ★고칠 때마다 축이 옮겨 다니는 데는 까닭이 있다.★ 이 각도(C12-028[1])는 ★정답이 표가
  무엇인가를 말하고 오답은 모두 표에서 끌어낸 잘못된 추론★ 이라, 추론에는 추론 구문이 붙는다.
  ▸ 그래서 이번에는 ★오답 하나를 서술문으로 돌려 2 : 2 를 만든다.★ ③ 을 고른 까닭은
    defender 가 이번 회차에 ③ 을 '논리적으로 무효한 함의'라 하여 셋 가운데 가장 약하게
    본 자리이기 때문이다. 겨누는 오개념(준위의 부호)은 문면에 그대로 남는다.
  ▸ solver 의 ① 교체안은 반려한다 — ★50 자에 이르러 ②(39 자)를 훌쩍 넘어 G3 최장★ 이 되고,
    4차에 defender 의 지적을 닫으려고 넣은 '칸 이름' 이 그 안에서 흐려진다.
  ▸ ★이번에도 3 : 1 이 남으면 더 쫓지 않고 각도에 붙박인 구조로 기록해 마감할 것.★
    세 회차를 고쳐 축만 옮겨 다녔다는 사실 자체가 그 진단의 근거다.

■ ★반려 — 근거와 함께★
  ▸ solver 'M01951 ① 의 셋째 칸을 ④ 와 같은 양성자로'(참고) — 격자는 더 깔끔해지지만
    ★sim 이 4차에 이 ① 을 성공으로 판정했고(C 가 실제로 물었다), M01951 은 이 배치에서
    C ≠ D 인 단 하나의 문항★ 이다. 살아 있는 데다 유일한 상위권 변별점인 선지를
    형태 휴리스틱 하나 때문에 갈지 않는다.
  ▸ solver 'M01948 ① 을 관 속 기체 실험으로'(참고) — 첫 회차 지적이고, 새 문면은
    ★톰슨의 네 실험 밖의 다섯째 실험★ 을 끌어들이면서 ④ 의 정량 불변성 결과 겹친다.
    ① 은 sim 표에서 B 가 무는 살아 있는 선지다.
  ▸ defender 'M01954 ③ 을 전하 절반으로'(참고) — ③ 은 sim 4차에서 B 가 물었다.
    바꿀 까닭이 약하고, 4차에 없앤 ③④ 쌍둥이 구도를 되부를 위험이 있다.
  ▸ defender 'M01955 ② 를 실제로 퍼져 있는 정도로'(참고) — 앞 절이 이미 경계면을 말하므로
    혼동 가능성이 낮다고 defender 자신이 적었다. ②(정답) 를 또 건드리는 값어치가 없다.
"""
import json
import os

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


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    d = {x['id']: x for x in bank}

    # ══ M01949 ─ ③ 을 서술문으로 돌려 어미 2 : 2 ═══════════════════════════
    swap_choice(d['M01949'], 2, '수소의 에너지 준위 역시 표의 값과 마찬가지로 모두 양수다',
                '표에 적힌 것은 차의 크기야. 수소의 준위 값은 −1312/n² 로 모두 음수지.')

    # ══ M01954 ─ ④ 의 수치를 걷어 ①④ 정성 · ②③ 수치의 2 : 2 ═══════════════
    swap_choice(d['M01954'], 3, '그 금속에서는 음극선이 유난히 느리게 날아왔을 수 있다',
                '비전하는 알갱이 하나가 지닌 값이라 얼마나 빨리 달리는지와는 상관없어. '
                '톰슨도 전기장과 자기장을 함께 걸어 속도를 먼저 알아낸 뒤에 비전하를 구했지.')

    # ══ M01956 ─ 갈라 주지 않는 판별 기준을 배수 견줌으로 ═══════════════════
    sub(d['M01956'],
        '4 × 10⁻⁷ 도 자릿수로 재면 10⁻⁷ 보다 10⁻⁶ 쪽이 가까워 — 열 배 안에 드는지로 '
        '가르면 되거든.',
        '4 × 10⁻⁷ 도 자릿수로 재면 10⁻⁷ 보다 10⁻⁶ 쪽이 가까워 — 10⁻⁶ 까지는 2.5 배, '
        '10⁻⁷ 까지는 4 배니까 몇 배 차이인지로 견주면 되거든.')

    for x in bank:
        assert '**' not in x['stem'] and '**' not in x['solution'], x['id']
        assert '★' not in x['stem'] and '★' not in x['solution'], x['id']

    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('P15 5차 조치 완료 — 오답 교체 2 · 해설 1')
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
