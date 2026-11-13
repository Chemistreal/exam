# -*- coding: utf-8 -*-
"""reprep — ★조치한 문항이 든 검증 범위를 다시 깐다★

  쓰임:  python3 reprep.py            (마지막 커밋에서 바뀐 문항을 찾아 그 범위만)
         python3 reprep.py M02767 M02790   (범위를 손으로 줄 때)

  ★왜 세우는가★ — T22 M02767~M02790 순회의 지적 열여섯 가운데 ★여섯이 지금 문면에 없는 문장★
  을 인용했다. 그 범위의 검증 파일은 14:48 에 깔렸고 조치는 그 뒤 두 차례 있었다.
  낡은 파일은 ★이미 고친 자리를 다시 지적하고★, 그 지적을 그대로 따르면 고친 것을 되돌린다.
  판정 단계가 막아 주었지만, 검증자 아홉과 판정자 넷의 품이 헛되게 들었다.
  ▸ 그래서 규약을 도구로 옮긴다: ★조치를 은행에 쓴 뒤에는 그 범위를 다시 깐다.★

  은행의 문항은 열씩 한 범위(M02765 → M02757_M02766 이 아니라 ★배치 경계★ 를 따른다 —
  agent_pipeline 이 쓰는 열 칸 창과 같게 M0xxx1~M0xxy0 으로 자른다).
"""
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ID_RE = re.compile(r'M(\d{5})')


def sh(*args):
    return subprocess.run(args, cwd=HERE, capture_output=True, text=True).stdout


def theme_span():
    """테마마다 ★첫 문항 번호와 마지막 번호★ 를 읽는다 — 배치 경계가 여기서 나온다."""
    import json
    d = json.load(io.open(os.path.join(HERE, 'master_bank.json'), encoding='utf-8'))
    pool = d['items'] if isinstance(d, dict) else d
    span = {}
    for x in pool:
        t = x.get('theme_no') or x.get('tt') or x.get('textbook_theme') or x.get('theme')
        n = int(x['id'][1:])
        lo, hi = span.get(t, (n, n))
        span[t] = (min(lo, n), max(hi, n))
    return sorted(span.values())


def blocks(nums):
    """번호들을 배치 창으로 묶는다 — ★테마의 첫 문항부터 열씩★ 이 이 은행의 배치다.
      (2765 는 T22 가 M02627 에서 시작하므로 M02757~M02766 창에 든다 — 열 칸을 그냥
       끊으면 M02761~M02770 이 되어 ★있지도 않은 범위★ 를 깔게 된다.)"""
    spans = theme_span()
    out = set()
    for n in nums:
        for lo0, hi0 in spans:
            if lo0 <= n <= hi0:
                lo = lo0 + ((n - lo0) // 10) * 10
                out.add((lo, min(lo + 9, hi0)))
                break
    return sorted(out)


def main():
    if len(sys.argv) >= 3:
        a, b = int(sys.argv[1][1:]), int(sys.argv[2][1:])
        nums = list(range(a, b + 1))
    else:
        msg = sh('git', 'log', '-1', '--pretty=%B')
        nums = sorted({int(m) for m in ID_RE.findall(msg)})
        if not nums:
            print('마지막 커밋 메시지에 문항 번호가 없다 — 범위를 손으로 줄 것')
            return
        print('마지막 커밋이 이름을 부른 문항 %d개' % len(nums))
    todo = blocks(nums)
    print('다시 깔 범위 %d' % len(todo))
    for lo, hi in todo:
        r = sh('python3', 'agent_pipeline.py', 'prep', 'M%05d' % lo, 'M%05d' % hi)
        ok = 'items_solve.md' in r or '보고' in r
        print('  %s M%05d~M%05d' % ('✅' if ok else '⛔', lo, hi))


if __name__ == '__main__':
    main()
