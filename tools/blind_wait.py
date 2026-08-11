#!/usr/bin/env python3
"""검사가 "이쯤이면 됐겠지" 하고 재우는 시간을 잰다.

브라우저 검사에서 `waitForTimeout(400)` 은 **짐작**이다. 빠른 기계에서는
400ms 를 헛되이 버리고, 느린 기계에서는 아직 안 끝난 화면을 본다. 코드는
그대로인데 검사가 이따금 빨간불이 되는 뿌리가 거의 여기 있다.

흔들리는 검사는 실패하는 검사보다 나쁘다. 사람이 빨간불을 안 믿게 되고,
그러면 진짜 고장도 같이 묻힌다. 실제로 `hub-live.js` 는 고정 대기가 여든아홉
군데, 합쳐 46초였고 여덟 번에 한 번쯤 까닭 없이 깨졌다.

고칠 길은 정해져 있다. **조건이 참이 될 때까지** 기다리거나(waitForFunction),
**값이 더 이상 안 바뀔 때까지** 기다린다. 둘 다 빠른 기계에서는 빠르고 느린
기계에서는 기다린다.

여기서는 파일마다 천장을 정해 두고 넘지 않는지만 본다. 한 번에 다 걷어내지
않는다 — 천장은 내려가기만 하면 된다. 줄인 만큼 천장을 낮춰 두면 다음 사람이
도로 늘리지 못한다.

    python3 tools/blind_wait.py           # 파일마다 얼마나 재우는지
    python3 tools/blind_wait.py --check   # 천장을 넘었으면 빨간불 (CI용)
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 파일별 천장 (군데 수, 합계 ms). 줄였으면 여기도 같이 낮춘다 — 낮추지 않으면
# 다음 사람이 도로 채워 넣어도 초록불이다.
CEIL = {
    'tests/hub-live.js': (71, 27680),
    # 허브를 쓰는 방법을 보는 두 자. 처음부터 조건 대기로 지었다 —
    # 남은 것은 서버가 뜨기를 기다리는 한 줄뿐이다.
    'tests/hub-a11y.js': (4, 1250),
    'tests/hub-calls.js': (2, 820),
    'tests/web-store.js': (13, 23100),
    'tests/exams-fallback.js': (7, 16700),
    'tests/hero3d.js': (9, 16250),
    'tests/roster-admin.js': (13, 6800),
    'tests/share-link.js': (6, 12700),
    'tests/grading-input.js': (8, 8300),
    'tests/prereq-drill.js': (4, 7000),
    'tests/gate.js': (6, 5150),
    # 2026-08-10 — 표에 없어 기본 천장(4군데·4000ms)을 쓰고 있던 것들.
    # 실제로는 훨씬 적게 자므로 그 값으로 박아 둔다. 그래야 도로 늘면 걸린다.
    'tests/area-verdict.js': (1, 700),
    'tests/narrow.js': (2, 1050),
    # 학부모가 걷는 길. 처음부터 조건 대기로 지었다 — 고정 대기가 없다.
    'tests/parent-walk.js': (0, 0),
    'tests/rank-baseline.js': (3, 5200),
    'tests/docx-report.js': (3, 4900),
    'tests/wrongbook-interactive.js': (4, 4600),
    'tests/offline.js': (2, 4500),
    'tests/retest-sheet.js': (4, 4300),
    'tests/hub-touch.js': (3, 4200),
    'tests/lec-back.js': (7, 4150),
    'tests/dupe-name.js': (2, 3300),
    'tests/hub-batch.js': (2, 3200),
    'tests/theme.js': (3, 1900),
    'tests/report-all.js': (1, 900),
    'tests/first-paint.js': (1, 700),
    'tests/page-health.js': (1, 600),
    'tests/print-lec.js': (1, 700),
}
# 표에 없는 새 검사가 처음부터 마흔 군데씩 재우면서 시작하면 안 된다.
NEW = (4, 4000)

PAT = (re.compile(r'waitForTimeout\(\s*(\d+)\s*\)'),
       re.compile(r'setTimeout\(\s*[\w$]+\s*,\s*(\d+)\s*\)'))


def measure(path):
    s = open(path, encoding='utf-8').read()
    ms = [int(m) for p in PAT for m in p.findall(s)]
    return len(ms), sum(ms)


def main():
    check = '--check' in sys.argv
    over, slack = [], []
    print('짐작으로 재우는 시간 (조건 대기로 바꿀수록 줄어든다)\n')
    print('  %-32s %8s %10s   %s' % ('검사', '군데', '합계', '천장'))
    tot_n = tot_ms = 0
    for path in sorted(glob.glob(os.path.join(ROOT, 'tests', '*.js'))):
        rel = 'tests/' + os.path.basename(path)
        n, ms = measure(path)
        if not n:
            continue
        tot_n += n
        tot_ms += ms
        cn, cms = CEIL.get(rel, NEW)
        mark = ''
        if n > cn or ms > cms:
            mark = '  ← 넘었다'
            over.append((rel, n, ms, cn, cms))
        elif ms <= cms - 1000 or n <= cn - 2:
            mark = '  (천장 낮출 수 있다)'
            slack.append((rel, n, ms, cn, cms))
        print('  %-32s %5d군데 %8dms   %d/%dms%s' % (rel, n, ms, cn, cms, mark))
    print('\n  합계 %d군데 · %.1f초' % (tot_n, tot_ms / 1000))

    if slack:
        print('\n줄여 놓고 천장을 안 낮춘 검사 %d개 — 낮춰야 도로 늘어나는 것을 막는다.' % len(slack))
        for rel, n, ms, cn, cms in slack:
            print("    '%s': (%d, %d)," % (rel, n, ms))

    if over:
        print('\n천장을 넘은 검사 %d개:' % len(over))
        for rel, n, ms, cn, cms in over:
            print('  %-32s %d군데 %dms (천장 %d군데 %dms)' % (rel, n, ms, cn, cms))
        print('\n고정 대기 대신 조건 대기를 쓴다.')
        print('  · 언제 참이 되는지 아는 자리  → waitForFunction(조건)')
        print('  · 언제 끝나는지 모르는 자리    → 값이 안 바뀔 때까지 (tests/hub-live.js 의 settled)')
        print('기대값으로 기다리면 안 된다 — 검사가 스스로 답을 맞춰 주는 꼴이 된다.')
        return 1 if check else 0

    print('\n천장을 넘은 검사는 없다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
