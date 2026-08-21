#!/usr/bin/env python3
"""선생님이 한글(HWPX)로 만든 시험지를 읽어 구조로 바꾼다.

한 파일 안에 네 덩이가 있다.

  1. 앞머리      — 판정·4시간 운영표·확신도 표
  2. 문제 1~N    — 「문제 NN」 머리표 + 지문 + 표·그림 + 선지 ①②③④
  3. 빠른 정답   — 20개씩 (변형본에만 있다)
  4. 해설 1~N    — 「정  답 ④」 + 풀이

두 갈래가 온다.

  변형본 60제   머리표 = 문제 NN · 영역 · 「변형」
  실전 30제     머리표 = 문제 NN · 단원 · 「난이도 상/중/하」 + 출전 한 줄

문제도 해설도 글자다 — 표는 표대로, 그림은 그림대로 자리를 지켜 옮긴다.
한글 프로그램 없이 읽으므로 PDF 로 바꿔 잘라 낼 것이 없다.
"""
import json, re, sys, zipfile
from xml.etree import ElementTree as ET

HP = '{http://www.hancom.co.kr/hwpml/2011/paragraph}'
CIRCLED = '①②③④⑤'
HEAD = re.compile(r'^문제\s*(\d{1,3})$')
ANS_CELL = re.compile(r'^정\s*답$')
LEVEL = re.compile(r'^(변형|난이도\s*[상중하])$')
SRC = re.compile(r'^(기출동형|KMChC|USNCO|화올|파이널)\b.*\d')
TAIL = re.compile(r'·\s*난이도\s*(변형|[상중하])\s*$')
# 문제 덩이가 여기서 끝난다 — 뒤는 정답·해설이다
STOP = re.compile(r'^(빠른\s*정답|PART|[가-힣]\s*[가-힣]?\s*[가-힣]?\s*해\s*설.*)$')
# 마지막 해설 뒤에 붙는 맺음말 — 해설로 새어 들어가면 안 된다
OUTRO = re.compile(r'^(마\s*감\s*카\s*드|맺\s*음|여기까지 온 것만으로)')


# ── 읽기 ────────────────────────────────────────────────────────────────
def _runs(p):
    """한 문단 안의 글자와 그림. 표는 밖에서 따로 다룬다."""
    out = []
    buf = []

    def flush():
        if buf:
            out.append({'t': 'p', 'x': ''.join(buf)})
            buf.clear()

    def walk(node):
        for ch in node:
            if ch.tag in (HP + 'tbl',):
                continue
            if ch.tag == HP + 't':
                buf.append(''.join(ch.itertext()))
            elif ch.tag == HP + 'pic':
                ref = next((im.get('binaryItemIDRef') for im in ch.iter()
                            if im.tag.endswith('}img')
                            and im.get('binaryItemIDRef')), None)
                sz = next((s for s in ch.iter(HP + 'sz')), None)
                if ref:
                    flush()
                    out.append({'t': 'img', 'ref': ref,
                                'w': int(sz.get('width', 0)) if sz is not None else 0,
                                'h': int(sz.get('height', 0)) if sz is not None else 0})
            else:
                walk(ch)

    walk(p)
    flush()
    return out


def _tbl(tbl):
    """표를 줄·칸으로 되살린다. cellAddr 로 자리를 잡는다."""
    rows = int(tbl.get('rowCnt') or 0)
    cols = int(tbl.get('colCnt') or 0)
    grid = {}
    for tr in tbl.findall(HP + 'tr'):
        for tc in tr.findall(HP + 'tc'):
            ad = tc.find(HP + 'cellAddr')
            sp = tc.find(HP + 'cellSpan')
            r = int(ad.get('rowAddr')) if ad is not None else 0
            c = int(ad.get('colAddr')) if ad is not None else 0
            body = []
            for sub in tc.findall(HP + 'subList'):
                body.extend(_body(sub))
            grid[(r, c)] = {'b': body,
                            'cs': int(sp.get('colSpan') or 1) if sp is not None else 1,
                            'rs': int(sp.get('rowSpan') or 1) if sp is not None else 1}
            rows = max(rows, r + 1)
            cols = max(cols, c + 1)
    out = []
    for r in range(rows):
        row = [grid[(r, c)] for c in range(cols) if (r, c) in grid]
        if row:
            out.append(row)
    return {'t': 'tbl', 'rows': out}


def _body(el):
    out = []
    for ch in el:
        if ch.tag == HP + 'p':
            out.extend(_runs(ch))
            for tbl in ch.iter(HP + 'tbl'):
                out.append(_tbl(tbl))
        elif ch.tag == HP + 'tbl':
            out.append(_tbl(ch))
        else:
            out.extend(_body(ch))
    return out


def read_doc(path):
    z = zipfile.ZipFile(path)
    names = sorted(n for n in z.namelist()
                   if re.match(r'Contents/section\d+\.xml$', n))
    out = []
    for n in names:
        out.extend(_body(ET.fromstring(z.read(n))))
    return out


