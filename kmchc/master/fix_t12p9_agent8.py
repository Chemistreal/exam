"""T12 P9 8차 순회 조치 — solver 0 · factchecker ✗0 △2(둘 다 채택) · defender 1(채택)

★내가 일곱 회 반려한 자리가 결국 옳았다.★ 기록으로 남긴다.

■ 채택1 M01889 ③ "전자 한 개를 떼는 데에 드는 에너지" — ★7회차에 반려를 뒤집는다★
  나는 2~7차에 걸쳐 ★두 겹으로 거짓★ 이라며 반려해 왔다 — (a) 부호가 반대이고
  (b) 단위가 kJ/mol 인데 선지는 '한 개'라는 것.
  ▸ ★(b)가 틀렸다.★ 한국 교과서의 이온화 에너지 정의가 "기체 상태의 원자 1 mol 에서
    ★전자 1개★ 를 떼어내는 데 필요한 에너지, 단위 ★kJ/mol★" 이다. 곧 '전자 한 개를 떼는'은
    입자당 양이 아니라 ★과정의 종류★ 를 가리키는 관용 표현이고 그 단위가 바로 kJ/mol 이다.
    ③은 ①과 같은 편이 아니라 ★정답 ④와 같은 편(몰당)★ 에 서 있었다.
  ▸ 그러면 남는 근거는 부호 하나인데, 발문이 "무엇을 ★나타내는지★"라 부호를 쟁점화하지 않고,
    E₁ = −13.6 eV 를 "결합 에너지 13.6 eV"라 부르는 관용이 널리 쓰인다. 얇다.
  ▸ ★조치: 이온화 틀을 통째로 버린다.★ ③을 "수소 분자 1 mol 이 지닌 에너지"로 바꾼다.
    · 거짓인가 — 이 식은 수소 ★원자★ 의 준위를 준다. 분자 1 mol 이면 원자가 2 mol 이라 값이 다르고,
      애초에 H₂ 에는 보어 준위가 없다. ★부호가 아니라 대상이 어긋나므로 어떤 독법에서도 거짓이다.★
    · 이름 붙는 오류인가 — ★원자와 분자를 가르지 못하는 것★ 은 '수소 = H₂'로 쓰는 일상어 탓에
      한국 학생에게 매우 흔하다.
    · 축이 맞는가 — 이 문항의 출제 의도는 '단위가 어느 층위에 붙었나'다. ①(원자 한 개) ·
      ③(분자 1 mol) · ④(원자 1 mol)이 같은 축 위에 셋으로 늘어서고, ②만 전이 축이다.
    · ★덤★ — sim 이 3차에 지적한 요령("kJ/mol 과 낱말이 겹치는 선지가 정답")이 사라진다.
      이제 ③도 '1 mol' 을 달고 있다.
  ▸ ★교훈★ 반려를 되풀이할 때는 '내가 든 근거가 몇 개인가'가 아니라 ★그 근거들이 각각 살아 있는가★ 를
    다시 봐야 한다. 나는 (a)+(b) 두 겹이라 안심했는데 (b)는 처음부터 없는 근거였다.
    ★검증자가 같은 자리를 되풀이해 올리면, 반려 사유 자체를 재검토할 것.★

■ 채택2 M01890 ① 해설 "발머는 눈에 보이지만" (factchecker)
  발머 계열 전체가 가시광선인 것처럼 읽힌다. 실제로는 n=3~6 의 네 선만 가시 영역이고
  그 위는 364.6 nm 계열 한계를 향해 근자외선으로 이어진다. 같은 배치 M01892 가
  "발머 계열 자체는 더 짧은 쪽으로 이어지고"라 정확히 적어 두어 ★두 해설이 나란히 어긋나 보인다.★
  ▸ "앞의 네 선이 눈에 보이지만"으로 범위를 묶는다.

■ 채택3 M01894 "본 뒤에야 나온 결론이고, 그 결론이 나온 것은 … 열네 해 뒤" (factchecker)
  서술 자체는 참이나(핵 모형 결론 1911, 열네 해 뒤), 앞 절의 '본 뒤에야'와 붙어 읽히면
  ★산란 관측(1909, 열두 해)이 열네 해 뒤★ 라는 인상을 준다. 같은 배치가 연대를 정밀하게 쓰고 있어 더 그렇다.
  ▸ 문장을 갈라 '결론이 세워진 해'에 숫자를 붙인다.
"""
import json, os

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')
CIR = '①②③④'

