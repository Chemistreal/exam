#!/usr/bin/env python3
"""HWP 5.0(바이너리) 문제지에서 글자를 뽑는다 — **수식까지 제자리에**.

화올·KMChC 문제지는 반응식·이온·선택지를 **수식 개체**로 넣어 둔다. 문단
글자만 뽑으면 그 자리가 통째로 비어 이렇게 나온다.

    다음 이온들의 크기를 바르게 비교한 것은?   ① ② ③ ④

답지 서른두 문항에 "원본서 렌더 누락" 이라 적혀 있던 것이 이것이다. 답은
채점표를 보고 적었지만 **왜 그 답인지**를 쓸 수 없었다.

수식은 사라진 것이 아니라 HWPTAG_EQEDIT(88) 레코드에 스크립트로 남아 있다.
레코드는 문서 차례대로 오므로 문단 글자와 수식을 만나는 대로 이어 붙이면
제자리에 들어간다.

    다음 이온들의 크기를 바르게 비교한 것은?
    ① Br^- > Se^2- , Rb^+ > Sr^2+    ② Br^- > Se^2- , Rb^+ < Sr^2+
    ③ Br^- < Se^2- , Rb^+ > Sr^2+    ④ Br^- < Se^2- , Rb^+ < Sr^2+

⚠ 문제지 원본은 대회 문제라 저장소에 넣지 않는다. 이 파일은 **읽는 법**만
   담는다 — 뽑은 글은 작업 폴더에만 두고, 저장소에는 그것을 보고 쓴 해설만
   들어간다.

문항은 '문제 N' 으로 시작하고, 회차에 따라 '정답률 : NN%' 가 붙어 있다.

    python3 tools/hwp_text.py <파일.hwp>
"""
import olefile, zlib, struct, sys, re

CTRL_EXT = {1,2,3,11,12,14,15,16,17,18,21,22,23}
CTRL_INLINE = {4,5,6,7,8,9,19,20}


def records(buf):
    i = 0
    while i + 4 <= len(buf):
        h = struct.unpack('<I', buf[i:i+4])[0]
        tag, lvl, sz = h & 0x3FF, (h >> 10) & 0x3FF, (h >> 20) & 0xFFF
        i += 4
        if sz == 0xFFF:
            sz = struct.unpack('<I', buf[i:i+4])[0]; i += 4
        yield tag, lvl, buf[i:i+sz]
        i += sz


def para_text(d):
    out, i = [], 0
    while i + 1 < len(d):
        c = struct.unpack('<H', d[i:i+2])[0]
        if c in CTRL_EXT or c in CTRL_INLINE:
            i += 16; continue
        if c in (10, 13):
            out.append('\n'); i += 2; continue
        if c < 32:
            i += 2; continue
        out.append(chr(c)); i += 2
    return ''.join(out)


def eq_script(d):
    """수식 스크립트를 사람이 읽는 꼴로. ` 는 HWP 의 사이띄개다."""
    n = struct.unpack('<H', d[4:6])[0]
    try:
        s = d[6:6+n*2].decode('utf-16le')
    except Exception:
        return ''
    s = s.replace('`', ' ').replace('#', ' / ')
    s = re.sub(r'_\{([^}]*)\}', r'_\1', s)
    s = re.sub(r'\^\{([^}]*)\}', r'^\1', s)
    for a, b in (('DELTA', 'Δ'), ('BULLET', '·'), ('EXARROW', '⇄'),
                 ('RIGHTARROW', '→'), ('LEFTARROW', '←'), ('->', '→'),
                 ('LEQ', '≤'), ('GEQ', '≥'), ('NEQ', '≠'), ('TIMES', '×'),
                 ('ALPHA', 'α'), ('BETA', 'β'), ('GAMMA', 'γ'), ('LAMBDA', 'λ')):
        s = s.replace(a, b)
    return re.sub(r'\s{2,}', ' ', s).strip()


def text(path):
    o = olefile.OleFileIO(path)
    comp = struct.unpack('<I', o.openstream('FileHeader').read()[36:40])[0] & 1
    parts = []
    for s in sorted('/'.join(x) for x in o.listdir()):
        if not s.startswith('BodyText'):
            continue
        b = o.openstream(s).read()
        if comp:
            b = zlib.decompress(b, -15)
        for tag, lvl, d in records(b):
            if tag == 67:
                parts.append(para_text(d))
            elif tag == 88:
                e = eq_script(d)
                if e:
                    parts.append('〔' + e + '〕')
    return '\n'.join(parts)


if __name__ == '__main__':
    sys.stdout.write(text(sys.argv[1]))
