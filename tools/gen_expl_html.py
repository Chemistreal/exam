#!/usr/bin/env python3
"""`explanation`(글) 에서 `explanationHtml`(해설지에 실릴 꼴) 을 만든다.

해설지 생성기(`gen_sol_page.py`)는 `explanationHtml` 만 읽는다. 글만 써 넣고
이것을 빠뜨리면 **해설지가 통째로 비어 나온다** — 파일은 만들어지고 검사도
지나가므로 아무도 모른다(2026-08-07 에 실제로 그랬다).

글의 꼴은 정해져 있다.

    사고과정 <문장> <문장> … → ③

'사고과정' 을 머리글로 올리고, 문장마다 한 줄로 끊고, 마지막 '→ ③' 을
굵게 세운다. 이미 explanationHtml 이 있는 문항은 건드리지 않는다 —
손으로 공들여 쓴 것을 기계가 덮어쓰면 안 된다.

■ 낡은 꼴도 본다

건드리지 않는 규칙에는 구멍이 있었다. 글을 **고치면** 꼴은 옛 글을 그대로
들고 있는데, '이미 있으니 건너뛴다' 로 지나가 아무도 모른다. 성적표는 새 글을,
해설지는 옛 글을 보여 준다 — 같은 문항인데 두 곳이 다른 말을 한다.

실제로 그랬다. 내부 메모(정답표 오류 지적 같은 것)를 학생용 글에서 걷어냈는데
해설지에는 그대로 남아 있었다.

그래서 글과 꼴이 **같은 말인지** 본다. 태그·공백·아래첨자·따옴표 실체·정답
표시(→ / 정답)는 꼴마다 다르므로 지우고 견준다. 서식은 손봐도 되고, 내용이
갈리면 알린다.

    python3 tools/gen_expl_html.py <시험id> [--write]
    python3 tools/gen_expl_html.py --check      # 꼴이 없거나 글과 어긋나는 곳
"""
import glob
import html
import json
import os
import re
import unicodedata
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIRC = {1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤'}


def build(text):
    """글 한 덩이를 해설지 꼴로 바꾼다."""
    t = text.strip()
    if not t:
        return ''
    head = ''
    m = re.match(r'^(사고과정)\s*', t)
    if m:
        head = '<h4>사고과정</h4>\n'
        t = t[m.end():]

    # 맨 끝의 '→ ③' 은 따로 세운다. 그 뒤에 말이 더 있으면 그것은 오개념 한
    # 줄이다 — 먼저 쓰인 회차들이 그렇게 적어 두었고(hwol-2013·2014), 해설지는
    # 그것을 사고과정이 아니라 <div class="tip"> 으로 세운다. 여기서 '→' 만
    # 끝으로 보면 오개념이 사고과정의 마지막 단계처럼 붙는다.
    #
    # ⚠ **마지막** 화살표를 잡는다. 보기를 하나씩 짚는 해설은 글 가운데에도
    #   '④ … → ③' 처럼 동그라미가 나온다(donghyung-1 #23 외 여덟). 처음 것을
    #   잡으면 답 표시가 문장 한가운데로 가고 뒤가 통째로 오개념이 된다.
    tail = ''
    m = re.search(r'^(.*)→\s*([①-⑤])\s*(.*)$', t, re.S)
    if m:
        tail = '<p class="step">→ <b>%s</b></p>' % m.group(2)
        rest = m.group(3).strip()
        if rest:
            tail += '\n<div class="tip">%s</div>' % _fmt(rest)
        t = m.group(1).strip()

    # 문장마다 한 줄. 마침표 뒤가 공백이면 끊는다(소수점은 뒤에 숫자가 와서 안 끊긴다).
    parts = [s.strip() for s in re.split(r'(?<=[.。])\s+', t) if s.strip()]
    parts = _mend(parts)
    body = '\n'.join('<p class="step">%s</p>' % _fmt(s) for s in parts)
    return head + body + ('\n' + tail if tail else '')


# 항목표 머리 — 「a.」 「나.」 「ㄱ.」 같은 한 글자 딱지. 마침표로 끝나서
# 문장 나누개가 여기서도 끊는 바람에, 딱지 혼자 한 줄이 되고 설명은 다음
# 줄로 밀려났다(kch1u1 15번: <p>a.</p> <p>¹₁H·²₁H…, b.</p> …).
_MARK = r'[a-zA-Zㄱ-ㅎ가나다라마①-⑤ⓐ-ⓔ]'
_MARK_ONLY = re.compile(r'^%s\s*\.$' % _MARK)
_MARK_TAIL = re.compile(r'([,;·]?\s+)(%s)\s*\.$' % _MARK)


def _mend(parts):
    """짝 잃은 항목표 딱지를 제 설명에 도로 붙인다.

    두 모양이 있다 — 딱지 혼자 한 조각(「a.」)이면 다음 조각 머리에 붙이고,
    조각 꼬리에 다음 딱지가 매달려 있으면(「…(원자번호 1 동일), b.」) 떼어
    다음 조각에 넘긴다. 둘 다 마지막 조각이면 그대로 둔다 — 붙일 곳이 없다."""
    out = []
    carry = ''
    for i, s in enumerate(parts):
        s = (carry + ' ' + s).strip() if carry else s
        carry = ''
        if i < len(parts) - 1:
            if _MARK_ONLY.match(s):
                carry = re.sub(r'\s+', '', s)
                continue
            m = _MARK_TAIL.search(s)
            if m:
                carry = m.group(2) + '.'
                s = s[:m.start()] + (m.group(1).strip() or '')
                s = s.rstrip()
        if s:
            out.append(s)
    if carry:
        out.append(carry)
    return out


# 유니코드 위·아래 첨자 — 화면 글꼴에 따라 「¹₁H」 가 콩알만 하게 붙거나
# 아예 네모로 나온다. 해설지·성적표가 쓰는 <sup>/<sub> 로 바꾼다.
# 핵종 표기(²³⁸₉₂U)는 첨자 묶음이 「위 → 아래 → 원소」 순서라, 묶음별로
# 바꾸면 그대로 <sup>238</sup><sub>92</sub>U 표준꼴이 된다.
_SUP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ⁿ', '0123456789+−n')
_SUB = str.maketrans('₀₁₂₃₄₅₆₇₈₉₊₋', '0123456789+−')
_SUP_RUN = re.compile('[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ⁿ]+')
_SUB_RUN = re.compile('[₀₁₂₃₄₅₆₇₈₉₊₋]+')


def _fmt(s):
    s = html.escape(s, quote=False)
    s = _SUP_RUN.sub(lambda m: '<sup>%s</sup>' % m.group(0).translate(_SUP), s)
    s = _SUB_RUN.sub(lambda m: '<sub>%s</sub>' % m.group(0).translate(_SUB), s)
    # 끝맺는 「정답 ④.」 줄은 화살표 꼬리(→ <b>④</b>)와 같은 무게로 세운다.
    if s.startswith('정답'):
        s = re.sub(r'([①-⑤])', r'<b>\1</b>', s, count=1)
    return s


def squash(s):
    """서식을 걷어내고 '무슨 말인가' 만 남긴다.

    같은 내용이라도 꼴에는 아래첨자 태그·줄바꿈·실체 참조가 들어가고, 정답
    표시도 '→ ②' 와 '정답 ②' 로 갈린다. 그런 차이로 낡았다고 하면 아무도
    안 믿는 검사가 된다. 지우고 견준다.
    """
    for a, b in (('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'),
                 ('&#x27;', "'"), ('&#39;', "'"), ('&nbsp;', ''), ('&amp;', '&')):
        s = s.replace(a, b)
    s = re.sub(r'\s+', '', unicodedata.normalize('NFKC', s))
    # 빼기 부호 셋(U+2212 −·하이픈·엔대시)을 하나로 — NFKC 가 '⁻' 를 U+2212 로
    # 보내는데 손으로 쓴 글은 하이픈이라, 같은 말이 다른 글자로 비교된다.
    s = s.replace('\u2212', '-').replace('\u2013', '-')
    return re.sub(r'(정답|→)+', '→', s)


def same_words(expl, html_):
    return squash(expl) == squash(re.sub(r'<[^>]+>', '', html_))


def machine_made(h):
    """이 생성기가 만든 꼴인가 — 생성기 어휘(step·tip·h4·b·첨자) 밖의 태그가
    하나라도 있으면 사람 손이 간 것이다(.k/.x 표식, 절 나눔 해설). 그런 것은
    절대 덮어쓰지 않는다."""
    rest = re.sub(r'</?(?:h4|b|sup|sub)>|<p class="step">|</p>|<div class="tip">|</div>', '', h)
    return '<' not in rest


def run(path, write):
    data = json.load(open(path, encoding='utf-8'))
    qs = data.get('questions') or {}
    made = missing = refit = 0
    stale, blank = [], []
    for k in sorted(qs, key=int):
        q = qs[k]
        expl = str(q.get('explanation') or '').strip()
        cur = str(q.get('explanationHtml') or '').strip()
        if not expl:
            # 글이 아예 없으면 오답 카드가 **빈칸**으로 나간다. 학생은 왜 틀렸는지
            # 한 줄도 못 본다. 출제 취소된 문항도 '왜 취소됐는지' 는 적어야 한다 —
            # kmchc-2025-1-simhwa 38·41번이 그렇게 비어 있었다.
            blank.append(k)
            continue
        if not cur:
            missing += 1
            if write:
                q['explanationHtml'] = build(expl)
                made += 1
            continue
        # 꼴은 있는데 글과 다른 말을 한다 — 글을 고치고 꼴을 안 고친 자리다.
        if not same_words(expl, cur):
            stale.append(k)
            if write:
                q['explanationHtml'] = build(expl)
                made += 1
            continue
        # 같은 말인데 옷이 낡았다(항목표 딱지가 떨어져 있거나 첨자가 유니코드
        # 그대로거나). 기계가 입힌 옷만 다시 입힌다 — 사람이 쓴 꼴은 그대로.
        if machine_made(cur):
            fresh = build(expl)
            if fresh != cur:
                refit += 1
                if write:
                    q['explanationHtml'] = fresh
                    made += 1
    if write and made:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
    return missing, made, stale, blank, refit


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    write = '--write' in sys.argv
    check = '--check' in sys.argv

    paths = ([os.path.join(ROOT, 'answers', '%s.json' % a) for a in args]
             if args else sorted(glob.glob(os.path.join(ROOT, 'answers', '*.json'))))

    total = old = empty = 0
    for p in paths:
        missing, made, stale, blank, refit = run(p, write)
        name = os.path.basename(p)
        if missing:
            total += missing
            print('  %-34s 글은 있는데 꼴이 없는 문항 %d개%s'
                  % (name, missing, ' → 만들었다' if made else ''))
        if blank:
            empty += len(blank)
            print('  %-34s 해설 글이 비어 있는 문항 %d개 (%s)'
                  % (name, len(blank), ', '.join(b + '번' for b in blank[:8])))
        if refit:
            total += refit
            print('  %-34s 옷이 낡은 문항 %d개 (첨자·항목표)%s'
                  % (name, refit, ' → 다시 입혔다' if write else ''))
        if stale:
            old += len(stale)
            print('  %-34s 꼴이 옛 글을 들고 있는 문항 %d개 (%s)%s'
                  % (name, len(stale), ', '.join(s + '번' for s in stale[:8]),
                     ' → 다시 만들었다' if write else ''))
    if not total and not old and not empty:
        print('해설 글이 모든 문항에 있고, 해설지 꼴도 글과 같은 말을 한다')
        return 0
    if empty:
        print('\n빈 해설은 만들어 줄 수 없다 — 사람이 쓴다. 출제 취소된 문항도 '
              '왜 취소됐는지는 적는다.')
        return 1 if check else 0
    if write:
        return 0
    if old:
        print('\n글을 고치고 꼴을 안 고쳤다 — 성적표와 해설지가 다른 말을 하게 된다.')
    print('python3 tools/gen_expl_html.py --write 로 맞춘다.')
    return 1 if check else 0


if __name__ == '__main__':
    sys.exit(main())