REPL = {}

# ══ M01889 — ③ 의 이온화 틀을 버리고 '대상' 축으로 ═════════
REPL['M01889'] = dict(
    choices=["수소 원자 한 개가 지닌 에너지", "바닥으로 떨어질 때 내놓는 빛의 에너지",
             "수소 분자 1 mol 이 지닌 에너지", "수소 원자 1 mol 이 지닌 에너지"],
    answer_proof=("단위가 kJ/mol 이니 몰당 값이고, 이 식이 다루는 것은 수소 원자다. 그러므로 이 값은 수소 "
                  "원자 1 mol 이 지닌 에너지다. 원자 한 개의 값을 얻으려면 아보가드로수로 한 번 더 나누어야 "
                  "하는데 그 수는 이 식에 들어 있지 않고, 수소 분자 1 mol 이라면 원자가 2 mol 이라 값이 "
                  "달라진다. 바닥으로 떨어질 때 내놓는 빛의 에너지는 준위 하나가 아니라 두 준위의 차에서 나온다"),
    errors={0: "한 개 값을 얻으려면 아보가드로수로 나누어야 한다",
            1: "떨어질 때 내놓는 빛의 에너지는 준위 하나가 아니라 두 준위의 차에서 나온다",
            2: "이 식은 수소 원자의 준위를 준다. 분자 1 mol 이면 원자가 2 mol 이라 값도 달라진다"},
    types={2: 'scale'},
    solution=(
        "식에 붙은 단위 하나가 값의 층위를 정해 주는 문항이야.\n\n"
        "[정답] ④ 수소 원자 1 mol 이 지닌 에너지 — 단위가 kJ/mol 이니 이 값은 몰당이야. 그리고 이 식이 다루는 "
        "것은 수소 원자지 — ④가 옳아. 원자 한 개의 값을 얻으려면 아보가드로수로 한 번 더 나누어야 하는데, 그 수는 "
        "이 식 어디에도 없어. 이 구별을 흘리면 뒤에 파장을 구할 때 반드시 사고가 나. 광자 하나의 에너지가 필요한데 "
        "몰당 값을 그대로 넣으면 아보가드로수만큼, 그러니까 6×10²³ 배쯤 어긋나거든. 식을 볼 때는 수보다 단위를 "
        "먼저 읽고, 그 단위가 ‘무엇 하나’에 붙은 것인지까지 읽는 버릇을 들이면 좋아.\n\n"
        "① 수소 원자 한 개가 지닌 에너지: 한 개 값을 얻으려면 아보가드로수로 나누어야 해.\n"
        "② 바닥으로 떨어질 때 내놓는 빛의 에너지: 떨어질 때 내놓는 빛의 에너지는 준위 하나가 아니라 두 준위의 "
        "차에서 나오지.\n"
        "③ 수소 분자 1 mol 이 지닌 에너지: 이 식은 수소 원자의 준위를 주는 거야. 분자 1 mol 이면 원자가 "
        "2 mol 이라 값도 달라지지.\n\n"
        "자가진단: 단위가 층위를 말한다 — kJ/mol 은 원자 1 mol 당."),
)


SUB = [
    # 채택2 발머는 앞의 네 선만 가시 영역이다 (계열 한계 364.6 nm 까지 이어진다)
    ('M01890', 'answer_proof',
     '발머는 눈에 보이지만 빨강부터 보라까지 여러 색이 섞여 있어 연두 하나로 대표되지 않는다',
     '발머는 앞의 네 선이 눈에 보이지만 그 색이 빨강부터 보라까지 걸쳐 있어 연두 하나로 대표되지 않는다'),
    ('M01890', 'solution',
     '발머는 눈에 보이지만 빨강부터 보라까지 섞여 있어 연두 하나로 대표되지 않지.',
     '발머는 앞의 네 선이 눈에 보이지만 그 색이 빨강부터 보라까지 걸쳐 있어 연두 하나로 대표되지 않지.'),
    # 채택3 '본 뒤에야'와 붙어 읽히면 산란 관측(1909)이 열네 해 뒤로 읽힌다 — 문장을 가른다
    ('M01894', 'answer_proof',
     '알파 입자를 쏘아 크게 되튀는 것을 본 뒤에야 나온 결론이고, 그 결론이 나온 것은 이 실험보다 열네 해 뒤의 일이다.',
     '알파 입자를 쏘아 크게 되튀는 것을 보고 나서 세운 결론이다. 그 결론이 세워진 해는 이 실험보다 열네 해 뒤다.'),
    ('M01894', 'solution',
     '알파 입자를 쏘아 크게 되튀는 것을 본 뒤에야 나온 결론이고, 그 결론이 나온 것은 이 실험보다 열네 해 뒤의 일이야 — ④가 옳아.',
     '알파 입자를 쏘아 크게 되튀는 것을 보고 나서 세운 결론이야. 그 결론이 세워진 해는 이 실험보다 열네 해 뒤지 — ④가 옳아.'),
]


