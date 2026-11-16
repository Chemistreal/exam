# -*- coding: utf-8 -*-
"""T16 P11 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-020', 1, 'M02563'), ('C16-020', 2, 'M02564'), ('C16-020', 3, 'M02565'),
        ('C16-020', 5, 'M02566'), ('C16-020', 6, 'M02567'), ('C16-018', 1, 'M02568'),
        ('C16-018', 4, 'M02569'), ('C16-018', 6, 'M02570'), ('C16-016', 5, 'M02571'),
        ('C16-014', 6, 'M02572')]

NOTES = {
    'C16-020': (
        "★저작 주의(T16 P11)★ 이 개념에서 한 배치에 다섯 각도를 뽑았더니 ★자리 이름(scenario)이 "
        "겹쳐 selfaudit 가 R1 강한 충돌을 넷 냈다★ — '한 학생의 표현' 같은 ★두루뭉술한 자리 "
        "이름은 곧바로 앞 문항과 부딪친다★. 자리 이름에 그 문항만의 낱말을 넣을 것('염화 나트륨을 "
        "분자로 부른 표현' · '결합이라는 이름에 이끌린 표현'). ▸ 남은 각도는 [4](성질에서 결합을 "
        "되돌릴 때의 한계) 하나인데 ★P10 M02553(C16-019[1])과 겨냥이 거의 같다★ — 다시 쓰려면 "
        "물음의 꼴을 바꿔야 한다."),
    'C16-018': (
        "★소진 알림(T16 P11)★ 일곱 각도가 모두 소진됐다. [1] 은 M02568 이 ★메테인★ 을 반례로, "
        "[4] 는 M02569 가 ★족을 밝히지 않고 '어떤 족'★ 으로 물어 값 누출을 피했다."),
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
    print('T16 P11 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