def bindata(path):
    z = zipfile.ZipFile(path)
    out = {}
    for n in z.namelist():
        m = re.match(r'BinData/(BIN[0-9A-Fa-f]+)\.(\w+)$', n)
        if m:
            out[m.group(1)] = (m.group(2).lower(), z.read(n))
    return out


# ── 납작하게 ────────────────────────────────────────────────────────────
def flat_text(blocks):
    """('p'|'cell'|'img', 글자) 차례 — 머리 찾기·정답 캐기에 쓴다."""
    out = []
    for b in blocks:
        if b['t'] == 'p':
            t = b['x'].strip()
            if t:
                out.append(('p', t))
        elif b['t'] == 'img':
            out.append(('img', b['ref']))
        elif b['t'] == 'tbl':
            for row in b['rows']:
                for cell in row:
                    for k, t in flat_text(cell['b']):
                        out.append(('cell' if k == 'p' else k, t))
    return out


def cell_text(cell):
    return '\n'.join(t for k, t in flat_text(cell['b']) if k != 'img').strip()


# ── 덩이 나누기 ──────────────────────────────────────────────────────────
def _heads(blocks):
    """머리표를 찾는다. 「문제 NN」 은 늘 표 첫 칸에 있다."""
    at = []
    for i, b in enumerate(blocks):
        if b['t'] != 'tbl' or not b['rows']:
            continue
        first = cell_text(b['rows'][0][0]) if b['rows'][0] else ''
        m = HEAD.match(first.split('\n')[0].strip())
        if m:
            cells = [cell_text(c) for row in b['rows'] for c in row]
            at.append((i, int(m.group(1)), cells))
    return at


def _quick_key(blocks, n):
    """빠른 정답 표 — 「정답」 칸 뒤로 스무 개씩."""
    key = {}
    for b in blocks:
        if b['t'] != 'tbl':
            continue
        cells = [cell_text(c) for row in b['rows'] for c in row]
        for i, t in enumerate(cells):
            if t != '정답':
                continue
            nums = [int(x) for x in cells[max(0, i - 20):i]
                    if x.isascii() and x.isdigit()]
            vals = []
            for v in cells[i + 1:i + 21]:
                if len(v) == 1 and v in CIRCLED:
                    vals.append(CIRCLED.index(v) + 1)
                else:
                    break
            if len(nums) == len(vals) == 20:
                key.update(zip(nums, vals))
    return [key.get(i, 0) for i in range(1, n + 1)] if len(key) == n else []


def _answer(blocks):
    """해설 덩이에서 정답 번호. 「정  답」 칸 바로 뒤가 ①~⑤."""
    fl = flat_text(blocks)
    for i, (k, t) in enumerate(fl):
        if ANS_CELL.match(t) or re.match(r'^■?\s*정\s*답$', t):
            for j in range(i + 1, min(len(fl), i + 3)):
                v = fl[j][1].strip()
                if v and v[0] in CIRCLED:
                    return CIRCLED.index(v[0]) + 1
    return 0


def _choices(blocks):
    """선지 ①②③④ 를 모은다. 한 칸에 붙어 온 것은 쪼갠다."""
    out = []
    for k, t in flat_text(blocks):
        if k == 'img' or not t or t[0] not in CIRCLED:
            continue
        if sum(t.count(c) for c in CIRCLED) >= 2:
            out.extend(x.strip() for x in re.split(r'(?=[①-⑤])', t) if x.strip())
        elif len(t) > 1:
            out.append(t)
    seen, uniq = set(), []
    for c in out:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


def _regrid(body):
    """줄로 흩어진 짝지음 표를 표로 되살린다.

    원본이 PDF 에서 붙여 넣은 자리라 표가 문단 열다섯 줄로 풀려 있다 —
    「A B C · 물 설탕 CaCl₂ · …」. 뒤에 ①②③④ 만 든 표가 붙어 있으면
    머리 k 칸 + 네 줄로 다시 짠다.
    """
    idx = None
    for i, b in enumerate(body):
        if b['t'] != 'tbl' or len(b['rows']) != 1:
            continue
        cells = [cell_text(c) for c in b['rows'][0]]
        if len(cells) == 4 and all(len(t) == 1 and t in CIRCLED for t in cells):
            idx = i
            break
    if idx is None:
        return body
    j = idx
    run = []
    while j > 0:
        prev = body[j - 1]
        if prev['t'] == 'p' and 0 < len(prev['x'].strip()) <= 14 \
                and not prev['x'].strip().endswith(('?', '.', '다')):
            run.insert(0, prev['x'].strip())
            j -= 1
        elif prev['t'] == 'p' and not prev['x'].strip():
            j -= 1
        else:
            break
    L = len(run)
    for k in range(2, 9):
        if L <= k or (L - k) % 4:
            continue
        w = (L - k) // 4
        if w not in (k, k - 1):
            continue
        head = run[:k]
        rows = [run[k + r * w:k + (r + 1) * w] for r in range(4)]
        if w == k:                       # 번호 칸을 앞에 붙인다
            head = [''] + head
            rows = [[CIRCLED[r]] + rows[r] for r in range(4)]
        else:                            # 첫 머리칸이 번호 칸이다
            rows = [[CIRCLED[r]] + rows[r] for r in range(4)]
        cell = lambda t: {'b': [{'t': 'p', 'x': t}], 'cs': 1, 'rs': 1}
        tbl = {'t': 'tbl', 'rows': [[cell(t) for t in head]]
                                   + [[cell(t) for t in r] for r in rows]}
        return body[:j] + [tbl] + body[j:idx] + body[idx + 1:]
    return body


