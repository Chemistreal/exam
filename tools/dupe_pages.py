#!/usr/bin/env python3
"""같은 화면이 두 이름으로 있는 것을 찾고, **한쪽만 고치는 것**을 막는다.

해설지 77장 중 **52장이 26쌍의 복사본**이다. 바이트 단위로 똑같다.

    sol-final-jmchc-5.html   ==   sol-jmchc-5-full.html
    sol-final-hwol-2013.html ==   sol-kmchc-2013-full.html   … 26쌍 (1.64MB)

둘 다 2026-06-20 한 커밋에서 같이 생겼다 — 만드는 도구가 이름 두 벌로 뽑았다.
지금은 내용이 같으니 아무 일도 안 일어난다. 무서운 것은 **다음 손질**이다.
선생님이 해설의 오타 하나를 고치면 그 고침은 **한쪽에만** 닿는다. 화면은
멀쩡하고 검사도 다 통과한다. 어느 쪽을 연 학생이 틀린 해설을 보는지는
그때 가서도 모른다 — 이 저장소에서 오늘 하루에만 세 번 겪은 모양이다.

**지우지는 않는다.** `orphan_scan.py` 와 같은 방침이다 — 무엇이 겹쳐 있는지
알려 주고 지우는 명령만 찍어 준다. 어느 이름을 남길지는 선생님이 정할 일이다.
대신 **갈라지는 것은 그 자리에서 막는다.**

    python3 tools/dupe_pages.py            # 겹친 것 목록 · 누가 부르는지
    python3 tools/dupe_pages.py --check    # 갈라졌거나 새 복사본이 생기면 빨간불
    python3 tools/dupe_pages.py --write    # 지금 상태를 기록에 담는다
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.path.join(ROOT, 'tools', 'dupe_pages.json')
SKIP_DIR = {'.git', 'node_modules', '__pycache__', 'tests'}
# 부르는 쪽을 찾을 때 읽는 확장자.
READ = ('.html', '.js', '.json', '.py', '.gs', '.md', '.yml', '.txt', '.webmanifest')


def pages():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIR]
        for f in sorted(fn):
            if f.endswith('.html'):
                yield os.path.relpath(os.path.join(dp, f), ROOT)


def sha(rel):
    with open(os.path.join(ROOT, rel), 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def groups():
    """지금 내용이 똑같은 묶음들. 이름순으로 정렬해 돌려준다."""
    by = {}
    for rel in pages():
        by.setdefault(sha(rel), []).append(rel)
    return sorted((sorted(v) for v in by.values() if len(v) > 1))


def callers(names):
    """각 이름을 부르는 파일. 자기 자신은 안 센다."""
    out = {n: set() for n in names}
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIR]
        for f in fn:
            if not f.endswith(READ):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ROOT)
            if os.path.abspath(p) in (os.path.abspath(__file__), os.path.abspath(NOTE)):
                continue          # 이 도구와 그 기록에 이름이 적혀 있다 — 부르는 것이 아니다
            try:
                with open(p, encoding='utf-8') as fh:
                    s = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            for n in names:
                if rel != n and os.path.basename(n) in s:
                    out[n].add(rel)
    return out


def load():
    try:
        with open(NOTE, encoding='utf-8') as fh:
            return json.load(fh).get('groups', [])
    except (OSError, ValueError):
        return []


def main():
    check = '--check' in sys.argv[1:]
    write = '--write' in sys.argv[1:]
    now = groups()
    known = [sorted(g) for g in load()]

    if write:
        with open(NOTE, 'w', encoding='utf-8') as fh:
            json.dump({
                '설명': '내용이 똑같은 화면 묶음. 여기 적힌 것은 선생님이 남겨 둔 것이고, '
                        '한쪽만 고치면 검사가 막는다. 새 복사본이 생겨도 막는다.',
                'groups': now,
            }, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        print('기록했다: ' + str(len(now)) + '묶음')
        return 0

    dup_mb = sum(os.path.getsize(os.path.join(ROOT, g[0])) * (len(g) - 1)
                 for g in now) / 1024 / 1024
    print('내용이 똑같은 묶음 ' + str(len(now)) + '개 · 겹쳐서 든 용량 '
          + str(round(dup_mb, 2)) + 'MB')

    bad = []
    # ① 기록에 있는 쌍이 **갈라졌는가** — 한쪽만 고친 것이다. 제일 무서운 경우.
    for g in known:
        live = [n for n in g if os.path.exists(os.path.join(ROOT, n))]
        if len(live) < 2:
            continue                       # 한쪽을 지웠다 — 겹침이 풀린 것이라 괜찮다
        hs = {sha(n) for n in live}
        if len(hs) > 1:
            bad.append(('갈라졌다 (한쪽만 고쳤습니다)', live))
    # ② 기록에 없는 **새 복사본**이 생겼는가.
    kn = {tuple(g) for g in known}
    for g in now:
        if tuple(g) not in kn:
            bad.append(('새 복사본', g))

    if not check:
        for g in now:
            c = callers(g)
            print('\n  ' + ' == '.join(g))
            for n in g:
                who = sorted(c[n])
                print('     ' + n + ' ← ' + (', '.join(who) if who else '아무도 안 부른다'))
        if now:
            print('\n  한쪽을 지우려면: git rm <남길 것이 아닌 이름> '
                  '(부르는 곳도 같이 고쳐야 합니다)')
            print('  지금 상태를 기록에 담으려면: python3 tools/dupe_pages.py --write')
        return 0

    if bad:
        print('')
        for why, g in bad:
            print('  ✗ ' + why + ': ' + ' / '.join(g))
        print('\nFAIL 같은 화면 두 벌 중 한쪽만 손댔거나, 새 복사본이 생겼습니다.')
        print('     같게 두려면 나머지에도 같은 손질을 하고,')
        print('     갈라 둘 생각이면 python3 tools/dupe_pages.py --write 로 기록을 고치세요.')
        return 1
    print('\nPASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
