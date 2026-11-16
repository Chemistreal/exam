# -*- coding: utf-8 -*-
"""T16 P9 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-015', 2, 'M02543'), ('C16-015', 4, 'M02544'), ('C16-016', 1, 'M02545'),
        ('C16-016', 6, 'M02546'), ('C16-017', 4, 'M02547'), ('C16-018', 3, 'M02548'),
        ('C16-018', 5, 'M02549'), ('C16-020', 0, 'M02550'), ('C16-012', 3, 'M02551'),
        ('C16-014', 3, 'M02552')]

NOTES = {
    'C16-012': (
        "★저작 주의(T16 P9)★ 각도[3](세 성격을 전기음성도 차의 순서로)은 발문이 세 이름을 "
        "그대로 부르면 ★정답이 발문과의 어휘 겹침 최다★ 가 된다 — 차례를 묻는 물음의 꼴 자체가 "
        "정답에만 세 이름을 몰아 주기 때문이다. 발문을 '차가 0 인 결합 · 조금 있는 결합 · 아주 "
        "큰 결합' 처럼 ★차의 크기로만 적으면★ 겹침이 사라지고 이름은 정답 쪽에만 남는다"
        "(M02551). 다만 선지 넷을 세 이름의 순열로 채우면 오답끼리 자카드가 1.00 이 되므로, "
        "★오답은 자리를 말로 짚고(맨 앞·두 번째 자리) 정답만 이름을 늘어놓는다★."),
    'C16-020': (
        "★저작 주의(T16 P9)★ 각도[0](결합의 극성과 분자의 극성은 다른 층)은 반례로 이산화 "
        "탄소를 드는 순간 016 계열의 여러 각도와 겨냥이 겹친다(M02550 이 강한 충돌 1건으로 "
        "걸렸다). 이 각도를 다시 쓸 일이 있으면 ★사플루오린화 탄소나 삼플루오린화 붕소★ 처럼 "
        "다른 반례로 갈아 끼울 것."),
}


def main():
    cj = json.load(open(CJ, encoding='utf-8'))
    cs = {c['id']: c for c in cj[THEME]}
    n = 0
    for cid, idx, mid in LINK:
        a = cs[cid]['angles'][idx]
        a.setdefault('by', [])
        if mid not in a['by']:
            a['by'].append(mid)
            n += 1
    for cid, note in NOTES.items():
        old = cs[cid].get('note') or ''
        if note not in old:
            cs[cid]['note'] = (old + ' ' + note).strip()
    json.dump(cj, open(CJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    tot = sum(len(c['angles']) for c in cj[THEME])
    used = sum(1 for c in cj[THEME] for a in c['angles'] if a.get('by'))
    print('T16 P9 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
