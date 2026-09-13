"""T12 P15 4차 보정 — M01954 정답이 유일 최단이 되어 G3 에 걸렸다

4차에서 ④ 를 '속도가 절반이었을 수 있다'(29자)로 갈면서 ①②③④ = 25 · 28 · 28 · 29 가 되어
★정답 ① 이 홀로 가장 짧아졌다★ — 길이만 보고 짧은 것을 고르는 요령에 문이 열린다.
① 에 '애초에' 를 넣어 29 자로 맞춘다(④ 와 동률이라 최장도 아니게 된다).
문면 뜻도 오히려 또렷해진다 — 재는 도중이 아니라 ★재기 전부터★ 전자가 아니었다는 뜻이다.
"""
import json
import os

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')
MK = '①②③④'


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    d = {x['id']: x for x in bank}
    it = d['M01954']
    old, new = '그 금속에서 잰 것이 전자가 아니었을 수 있다', '그 금속에서 잰 것이 애초에 전자가 아니었을 수 있다'
    assert it['choices'][it['answer']] == old, it['choices']
    assert it['solution'].count(f'[정답] ① {old} — ') == 1
    it['choices'][it['answer']] = new
    it['solution'] = it['solution'].replace(f'[정답] ① {old} — ', f'[정답] ① {new} — ')
    it['answer_proof'] = it['answer_proof'].replace(
        '잰 대상을 먼저 의심해야 한다', '잰 대상이 애초에 전자였는지를 먼저 의심해야 한다')

    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
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
