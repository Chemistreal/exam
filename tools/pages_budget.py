#!/usr/bin/env python3
"""GitHub Pages 한도에 얼마나 가까운지 잰다.

왜 이 자가 있나
---------------
네 앱이 다 GitHub Pages 로 나간다. 그런데 **거기에 한도가 있다는 것을 아무도
안 재고 있었다**(`docs/앱별-전수조사.md` 4절 다섯째 칸).

    올린 사이트     1GB      넘으면 배포가 통째로 멈춘다
    파일 하나       100MB    넘으면 그 파일은 아예 못 올린다

이 한도는 **벽에 닿아야 알게 된다.** 어느 날 크롭을 더 넣거나 문제집 PDF 를
한 권 더 올렸는데 배포가 안 되고, 그때서야 무엇이 무거운지 찾기 시작한다.
그날 학생은 화면이 안 바뀐 이유를 모른다.

무엇을 재나
-----------
**시트에 실리는 것**이 아니라 **저장소에 올라가는 것**을 잰다 —
`git ls-files` 가 그 목록이다. `node_modules/` 처럼 추적 안 되는 것은 Pages
가 안 올리므로 세지 않는다(study64-report 의 작업본 200MB 가운데 27MB 가
그것이다).

`.git` 도 안 센다. 그것은 Pages 가 올리는 것이 아니다 — 다만 저장소를 받는
사람에게는 무게라, 참고로만 적어 둔다.

언제 빨간불인가
---------------
**벽(1GB)이 아니라 문턱(700MB)에서** 켠다. 벽에서 켜면 이미 늦다 — 그때는
지울 것을 고르는 일이 급해지고, 급하면 지우면 안 될 것을 지운다.

    python3 tools/pages_budget.py           # 지금 무게와 무거운 자리
    python3 tools/pages_budget.py --check   # 문턱을 넘으면 빨간불
"""
import os
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LIMIT = 1024 * 1024 * 1024          # Pages 사이트 한도 1GB
FLOOR = 700 * 1024 * 1024           # 문턱 — 벽이 아니라 여기서 켠다
FILE_LIMIT = 100 * 1024 * 1024      # 파일 하나 한도


def mb(n):
    return n / 1048576.0


def tracked():
    """Pages 가 올리는 것 = 저장소에 추적되는 파일."""
    out = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT,
                         capture_output=True, text=True)
    names = [n for n in out.stdout.split('\0') if n]
    rows = []
    for n in names:
        p = os.path.join(ROOT, n)
        try:
            rows.append((n, os.path.getsize(p)))
        except OSError:
            pass                      # 지워졌는데 아직 커밋 안 된 것
    return rows


def main():
    check = '--check' in sys.argv
    rows = tracked()
    total = sum(s for _, s in rows)

    # 첫 칸(폴더)으로 묶는다. 뿌리에 있는 것은 '(뿌리)' 로 모은다.
    by_dir = defaultdict(int)
    for n, s in rows:
        by_dir[n.split('/')[0] if '/' in n else '(뿌리)'] += s

    print('Pages 가 올리는 것 %.1fMB · 파일 %d개' % (mb(total), len(rows)))
    print('한도 %.0fMB · 문턱 %.0fMB · 남은 자리 %.0fMB\n'
          % (mb(LIMIT), mb(FLOOR), mb(LIMIT - total)))

    print('무거운 자리')
    for d, s in sorted(by_dir.items(), key=lambda kv: -kv[1])[:8]:
        bar = '█' * max(1, int(30 * s / max(total, 1)))
        print('  %-22s %7.1fMB  %s' % (d, mb(s), bar))

    big = sorted((r for r in rows if r[1] > FILE_LIMIT * 0.5), key=lambda r: -r[1])
    if big:
        print('\n큰 파일(한도 %.0fMB 의 절반을 넘은 것)' % mb(FILE_LIMIT))
        for n, s in big[:8]:
            print('  %7.1fMB  %s' % (mb(s), n))

    bad = []
    over = [(n, s) for n, s in rows if s > FILE_LIMIT]
    if over:
        bad.append('파일 하나가 %.0fMB 한도를 넘었다 — 그 파일은 아예 안 올라간다:\n    '
                   % mb(FILE_LIMIT)
                   + '\n    '.join('%.1fMB %s' % (mb(s), n) for n, s in over))
    if total > FLOOR:
        bad.append('올리는 것이 %.0fMB 로 문턱(%.0fMB)을 넘었다. 한도는 %.0fMB 다 — '
                   '벽에 닿기 전에\n  무엇을 덜어낼지 정할 자리다.'
                   % (mb(total), mb(FLOOR), mb(LIMIT)))

    if bad:
        print('\n' + '\n'.join('⚠ ' + b for b in bad))
        if check:
            print('\nFAIL')
            return 1
        return 0

    print('\n한도까지 %.0fMB 남았다(%.0f%% 씀).' % (mb(LIMIT - total), 100.0 * total / LIMIT))
    if check:
        print('PASS')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
