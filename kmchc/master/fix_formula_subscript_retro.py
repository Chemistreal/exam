# -*- coding: utf-8 -*-
"""fix_formula_subscript_retro — 화학식의 숫자를 ★아래 첨자★ 로 되돌려 적는다

  ■ 무엇을 재었나
    감사41 의 Y 가 '로마자 화학식' 을 세었더니 38제가 울었다. 그런데 열어 보니 대부분은
    화학식이 아니라 ★딴 것★ 이었다 — 'T4'(테마 번호) · 'M393'(문항 가리킴) · 'K4'.
    ★원소 기호로 시작하는 것만★ 남기자 22제, 그 가운데 'K4' 여덟 제를 걷어내면 14제다.

  ■ 왜 고치는가
    이 은행은 화학식을 ★아래 첨자로 적는다★ — 계수 맞추기 2,140 · 양적관계 1,353 ·
    물질의 조성 1,339 … 5,400 자리가 그렇게 적혀 있다. 그런데 탄화수소 13제와 화학결합
    1제만 'C3H8' 처럼 민숭민숭하게 적혀 있었다. ★같은 것을 두 가지로 적는 자리★ 다.
    학생이 보는 화면에서 C3H8 은 '탄소 3 수소 8' 이 아니라 다른 무엇으로 읽힐 수 있다.

  ■ 어떻게 고치는가
    ★첫 판이 개념 id 를 물었다★ — 문항 블록의 주석에 적힌 'C22-002' 가 'C₂₂₋₀₀₂' 이 되었다.
    일반식의 'CₙH₂ₙ₋₂' 는 붙임표가 아니라 ★빼기표(−)★ 이므로, 이음표를 빼기표만 받게
    좁혀 갈랐다. 블록 안이라고 안전한 것이 아니라 ★주석도 블록 안★ 이다.

    ★문항 블록 안에서만★ 바꾼다 — 배치 파일 전체에 정규식을 걸면 id(M02628)나 주석의
    숫자까지 물린다. 원소 기호 뒤에 붙은 숫자·n·부호만 아래 첨자로 옮기고,
    ★계수는 건드리지 않는다★(2O₂ 의 앞 2 는 그대로다 — 원소 기호 뒤가 아니기 때문).
"""
import glob
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
EL = set('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Fe Cu Zn Br I'.split())
SUB = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆',
       '7': '₇', '8': '₈', '9': '₉', 'n': 'ₙ', '+': '₊', '-': '₋', '−': '₋'}
TARGETS = ['M02497', 'M02628', 'M02637', 'M02641', 'M02650', 'M02687', 'M02688',
           'M02689', 'M02712', 'M02724', 'M02728', 'M02749', 'M02757', 'M02772']
#   화학식 한 덩이 — 원소 기호로 시작해 (기호|숫자|n|부호) 가 이어 붙은 자리
#   ▸ ★앞의 계수를 넘어서 잡는다★ — '2O2' 처럼 계수가 붙으면 O 앞에 낱말 경계가 없다.
#     그래서 \b 대신 '로마자·아래첨자가 앞에 없을 것' 으로 연다.
TOKEN = re.compile(r'(?<![A-Za-z₀-₉ₙ])(?:[A-Z][a-z]?(?:\d+n?|n(?![a-z]))?)+'
                   r'(?:[+−]\d+)?')
#   개념 id(C22-002 · C16-006) — ★먼저 가려 두고★ 바꾼 뒤 되돌린다.
#   뒤보기(?!-\d) 로 막으려 했더니 정규식이 한 글자 물러서서 'C₂2-002' 가 되었다.
CID = re.compile(r'\b[A-Z]\d{1,2}-\d{3}\b')


def conv(tok):
    """원소 기호는 그대로, 그 뒤에 붙은 숫자·n·부호만 아래 첨자로."""
    #   ▸ ★두 글자 기호를 먼저 대 보되, 표에 없으면 한 글자로 물러선다★ —
    #     'CnH2n−2' 의 'Cn' 을 코페르니슘으로 읽어 통째로 손대지 못하던 자리다.
    out, i = [], 0
    while i < len(tok):
        two = tok[i:i + 2]
        sym = two if (len(two) == 2 and two[1].islower() and two in EL) else tok[i:i + 1]
        if sym in EL:
            out.append(sym)
            i += len(sym)
            while i < len(tok) and tok[i] in SUB:
                out.append(SUB[tok[i]])
                i += 1
        else:                       # 원소 기호가 아니면 그 덩이는 손대지 않는다
            return None
    return ''.join(out)


def fix_text(s):
    keep = CID.findall(s)
    for k, cid in enumerate(keep):
        s = s.replace(cid, '\x00%d\x00' % k, 1)

    def r(m):
        t = m.group(0)
        if not re.search(r'\d|n', t) or re.match(r'^[A-Z][a-z]?$', t):
            return t
        c = conv(t)
        return c if c and c != t else t
    s = TOKEN.sub(r, s)
    for k, cid in enumerate(keep):
        s = s.replace('\x00%d\x00' % k, cid, 1)
    return s


def block(src, mid):
    """문항 블록의 자리 — q('MID' 부터 다음 it.append( 또는 return it 까지."""
    for qt in ("'%s'" % mid, '"%s"' % mid):
        k = src.find('q(' + qt)
        if k >= 0:
            nxt = [x for x in (src.find('it.append(', k + 4), src.find('return it', k))
                   if x > 0]
            return k, min(nxt) if nxt else len(src)
    return None


def main():
    total = 0
    for f in sorted(glob.glob(os.path.join(HERE, 'build_*.py'))):
        s = io.open(f, encoding='utf-8').read()
        hit = [t for t in TARGETS if block(s, t)]
        if not hit:
            continue
        for mid in hit:
            a, b = block(s, mid)
            new = fix_text(s[a:b])
            if new != s[a:b]:
                got = sorted({m.group(0) for m in re.finditer(r'[A-Z][a-z]?[₀-₉ₙ₊₋]+', new)})
                print('  %-22s %s  ← %s' % (os.path.basename(f), mid, ' '.join(got[:6])))
                s = s[:a] + new + s[b:]
                total += 1
        io.open(f, 'w', encoding='utf-8').write(s)
    print('✅ %d 문항의 화학식을 아래 첨자로 되돌렸다 — patch_batch 로 은행에 옮긴다' % total)


if __name__ == '__main__':
    main()
