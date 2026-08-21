#!/usr/bin/env python3
"""선생님이 PDF 로 낸 학생별 시험지를 회차로 들인다.

한글(HWPX)로 온 것은 `tools/ingest_hwpx_exam.py` 가 글자를 읽어 다시 조판한다.
PDF 로만 온 것은 그 길이 없다 — 대신 **쪽을 그대로 잘라** 크롭을 만들고,
글자층에서 정답과 해설만 캔다. 그림·표가 원본 그대로 실린다는 것이 이 길의
장점이고, 글꼴이 문서마다 다를 수 있다는 것이 값이다.

문서 꼴은 한글 쪽과 같다.

    문제 01 / <영역> / 변형|난이도 상  … 지문 … ① ② ③ ④
    빠른 정답   번호 1..20 / 정답 ①..④
    문제 01 / <영역> / 변형  정 답 ④  풀이 …  원본과 달라진 점 …
    마 감 카 드                       ← 여기부터는 해설이 아니다

쓰기:
    python3 tools/ingest_pdf_exam.py <파일.pdf> [--code CODE] [--kind 변형본] [--write]
    python3 tools/ingest_pdf_exam.py --check
"""
from __future__ import annotations

import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from ingest_teacher_exam import trim_white                    # noqa: E402
from ingest_hwpx_exam import (cut_of, load_finals, tidy, map_area,  # noqa: E402
                              type_of, MIS_SPLIT, SHELL, TAILER, LEAD, check)

HEAD = re.compile(r'^문제\s*(\d{1,3})$')
LEVEL = re.compile(r'^(변형|난이도\s*[상중하])$')
STOP = re.compile(r'^(빠른\s*정답|PART|답안지)$')
OUTRO = re.compile(r'^(마\s*감\s*카\s*드|여기까지 온 것만으로)')
CIRCLED = '①②③④⑤'


# ── 크롭 ────────────────────────────────────────────────────────────────
RENDER_SCALE = 4
IMG_W = 955
FOOT = re.compile(r'^\d{1,3}$')


def bands(doc):
    """쪽마다 글이 실제로 있는 위쪽·아래쪽. 쪽번호는 뺀다.

    문항이 쪽을 넘어가면 두 조각을 이어 붙이는데, 조각을 쪽 끝까지 잡으면
    가운데에 **여백과 쪽번호**가 그대로 낀다. 실제로 「지문은 7쪽 맨 아래,
    선지는 8쪽 맨 위」인 문항이 가운데에 '7' 을 달고 나왔다.
    """
    out = []
    for page in doc:
        ys = []
        for blk in page.get_text('dict').get('blocks', []):
            for ln in blk.get('lines', []):
                t = ''.join(sp.get('text', '') for sp in ln.get('spans', [])).strip()
                if not t:
                    continue
                b = ln['bbox']
                if FOOT.match(t) and b[1] > page.rect.height * 0.88:
                    continue                      # 쪽번호
                ys.append((b[1], b[3]))
        if ys:
            out.append((min(y[0] for y in ys) - 4, max(y[1] for y in ys) + 4))
        else:
            out.append((page.rect.y0, page.rect.y1))
    return out


def crop_pdf(doc, band, start, end, out_path, pymupdf):
    """한 문항을 그림으로. 쪽을 넘어가면 글이 있는 데까지만 이어 붙인다."""
    from PIL import Image
    mat = pymupdf.Matrix(RENDER_SCALE, RENDER_SCALE)
    p0, y0 = start['page'], start['y']
    p1, y1 = (end['page'], end['y']) if end else (doc.page_count - 1, None)
    pieces = []
    for pi in range(p0, p1 + 1):
        page = doc[pi]
        bt, bb = band[pi]
        top = (y0 - 4) if pi == p0 else bt
        bot = (y1 - 2) if (end and pi == p1) else bb
        top, bot = max(top, page.rect.y0), min(bot, page.rect.y1)
        if bot - top < 6:
            continue
        pm = page.get_pixmap(matrix=mat, alpha=False,
                             clip=pymupdf.Rect(page.rect.x0, top, page.rect.x1, bot))
        pieces.append(Image.frombytes('RGB', (pm.width, pm.height), pm.samples))
    if not pieces:
        return False
    if len(pieces) == 1:
        im = pieces[0]
    else:
        w = max(p.width for p in pieces)
        im = Image.new('RGB', (w, sum(p.height for p in pieces)), 'white')
        y = 0
        for p in pieces:
            im.paste(p, (0, y))
            y += p.height
    im = trim_white(im)
    if im.width != IMG_W:
        im = im.resize((IMG_W, max(1, round(im.height * IMG_W / im.width))), Image.LANCZOS)
    im.convert('P', palette=Image.ADAPTIVE, colors=256).save(
        out_path, 'PNG', optimize=True, compress_level=9)
    return True


