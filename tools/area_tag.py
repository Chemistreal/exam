#!/usr/bin/env python3
"""회차의 **영역 이름**이 성적표가 아는 이름인지 본다.

성적표는 문항의 `area` 로 영역별 진단과 처방을 만든다. 아는 이름은 두 곳에
적혀 있다 — `RX`(열여섯 영역과 그 처방)와 `RXMAP`(다른 이름으로 적힌 것을
그 열여섯 중 하나로 보내는 표).

둘 중 어디에도 없는 이름이 오면 그 문항은 **처방 없이 흘러간다**. 화면은
멀쩡히 나오고 점수도 맞으니 아무도 모른다. 실제로 열다섯 문항이 그랬다.

    분자간힘        4문항   ← '분자간인력' 의 다른 표기
    용액           4문항
    헨더슨-하셀바흐식   3문항   ← '헨더슨하셀바흐식' 의 다른 표기
    원자핵          2문항
    원소           1문항
    물질의분리        1문항

철자만 다른 것은 이미 있는 이름으로 모으고, 뜻이 다른 것은 RXMAP 에
어느 영역으로 보낼지 적었다.

성적표 안에도 같은 것을 보는 `qbankAudit()` 이 있지만 그것은 브라우저에서
선생님이 열어야 보인다. 회차를 넣는 자리에서 바로 걸리게 여기에도 둔다.

    python3 tools/area_tag.py           # 등록 안 된 이름을 보여 준다
    python3 tools/area_tag.py --check   # 있으면 빨간불 (CI용)
"""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL = os.path.join(ROOT, 'final.html')


def block(src, name):
    """`const 이름={ … }` 의 몸통을 괄호를 세어 잘라 온다."""
    m = re.search(r'const\s+%s\s*=\s*\{' % name, src)
    if not m:
        return ''
    i = m.end() - 1
    depth, j = 0, i
    while j < len(src):
        c = src[j]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
        elif c in '\'"':
            q, j = c, j + 1
            while j < len(src) and src[j] != q:
                j += 2 if src[j] == '\\' else 1
        j += 1
    return ''


def known():
    src = open(FINAL, encoding='utf-8').read()
    rx = set(re.findall(r"[{,]\s*'([^']+)'\s*:", block(src, 'RX')))
    rxmap = set(re.findall(r"'([^']+)'\s*:", block(src, 'RXMAP')))
    # '기타' 는 성적표가 스스로 붙이는 이름이라 표에 없어도 된다.
    return rx | rxmap | {'기타'}, len(rx), len(rxmap)


def main():
    check = '--check' in sys.argv
    ok, nrx, nmap = known()
    bad = collections.defaultdict(list)

    for e in json.load(open(os.path.join(ROOT, 'exams.json'), encoding='utf-8')):
        for i, a in enumerate(e.get('area') or []):
            if a and a not in ok:
                bad[a].append('%s %d번' % (e['id'], i + 1))
    for p in sorted(glob.glob(os.path.join(ROOT, 'answers', '*.json'))):
        d = json.load(open(p, encoding='utf-8'))
        for q, v in (d.get('questions') or {}).items():
            a = v.get('area')
            if a and a not in ok:
                bad[a].append('%s %s번' % (os.path.basename(p)[:-5], q))

    print('성적표가 아는 영역 이름 %d개 (RX %d · RXMAP %d)' % (len(ok), nrx, nmap))
    if bad:
        print('\n등록 안 된 이름 %d개 — 이 문항들은 처방 없이 흘러간다:' % len(bad))
        for a, where in sorted(bad.items(), key=lambda x: -len(x[1])):
            print('  %-16s %3d문항  %s' % (a, len(where), ', '.join(where[:4])
                                          + (' …' if len(where) > 4 else '')))
        print('\n철자만 다르면 이미 있는 이름으로 모으고, 뜻이 다르면 final.html 의')
        print('RXMAP 에 어느 영역으로 보낼지 적는다.')
        return 1 if check else 0

    print('등록 안 된 영역 이름은 없다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
