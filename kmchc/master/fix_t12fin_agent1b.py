"""T12 마감 14제 1차 보정 — 1차 조치가 길이순위를 2 위에 몰아 놓았다

1차 조치로 선지 열둘을 갈면서 ★14 제 가운데 일곱이 길이순위 2 위★ 가 되었고
게이트가 '최근 100 제 2 위 36 % — 편중' 으로 경고했다. 세 문항을 옮겨 3·4·4·3 으로 편다.
◆규칙: 한 배치에서 선지를 여럿 갈면 ★배치 전체의 길이순위 분포★ 를 반드시 다시 볼 것.
  문항 하나하나는 G3·G3b 를 통과해도 배치가 한쪽으로 쏠릴 수 있다.◆

  M01958 ② 를 늘려 정답을 2 위 → 3 위로 ('정해진 궤도에서는' → '정해진 궤도에 있는 동안')
  M01967 ① 을 늘려 정답을 2 위 → 3 위로 ('쪽 끝의' → '쪽 끝자리의')
  M01962 ③ 을 늘려 정답을 2 위 → 1 위로 ('정확히 읽어 내는 일' → '눈금에서 정확히 읽는 일')
    — ④ 와 길이가 같아지므로 정답이 유일 최장이 되지는 않는다.
"""
import json
import os
from collections import Counter

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')


def swap_text(it, idx, old, new):
    assert it['choices'][idx] == old, (it['id'], it['choices'][idx])
    it['choices'][idx] = new
    if idx != it['answer']:
        mark = '①②③④'[idx]
        assert it['solution'].count(f'{mark} {old}: ') == 1, it['id']
        it['solution'] = it['solution'].replace(f'{mark} {old}: ', f'{mark} {new}: ')
    else:
        assert it['solution'].count(f'[정답] {"①②③④"[idx]} {old} — ') == 1, it['id']
        it['solution'] = it['solution'].replace(f'[정답] {"①②③④"[idx]} {old} — ',
                                                f'[정답] {"①②③④"[idx]} {new} — ')


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    d = {x['id']: x for x in bank}

    swap_text(d['M01958'], 1, '전자는 정해진 궤도에서는 빛을 내지 않는다',
              '전자는 정해진 궤도에 있는 동안 빛을 내지 않는다')
    swap_text(d['M01967'], 0, '발머 계열의 선이 모여드는 쪽 끝의 파장이다',
              '발머 계열의 선이 모여드는 쪽 끝자리의 파장이다')
    swap_text(d['M01962'], 2, '수소의 어느 선이 몇 nm 인지 정확히 읽어 내는 일',
              '수소의 어느 선이 몇 nm 인지 눈금에서 정확히 읽는 일')

    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ranks = []
    for i in range(1957, 1971):
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