# ── 글자층 ──────────────────────────────────────────────────────────────
def lines_of(doc):
    """(쪽, y, x0, x1, 글자) — 읽는 차례대로."""
    out = []
    for pi, page in enumerate(doc):
        for blk in page.get_text('dict').get('blocks', []):
            for ln in blk.get('lines', []):
                t = ''.join(s.get('text', '') for s in ln.get('spans', []))
                if t.strip():
                    b = ln['bbox']
                    out.append({'p': pi, 'y': b[1], 'x0': b[0], 'x1': b[2],
                                't': t.strip(), 'w': page.rect.width})
    out.sort(key=lambda d: (d['p'], round(d['y'], 1), d['x0']))
    return out


def join(lines):
    """소프트 줄바꿈은 붙이고, 진짜 줄바꿈은 끊는다.

    한글은 줄 끝에 붙임표가 없어서 그냥 이으면 「줄 고」 처럼 벌어지고,
    그냥 붙이면 「③원본과」 처럼 문장이 눌어붙는다. 줄이 오른쪽 끝까지
    닿았으면 소프트 줄바꿈으로 본다.
    """
    if not lines:
        return ''
    right = max(l['x1'] for l in lines)
    out = ''
    for i, l in enumerate(lines):
        out += l['t']
        if i + 1 == len(lines):
            break
        soft = l['x1'] >= right - 12 and l['p'] == lines[i + 1]['p']
        out += '' if soft else '\n'
    return out


def heads(lines):
    return [(i, int(HEAD.match(l['t']).group(1)))
            for i, l in enumerate(lines) if HEAD.match(l['t'])]


def quick_key(lines, n):
    """빠른 정답 — 「정답」 줄 뒤로 ①~④ 스무 개."""
    ts = [l['t'] for l in lines]
    key = {}
    for i, t in enumerate(ts):
        if t != '정답':
            continue
        nums = [int(x) for x in ts[max(0, i - 20):i] if x.isascii() and x.isdigit()]
        vals = []
        for v in ts[i + 1:i + 21]:
            if len(v) == 1 and v in CIRCLED:
                vals.append(CIRCLED.index(v) + 1)
            else:
                break
        if len(nums) == len(vals) == 20:
            key.update(zip(nums, vals))
    return [key.get(i, 0) for i in range(1, n + 1)] if len(key) == n else []


def answer_of(chunk):
    """「정 답」 칸 옆의 ①~⑤.

    PDF 의 읽는 차례는 표 칸을 늘 왼쪽→오른쪽으로 주지 않는다. 실제로 어떤
    문서는 답 칸을 머리말보다 **먼저** 내놓는다(「② / 정 답」). 뒤만 보면
    답을 못 찾고 빠른정답표와 어긋난 것처럼 보인다 — 양쪽을 다 본다.
    """
    ts = [l['t'] for l in chunk]
    for i, t in enumerate(ts):
        if not re.match(r'^■?\s*정\s*답$', t):
            continue
        for j in (i + 1, i + 2, i - 1, i - 2):
            if 0 <= j < len(ts):
                v = ts[j].strip()
                if len(v) == 1 and v in CIRCLED:
                    return CIRCLED.index(v) + 1
        for j in (i + 1, i + 2):
            if j < len(ts) and ts[j][:1] in CIRCLED:
                return CIRCLED.index(ts[j][0]) + 1
    return 0


def sol_of(chunk, area):
    keep = []
    for l in chunk:
        t = l['t']
        if SHELL.match(t) or TAILER.search(t) or t == area:
            continue
        if len(t) <= 2 and t[0] in CIRCLED:
            continue
        keep.append(l)
    whole = LEAD.sub('', join(keep).replace('\n', ' ')).strip()
    m = MIS_SPLIT.search(whole)
    return (whole[:m.start()].strip(), whole[m.end():].strip()) if m else (whole, '')


