#!/usr/bin/env python3
"""HWPX 에서 캔 문제 덩이를 시험지 HTML 로 옮긴다.

크롭(crops/<시험ID>/<번호>.png)과 문제지 PDF 를 같은 HTML 한 장에서 뽑는다.
글꼴은 화면과 같은 Noto Serif KR · Noto Sans KR 을 쓴다.
"""
import base64, html, re

PX = 7200.0 / 955.0          # HWPUNIT(1/7200 inch) → 크롭 폭 955px 기준
MAXW = 900


def esc(s):
    return html.escape(s, quote=False)


def _img(b, bins):
    ext, raw = bins.get(b['ref'], ('png', b''))
    if not raw:
        return ''
    w = b.get('w') or 0
    px = min(MAXW, round(w / PX)) if w else 420
    mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else 'image/' + ext
    return ('<img alt="" style="width:%dpx" src="data:%s;base64,%s">'
            % (px, mime, base64.b64encode(raw).decode()))


def blocks_html(blocks, bins, depth=0):
    out = []
    for b in blocks:
        if b['t'] == 'p':
            t = b['x'].strip()
            if not t:
                continue
            cls = ' class="ch"' if t[0] in '①②③④⑤' else ''
            out.append('<p%s>%s</p>' % (cls, esc(t)))
        elif b['t'] == 'img':
            out.append('<figure>%s</figure>' % _img(b, bins))
        elif b['t'] == 'tbl':
            rows = []
            for row in b['rows']:
                tds = []
                for c in row:
                    inner = blocks_html(c['b'], bins, depth + 1)
                    sp = ''
                    if c.get('cs', 1) > 1:
                        sp += ' colspan="%d"' % c['cs']
                    if c.get('rs', 1) > 1:
                        sp += ' rowspan="%d"' % c['rs']
                    tds.append('<td%s>%s</td>' % (sp, inner))
                rows.append('<tr>%s</tr>' % ''.join(tds))
            out.append('<table class="%s">%s</table>'
                       % (_kind(b), ''.join(rows)))
    return ''.join(out)


def _kind(b):
    """선지만 든 표는 줄을 긋지 않는다 — 그림이 들어간 선지 표는 칸을 살린다."""
    cells, imgs, opts = 0, 0, 0
    for row in b['rows']:
        for c in row:
            t = ''.join(x['x'] for x in c['b'] if x['t'] == 'p').strip()
            has = any(x['t'] == 'img' for x in c['b'])
            imgs += has
            if t or has:
                cells += 1
            if t[:1] in '①②③④⑤':
                opts += 1
    if cells and opts == cells and not imgs:
        return 'opts'
    return 'grid' if len(b['rows'][0]) > 1 else 'plain'


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#fff;color:#16181d;font-family:'Noto Serif KR',serif;
     font-size:17px;line-height:1.62;-webkit-font-smoothing:antialiased}
.q{width:955px;padding:14px 16px 18px;background:#fff}
.qh{display:flex;align-items:baseline;gap:10px;margin:0 0 9px;
    font-family:'Noto Sans KR',sans-serif;border-bottom:2px solid #16181d;
    padding-bottom:5px}
.qn{font-weight:700;font-size:19px;letter-spacing:-.01em}
.qa{font-size:14px;color:#5b6270;font-weight:500}
.ql{margin-left:auto;font-size:12px;color:#8a90a0}
.q p{margin:.30em 0;text-align:justify;word-break:keep-all}
.q p.ch{margin:.16em 0 .16em .2em}
figure{margin:.5em 0;text-align:center}
figure img{max-width:100%;height:auto}
table{border-collapse:collapse;margin:.5em 0}
table.grid{width:auto;border:1.4px solid #16181d}
table.grid td{border:1px solid #9aa0ad;padding:4px 9px;font-size:15.5px;
              text-align:center;vertical-align:middle}
table.opts{width:100%;border:0;margin:.34em 0 .1em}
table.opts td{border:0;padding:1px 16px 1px 0;font-size:16.5px;
              text-align:left;vertical-align:top;white-space:nowrap}
table.plain{width:100%;border:0}
table.plain td{border:0;padding:1px 0}
table td p{margin:0}
@media print{.q{page-break-inside:avoid}}
"""


def exam_html(doc, title, bins, sol=False):
    body = []
    for q in doc['q']:
        blocks = q['sol'] if sol else q['body']
        lab = []
        if q['area']:
            lab.append(esc(q['area']))
        if q['level']:
            lab.append(esc(q['level']))
        body.append(
            '<section class="q" data-n="%d">'
            '<div class="qh"><span class="qn">문제 %02d</span>'
            '<span class="qa">%s</span>%s</div>%s</section>'
            % (q['n'], q['n'], ' · '.join(lab),
               '<span class="ql">%s</span>' % esc(q['src']) if q['src'] else '',
               blocks_html(blocks, bins)))
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<title>%s</title><style>%s</style></head><body>%s</body></html>'
            % (esc(title), CSS, ''.join(body)))
