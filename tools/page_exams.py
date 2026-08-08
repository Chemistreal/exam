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

  --fix 는 빠진 회차도 채운다. 다만 **지어내지 않는 것만** 채운다.

    key       exams.json 의 정답키 그대로
    nQ · q    exams.json 의 문항 수 그대로
    concepts  전부 null

  개념 코드는 화면마다 손으로 붙여 온 것이라 exams.json 에 없다. 없는 것을
  지어내면 분석이 거짓말을 한다. 그래서 null 로 둔다 — 이미 2024 제2차부터
  다섯 회차가 그렇게 들어가 있다. 회차가 목록에 뜨고 정답키로 되는 분석은
  되고, 개념별 분석만 비는 것이 목록에서 아예 빠지는 것보다 낫다.

  diagnosis-v1.html 은 예외다. 그 화면은 개념 코드 **하나로** 돌아가서,
  전부 null 인 회차를 넣으면 고르는 순간 빈 화면이 된다 — 이 검사가 막으려던
  바로 그 증상이다. 그래서 개념 코드가 없는 회차는 넣지 않는다.

    python3 tools/page_exams.py            # 어긋난 곳을 보여 준다
    python3 tools/page_exams.py --fix      # 회차·제목·문항 수를 맞추고 빠진 회차를 채운다
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


def fields(ent):
    """항목 하나가 쓰는 칸 이름을 적힌 차례대로. 배열·글자열 속은 안 본다."""
    out, depth, p = [], 0, 0
    while p < len(ent):
        c = ent[p]
        if c in '{[':
            depth += 1
        elif c in '}]':
            depth -= 1
        elif c in '\'"':
            q, p = c, p + 1
            while p < len(ent) and ent[p] != q:
                p += 2 if ent[p] == '\\' else 1
        elif depth == 1 and (p == 0 or ent[p-1] in '{,'):
            m = re.match(r'(\w+):', ent[p:])
            if m:
                out.append(m.group(1))
        p += 1
    return out


def build(ex, order, group):
    """빠진 회차 하나를 그 화면이 쓰는 칸 차례대로 짓는다.

    지어내는 값은 없다 — 정답키·문항 수는 exams.json 에서 그대로 오고,
    개념 코드는 없으니 null 이다.
    """
    nQ = int(ex['nQ'])
    nulls = '[' + ','.join(['null'] * nQ) + ']'
    val = {
        'id': "'%s'" % ex['id'],
        'title': "'%s'" % ex['title'],
        'group': "'%s'" % group,
        # exams.json 의 정답은 0부터 세고, 화면의 key 는 1부터 센다(①=1).
        'key': '[' + ','.join(str(int(k) + 1) for k in ex['key']) + ']',
        'nQ': str(nQ),
        'concepts': nulls,
        'q': nulls,
    }
    return '{' + ','.join('%s:%s' % (f, val[f]) for f in order if f in val) + '}'


def main():
    fix = '--fix' in sys.argv
    check = '--check' in sys.argv
    real = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'exams.json'),
                                              encoding='utf-8'))}
    bad, gaps, fixed, added = [], [], 0, 0

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

        order = fields(body[ents[0][0]:ents[0][1]])
        # 개념 코드 하나로만 도는 화면(diagnosis-v1)은 전부 null 인 회차를 넣으면
        # 고르는 순간 빈 화면이 된다. 넣지 않는 편이 낫다.
        concept_only = 'key' not in order and 'nQ' not in order

        missing = [i for i in real if i not in {e[2] for e in ents}]
        if drop or retitle or renq:
            bad.append((name, drop, retitle, renq))
        if missing:
            gaps.append((name, missing, concept_only))

        if fix and (drop or retitle or renq or (missing and not concept_only)):
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
            if missing and not concept_only:
                # 회차 묶음 이름은 화면마다 다르게 붙여 왔다(exams.json '이전' ↔
                # 화면 '화올'). 새 회차는 같은 묶음의 이웃이 쓰는 이름을 따른다.
                seen = {}
                for s, e, i in entries(nb):
                    if i not in real:
                        continue
                    m = re.search(r"group:'([^']*)'", nb[s:e])
                    if m:
                        seen.setdefault(real[i].get('group'), m.group(1))
                ids = list(real)
                for eid in missing:
                    ex = real[eid]
                    ent = build(ex, order, seen.get(ex.get('group'), ex.get('group') or ''))
                    here = {i: (s, e) for s, e, i in entries(nb)}
                    k = ids.index(eid)
                    at = None
                    for j in range(k - 1, -1, -1):      # exams.json 차례를 따른다
                        if ids[j] in here:
                            at, ent = here[ids[j]][1], ',' + ent
                            break
                    if at is None:
                        for j in range(k + 1, len(ids)):
                            if ids[j] in here:
                                at, ent = here[ids[j]][0], ent + ','
                                break
                    if at is None:
                        continue
                    nb = nb[:at] + ent + nb[at:]
                    added += 1
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

    fillable = [g for g in gaps if not g[2]]
    if fillable:
        print('회차가 빠진 화면 %d장%s' % (len(fillable), ' → 채웠다' if fix else ''))
        for name, miss, _ in fillable:
            print('  %-26s %d개: %s' % (name, len(miss), ', '.join(sorted(miss)[:5])
                                        + (' …' if len(miss) > 5 else '')))
        print()
    skipped = [g for g in gaps if g[2]]
    if skipped:
        print('개념 코드로만 도는 화면 %d장 — 코드가 없는 회차는 넣지 않는다 '
              '(넣으면 고르는 순간 빈 화면이 된다).' % len(skipped))
        for name, miss, _ in skipped:
            print('  %-26s %d개: %s' % (name, len(miss), ', '.join(sorted(miss)[:5])
                                        + (' …' if len(miss) > 5 else '')))
        print()

    if fix:
        print('%d장을 맞췄다 (회차 %d개를 채웠다).' % (fixed, added))
        return 0
    if bad or fillable:
        print('python3 tools/page_exams.py --fix 로 맞춘다.')
        return 1 if check else 0
    print('분석 화면의 회차 목록이 exams.json 과 맞는다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
