#!/usr/bin/env python3
"""허브(`hub.html`)의 **0회차 표**를 다시 잰다 — 브라우저 없이.

`docs/허브-200턴.md` 의 첫 표는 사람이 브라우저를 띄워 손으로 잰 값이다.
손으로 잰 값은 여섯 달 뒤에 아무도 다시 안 잰다. 그러면 좋아졌는지 나빠졌는지
모르는 채로 계획만 남는다.

여기서 재는 것은 **글에서 알 수 있는 것**뿐이다. 실제로 화면을 띄워야 아는
것(첫 그림 시간 · 손가락 자리 크기 · 초점이 닿는 자리 수)은 `tests/hub-a11y.js`
와 `tests/hub-touch.js` 가 브라우저로 잰다. 둘을 갈라 두는 까닭은 이 자가
**빠르게, 늘** 돌 수 있어야 하기 때문이다 — 브라우저를 띄우면 20초가 든다.

    · 파일 크기와 바깥 파일 수 (바깥 CSS·JS 는 첫 그림을 막는다)
    · 주석 비중 (이 저장소는 소스 보기가 곧 설명서다)
    · 탭 수와 tablist 수
    · 낭독기에게 알리는 칸이 있는가
    · 창을 여는 방식이 전부 `showModal()` 인가 (`show()` 는 초점을 안 가둔다)
    · 창을 닫을 때 초점을 돌려주는가
    · 색만으로 말하는 자리가 없는가 (점은 모양으로도 갈린다)

**나빠지면 빨간불.** 좋아지는 것은 막지 않는다 — 자물쇠는 되돌아가는 것만 막는다.

    python3 tools/hub_audit.py           # 지금 값
    python3 tools/hub_audit.py --check   # 나빠졌으면 빨간불 (CI용)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'hub.html')

# ── 되돌아가면 안 되는 값 ────────────────────────────────────────────
# 2026-08-09 에 잰 값이다. 숫자를 고칠 때는 **좋아져서** 고치는 것이어야 한다.
LOCK = {
    'bytes_max': 380_000,      # 지금 34만. 한 파일로 가는 대신 살은 안 찌운다
    'external_max': 0,         # 바깥 CSS·JS 는 첫 그림을 막는다 — 하나도 없다
    'comment_min': 15,         # 주석 비중 %. 지금 21%
    'tabs': 12,
    'tablists': 2,
    'live_min': 1,             # role=status 알림 칸
    'bare_show_max': 0,        # dialog.show() — 초점을 안 가둔다
}


def main():
    check = '--check' in sys.argv
    src = open(PAGE, encoding='utf-8').read()
    js = '\n'.join(re.findall(r'<script>(.*?)</script>', src, re.S))
    css = '\n'.join(re.findall(r'<style>(.*?)</style>', src, re.S))
    body = re.sub(r'<script>.*?</script>|<style>.*?</style>', '', src, flags=re.S)

    comment = sum(len(m) for m in re.findall(r'/\*.*?\*/', js + css, re.S))
    got = {
        'bytes': os.path.getsize(PAGE),
        'external': len(re.findall(r'<link[^>]+rel=["\']?stylesheet', src, re.I))
                    + len(re.findall(r'<script[^>]+\bsrc=', src, re.I)),
        'comment_pct': round(100 * comment / max(1, len(js) + len(css))),
        # ⚠ 여기서 자가 한 번 거짓말했다. `src` 전체에서 세니 **JS 안의 선택자
        #   문자열**('[role="tab"]')까지 세어 탭이 13개·tablist 4줄로 나왔다.
        #   글 본문(script·style 을 뺀 것)에서만 센다.
        'tabs': len(re.findall(r'role="tab"', body)),
        'tablists': len(re.findall(r'role="tablist"', body)),
        'live': len(re.findall(r'aria-live=', body)),
        'status': len(re.findall(r'role="status"|role="alert"', body)),
        'show_modal': len(re.findall(r'\.showModal\(\)', js)),
        'bare_show': len(re.findall(r'(?<![a-zA-Z])\w+\.show\(\)', js)),
        'roving': len(re.findall(r'\btabIndex\s*=', js)),
        'dlg_back': len(re.findall(r'dlgBack\(', js)),
        'arrow': len(re.findall(r"ArrowLeft", js)),
        'dots_named': len(re.findall(r'class="dots" role="img" aria-label=', js)),
    }

    print('허브 — 글에서 알 수 있는 값\n')
    print('  %-22s %s' % ('파일 크기', '{:,} B'.format(got['bytes'])))
    print('  %-22s %d개' % ('바깥 CSS·JS', got['external']))
    print('  %-22s %d%%' % ('주석 비중', got['comment_pct']))
    print('  %-22s %d개 · tablist %d줄' % ('탭', got['tabs'], got['tablists']))
    print('  %-22s aria-live %d · role=status %d' % ('낭독기 알림', got['live'], got['status']))
    print('  %-22s showModal %d · show %d' % ('창 여는 법', got['show_modal'], got['bare_show']))
    print('  %-22s %s' % ('창 닫고 초점 돌려주기', '있다' if got['dlg_back'] else '없다'))
    print('  %-22s %s' % ('탭 줄 화살표', '있다' if got['arrow'] else '없다'))
    print('  %-22s %s' % ('점 칸에 이름 붙이기', '있다' if got['dots_named'] else '없다'))

    bad = []
    if got['bytes'] > LOCK['bytes_max']:
        bad.append('파일이 %s B 로 커졌다 (한도 %s)'
                   % ('{:,}'.format(got['bytes']), '{:,}'.format(LOCK['bytes_max'])))
    if got['external'] > LOCK['external_max']:
        bad.append('바깥 CSS·JS 가 %d개 생겼다 — 브라우저가 그리기를 멈추고 기다린다'
                   % got['external'])
    if got['comment_pct'] < LOCK['comment_min']:
        bad.append('주석이 %d%% 로 줄었다 (아래 한도 %d%%) — 이 저장소는 소스 보기가 곧 설명서다'
                   % (got['comment_pct'], LOCK['comment_min']))
    if got['tabs'] != LOCK['tabs']:
        bad.append('탭이 %d개다 (적어 둔 값 %d) — 늘리거나 줄였으면 이 자와 계획서를 같이 고친다'
                   % (got['tabs'], LOCK['tabs']))
    if got['tablists'] != LOCK['tablists']:
        bad.append('tablist 가 %d줄이다 (적어 둔 값 %d)' % (got['tablists'], LOCK['tablists']))
    if got['live'] + got['status'] < LOCK['live_min']:
        bad.append('낭독기에게 알리는 칸이 사라졌다 — 숫자가 차올라도 안 들린다')
    if got['bare_show'] > LOCK['bare_show_max']:
        bad.append('초점을 안 가두는 방식(dialog.show())으로 여는 창이 %d개 있다'
                   % got['bare_show'])
    if not got['dlg_back']:
        bad.append('창을 닫을 때 초점을 돌려주지 않는다 — 닫으면 화면 맨 위로 흩어진다')
    if not got['arrow']:
        bad.append('탭 줄이 화살표를 안 받는다 (ARIA APG)')
    if not got['roving']:
        bad.append('로빙 tabindex 가 없다 — 탭 열둘이 전부 탭 순서에 선다')
    if not got['dots_named']:
        bad.append('자료 표의 점 칸이 낭독기에게 아무 말도 안 한다')

    if bad:
        print('\n되돌아간 곳 %d:' % len(bad))
        for b in bad:
            print('  ' + b)
        print('\n좋아지는 것은 안 막는다 — 이 자는 **되돌아가는 것**만 막는다.')
        print('일부러 바꾼 것이면 tools/hub_audit.py 의 LOCK 과 docs/허브-200턴.md 를 같이 고친다.')
        return 1 if check else 0

    print('\n0회차에 적어 둔 값에서 되돌아간 곳이 없다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