def spread(ch):
    L = sorted(len(str(c)) for c in ch)
    return (L[3] - L[0]) / ((L[1] + L[2]) / 2)


def rank(it):
    L = [len(str(c)) for c in it['choices']]
    return sorted(range(4), key=lambda i: -L[i]).index(it['answer']) + 1


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    d = {x['id']: x for x in bank}
    n = 0
    for fid, r in REPL.items():
        x = d[fid]
        for key in ('stem', 'answer_proof', 'solution', 'choices'):
            if key in r:
                assert x[key] != r[key], f'{fid}: {key} 가 이미 같음'
                x[key] = r[key]; n += 1
        for w in x['distractors']:
            for k, fld in (('errors', 'error'), ('types', 'type')):
                if k in r and w['opt'] in r[k]:
                    w[fld] = r[k][w['opt']]; n += 1
    for fid, field, old, new in SUB:
        x = d[fid]
        assert old in x[field], f'{fid}.{field}: 대상 문면 없음 -> {old}'
        x[field] = x[field].replace(old, new, 1); n += 1

    touched = set(REPL) | {s[0] for s in SUB}
    for fid in touched:
        x = d[fid]
        ch, a, sol = x['choices'], x['answer'], x['solution']
        L = [len(str(c)) for c in ch]
        assert not (L[a] == max(L) and L.count(max(L)) == 1), f'{fid}: 정답=유일 최장 {L}'
        assert not (L[a] == min(L) and L.count(min(L)) == 1), f'{fid}: 정답=유일 최단 {L}'
        if sorted(L)[1] >= 8:
            assert spread(ch) <= 0.25, f'{fid}: 산포 {spread(ch):.3f} {L}'
        assert len(set(ch)) == 4, f'{fid}: 선지 중복'
        assert len(sol) >= 300, f'{fid}: 해설 {len(sol)}자'
        for w in x['distractors']:
            assert ch[w['opt']] in sol, f'{fid} {CIR[w["opt"]]}: 해설에 오답 문면 없음 -> {ch[w["opt"]]}'
        assert ch[a] in sol, f'{fid}: 해설에 정답 문면 없음'
        for f in ('stem', 'solution'):
            for bad in ('**', '★'):
                assert bad not in x[f], f'{fid}: {f} 에 {bad}'
    # M01889 — 층위 축이 셋(원자 한 개 · 분자 1 mol · 원자 1 mol)으로 늘어섰는지
    ch = d['M01889']['choices']
    assert sum('1 mol' in c for c in ch) == 2, 'M01889: 1 mol 표시가 둘이 아님 — 요령이 되살아난다'
    assert '이온화' not in json.dumps(d['M01889'], ensure_ascii=False), 'M01889: 이온화 틀 잔존'

    STALE = {
        'M01889': ['떼는 데에 드는 에너지', '떼어 내는 데 드는'],
        'M01890': ['발머는 눈에 보이지만'],
        'M01894': ['본 뒤에야 나온 결론'],
    }
    for fid, pats in STALE.items():
        blob = json.dumps(d[fid], ensure_ascii=False)
        for p in pats:
            assert p not in blob, f'{fid}: 걷어낸 문면 잔존 -> {p}'

    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'P9 8차 조치 {n}곳 · 채택 3 · 반려 0 · ★7회 반려한 자리를 뒤집었다★')
    for fid in sorted(touched):
        x = d[fid]
        L = [len(str(c)) for c in x['choices']]
        print(f'  {fid} 정답{CIR[x["answer"]]} 길이{L} 산포{spread(x["choices"]):.2f} '
              f'길이순위{rank(x)} 해설{len(x["solution"])}자')


if __name__ == '__main__':
    main()
