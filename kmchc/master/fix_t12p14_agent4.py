"""T12 P14 4차 조치 — 오답 되돌림 1 · 문장 1

■ ★M01937 — 3차 조치가 만든 어긋남 + 귀속 오류 (factchecker ✗ · sim 제안, 근거가 다름)★
  3차에 ④ 를 '두 원소가 서로 만들 수 있는 화합물은 한 가지뿐이다' 로 바꿨는데
  ★본문의 소거 문장은 그대로 옛 ④(1 : 1)를 겨누고 있었다★ —
  "두 원소가 언제나 1 : 1 로 붙는다는 가정은 물이 H 둘에 O 하나라는 사실이 깨뜨렸어."
  H₂O 하나는 '화합물이 한 가지뿐'의 반례가 되지 못한다(오히려 한 가지의 예시다).
  ★그리고 sim 이 별개로 짚은 것 — '화합물은 한 가지뿐'을 돌턴에게 씌우는 것은 귀속 오류다.★
  배수 비례 법칙을 세운 사람이 돌턴이다. 돌턴이 실제로 세운 것은 최대 단순성 가정
  (화합물이 하나만 알려진 두 원소를 1 : 1 로 봄 — 그래서 물을 HO 로 적었다)이다.
  ④ 를 1 : 1 꼴로 되돌린다 — ★본문·반박·귀속 셋이 한 번에 맞는다.★
  자수는 32 자로 잡아 산포 0.18 을 지켰다(sim 이 낸 문면 그대로면 34 자라 0.25 를 넘는다).
  ▸ 1·2차의 '언제나 1 : 1 의 개수비로만 짝지어진다'와는 다르다 — 주어를 '화합물 속 원자들'로
    옮겨 배수 비례를 배운 학생이 실제로 반례를 떠올리게 했고, '만'을 걷어 극단어를 줄였다.

■ M01942 △ — '가시광선 안이라, 값도 판정도 어긋났어'에서 주어가 겹친다
  앞 절의 주어는 410, 뒤 절의 주어는 선지 ③ 이다. 끊어 준다.

■ solver 4차 '없습니다'(F1 0 · F5 0) · defender 4차 '없습니다' · factchecker ✗ 1 △ 1
■ 반려·기록
  ▸ sim 4차 — 죽은 선지 아홉 가운데 여덟은 sim 스스로 유지 권고했다.
    ★'응시자 4 명 · 선지 4 개라 완전순열이 아니면 죽은 선지가 산술적으로 불가피하다'★ 는
    방법론 경고를 sim 이 먼저 적었다. 앞으로 sim 의 죽은 선지 판정을 읽을 때 함께 볼 것.
  ▸ ★C = D 8/10 (3·4차 같음) — 배치 부채로 기록★ 변별이 M01941·M01943 둘에 몰려 있다.
    sim 은 M01943 ④('참이지만 이유가 못 되는' 극한 논거)를 날카롭게 다듬는 쪽을 지렛대로
    꼽으면서도 관문을 통과시키지 못해 정식 제안으로 올리지 않았다. ★T12 마감 4제와 P16 은
    상위권 변별 쪽으로 기울인다.★
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
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:30]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    d = {x['id']: x for x in bank}

    swap_choice(d['M01937'], 3, '화합물 속 원자들은 항상 1 : 1 의 개수비로 결합한다',
                '돌턴이 실제로 세운 어림이야 — 화합물이 하나만 알려진 두 원소를 가장 단순하게 '
                '1 : 1 로 보아 물을 HO 로 적었지. 그 어림은 폐기됐어. 물은 H 둘에 O 하나, '
                '암모니아는 H 셋에 N 하나거든.',
                '돌턴의 최대 단순성 가정을 지금도 유효한 것으로 봄', 'overgen')

    sub(d['M01942'], '게다가 410 은 400 보다 기니 가시광선 안이라, 값도 판정도 어긋났어.',
        '게다가 410 은 400 보다 기니 가시광선 안이고, 그래서 값도 판정도 어긋났어.')

    for x in bank:
        assert '**' not in x['stem'] and '**' not in x['solution'], x['id']
        assert '★' not in x['stem'] and '★' not in x['solution'], x['id']
    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    x = d['M01937']
    L = [len(c) for c in x['choices']]
    s = sorted(L)
    print('P14 4차 조치 완료 — 오답 되돌림 1 · 문장 1')
    print(f'  M01937 {L} 산포{(s[3]-s[0])/((s[1]+s[2])/2):.2f} '
          f'순위{sorted(range(4), key=lambda j: -L[j]).index(x["answer"])+1}')


if __name__ == '__main__':
    main()
