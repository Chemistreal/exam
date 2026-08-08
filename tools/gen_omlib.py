#!/usr/bin/env python3
"""오개념 라이브러리(OMLIB)를 **한 벌로** 맞춘다 — final.html 이 원본이다.

같은 표가 두 화면에 따로 적혀 있었다.

    final.html   641줄   모든 유형을 덮는다. tools/om_cover.py 가 지킨다
    index.html    83줄   그 가운데 여든셋만. 지키는 것이 없었다

둘은 같은 함수(`omFor(type)`)로 쓰인다. 학생이 보는 오개념 한 줄이 화면마다
다르다는 뜻이고, 실제로 두 줄이 갈라져 있었다.

    분자간력  final: 이온결합>이온-쌍극자>…      index: 이온-이온>이온-쌍극자>…
    충돌      final: 평균자유행로는 온도 무관   index: 부피 일정 시 온도 무관,
                                                     압력 일정 시 온도에 비례

뒤엣것은 index 쪽이 옳다 — 평균자유행로는 수밀도에 반비례하므로 압력이
일정하면 온도에 비례한다. 그 두 줄을 원본(final.html)에 올려 두고, 여기서는
원본을 그대로 옮기기만 한다.

**찾는 법까지 옮긴다.** index.html 의 `omFor` 는 부분 일치만 보았는데,
final.html 은 ① 이름이 똑같은 것을 먼저 찾고 ② 그 다음에 부분 일치를 보되
세 번째 칸이 켜진 줄(정확히 일치할 때만 쓰라는 표시)은 건너뛴다. 표만
옮기고 찾는 법을 안 옮기면, 정확히 쓰라고 표시해 둔 줄이 엉뚱한 유형을
가로챈다.

옮기고 나면 index.html 의 문제지 유형 217종 가운데 카드가 붙는 것이
69종에서 177종이 된다.

    python3 tools/gen_omlib.py           # 어긋난 곳
    python3 tools/gen_omlib.py --write   # 옮긴다
    python3 tools/gen_omlib.py --check   # 어긋나면 빨간불 (CI용)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'final.html')
DST = os.path.join(ROOT, 'index.html')

OMFOR = ("function omFor(type){ if(!type) return null;\n"
         "  for(const e of OMLIB){ if(type===e[0]) return e[1]; }\n"
         "  for(const e of OMLIB){ if(e[2]) continue; if(type.indexOf(e[0])>=0) return e[1]; }\n"
         "  return null; }")


def table(src):
    i = src.find('const OMLIB=[')
    if i < 0:
        raise RuntimeError('OMLIB 을 못 찾았다')
    j = src.find('];', i)
    return src[i:j + 2]


def omfor_span(src):
    i = src.find('function omFor(')
    j = src.find('return null; }', i)
    if i < 0 or j < 0:
        raise RuntimeError('omFor 를 못 찾았다')
    return i, j + len('return null; }')


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    src = open(SRC, encoding='utf-8').read()
    dst = open(DST, encoding='utf-8').read()

    want = table(src)
    cur = table(dst)
    i, j = omfor_span(dst)
    out = dst[:i] + OMFOR + dst[j:]
    out = out.replace(cur, want, 1)

    print('final.html %d줄 · index.html %d줄' % (want.count('["'), cur.count('["')))
    if out == dst:
        print('오개념 라이브러리가 두 화면에서 한 벌이다.')
        return 0
    print('\n두 화면이 갈라져 있다 — final.html 이 원본이다.')
    if write:
        open(DST, 'w', encoding='utf-8').write(out)
        print('index.html 에 옮겼다 (표와 찾는 법 둘 다).')
        return 0
    print('python3 tools/gen_omlib.py --write 로 맞춘다.')
    return 1 if check else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