# ── 본체 ────────────────────────────────────────────────────────────────
def parse(path):
    doc = read_doc(path)
    at = _heads(doc)
    firsts = [i for i, (_, n, _) in enumerate(at) if n == 1]
    if len(firsts) < 2:
        raise ValueError('문제·해설 두 덩이를 못 찾았다')
    qat, sat = at[:firsts[1]], at[firsts[1]:]
    n = max(v for _, v, _ in qat)
    if len(qat) != n or len(sat) != n:
        raise ValueError('머리 수가 안 맞는다 (문제 %d · 해설 %d · 최대 %d)'
                         % (len(qat), len(sat), n))

    # 마지막 문제는 「빠른 정답」·「PART」 앞에서 끊는다 — 안 그러면 정답표를 삼킨다
    qend = sat[0][0]
    for i in range(qat[-1][0] + 1, sat[0][0]):
        b = doc[i]
        if b['t'] == 'p' and STOP.match(b['x'].strip()):
            qend = i
            break

    fl = flat_text(doc)
    link = next((t for _, t in fl if 'final-submit.html?exam=' in t), '')
    code = (re.search(r'exam=([a-z0-9]+)', link) or [None, ''])[1]
    quick = _quick_key(doc, n)

    out = []
    for j, (i, num, cells) in enumerate(qat):
        stop = qat[j + 1][0] if j + 1 < len(qat) else qend
        body = doc[i + 1:stop]
        head = [c for c in cells[1:] if c]
        area = head[0] if head else ''
        level = next((c for c in head if LEVEL.match(c)), '')
        src = ''
        if body and body[0]['t'] == 'p' and SRC.match(body[0]['x'].strip()) \
                and len(body[0]['x'].strip()) < 40:
            src = body[0]['x'].strip()
            body = body[1:]
        body = _regrid(body)
        ch = _choices(body)
        fl = flat_text(body)
        marks = {c for k, t in fl for c in CIRCLED[:4] if c in t}
        kind = ('글' if len(ch) >= 4 else
                '표' if len(marks) >= 4 else
                '그림' if any(k == 'img' for k, _ in fl) else '없음')
        out.append({'n': num, 'area': area, 'level': level, 'src': src,
                    'body': body, 'choices': ch, 'choiceKind': kind,
                    'answer': 0, 'sol': []})

    # 맺음말은 마지막 해설이 아니다 — 「마 감 카 드」 앞에서 끊는다
    send = len(doc)
    for i in range(sat[-1][0] + 1, len(doc)):
        if doc[i]['t'] == 'p' and OUTRO.match(doc[i]['x'].strip()):
            send = i
            break

    for j, (i, num, cells) in enumerate(sat):
        stop = sat[j + 1][0] if j + 1 < len(sat) else send
        sol = doc[i + 1:stop]
        q = out[num - 1]
        q['sol'] = sol
        q['answer'] = _answer(sol)

    if quick:
        for q in out:
            k = quick[q['n'] - 1]
            if q['answer'] and k and q['answer'] != k:
                raise ValueError('%d번 정답이 빠른정답표와 다르다 (%s vs %s)'
                                 % (q['n'], q['answer'], k))
            q['answer'] = q['answer'] or k

    return {'source': path.split('/')[-1], 'code': code,
            'kind': '변형본' if quick else '실전세트', 'nQ': n, 'q': out}


def check(d):
    bad = []
    for q in d['q']:
        why = []
        if not [1 for k, t in flat_text(q['body']) if k in ('p', 'cell')]:
            why.append('지문없음')
        if q['choiceKind'] == '없음':
            why.append('선지%d' % len(q['choices']))
        if not q['answer']:
            why.append('정답없음')
        if not q['sol']:
            why.append('해설없음')
        # 문제 쪽에 정답이 새면 안 된다
        if any('빠른 정답' in t or ANS_CELL.match(t)
               for k, t in flat_text(q['body'])):
            why.append('정답유출')
        if why:
            bad.append('%d번(%s)' % (q['n'], ','.join(why)))
    return bad


def main():
    ap = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not ap:
        raise SystemExit('쓰기: hwpx_exam.py <파일.hwpx> [--json]')
    d = parse(ap[0])
    if '--json' in sys.argv:
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return 0
    bad = check(d)
    print('%-6s %-13s %2d문항 · 흠 %s'
          % (d['kind'], d['code'] or '코드없음', d['nQ'], ' '.join(bad) or '없음'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main() or 0)
