#!/usr/bin/env python3
"""분석 화면들이 저마다 품고 있는 회차 목록이 `exams.json` 과 맞는지 본다.

성적표(final.html)와 통합 셸(hub.html)은 회차 목록을 파일에서 읽거나, 못 읽으면
`tools/gen_exam_fallback.py` 가 심어 둔 예비본을 쓴다. 어느 쪽이든 한 곳에서
온다. 그런데 **분석 화면 열일곱 장**은 각자 `EXAMS=[…]` 를 통째로 품고 있고,
그것을 맞춰 주는 생성기가 없었다.

맞춰 주는 것이 없으면 갈라진다. 실제로 갈라져 있었다.

    kmchc-2024-1  "KMChC 2024 제1차"   ← exams.json 에 없는 회차
    hwol-2024     "화올 2024"          ← 같은 시험인데 제목이 낡음

회차 고르는 칸에 같은 시험이 **두 번** 뜨고, 위엣것을 고르면 데이터가 없어
빈 화면이 나온다. 셋이 그랬다(2024 제1차 · 2019 · 2018).

이 화면들은 자료를 지어내는 모의 도구라(Math.random) 학생 채점에는 닿지
않는다. 그래도 회차 목록은 선생님이 눈으로 고르는 자리다.

여기서 보는 것 — 화면마다 칸 구성이 달라(key·concepts·q·nQ) **회차와 제목만**
견준다. 문항별 배열은 화면마다 다른 뜻으로 쓰여 손대지 않는다.

  ① exams.json 에 없는 회차를 들고 있지 않은가
  ② 제목이 exams.json 과 같은가
  ③ 문항 수(nQ)를 적어 둔 화면은 그 값이 맞는가

  --fix 는 ①②③ 만 고친다. 빠진 회차를 **채워 넣지는 않는다** — 그 화면이
  쓰는 문항별 배열(정답키·개념 코드)을 지어낼 수는 없기 때문이다. 어디가
  비었는지 알리기만 한다.

    python3 tools/page_exams.py            # 어긋난 곳을 보여 준다
    python3 tools/page_exams.py --fix      # 회차·제목·문항 수를 맞춘다
    python3 tools/page_exams.py --check    # 어긋나면 빨간불 (CI용)
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 회차 목록이 아니라 **문항 풀**을 EXAMS 로 담은 화면들. 여기서 볼 것이 아니다.
SKIP = {'admin.html', 'index.html', 'final.html', 'final-submit.html'}


def find_array(src):
    """`EXAMS=[ … ]` 의 범위를 괄호를 세어 찾는다. 글자열 안의 괄호는 세지 않는다."""
    i = src.find('EXAMS=[')
    if i < 0:
        return None
    j = i + len('EXAMS=')
    depth, k = 0, j
    while k < len(src):
        c = src[k]
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return j, k + 1
        elif c in '\'"':
            q, k = c, k + 1
            while k < len(src) and src[k] != q:
                k += 2 if src[k] == '\\' else 1
        k += 1
    return None


def entries(body):
    """배열 안의 `{id:'…', …}` 를 하나씩 (시작, 끝, id) 로 돌려준다."""
    out, k = [], 0
    while True:
        m = re.compile(r"\{id:'([^']+)'").search(body, k)
        if not m:
            return out
        depth, p = 0, m.start()
        while p < len(body):
            c = body[p]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    p += 1
                    break
            elif c in '\'"':
                q, p = c, p + 1
                while p < len(body) and body[p] != q:
                    p += 2 if body[p] == '\\' else 1
            p += 1
        out.append((m.start(), p, m.group(1)))
        k = p


def main():
    fix = '--fix' in sys.argv
    check = '--check' in sys.argv
    real = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'exams.json'),
                                              encoding='utf-8'))}
    bad, gaps, fixed = [], [], 0

    for path in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        name = os.path.basename(path)
        if name in SKIP:
            continue
        src = open(path, encoding='utf-8').read()
        span = find_array(src)
        if not span:
            continue
        a, b = span
        body = src[a:b]
        ents = entries(body)
        if len(ents) < 5:                      # 회차 목록이라기엔 너무 짧다
            continue

        drop, retitle, renq = [], [], []
        for _, _, eid in ents:
            ex = real.get(eid)
            if not ex:
                drop.append(eid)
                continue
            m = re.search(r"\{id:'%s',title:'([^']*)'" % re.escape(eid), body)
            if m and m.group(1) != ex['title']:
                retitle.append((eid, m.group(1), ex['title']))
            m = re.search(r"\{id:'%s'[^}]*?nQ:(\d+)" % re.escape(eid), body)
            if m and int(m.group(1)) != int(ex['nQ']):
                renq.append((eid, int(m.group(1)), int(ex['nQ'])))

        missing = [i for i in real if i not in {e[2] for e in ents}]
        if drop or retitle or renq:
            bad.append((name, drop, retitle, renq))
        if missing:
            gaps.append((name, missing))

        if fix and (drop or retitle or renq):
            nb = body
            for eid, _, want in retitle:
                nb = re.sub(r"(\{id:'%s',title:')[^']*(')" % re.escape(eid),
                            lambda m: m.group(1) + want + m.group(2), nb, count=1)
            for eid, _, want in renq:
                nb = re.sub(r"(\{id:'%s'[^}]*?nQ:)\d+" % re.escape(eid),
                            lambda m: m.group(1) + str(want), nb, count=1)
            for eid in drop:                   # 뒤에서부터 지워야 자리가 안 밀린다
                for s, e, i in reversed(entries(nb)):
                    if i != eid:
                        continue
                    e2 = e
                    while e2 < len(nb) and nb[e2] in ' \n':
                        e2 += 1
                    if e2 < len(nb) and nb[e2] == ',':
                        e2 += 1
                    else:
                        while s > 0 and nb[s-1] in ' \n':
                            s -= 1
                        if s > 0 and nb[s-1] == ',':
                            s -= 1
                    nb = nb[:s] + nb[e2:]
                    break
            open(path, 'w', encoding='utf-8').write(src[:a] + nb + src[b:])
            fixed += 1

    if bad:
        print('회차 목록이 exams.json 과 어긋난 화면 %d장%s\n'
              % (len(bad), ' → 맞췄다' if fix else ''))
        for name, drop, retitle, renq in bad:
            print('  %s' % name)
            for eid in drop:
                print('     없는 회차: %s' % eid)
            for eid, got, want in retitle:
                print("     제목이 낡음: %s  '%s' → '%s'" % (eid, got, want))
            for eid, got, want in renq:
                print('     문항 수가 다름: %s  %d → %d' % (eid, got, want))
        print()

    if gaps:
        print('회차가 빠진 화면 %d장 — 문항별 배열(정답키·개념 코드)을 지어낼 수 '
              '없어 채우지 않는다.' % len(gaps))
        for name, miss in gaps:
            print('  %-26s %d개: %s' % (name, len(miss), ', '.join(sorted(miss)[:5])
                                        + (' …' if len(miss) > 5 else '')))
        print()

    if fix:
        print('%d장을 맞췄다. 빠진 회차는 손으로 채워야 한다.' % fixed)
        return 0
    if bad:
        print('python3 tools/page_exams.py --fix 로 맞춘다.')
        return 1 if check else 0
    print('분석 화면의 회차 목록이 exams.json 과 맞는다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
