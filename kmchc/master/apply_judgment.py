# -*- coding: utf-8 -*-
"""apply_judgment — 조치 담당 에이전트가 돌려준 edits 를 ★배치 빌더 안의 문항 블록★ 에 붙인다

  쓰임:  python3 apply_judgment.py <워크플로 출력.json> [--write]

  왜 빌더에 붙이는가
    은행(master_bank.json)을 직접 고치면 빌더와 은행이 갈리고, 다음 조치 회차에 patch_batch 가
    ★내가 고친 자리를 되돌린다★. 그래서 고침은 언제나 빌더에 붙이고 patch_batch 로 옮긴다.

  왜 ★문항 블록 안에서만★ 바꾸는가
    같은 문면이 다른 문항에도 있을 수 있다. 블록은 `q('MID'` 부터 다음 `it.append(` 까지다.

  ★칸 이름을 옮기지 않는다★
    에이전트는 은행의 칸 이름(stem·choices·answer_proof·calc_check·solution·device)으로 적어 오지만,
    빌더에는 solution 이라는 칸이 없다 — lead·prose·wmap·diag 가 모여 solution 이 된다.
    그래서 ★칸을 보지 않고 블록 안의 문자열을 그대로 찾아 바꾼다★. 어느 칸이든 블록 안에 있다.

  ★두 번 돌려도 되게★
    before 가 없고 after 가 이미 있으면 '이미 고쳐져 있다' 로 넘긴다(회차가 겹칠 수 있다).
"""
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


#  ★빌더의 문자열은 여러 줄로 접혀 있다★ — '…앞부분 '\n        '뒷부분…' 꼴이라 문장 하나가
#  이어진 문자열이 아니다. 그래서 글자 사이에 ★접힘★ 이 끼어도 찾도록 정규식을 만든다.
BREAK = r"(?:['\"]\s*\n\s*['\"])?"


def fold_re(text):
    return re.compile(BREAK.join(re.escape(ch) for ch in text))


#  ★해설의 오답 단평은 빌더에 그 꼴로 없다★ — '③ 선지문면: 되받이' 는 T.sol 이 wmap 에서
#  지어 내는 줄이다. 그래서 단평 꼴이 오면 ★되받이만★ 떼어 바꾼다.
#  ▸ 번호가 없는 꼴('자가진단: …' · '…본다: 손으로 할 일이야')도 같은 셈이다 — 번호를 뺀다.
NOTE = re.compile(r'^\s*(?:[①②③④]\s*)?(?P<txt>.+?)\s*:\s*(?P<ret>.+?)\.?\s*$')


def smart_replace(seg, before, after):
    """붙였으면 (새 seg, True), 못 붙였으면 (seg, False)."""
    if before in seg:
        return seg.replace(before, after), True
    m = fold_re(before).search(seg)                    # 접힌 문자열
    if m:
        return seg[:m.start()] + after + seg[m.end():], True
    #  ★해설의 '— ' 는 T.sol 이 붙이는 이음표다★ — 빌더의 prose 는 그 뒤부터 시작한다.
    for lead in ('— ', '-- ', '– '):
        if before.startswith(lead) and after.startswith(lead):
            seg2, ok2 = smart_replace(seg, before[len(lead):], after[len(lead):])
            if ok2 is not False:
                return seg2, ok2
    a, b = NOTE.match(before), NOTE.match(after)        # 오답 단평 → 되받이만
    if a and b:
        ra, rb = a.group('ret'), b.group('ret')
        if ra != rb and ra in seg:
            return seg.replace(ra, rb), True
        if rb in seg:
            return seg, None                            # 이미 고쳐져 있다
    #  ★앞선 선지 치환이 이미 인용을 바꿔 버린 자리★ — 그러면 남은 것은 되받이 한 마디다.
    #  '…라고 했어. ' 뒤의 꼬리만 떼어 바꾼다(규약 ⓖ의 그 자리다).
    for sep in ('라고 했어. ', '했어. ', '. '):
        pa, pb = before.rsplit(sep, 1), after.rsplit(sep, 1)
        if len(pa) == 2 and len(pb) == 2 and pa[1] != pb[1]:
            if pa[1] in seg:
                return seg.replace(pa[1], pb[1]), True
            if pb[1] in seg:
                return seg, None
    return seg, False


def block(src, mid):
    for qt in ("'%s'" % mid, '"%s"' % mid):
        k = src.find('q(' + qt)
        if k >= 0:
            nxt = [x for x in (src.find('it.append(', k + 4), src.find('return it', k)) if x > 0]
            return k, min(nxt) if nxt else len(src)
    return None


def find_owner(mid, cache={}):
    if not cache:
        for f in glob.glob(os.path.join(HERE, 'build_*.py')):
            s = io.open(f, encoding='utf-8').read()
            for tok in ("q('M", 'q("M'):
                i = 0
                while True:
                    i = s.find(tok, i)
                    if i < 0:
                        break
                    cache.setdefault(s[i + 3:i + 9], f)
                    i += 1
    return cache.get(mid)


def main():
    src = sys.argv[1]
    write = '--write' in sys.argv
    res = json.load(open(src, encoding='utf-8'))
    res = res.get('result', res)
    rows = [(x, 'judge') for x in res.get('judge', [])] + [(x, 'calc') for x in res.get('calc', [])]

    per_file, hit, skip, miss = {}, 0, 0, []
    for x, kind in rows:
        if x['verdict'] != '고친다' or not x['edits']:
            continue
        f = find_owner(x['id'])
        if not f:
            miss.append('%s — 빌더를 찾지 못했다' % x['id'])
            continue
        s = per_file.get(f) or io.open(f, encoding='utf-8').read()
        a, b = block(s, x['id'])
        seg = s[a:b]
        for e in x['edits']:
            before, after = e.get('before', ''), e.get('after', '')
            if not before or before == after:
                continue
            seg, ok = smart_replace(seg, before, after)
            if ok is True:
                hit += 1
            elif ok is None or (after and after in seg):
                skip += 1
            else:
                miss.append('%s %s — 찾지 못했다: %s' % (x['id'], e.get('field'), before[:46]))
        per_file[f] = s[:a] + seg + s[b:]

    print('붙인 자리 %d · 이미 있던 자리 %d · 빗나감 %d · 파일 %d'
          % (hit, skip, len(miss), len(per_file)))
    for m in miss:
        print('  ❌', m)
    if write:
        for f, s in per_file.items():
            io.open(f, 'w', encoding='utf-8').write(s)
        print('✅ %d 파일에 썼다 — patch_batch 로 은행에 옮긴다' % len(per_file))
        print('   모듈:', ' '.join(sorted(os.path.basename(f)[:-3] for f in per_file)))
    else:
        print('※ 쓰지 않았다 — --write 를 붙일 것')
        print('   모듈:', ' '.join(sorted(os.path.basename(f)[:-3] for f in per_file)))


if __name__ == '__main__':
    main()
