#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""공개 저장소에 학생 실명이 다시 들어오는 것을 막는다.

이 저장소는 **공개**이고 GitHub Pages 로 그대로 서빙된다. 학생은 미성년자다.
그래서 규칙은 하나다 — 이름은 저장소가 아니라 선생님 브라우저의 표에서 온다.

그런데 그 규칙을 지키는 것이 사람의 기억뿐이었다. 실제로 세 번 깨졌다:

  · student-finals.json 의 source.file 에 원본 PDF 파일명(실명 13명 × 25곳)
  · docs 예시에 「<실명>_파이널.docx --for <학생코드>」 — 가명화가 통째로 풀린다
  · tests/ 픽스처와 주석 — 값은 가명으로 바꾸고 **주석은 실명 그대로** 두었다

세 번째가 특히 조용했다. 코드는 가명인데 그 옆 주석이 「<실명>은 두 줄로 준다」
라고 적어 두어, 가명↔실명 대응표를 저장소가 스스로 들고 있는 꼴이었다.
tests/ 는 Pages 로 공개 서빙되므로 그 주석도 브라우저에서 그냥 열린다.

■ 왜 이름을 여기 안 적나
  금지 명단을 이 파일에 적으면 **검사 도구 자체가 유출**이다. 그래서 이름은
  안 적고 **해시만** 적는다. 검사는 파일에서 이름처럼 생긴 토막을 뽑아 같은
  방식으로 해시해 대조한다. 사람이 이 파일을 읽어도 이름은 안 나온다.

  (해시가 완벽한 봉인은 아니다 — 한국 이름은 경우의 수가 적어 작정하면 되짚을
   수 있다. 여기서 막는 것은 «지나가다 보는 것»·«검색에 걸리는 것» 이고,
   그것이 실제 위험이다. 완전한 봉인은 저장소를 비공개로 돌리는 것뿐이다.)

■ 명단을 고치려면
    python3 tools/name_guard.py --add "홍길동"      # 해시만 적는다
    python3 tools/name_guard.py --check             # CI 가 도는 것

사용:
    python3 tools/name_guard.py --check
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'name_guard.json')

# 해시에 섞는 고정 소금. 비밀이 아니다 — 다른 저장소의 표와 값이 겹치지
# 않게 하는 것뿐이다.
SALT = 'chemistreal/exam·학생실명·v1'

# 안 보는 곳. 지난 응시 기록(backup)은 시트에서 내려받은 것이라 이름이 있고,
# 그것은 별건으로 다룬다(여기서 잡으면 매번 빨간불이라 아무도 안 읽게 된다).
SKIP_DIRS = {'.git', 'crops', 'backup', 'node_modules', '__pycache__'}
SKIP_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.docx', '.hwpx', '.zip',
            '.woff', '.woff2', '.ttf', '.otf', '.ico', '.p12', '.mp4'}

KO = re.compile(r'[가-힣]+')


def h(name):
    return hashlib.sha256((SALT + '\x1f' + name).encode('utf-8')).hexdigest()[:20]


def load():
    try:
        with open(LIST, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'note': '학생 실명의 해시. 이름 자체는 절대 적지 않는다.', 'hashes': []}


def candidates(text):
    """이름처럼 생긴 토막을 뽑는다.

    한국 이름은 두~네 글자다. 본문에서는 «김마루은 두 줄» 처럼 조사가 붙어
    한글 덩어리의 **앞쪽**에 온다. 그래서
      (가) 덩어리 경계에서 시작하는 두~네 글자   ← 대부분 여기 걸린다
      (나) 아무 자리에서나 시작하는 세 글자       ← 붙여 쓴 경우까지
    둘을 본다. 덩어리 전체를 다 자르면 큰 파일에서 너무 느려진다.
    """
    out = set()
    for m in KO.finditer(text):
        run = m.group(0)
        n = len(run)
        for L in (2, 3, 4):
            if n >= L:
                out.add(run[:L])
        for i in range(n - 2):
            out.add(run[i:i + 3])
    return out


def files():
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for nm in names:
            if os.path.splitext(nm)[1].lower() in SKIP_EXT:
                continue
            p = os.path.join(base, nm)
            if os.path.getsize(p) > 8 * 1024 * 1024:
                continue
            yield p


def scan():
    want = set(load().get('hashes') or [])
    if not want:
        return []
    bad = []
    for p in files():
        try:
            with open(p, encoding='utf-8') as f:
                text = f.read()
        except Exception:
            continue
        rel = os.path.relpath(p, ROOT)
        # 파일 **이름** 에도 이름이 들어올 수 있다(«<실명>_파이널.docx»).
        for cand in candidates(text) | candidates(rel):
            if h(cand) in want:
                where = []
                for i, line in enumerate(text.split('\n'), 1):
                    if cand in line:
                        where.append(i)
                    if len(where) >= 4:
                        break
                bad.append((rel, tuple(where)))
                break
    return sorted(set(bad))


def main():
    args = sys.argv[1:]
    if '--add' in args:
        i = args.index('--add')
        names = [a for a in args[i + 1:] if not a.startswith('--')]
        if not names:
            print('이름을 하나 이상 주세요'); return 2
        doc = load()
        hs = set(doc.get('hashes') or [])
        before = len(hs)
        for nm in names:
            hs.add(h(nm.strip()))
        doc['hashes'] = sorted(hs)
        with open(LIST, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print('명단 %d → %d (이름은 안 적혔습니다)' % (before, len(hs)))
        return 0

    bad = scan()
    n = len(load().get('hashes') or [])
    if not bad:
        print('PASS 금지 명단 %d명 — 저장소에 실명이 없습니다' % n)
        return 0
    print('FAIL 공개 저장소에 학생 실명이 있습니다 (금지 명단 %d명):' % n)
    for rel, lines in bad:
        print('  %s%s' % (rel, (' : ' + ', '.join(str(x) + '행' for x in lines)) if lines else ''))
    print('\n  이 저장소는 공개이고 미성년자 이름입니다. 가명으로 바꾸세요.')
    print('  (값만 바꾸고 주석을 그대로 두는 실수가 잦습니다 — 주석도 보세요)')
    return 1


if __name__ == '__main__':
    sys.exit(main())
