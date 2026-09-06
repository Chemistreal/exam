# -*- coding: utf-8 -*-
"""anspick — 다음 배치의 ★정답 자리 열★ 을 미리 고른다

  쓰임:  python3 anspick.py [문항수]        (기본 10)

  ★왜 도구로 두는가★ — 배치마다 손으로 셈하던 자리다. 그런데 손 셈은 두 번 샜다.
    ① T22 P14 에서 G3f 의 간격을 range(1,5) 로 보아 ★간격 5 사슬을 놓쳤다★.
       게이트는 for d in (1, 2, 3, 4, 5) 다.
    ② 배치 안 등간격(G3e)은 세 번, 꼬리를 잇는 등차(G3f)는 네 번 — 문턱이 서로 다르다.
    이 파일은 batch_template 의 검사와 ★같은 코드를 다시 적지 않고★ 규칙만 옮겨 놓되,
    문턱과 간격 범위를 게이트와 나란히 둔다. 고칠 일이 생기면 두 곳을 함께 고칠 것.

  고르는 차례
    1. 은행 꼬리 8 자리를 읽는다(G3f 가 보는 창과 같다).
    2. 네 번호가 2 개 또는 3 개씩 들도록 자리 수를 나눈다 — 은행 편차를 키우지 않는다.
    3. G3d(주기) · G3e(배치 안 등간격 3 연) · G3f(꼬리까지 잇는 등차 4 연, 간격 1~5) ·
       G3h(주기 되풀이 (2,4)/(3,3)/(4,2)) 를 모두 넘는 열만 남긴다.
    4. 남은 열 가운데 ★같은 번호가 잇달아 오는 자리가 적은★ 것부터 보여 준다.
"""
import json
import os
import random
import sys
from collections import Counter
from itertools import product

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')
CIR = '①②③④'


def g3d(seq):
    for p in (2, 3, 4, 5):
        if len(seq) >= 2 * p and all(seq[k] == seq[k % p] for k in range(len(seq))):
            return False
    return True


def g3e(seq):
    for v in set(seq):
        pos = [k for k, a in enumerate(seq) if a == v]
        if len(pos) >= 3 and len({pos[k + 1] - pos[k] for k in range(len(pos) - 1)}) == 1:
            return False
    return True


def g3h(seq):
    for per, need in ((2, 4), (3, 3), (4, 2)):
        L = per * need
        for i in range(len(seq) - L + 1):
            if all(seq[i + k] == seq[i + k % per] for k in range(L)):
                return False
    return True


def g3f(seq, tail):
    ext, off = list(tail) + list(seq), len(tail)
    for d in (1, 2, 3, 4, 5):                     # ★게이트와 같은 범위 — 5 까지★
        for i in range(len(ext)):
            if i - d >= 0 and ext[i - d] == ext[i]:
                continue
            L = 1
            while i + L * d < len(ext) and ext[i + L * d] == ext[i]:
                L += 1
            if L >= 4 and i + (L - 1) * d >= off:
                return False
    return True


def runs(seq):
    return sum(1 for i in range(len(seq) - 1) if seq[i] == seq[i + 1])


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    bank = json.load(open(BANK, encoding='utf-8'))
    tail = [x['answer'] for x in bank][-8:]
    #  ★아직 병합하지 않은 배치를 꼬리에 이어 붙인다★ — 배치 셋을 ★동시에★ 지으려면 P12 의 열을
    #  고를 때 P11 의 열이 이미 꼬리에 있어야 한다(G3f 는 꼬리 여덟을 넘어 잇는 등차를 본다).
    #    쓰임:  python3 anspick.py 10 2432341413        (앞 배치 열을 자리표 숫자로 이어 준다)
    if len(sys.argv) > 2:
        for ch in sys.argv[2]:
            if ch in '1234':
                tail.append(int(ch) - 1)
        tail = tail[-8:]
    dist = Counter(x['answer'] for x in bank)
    print('  은행 %d제 · 분포 %s' % (len(bank), ' '.join(
        '%s%d' % (CIR[v], dist[v]) for v in range(4))))
    print('  꼬리 8 자리 %s' % '-'.join(str(a + 1) for a in tail))

    lo, hi = n // 4, (n + 3) // 4
    good = []
    rnd = random.Random(0)
    for seq in product(range(4), repeat=n):
        c = Counter(seq)
        if any(not lo <= c[v] <= hi for v in range(4)):
            continue
        if not (g3d(seq) and g3e(seq) and g3h(seq) and g3f(seq, tail)):
            continue
        good.append(seq)
    rnd.shuffle(good)
    good.sort(key=runs)
    print('  통과한 열 %d 가지 — 잇단 자리가 적은 차례로 다섯 가지' % len(good))
    for seq in good[:5]:
        c = Counter(seq)
        print('    %s   (①%d②%d③%d④%d · 잇달음 %d)'
              % ('-'.join(str(a + 1) for a in seq),
                 c[0], c[1], c[2], c[3], runs(seq)))


if __name__ == '__main__':
    main()