# ── 본체 ────────────────────────────────────────────────────────────────
def runs_of(at):
    """1 로 되돌아갈 때마다 새 덩이. 문제 한 덩이 · 해설 한 덩이가 짝이다.

    실전세트 문서에는 덩이가 넷 있다 — 「실전 30제」와 그 해설, 그 뒤에
    「즉시 재도전 10제」와 그 해설. 앞의 둘만 읽고 끊으면 열 문항이 사라진다.
    """
    out, cur = [], []
    for i, n in at:
        if n == 1 and cur:
            out.append(cur)
            cur = []
        cur.append((i, n))
    if cur:
        out.append(cur)
    return out


def sections(path):
    """이 PDF 안에 시험이 몇 벌 들어 있나 — (문항수, 덩이 번호) 목록."""
    import pymupdf
    rs = runs_of(heads(lines_of(pymupdf.open(path))))
    return [(len(rs[k]), k // 2) for k in range(0, len(rs) - 1, 2)]


def parse_pdf(path, section=0):
    import pymupdf
    doc = pymupdf.open(path)
    lines = lines_of(doc)
    at = heads(lines)
    rs = runs_of(at)
    if len(rs) < 2 * section + 2:
        raise SystemExit('%s: %d번째 시험이 없다 (덩이 %d개)'
                         % (Path(path).name, section + 1, len(rs)))
    qat, sat = rs[2 * section], rs[2 * section + 1]
    n = max(v for _, v in qat)
    if len(qat) != n or len(sat) != n:
        raise SystemExit('%s: 머리 수가 안 맞는다 (문제 %d · 해설 %d · 최대 %d)'
                         % (Path(path).name, len(qat), len(sat), n))

    # 마지막 문제는 「빠른 정답」·「PART」 앞에서 끊는다
    qend = sat[0][0]
    for i in range(qat[-1][0] + 1, sat[0][0]):
        if STOP.match(lines[i]['t']):
            qend = i
            break
    nxt = rs[2 * section + 2][0][0] if len(rs) > 2 * section + 2 else len(lines)
    send = nxt
    for i in range(sat[-1][0] + 1, nxt):
        if OUTRO.match(lines[i]['t']):
            send = i
            break

    link = next((l['t'] for l in lines if 'final-submit.html?exam=' in l['t']), '')
    code = (re.search(r'exam=([a-z0-9]+)', link) or [None, ''])[1]
    quick = quick_key(lines, n)

    qs = []
    for j, (i, num) in enumerate(qat):
        stop = qat[j + 1][0] if j + 1 < len(qat) else qend
        body = lines[i + 1:stop]
        # 머리표는 「문제 NN · 영역 · 난이도」 인데 PDF 의 읽는 차례가 셋을
        # 늘 그 순서로 주지는 않는다. 앞 세 줄에서 난이도가 아닌 첫 줄이 영역이다.
        area = ''
        for l in body[:3]:
            t = l['t'].strip()
            if t and not LEVEL.match(t) and not t.startswith('즉시'):
                area = re.split(r'\s*←', t)[0].strip()
                break
        qs.append({'n': num, 'area': area, 'mark': lines[i],
                   'end': lines[stop] if stop < len(lines) else None})
    for j, (i, num) in enumerate(sat):
        stop = sat[j + 1][0] if j + 1 < len(sat) else send
        chunk = lines[i + 1:stop]
        q = qs[num - 1]
        q['answer'] = answer_of(chunk) or (quick[num - 1] if quick else 0)
        if quick and q['answer'] and quick[num - 1] and q['answer'] != quick[num - 1]:
            raise SystemExit('%s %d번: 정답이 빠른정답표와 다르다 (%s vs %s)'
                             % (Path(path).name, num, q['answer'], quick[num - 1]))
        body, tip = sol_of(chunk, q['area'])
        q['sol'], q['tip'] = body, tip
    return {'doc': doc, 'band': bands(doc), 'code': code, 'nQ': n, 'q': qs,
            'section': section,
            'kind': '변형본' if quick else '실전세트', 'source': Path(path).name}


def to_hwpx_shape(d):
    """ingest_hwpx_exam 의 답지 생성기가 먹는 꼴로 바꾼다."""
    return {'examId': d['examId'], 'title': d['title'], 'kind': d['kind'],
            'q': [{'n': q['n'], 'area': q['area'], 'answer': q['answer'],
                   'sol': None, '_body': q['sol'], '_tip': q['tip']} for q in d['q']]}


# 한 학생이 시험지를 셋 받는다. 뒤에 붙는 번호가 곧 그 차례다.
SUFFIX = {'변형본': '2', '실전세트': '3', '즉시재도전': '4'}
TITLE = {'변형본': '파이널 변형본 %d제 · %s',
         '실전세트': '실전 %d제 · %s',
         '즉시재도전': '즉시 재도전 %d제 · %s'}


def ingest(path, code=None, kind=None, section=0, write=False):
    import pymupdf
    d = parse_pdf(path, section)
    d['code'] = code or d['code']
    if not d['code']:
        raise SystemExit('%s: 학생 코드를 못 찾았다 — --code 로 준다' % path)
    if kind:
        d['kind'] = kind
    elif d['kind'] == '실전세트' and section:
        d['kind'] = '즉시재도전'
    d['examId'] = '%s-%s' % (d['code'], SUFFIX[d['kind']])
    d['title'] = TITLE[d['kind']] % (d['nQ'], d['code'])

    qs = {}
    for q in d['q']:
        area = map_area(tidy(q['area']))
        qs[str(q['n'])] = {
            'answer': q['answer'], 'acceptableAnswers': [q['answer']],
            'excluded': False, 'concept': type_of(area), 'area': area,
            'learningPoint': type_of(area), 'explanation': tidy(q['sol']),
            'explanationHtml': '', 'misconception': tidy(q['tip']),
            'sourceSolution': '선생님 원본 해설 (%s · PDF)' % d['kind'],
            'verificationStatus': 'verified_against_supplied_solution_book'}
    ans = {'schemaVersion': 1, 'examId': d['examId'], 'examTitle': d['title'],
           'note': 'tools/ingest_pdf_exam.py 가 선생님 PDF 원본에서 옮겼다. '
                   '손으로 고치면 --check 가 어긋난다.',
           'questions': qs}
    ent = {'id': d['examId'], 'title': d['title'], 'group': '파이널',
           'hidden': True, 'nQ': d['nQ'], 'mode': 'auto', 'cut': cut_of(d['nQ']),
           'key': [q['answer'] for q in d['q']], 'miss': [],
           'area': [map_area(tidy(q['area'])) for q in d['q']],
           'type': [type_of(map_area(tidy(q['area']))) for q in d['q']],
           'crops': True,
           'source': {'tool': 'tools/ingest_pdf_exam.py', 'kind': d['kind'],
                      'file': d['source']}}

    if not write:
        print('%s → %s · %s · %d문항 · 정답 %s…'
              % (Path(path).name, d['examId'], d['kind'], d['nQ'],
                 ''.join(str(k) for k in ent['key'][:10])))
        return ent

    cd = ROOT / 'crops' / d['examId']
    cd.mkdir(parents=True, exist_ok=True)
    for old in cd.glob('*.png'):
        old.unlink()
    for q in d['q']:
        ok = crop_pdf(d['doc'], d['band'],
                      {'page': q['mark']['p'], 'y': q['mark']['y']},
                      ({'page': q['end']['p'], 'y': q['end']['y']} if q['end'] else None),
                      cd / ('%d.png' % q['n']), pymupdf)
        if not ok:
            raise SystemExit('%s %d번 크롭 실패' % (d['examId'], q['n']))
    (ROOT / 'answers' / ('%s.json' % d['examId'])).write_text(
        json.dumps(ans, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    doc, p = load_finals()
    doc['exams'] = [e for e in doc['exams'] if e['id'] != d['examId']] + [ent]
    doc['exams'].sort(key=lambda e: e['id'])
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('%s 들였다 — 크롭 %d · 답지 · 회차' % (d['examId'], d['nQ']))
    return ent


def main():
    argv = sys.argv[1:]
    if '--check' in argv:
        return check()
    args = [a for a in argv if not a.startswith('--')]
    code = kind = None
    if '--code' in argv:
        code = argv[argv.index('--code') + 1]
        args = [a for a in args if a != code]
    if '--kind' in argv:
        kind = argv[argv.index('--kind') + 1]
        args = [a for a in args if a != kind]
    sec = int(argv[argv.index('--section') + 1]) if '--section' in argv else 0
    if not args:
        print(__doc__)
        return 2
    for f in args:
        ingest(f, code=code, kind=kind, section=sec, write='--write' in argv)
    return 0


if __name__ == '__main__':
    sys.exit(main())
