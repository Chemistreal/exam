#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""입력칸에 **이름**이 있는지 보고, placeholder 로 지을 수 있으면 지어 넣는다.

왜 필요한가
-----------
화면 낭독기는 입력칸에 닿으면 "무엇을 넣는 칸인가" 를 읽어 준다. 그 이름은
`<label for>` · `aria-label` · `title` 에서 나온다. 셋 다 없으면 **"편집"** 이라고만
읽는다 — 열 칸이 나란히 있으면 열 번 다 "편집" 이다.

placeholder 는 이름이 아니다. 두 가지 이유로 그렇다.

  1. 글자를 넣는 순간 사라진다. 다시 보려면 지워야 한다.
  2. 낭독기마다 읽는 것이 다르다 — 안 읽는 것도 있다.

placeholder 를 **그대로 베끼면 안 된다**
---------------------------------------
처음에는 placeholder 를 그대로 aria-label 로 옮겼다. 그랬더니 이런 것이
나왔다.

    <label>학년</label><input placeholder="예: 2">  →  aria-label="예: 2"
    <textarea placeholder="홍길동,1,3,2,5,4,…">     →  aria-label="홍길동,1,3,…"

이름이 아니라 **예시 데이터**다. 낭독기가 "편집" 이라고만 읽던 것이
"예 2 편집" 이 됐을 뿐, 무엇을 넣는 칸인지는 여전히 모른다. 나쁜 이름은
없는 이름보다 나쁘다 — 고쳤다고 믿고 지나가기 때문이다.

그래서 두 가지만 자동으로 한다.

  1. **바로 앞에 눈에 보이는 `<label>` 이 있는데 `for` 가 없는 경우.**
     이미 사람이 지어 둔 이름이다. `for`/`id` 로 이어 주기만 하면 된다.
     화면도 안 바뀌고, 라벨을 눌러 칸으로 들어가는 것까지 덤으로 생긴다.
  2. **placeholder 가 이름처럼 읽히는 경우** — 짧고, '예:' 로 시작하지 않고,
     쉼표·줄바꿈으로 된 예시 데이터가 아닌 것.

나머지는 무엇을 넣는 칸인지 사람이 봐야 안다 — 세기만 하고 알린다.

이름을 이어 줘도 **화면은 하나도 안 바뀐다.**

    실행:  python3 tools/input_labels.py            # 세기만
           python3 tools/input_labels.py --write    # placeholder 로 지어 넣는다
           python3 tools/input_labels.py --check    # 지을 수 있는 것이 남으면 빨간불
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TAG = re.compile(r'<(input|select|textarea)\b([^>]*?)(/?)>', re.I)
LBL_FOR = re.compile(r'<label\b[^>]*\bfor\s*=\s*["\']([^"\']+)["\']', re.I)
# <label> … <input …> … </label> — 감싼 형태는 이름이 있는 것이다
WRAP = re.compile(r'<label\b[^>]*>(?:(?!</label>)[\s\S])*?</label>', re.I)

# 이름이 필요 없는 것들. 단추는 글자가 곧 이름이고, hidden 은 눈에 없다.
SKIP_TYPE = {'hidden', 'submit', 'button', 'reset', 'image'}


# 이름이 붙어 있는가 — **값은 안 본다.**
# `aria-label="'+q.n+'번 답"` 처럼 값을 자바스크립트로 이어 붙인 자리는
# 값 읽는 규칙(따옴표 안에 따옴표가 없다고 본다)에 안 걸려서, 이름이 멀쩡히
# 붙어 있는데도 '이름 없는 칸' 으로 세고 있었다(grade-j0.html 문항 60칸).
HAS_NAME = re.compile(r'\b(aria-label|aria-labelledby|title)\s*=', re.I)


def attr(name, tag):
    m = re.search(r'\b' + name + r'\s*=\s*["\']([^"\']*)["\']', tag, re.I)
    return m.group(1) if m else None


# placeholder 가 **이름**인가 **예시**인가.
# 예시는 이름이 아니다 — 그대로 옮기면 낭독기가 예시를 이름으로 읽는다.
EXAMPLEISH = re.compile(r'^\s*(예\s*[:)]|e\.?g\.?|ex\s*[:)]|보기\s*[:)])', re.I)
def name_like(ph):
    if not ph or len(ph) > 24:
        return False                       # 길면 문장이지 이름이 아니다
    if EXAMPLEISH.match(ph):
        return False
    if re.search(r'[\n,]|&#10;|\.\.\.|…', ph):
        return False                       # 예시 데이터(줄바꿈·쉼표·말줄임)
    # ⚠ 템플릿 문법이 든 자리는 손대면 안 된다. `placeholder="${m?'◎':'·'}"` 를
    #   그대로 옮기려다 `aria-label="${m?"` 로 잘려 화면이 깨진 적이 있다.
    #   따옴표·중괄호·역따옴표가 보이면 사람이 정한다.
    if re.search(r'[${}`\'"<>]', ph):
        return False
    return True

# 바로 앞의 <label> — for 가 없어 이어지지 않은 것. 이미 사람이 지은 이름이다.
LOOSE_LABEL = re.compile(r'<label\b(?![^>]*\bfor=)[^>]*>([^<]{1,20})</label>\s*$')

