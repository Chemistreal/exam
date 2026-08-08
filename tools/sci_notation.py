#!/usr/bin/env python3
"""학생이 읽는 글의 **과학 표기**가 한 벌인지 잰다 — 그리고 함부로 안 고친다.

이 저장소의 표기 원칙은 유니코드다(`tools/README.md` 9번). H₂O·10²³·Cu²⁺·
×·→ 를 쓴다. 기출동형은 `dh_normalize.py` 로 한 번 통일했는데, 해설
(`answers/`)은 그 손이 닿지 않았다.

재어 보면 이렇다(2026-08-08).

    아래첨자 꼴   H2O·CO2 …        1300곳 남짓
    전하         Na+·Mg2+ …        180곳 남짓
    10^n         10^-5             83곳
    ×            3 x 10⁻⁵          54곳

**그런데 이걸 기계로 한 번에 고치면 안 된다.** 같은 문서 9번 항목에 일괄
정정 도구가 새 오류를 만든 적이 세 번 있다고 적혀 있다. 셋 다 "화학식처럼
생겼으니 화학식일 것"이라고 넘겨짚은 데서 나왔다.

여기서도 그랬다. `->` 를 화살표로 바꾸려다 유일한 한 곳을 열어 보니

    산의 세기는 H3Y>H2Y->HY^2-

**화살표가 아니었다.** `H₂Y⁻ > HY²⁻` 의 음전하와 부등호였다. 바꿨으면 화학이
망가진다.

그 뒤에 한 번 더 해 봤다. 이번에는 정규식이 아니라 **원소 기호를 아는
문법**으로 화학식을 낱낱이 쪼개고, 되짚어 ASCII 로 돌리면 글자 하나까지
같은지까지 확인하는 방식이었다. 1117곳이 바뀌고 되짚기도 정확했다.

그런데 바뀌는 낱말 365종을 눈으로 훑으니 **일곱 갈래가 틀렸다.**

    CO32→CO₃₂        CO₃²⁻ 를 ASCII 로 적은 것. 2 는 아래첨자가 아니라 전하다
    CaCO3+→CaCO₃⁺    `CaCO3+2HCl` 의 `+` 는 반응식의 더하기지 전하가 아니다
    SN2→SN₂          입체수(steric number) 표기다. 황·질소 화합물이 아니다
    III-→III⁻        로마 숫자. `Fe(III)-` 같은 자리다
    C-→C⁻ · B-→B⁻    보기 이름표(A·B·C)에 붙은 붙임표다
    N2+→N²⁺          이질소 양이온인데 전하 2 로 읽었다
    Na2+→Na²⁺        나트륨은 2가가 없다. 애초에 수상한 표기다

일곱 갈래를 다 막으려면 규칙을 일곱 개 더 얹어야 하고, 그 하나하나가 또
넘겨짚기다. **얻는 것은 글자 모양이고 잃을 수 있는 것은 화학이다.** 그래서
안 한다. 이 기록을 남겨 다음 사람이 같은 길을 다시 걷지 않게 한다.

그래서 이 자는 **딱 한 갈래만 고친다.** 지수가 이미 윗첨자로 적힌 자리의
곱셈 기호다.

    4.14 x 10⁻⁹   →   4.14 × 10⁻⁹

앞뒤가 정해져 있어 넘겨짚을 여지가 없다. 나머지는 **세어서 알리기만** 한다.
sanyeom-60 처럼 한 회차가 처음부터 끝까지 ASCII 로 적힌 곳은, 절반만
바꾸면 되레 더 어지러워진다. 무엇을 통일할지는 사람이 정한다.

    python3 tools/sci_notation.py           # 갈래별로 몇 곳인지
    python3 tools/sci_notation.py --write   # 곱셈 기호만 고친다
    python3 tools/sci_notation.py --check   # 곱셈 기호가 도로 생기면 빨간불
"""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ('explanation', 'misconception', 'stem')

# 고치는 것: 윗첨자 지수 앞의 ASCII x. 앞은 숫자나 빈칸, 뒤는 10+윗첨자다.
MULT = re.compile(r'(?<=[\d\s])x(?=\s?10[⁰¹²³⁴⁵⁶⁷⁸⁹⁻])')

# 세기만 하는 것
COUNT = (
    ('아래첨자 꼴', re.compile(
        r'\b(?:H2O|CO2|O2|N2|H2|Cl2|F2|Br2|I2|NH3|NH4|NO2|NO3|SO2|SO3|SO4|CH4|'
        r'H2SO4|HNO3|CaCO3|Fe2O3|Al2O3|MnO4|CO3|HCO3|PO4|H3O|H2O2|N2O4)\b')),
    ('전하', re.compile(r'\b(?:H|Na|K|Li|Mg|Ca|Ba|Sr|Rb|Cs|Al|Fe|Cu|Ag|Zn|Mn|Sn|Pb|Be|Au)\d?[+-]{1,2}(?![\w⁺⁻²³])')),
    ('10^n', re.compile(r'10\^-?\d')),
)


def files():
    for pat in ('answers/*.json', 'donghyung/*.json'):
        for p in sorted(glob.glob(os.path.join(ROOT, pat))):
            if os.path.basename(p) in ('index.json', '_template.json'):
                continue
            yield p


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    fixed = 0
    tally = collections.Counter()
    spread = collections.defaultdict(collections.Counter)

    for path in files():
        data = json.load(open(path, encoding='utf-8'))
        eid = os.path.basename(path)[:-5]
        touched = False
        for k, q in (data.get('questions') or {}).items():
            for f in FIELDS:
                t = q.get(f)
                if not isinstance(t, str) or not t:
                    continue
                for name, pat in COUNT:
                    n = len(pat.findall(t))
                    if n:
                        tally[name] += n
                        spread[name][eid] += n
                n = len(MULT.findall(t))
                if n:
                    tally['× (고칠 수 있다)'] += n
                    spread['× (고칠 수 있다)'][eid] += n
                    if write:
                        q[f] = MULT.sub('×', t)
                        fixed += n
                        touched = True
        if write and touched:
            with open(path, 'w', encoding='utf-8') as fp:
                json.dump(data, fp, ensure_ascii=False, indent=1)
                fp.write('\n')

    print('학생이 읽는 글의 ASCII 과학 표기\n')
    for name, n in tally.most_common():
        top = ' · '.join('%s %d' % kv for kv in spread[name].most_common(3))
        print('  %-16s %5d곳   %s' % (name, n, top))

    if write:
        print('\n곱셈 기호 %d곳을 × 로 고쳤다. 나머지는 손대지 않는다.' % fixed)
        return 0
    left = tally.get('× (고칠 수 있다)', 0)
    if left:
        print('\n곱셈 기호 %d곳은 앞뒤가 정해져 있어 기계가 고칠 수 있다 — --write' % left)
        return 1 if check else 0
    print('\n기계가 고칠 수 있는 자리는 없다. 나머지는 사람이 정한다 '
          '(파일 머리의 H2Y->HY^2- 사연을 읽어라).')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
