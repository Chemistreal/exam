"""T12 P15 6차 조치 — 실체는 두 회차째 0건, 남은 둘은 내가 앞 회차에 만든 형태 흠이다

★6차 성적표★ defender 조치 0건 · factchecker 조치 0건 · solver ★내용 결함 0건★
(복수정답·무정답·미정의 기호 모두 0). sim 은 M01954·M01955 에서 ★완전순열★ 을 냈다.
남은 것은 solver 의 형태 단서 넷뿐이고, ★그 가운데 둘은 4·5차 조치가 만든 되튐★ 이다.

■ M01956 — ★내가 4차에 넣은 선지가 자릿수를 오름차순으로 만들어 버렸다★ (solver 두고 볼 것)
  ② 를 원자핵(10⁻¹⁴)에서 사람 세포(10⁻⁵)로 갈면서 선지 지수가
  ★10⁻¹⁰ → 10⁻⁵ → 10⁻⁴ → 10⁻⁶★ 이 되었다. 셋이 오르다 넷째에서 깨지므로
  ★'차례를 깨는 하나가 정답'★ 이 화학 지식 0 으로 성립한다. 4차 이전에는
  10⁻¹⁰ → 10⁻¹⁴ → 10⁻⁴ → 10⁻⁶ 으로 흩어져 있어 이 단서가 없었다.
  ▸ solver 는 크기순 단조 배열을 냈으나 ★그러면 정답이 ② 로 옮겨 가 은행의 정답 분포
    (①489 ②489 ③489 ④489, 편차 0)가 깨진다.★ 대신 ①② 를 맞바꿔 다시 흩는다 —
    10⁻⁵ → 10⁻¹⁰ → 10⁻⁴ → 10⁻⁶ 은 오르내림이 두 번 뒤집혀 차례 단서가 없다.
    두 선지 모두 오답이라 정답 자리는 그대로다.
  ◆규칙: 수치가 붙은 선지를 갈아 끼운 뒤에는 ★네 값의 차례가 무슨 모양이 되었는지★ 를
    반드시 다시 볼 것. 값 하나를 고치면 배열 전체가 바뀐다.◆

■ M01955 — ★5차에 ④ 를 고치면서 ① 과 '그만큼' 을 나눠 갖게 됐다★ (solver 참고)
  ①('오비탈 자체도 ★그만큼★ 커진 것이 된다')과 ④('어느 자리에서든 확률이 ★그만큼★ 커진다')이
  한 낱말을 공유해 ★쌍으로 함께 지워지고★, 남은 ③ 은 '아예' 라는 전면부정이라
  형태만으로 ② 가 남는다. ④ 의 '그만큼' 을 '함께' 로 바꿔 쌍을 깬다.
  ▸ ★defender 의 경고를 지킨다★ — ④ 에서 '어느 자리에서든' 을 빼면 안 된다.
    그것을 빼고 '안쪽에서 확률이 커진다' 로 줄이면 ★집계 독해(90 % → 99 %)로 참이 되어★
    복수정답이 된다. 전칭 표현이 방어의 핵심이다.
  ▸ 그리고 ③ 만 ★상태 진술★ 이었다 — 발문이 '어떻게 되는가' 를 묻는데 '볼 수 없다' 로 끝난다.
    5차에 옛 ④ 를 고치며 세운 규칙(발문이 변화를 물으면 선지도 모두 변화를 말할 것)을
    ③ 에도 적용해 '아예 못 보게 된다' 로 맞춘다. ★이제 네 선지가 모두 변화 서술이다.★

■ ★반려 — 근거와 함께★
  ▸ sim 'M01952 ③ 은 채점 여유가 한 전이 차이뿐이다' — ★정량 오독이다.★ 직접 검산했다:
    7→6 0.0074k · 6→5 0.0122k · 7→5 0.0196k · 5→4 0.0225k · 6→4 0.0347k · 7→4 0.0421k.
    k/100 미만은 7→6 하나이고 ★나머지 다섯이 반례★ 다. 선지가 '모두' 라는 전칭이므로
    반례 하나면 거짓이 확정되는데, sim 은 그것을 '여유가 얇다' 로 뒤집어 읽었다.
    defender 와 factchecker 도 같은 수를 내고 각각 '우수한 함정' · ○ 로 판정했다.
  ▸ sim 'M01949 ③ 은 실패, 교체할 것' — ★5차에 sim 스스로 이 선지를 성공(A 가 물었다)으로
    판정했고, 5차 조치는 문면의 ★어미만★ 바꾸었을 뿐 내용(준위의 부호)은 그대로다.★
    내용이 같은데 판정이 뒤집혔으니 회차 간 흔들림이다. sim 이 이번에 든 근거('준위는 음수는
    암기층도 안다')는 5차에도 똑같이 적용됐어야 한다.
  ▸ sim 'M01956 ③(머리카락)은 ② 와 같은 방향이라 죽었다' — ★5차에 sim 이 이 선지를
    "나노↔마이크로 접두어 혼동으로 정확히 도달하는 살아 있는 선지" 로 판정했다.★
    무엇이 달라졌는지 밝히지 않은 뒤집기다. 위 ①② 맞바꿈으로 같은 방향 둘이 이웃하지
    않게 되므로 지적의 실질도 완화된다.
  ▸ solver·sim 'M01953 ① 을 3 : 2 로 되돌릴 것' — ★두 검증자가 같은 회차에 같은 제안을
    했으나 반려한다.★ 3 : 2 를 뺀 것은 4차에 sim 이 낸 ★결정적 논리★ 때문이다 —
    발문이 발머(2)를 먼저 파셴(3)을 나중에 적으므로 선형 비 오류는 언제나 2 : 3 을 낳고
    3 : 2 는 어순 때문에 아무도 고를 수 없다. ★죽은 선지를 되살리는 되돌림이다.★
    거울쌍이 하나뿐이라 50 % 로 좁혀지는 것은 사실이나, solver 자신이 다른 문항의
    50 % 압축은 '허용 범위' 로 놓았다.
  ▸ solver 'M01953 발문에서 k 정의를 지울 것' — ★solver 는 4차와 5차에 이 k 를 두 번
    명시적으로 무해하다고 판정했다★("학생이 k/4 · k/9 를 세우게 하는 유효한 발판이므로
    결함이 아닙니다"). 6차에만 뒤집혔다.
  ▸ solver 'M01948 ④ 만 앞뒤 절이 메아리친다' — ★각도에 붙박인 성질이다.★ 이 문항의 관찰은
    '금속을 바꿔도 비전하가 같다'(불변)이고 결론은 '늘 같은 알갱이다'(동일성)인데,
    ★불변과 동일성은 뜻이 서로 묶여 있어 어떻게 적어도 메아리가 남는다.★ 짝짓기형에서
    옳은 짝만 앞뒤가 맞물리는 것은 문항 유형 자체의 성질이기도 하다.
    solver 의 대안(③ 을 '(+)극에서 나온다' 로)은 ★sim 표에서 B 가 무는 살아 있는 선지★ 를
    없애고 잔류기체설이라는 실재 오개념을 잃는다. 마감 부채로 적어 둔다.
  ▸ sim 'M01951 ④'(우선순위 낮음이라 스스로 적음) · 'M01947 ①④'(유지 판정) — 조치 없음.

■ ★기록해 둘 것 — C = D 는 8/10 이나 속이 달라졌다★
  sim: 이번 두 불일치(M01954 · M01955)는 ★직전 회차에 새로 넣은 선지가 C 를 정확히 낚은 것★ 이고,
  두 문항 모두 네 응시자가 서로 다른 선지로 흩어진 ★완전순열★ 이다. 앞 회차의 불일치가
  문면의 애매함에서 왔던 것과는 성질이 다르다. ★상위권 변별 부채가 조금 갚였다.★
  ▸ 다만 sim 이 붙인 단서: M01954 ④(속도)를 문 것은 A 가 아니라 B 이고, 그것도 톰슨 장치
    서술에 '속도' 라는 낱말이 들어 있어 생긴 ★어휘 우연★ 이다. 다음 감사에서 재점검할 것.
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


def swap_two_distractors(it, i, j):
    """오답 두 자리를 통째로 맞바꾼다 — 정답 자리는 건드리지 않는다."""
    a = it['answer']
    assert i != a and j != a, it['id']
    lead, cor, reb, diag = parts(it)
    it['choices'][i], it['choices'][j] = it['choices'][j], it['choices'][i]
    reb[i], reb[j] = reb[j], reb[i]
    for dd in it['distractors']:
        if dd['opt'] == i:
            dd['opt'] = j
        elif dd['opt'] == j:
            dd['opt'] = i
    it['distractors'].sort(key=lambda dd: dd['opt'])
    emit(it, lead, cor, reb, diag)


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    d = {x['id']: x for x in bank}

    # ══ M01955 ─ ①④ 의 '그만큼' 쌍을 깨고 ③ 도 변화 서술로 ═══════════════
    it = d['M01955']
    swap_choice(it, 3, '경계면이 커지고, 안쪽 어느 자리에서든 확률이 덩달아 커진다',
                '담는 확률이 늘어난 것은 더 넓게 둘러쌌기 때문이지 자리마다의 확률이 커져서가 '
                '아니야. 각 자리의 확률은 그대로고, 그것을 더 넓은 범위에서 모았을 뿐이지.')
    swap_choice(it, 2, '경계면이 커지고, 그 바깥에서 전자를 아예 못 보게 된다',
                '경계면은 넘지 못하는 벽이 아니야. 99 % 로 잡아도 남은 1 % 는 그 바깥에 있으니 '
                '전자가 없는 자리가 되는 것이 아니지.')

    # ══ M01956 ─ ①② 를 맞바꿔 자릿수 오름차순을 흩음 ═══════════════════════
    it = d['M01956']
    before = [c[-8:] for c in it['choices']]
    swap_two_distractors(it, 0, 1)
    print('  M01956 지수 차례', ' → '.join(before), '⇒', ' → '.join(c[-8:] for c in it['choices']))

    for x in bank:
        assert '**' not in x['stem'] and '**' not in x['solution'], x['id']
        assert '★' not in x['stem'] and '★' not in x['solution'], x['id']

    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('P15 6차 조치 완료 — 오답 문면 2 · 오답 자리 맞바꿈 1')
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