def spans_in_label(text):
    """<label> 로 감싸인 구간들. 그 안의 입력칸은 이름이 있다."""
    return [(m.start(), m.end()) for m in WRAP.finditer(text)]


def scan(text):
    """(이름 없는 칸, placeholder 로 지을 수 있는 칸) 을 (시작, 끝, 태그, 이름) 으로."""
    fors = set(LBL_FOR.findall(text))
    wrapped = spans_in_label(text)
    named_ok, fixable, unknown = 0, [], []
    for m in TAG.finditer(text):
        tag = m.group(0)
        typ = (attr('type', tag) or '').lower()
        if typ in SKIP_TYPE:
            continue
        if HAS_NAME.search(tag):
            named_ok += 1
            continue
        i = attr('id', tag)
        if i and i in fors:
            named_ok += 1
            continue
        if any(a <= m.start() < b for a, b in wrapped):
            named_ok += 1          # <label> 이 감싸고 있다
            continue
        # 1) 바로 앞에 이어지지 않은 <label> 이 있으면 그것을 잇는다.
        near = LOOSE_LABEL.search(text[max(0, m.start() - 120):m.start()])
        if near and i:
            fixable.append((m.start(), m.end(), tag, near.group(1).strip(), 'for'))
            continue
        # 2) placeholder 가 이름처럼 읽히면 그것으로.
        ph = (attr('placeholder', tag) or '').strip()
        if name_like(ph):
            fixable.append((m.start(), m.end(), tag, ph, 'aria'))
        else:
            unknown.append((m.start(), m.end(), tag))
    return named_ok, fixable, unknown


def files():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in ('.git', 'node_modules', '__pycache__')]
        for f in sorted(fn):
            if f.endswith('.html'):
                yield os.path.join(dp, f)


def put_label(tag, name):
    """여는 태그 안에 aria-label 을 끼운다. 자기닫음(/>)도 그대로 둔다."""
    # 따옴표가 든 이름은 실을 수 없다 — 그런 것은 사람이 정한다.
    if '"' in name:
        return None
    m = TAG.match(tag)
    close = '/>' if m.group(3) else '>'
    body = tag[:-len(close)].rstrip()
    return body + ' aria-label="' + name + '"' + close


def main():
    write = '--write' in sys.argv[1:]
    check = '--check' in sys.argv[1:]
    ok = fixed = left = 0
    todo = []
    for p in files():
        try:
            src = open(p, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
        named, fixable, unknown = scan(src)
        ok += named
        left += len(unknown)
        if unknown:
            todo.append((os.path.relpath(p, ROOT), len(unknown)))
        if not fixable:
            continue
        if not write:
            fixed += len(fixable)
            continue
        # 뒤에서부터 갈아 끼운다 — 앞에서부터 하면 뒤 자리가 밀린다.
        out = src
        for a, b, tag, nm, how in reversed(fixable):
            if how == 'for':
                # 라벨을 칸에 잇는다. 라벨 글자는 그대로 두고 for 만 더한다.
                i = attr('id', tag)
                j = out.rfind('<label', max(0, a - 120), a)
                if i is None or j < 0:
                    continue
                k = out.find('>', j)
                if k < 0 or k > a:
                    continue
                out = out[:j + 6] + ' for="' + i + '"' + out[j + 6:k] + out[k:]
                fixed += 1
                continue
            new = put_label(tag, nm)
            if new is None:
                continue
            out = out[:a] + new + out[b:]
            fixed += 1
        if out != src:
            open(p, 'w', encoding='utf-8').write(out)

    if write:
        print(f'이름을 이어 줬다: {fixed}개')
    else:
        print(f'이름 있는 칸 {ok}개 · 자동으로 이어 줄 수 있는 것 {fixed}개 · '
              f'사람이 봐야 하는 것 {left}개')
    if todo:
        print('\n사람이 봐야 하는 칸(무엇을 넣는 칸인지 화면을 봐야 안다):')
        for rel, n in sorted(todo, key=lambda x: -x[1])[:12]:
            print(f'   {rel}  {n}개')
        if len(todo) > 12:
            print(f'   … 외 {len(todo)-12}개 파일')
    if check and fixed:
        print('\nFAIL 자동으로 이어 줄 수 있는 칸이 남아 있다 — '
              'python3 tools/input_labels.py --write')
        return 1
    # 세 저장소 82칸을 사람이 하나씩 보고 이름을 지어 0으로 만들었다. 여기서
    # 세기만 하고 넘어가면 다음 화면 한 장에 다시 쌓인다 — 낭독기한테는
    # 이름 없는 칸이 열 개면 '편집' 이 열 번이다. 새로 생기면 그 자리에서 막는다.
    if check and left:
        print('\nFAIL 이름 없는 칸이 ' + str(left) + '개 있다 — 무엇을 넣는 '
              '칸인지 보고 aria-label 을 손으로 달아 주세요')
        return 1
    print('\nPASS' if check else '')
    return 0


if __name__ == '__main__':
    sys.exit(main())
