#!/usr/bin/env python3
"""강의 125장의 **내용**을 기계가 잴 수 있는 데까지 잰다.

앞의 tools/lec_audit.py 는 얼개를 본다(머리글·앞뒤 참조·오답 지도).
여기서는 **글 안의 화학**을 본다. 사람이 125장을 매번 훑을 수는 없고,
훑어도 계수 하나가 어긋난 것은 눈으로 잘 안 잡힌다.

  ① 반응식이 맞춰져 있는가
     본문의 `A + B → C + D` 를 원자 수로 세어 좌우가 같은지 본다.
     계수 하나가 틀리면 학생은 그 식을 그대로 외운다.

  ② 상수가 강의마다 같은가
     R · NA · h · c · F 같은 값이 장마다 다르면 학생은 어느 것이 맞는지
     모른다. 실제로 시험지 표지에 적힌 값과도 맞아야 한다.

  ③ 뼈대가 갖춰져 있는가
     보강 문구 · 절 번호(01,02,…) 연속 · '한 장 정리' · '직접 해보기'.
     한 장이라도 빠지면 그 강의만 다른 물건이 된다.

  ④ 표기가 깨지지 않았는가
     아래첨자 없이 쓴 화학식(H2O · CO2). NaCl 처럼 숫자가 없는 식은 안 센다.

화학 내용의 **옳고 그름 전부**를 여기서 판정하지는 못한다. 개념 설명이
맞는지는 사람이 읽어야 한다. 여기서는 **셀 수 있는 것만** 세되, 그것은
빠짐없이 센다.

실행:
    python3 tools/lec_content.py            # 전체 보고
    python3 tools/lec_content.py --check    # 새로 생긴 것이 있으면 빨간불
    python3 tools/lec_content.py --write    # 지금 상태를 기록에 담는다
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.path.join(ROOT, 'tools', 'lec_content.json')

# 시험지 표지에 적힌 값. 강의가 이와 다르게 적으면 학생이 헷갈린다.
CONSTS = {
    'R': ['0.082', '8.314'],
    'N_A': ['6.02'],
    'h': ['6.63'],
    'c': ['3.00', '3×10', '3 × 10'],
    'F': ['96485', '96500'],
}

SUB = str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')
UP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻', '0123456789+-')


# ── 확인 문제 덩이는 **강의가 지은 글이 아니다** ───────────────────────
#  `tools/lecture_quiz.py` 가 넣는 덩이는 사람이 이미 검수한 동형문항을
#  **그대로 인용한 것**이다(선생님 결정 #25). 강의 본문에 매기는 잣대를
#  거기 대면 옳은 화학이 빨간불로 나온다. 실제로 넷이 그랬다(2026-08-11):
#
#      실험 «I → II»          로마 숫자 실험 번호를 아이오딘 반응식으로 봤다
#      «hc = 1.240 × 10³»     플랑크 상수×빛속도인데 빛속도로 봤다
#      «5O₂ → 4CO₂ + 5H₂O»    좌변(C₄H₁₀ + 6.5O₂)이 분수 계수에서 잘렸다
#      «N_A = 6.0»            문항이 쓴 어림값(6.0×10²³)이지 강의의 값이 아니다
#
#  넷 다 화학은 멀쩡했다. 자가 인용문을 제 글로 오해한 것이다. 여기서
#  «고치면» 검수된 문항을 기계가 손대는 일이 된다 — 하면 안 되는 일이다.
QUIZ = re.compile(r'<!-- 확인문제:시작.*?확인문제:끝 -->', re.S)


def strip_tags(s):
    s = QUIZ.sub(' ', s)
    s = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', s)
    # 위첨자는 **표시로 남긴다.** 그냥 지우면 이온의 전하가 사라져
    # `HCl → H⁺ + Cl⁻` 이 `HCl → H` 가 되고, 안 맞는 식으로 잘못 잡힌다.
    s = re.sub(r'<sup>([^<]*)</sup>', r'^\1', s)
    s = re.sub(r'<sub>([^<]*)</sub>', r'\1', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = s.replace('&nbsp;', ' ').replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
    return re.sub(r'[ \t]+', ' ', s)


def parse_formula(f):
    """화학식 하나의 원자 수. 못 읽으면 None — 못 읽는 것을 틀렸다고 하지 않는다."""
    f = f.strip().translate(SUB)
    f = re.sub(r'\([^)]*\)$', '', f)             # 상태 표기 (s)(l)(g)(aq)
    f = f.replace('·', '')                       # 수화물 점은 곱으로 안 센다
    if not f or not re.fullmatch(r'[A-Za-z0-9\[\]()]+', f):
        return None

    def chunk(s, i):
        out, n = {}, len(s)
        while i < n:
            ch = s[i]
            if ch in '([':
                sub, i = chunk(s, i + 1)
                if sub is None:
                    return None, i
                m = re.match(r'\d+', s[i:])
                mult = int(m.group()) if m else 1
                i += len(m.group()) if m else 0
                for k, v in sub.items():
                    out[k] = out.get(k, 0) + v * mult
            elif ch in ')]':
                return out, i + 1
            elif ch.isupper():
                m = re.match(r'[A-Z][a-z]?', s[i:])
                el = m.group(); i += len(el)
                m2 = re.match(r'\d+', s[i:])
                cnt = int(m2.group()) if m2 else 1
                i += len(m2.group()) if m2 else 0
                out[el] = out.get(el, 0) + cnt
            else:
                return None, i                   # 소문자로 시작 = 화학식이 아니다
        return out, i

    got, _ = chunk(f, 0)
    return got or None


def parse_side(side):
    """`2H₂ + O₂` 한쪽. 계수를 곱해 원자 수를 합친다."""
    total = {}
    for term in re.split(r'\s*\+\s*', side):
        term = term.strip()
        if not term:
            return None
        m = re.match(r'^(\d+)\s*(.+)$', term)
        coef, body = (int(m.group(1)), m.group(2)) if m else (1, term)
        atoms = parse_formula(body)
        if atoms is None:
            return None
        for k, v in atoms.items():
            total[k] = total.get(k, 0) + v * coef
    return total


ARROW = re.compile(r'(?:→|->|⟶|⇌|=)')
EQ = re.compile(
    r'(?<![A-Za-z0-9])'
    r'((?:\d*\s*[A-Z][A-Za-z0-9₀-₉⁰-⁹⁺⁻^()\[\]]*(?:\([slgaq]+\))?)(?:\s*\+\s*\d*\s*[A-Z][A-Za-z0-9₀-₉⁰-⁹⁺⁻^()\[\]]*(?:\([slgaq]+\))?)*)'
    r'\s*(?:→|->|⟶|⇌)\s*'
    r'((?:\d*\s*[A-Z][A-Za-z0-9₀-₉⁰-⁹⁺⁻^()\[\]]*(?:\([slgaq]+\))?)(?:\s*\+\s*\d*\s*[A-Z][A-Za-z0-9₀-₉⁰-⁹⁺⁻^()\[\]]*(?:\([slgaq]+\))?)*)(?![A-Za-z0-9])')


ELEMENTS = set(('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni '
                'Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe '
                'Cs Ba La Ce Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th U').split())


def equations(text):
    """본문에서 반응식을 찾아 좌우 원자 수를 견준다.

    ⚠ 세 가지는 아예 안 본다. 안 그러면 보고가 잡음으로 덮인다.
      · **이온이 든 식** — 전하가 위첨자라 글로 훑으면 잘려 나간다
        (`HCl → H⁺ + Cl⁻` 이 `HCl → H` 가 된다). 전하까지 세지 않을 바에는
        판정하지 않는 것이 옳다.
      · **일부러 안 맞춘 식** — 계수 맞추기 강의는 '맞추기 전' 을 먼저 보여
        준다. 그것을 틀렸다고 하면 강의를 못 쓴다.
      · **원소 기호가 아닌 것** — IE₁→IE₂(이온화에너지) · 273 K → 546 K(온도).
    """
    bad = []
    for m in EQ.finditer(text):
        span = m.group(0)
        # 이온: 위첨자 +/− (strip_tags 가 ^ 로 남겨 둔다)
        # ⚠ span 안만 보면 못 잡는다. `CaCl₂ → Ca²⁺ + 2Cl⁻` 는 위첨자 ² 에서
        #   식 찾기가 끊겨 **`CaCl₂ → Ca` 까지만** 잡히고, 그 토막에는 ⁺ 가 없다.
        #   그래서 멀쩡한 이온화 식을 "Cl 2→0" 이라고 걸었다(2026-08-09).
        #   분수 계수와 같은 방식으로 **앞뒤를 조금 넓혀** 본다.
        around = text[max(0, m.start() - 4):m.end() + 8]
        if re.search(r'[⁺⁻]|\^\s*\d*\s*[+-]', around):
            continue
        # 분수 계수(½O₂)는 원자 수를 정수로 못 센다 — 판정하지 않는다
        if re.search(r'[½⅓⅔¼¾]', text[max(0, m.start() - 6):m.end() + 6]):
            continue
        # 원소 기호가 아닌 토막이 섞이면 화학식이 아니다
        syms = re.findall(r'[A-Z][a-z]?', re.sub(r'[₀-₉0-9()\[\]]', '', span))
        if any(x not in ELEMENTS for x in syms):
            continue
        # 앞뒤 문맥이 '맞추기 전' 이라고 말하면 건너뛴다. 창을 넉넉히 둔다 —
        # "…로 써. 그런데 이대로는 아직 완성이 아니야" 가 한 문장 뒤에 온다.
        near = text[max(0, m.start() - 120):m.end() + 130]
        if re.search(r'맞추|균형|미완성|아직|틀린 식|이대로|완성이 아', near):
            continue
        # **축약 표기**는 반응식이 아니다. 표의 검출 반응 칸에 'Na→H₂'(알코올에
        # 나트륨을 넣으면 수소가 난다) 처럼 쓴다. 양쪽이 한 종씩이고 화살표에
        # 공백이 없으면 그 꼴이다 — 좌우 원자 수를 맞출 식이 애초에 아니다.
        if re.search(r'\S(?:→|->|⟶|⇌)\S', span) and '+' not in span:
            continue
        # 273 K → 546 K 같은 온도. 화학 계수는 이렇게 크지 않다.
        if any(int(x) > 30 for x in re.findall(r'(?<![0-9])(\d+)\s*[A-Z]', span)):
            continue
        L, Rt = parse_side(m.group(1)), parse_side(m.group(2))
        if L is None or Rt is None:
            continue                             # 못 읽는 것은 넘긴다
        if not L or not Rt:
            continue
        # 전자(e) 가 든 반쪽반응은 전하까지 봐야 한다 — 여기서는 안 본다.
        if 'e' in L or 'e' in Rt:
            continue
        if L != Rt:
            diff = sorted(set(L) | set(Rt))
            why = ' · '.join(e + ' ' + str(L.get(e, 0)) + '→' + str(Rt.get(e, 0))
                             for e in diff if L.get(e, 0) != Rt.get(e, 0))
            bad.append((m.group(0).strip()[:60], why))
    return bad


def main():
    check = '--check' in sys.argv[1:]
    write = '--write' in sys.argv[1:]
    files = sorted(glob.glob(os.path.join(ROOT, 'lec-*.html')))
    bad = {'반응식': [], '상수': [], '뼈대': [], '표기': []}

    for p in files:
        rel = os.path.basename(p)
        with open(p, encoding='utf-8') as fh:
            src = fh.read()
        text = strip_tags(src)

        for eq, why in equations(text):
            bad['반응식'].append(rel + ' — ' + eq + '  [' + why + ']')

        # ② 상수: 값이 적혀 있으면 표지 값과 같은가
        for name, oks in CONSTS.items():
            for m in re.finditer(re.escape(name) + r'\s*=\s*([0-9.]+)', text):
                v = m.group(1).rstrip('.')
                if not any(v.startswith(o.split('×')[0].strip()) for o in oks):
                    bad['상수'].append(rel + ' — ' + name + ' = ' + v +
                                      ' (표지: ' + ' 또는 '.join(oks) + ')')

        # ③ 뼈대
        nos = [int(x) for x in re.findall(r'class="sec__no">(\d+)<', src)]
        if nos and nos != list(range(1, len(nos) + 1)):
            bad['뼈대'].append(rel + ' — 절 번호가 이어지지 않는다: ' +
                              ','.join(str(x) for x in nos))
        # 여는 문구는 두 꼴이다. 오답으로 온 학생에게는 "이번 진단에서 X가
        # 보강으로 잡혔어", **영역 첫 강**은 "오늘부터 … 영역이야(114~121, 8강)".
        # 뒤엣것이 더 낫다 — 글자만 보고 없다고 하면 안 된다.
        if not re.search(r'이번 진단에서|오늘부터.{0,30}영역', text):
            bad['뼈대'].append(rel + ' — 여는 문구가 없다')
        # '한 장 정리' 와 '한 장으로 정리' 는 같은 것이다.
        if not re.search(r'한 장(으로)? 정리', text):
            bad['뼈대'].append(rel + ' — 한 장 정리가 없다')
        if '직접 해보기' not in text:
            bad['뼈대'].append(rel + ' — 직접 해보기(숙제)가 없다')

        # ④ 표기: 아래첨자 없이 쓴 흔한 화학식
        flat = re.findall(r'(?<![A-Za-z0-9<>/=."\'-])'
                          r'(H2O|CO2|O2|H2|N2|NH3|CH4|H2SO4|HNO3|CaCO3|C6H12O6)'
                          r'(?![A-Za-z0-9<>])', text)
        if flat:
            u = sorted(set(flat))
            bad['표기'].append(rel + ' — 아래첨자 없이: ' + ', '.join(u[:6]) +
                              ' (' + str(len(flat)) + '곳)')

    if write:
        with open(NOTE, 'w', encoding='utf-8') as fh:
            json.dump({'설명': '선생님이 보고 남겨 둔 것. 여기 적힌 것은 빨간불을 '
                              '안 켜고, 새로 생기는 것만 막는다.', **bad},
                      fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        print('기록했습니다: ' + str(sum(len(v) for v in bad.values())) + '건')
        return 0

    try:
        with open(NOTE, encoding='utf-8') as fh:
            seen = json.load(fh)
    except (OSError, ValueError):
        seen = {}

    print('강의 ' + str(len(files)) + '장')
    fresh_total = 0
    for k in ['반응식', '상수', '뼈대', '표기']:
        v = bad[k]
        fresh = [x for x in v if x not in set(seen.get(k, []))]
        fresh_total += len(fresh)
        print('\n── ' + k + ' · ' + (str(len(v)) + '건' if v else '이상 없음') +
              (' (새것 ' + str(len(fresh)) + ')' if v and check else '') + ' ──')
        for line in (fresh if check else v)[:30]:
            print('  ✗ ' + line)
        rest = len(fresh if check else v) - 30
        if rest > 0:
            print('  … ' + str(rest) + '건 더')

    if check:
        if fresh_total:
            print('\nFAIL ' + str(fresh_total) + '건 (새로 생긴 것)')
            return 1
        print('\nPASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
