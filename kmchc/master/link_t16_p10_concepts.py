# -*- coding: utf-8 -*-
"""T16 P10 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-019', 1, 'M02553'), ('C16-019', 2, 'M02554'), ('C16-019', 3, 'M02555'),
        ('C16-019', 4, 'M02556'), ('C16-019', 5, 'M02557'), ('C16-019', 6, 'M02558'),
        ('C16-017', 1, 'M02559'), ('C16-017', 5, 'M02560'), ('C16-017', 6, 'M02561'),
        ('C16-013', 6, 'M02562')]

NOTES = {
    'C16-013': (
        "★소진 알림(T16 P10)★ [6](결합 에너지로 안정함을 단정하지 않기)까지 M02562 가 가져가면서 "
        "★쓰기로 한 [4][5][6] 이 모두 소진됐다★. 남은 [0][1][2][3] 은 C16-001[5]·005[2] 와 겨냥이 "
        "겹치므로 마감 때 ★겹침을 풀어 다시 적기 전에는 쓰지 않는다★."),
    'C16-017': (
        "★저작 주의(T16 P10)★ 각도[5](끓는점으로 결합의 세기를 재지 않기)를 물을 때 발문에 "
        "'분자' 를 쓰면 ★정답이 발문과의 어휘 겹침 최다★ 로 걸린다 — 정답이 '끊어지는 쪽은 분자 "
        "사이의 힘' 이라고 말할 수밖에 없기 때문이다. 발문의 미룸을 '그 안의 결합' 으로 적어 "
        "'분자' 를 비켜 두었다(M02560). 겹침은 '것은' 같은 ★군더더기 낱말에서도 생기므로★ 정답의 "
        "꼬리말을 발문과 다르게 둘 것('것은' → '쪽은')."),
    'C16-019': (
        "★소진 알림(T16 P10)★ 이 개념의 일곱 각도가 M02553~M02558 여섯과 앞서의 [0] 으로 "
        "★모두 소진됐다★. 되돌리기 계열을 더 쓸 자리는 C16-020 쪽에만 남아 있다."),
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
    print('T16 P10 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
