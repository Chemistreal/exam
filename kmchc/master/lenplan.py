# -*- coding: utf-8 -*-
"""배치 하나의 ★정답 길이순위★ 를 찍어 본다 — 저작 중에 쓰는 자

  쓰기: python3 lenplan.py build_t16e_p3

■ 왜 필요한가
  게이트는 최근 100제 창에서 '정답 길이순위 2분할'을 본다. 배치마다 개별 문항은
  통과해도, '정답이 유일 최장' 경고를 ★오답을 늘려★ 푸는 손버릇이 쌓이면 정답이
  2위로 몰린다(T22 P13·T16 P2·P3 에서 되풀이). 동률은 통계에서 빠지므로
  ★동률이 많으면 몇 문항이 창 전체를 끌고 간다★ — 이 자도 동률 수를 함께 찍는다.

■ 읽는 법
  · 2위 = 정답보다 긴 오답이 하나  · 3위 = 정답보다 긴 오답이 둘
  · 한 배치에서 ★2위와 3위를 반반 가까이★ 두는 것이 목표다.
  · 동률이 절반을 넘으면 통계에 거의 기여하지 못하니 한두 자씩 어긋내 준다.
"""
import importlib
import sys


def main():
    if len(sys.argv) < 2:
        raise SystemExit('쓰기: python3 lenplan.py <build 모듈 이름>')
    b = importlib.import_module(sys.argv[1])
    it = b.build()
    rank = {2: 0, 3: 0}
    tie = 0
    print('  id        선지 길이            정답  순위')
    for x in it:
        L = [len(c) for c in x['choices']]
        d = sorted(L, reverse=True)
        a = L[x['answer']]
        r = d.index(a) + 1
        t = d.count(a) > 1
        if t:
            tie += 1
        elif r in rank:
            rank[r] += 1
        sp = (max(L) - min(L)) / (sum(L) / 4)
        print('  %s  %-20s %3d  %d위%s  산포 %.2f'
              % (x['id'], L, a, r, ' 동률' if t else '    ', sp))
    n = rank[2] + rank[3]
    print('\n  동률 %d제 제외 — 2위 %d · 3위 %d' % (tie, rank[2], rank[3]))
    if tie > len(it) // 2:
        print('  ⚠ 동률이 절반을 넘는다 — 몇 문항의 길이를 한두 자 어긋내 통계에 실을 것')
    if n and (rank[2] == 0 or rank[3] == 0):
        print('  ⚠ 한쪽으로 쏠렸다 — 2위와 3위를 반반 가까이 둘 것')
    elif n and max(rank.values()) / n > 0.7:
        print('  ⚠ 한쪽이 7 할을 넘는다 — 한 문항을 반대쪽으로 옮길 것')
    else:
        print('  ✅ 두 자리가 갈려 있다')


if __name__ == '__main__':
    main()
