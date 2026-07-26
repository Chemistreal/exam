#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent_pipeline.py — 감사 층5 독립 패스를 '진짜 독립'으로 만드는 도구

왜 에이전트인가
--------------
감사14호가 실증한 이 프로젝트의 구조적 약점: *"같은 모델의 자기감사는 계산·경계·파서층은
무결하나 판정층에서 체계적으로 관대하다."* 그래서 selfaudit(기계 신호)을 도입했다.

층5의 F1·F2·F3·F5 는 기계로 못 하고 판단이 필요한데, 저작자가 스스로 하면 같은 함정에 빠진다.
'안 본 척'하는 것과 **별도 컨텍스트의 검증자가 실제로 모르는 것**은 다르다.
이 도구는 후자를 만든다 — 정답·근거·해설을 물리적으로 제거한 입력 파일을 생성한다.

산출 파일 (scratchpad/verify/<범위>/)
  items_solve.md     stem + choices 만          → solver   (F1 정답 정확성 · F5 자족성)
  items_defend.md    문항 + 정답 + 오답 목록     → defender (F2 복수 정답 위험)
  items_solution.md  해설만                     → factchecker (F3 해설 진술)
  items_sim.md       stem + choices 만          → student-sim (오답 매력도 예측)

★독립성 보장 3원칙★
  1. 입력 파일에 **필요 최소 정보만** 담는다 (solver 는 정답조차 모른다)
  2. 프롬프트에서 `kmchc/` 디렉터리 접근을 **명시적으로 금지**한다 (master_bank.json 에 답이 있다)
  3. 검증자끼리도 서로의 결과를 보지 않는다 — 병렬로 띄우고 결과는 저작자가 종합한다

사용
----
  python3 master/agent_pipeline.py prep M01817 M01826     입력 파일 + 프롬프트 생성
  python3 master/agent_pipeline.py record M01817 M01826 "F1~F7 통과" "감사36"
                                                          층5 통과를 verified 에 기록
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')
OUT_ROOT = os.environ.get(
    'KMCHC_VERIFY_DIR',
    '/tmp/claude-0/-home-user-exam/5f2ecfac-9847-5091-89ed-a121f3b6410f/scratchpad/verify')
CIR = '①②③④'

FORBID = ("★절대 금지★ `/home/user/exam/kmchc/` 아래의 어떤 파일도 열지 마십시오. "
          "`master_bank.json` 에 정답과 해설이 들어 있어 검증이 무효가 됩니다. "
          "아래 지정한 파일 **하나만** 읽으십시오.")


def load(lo, hi):
    bank = json.load(open(BANK, encoding='utf-8'))
    return [x for x in bank if lo <= x['id'] <= hi]


def write_inputs(items, d):
    os.makedirs(d, exist_ok=True)
    # ① solver — 정답·근거·해설 전부 제거
    with open(os.path.join(d, 'items_solve.md'), 'w', encoding='utf-8') as f:
        f.write("# 화학 문항 — 풀이 대상\n\n각 문항의 정답을 직접 고르시오.\n\n")
        for x in items:
            f.write(f"## {x['id']}\n\n{x['stem']}\n\n")
            for j, c in enumerate(x['choices']):
                f.write(f"{CIR[j]} {c}\n")
            f.write("\n")
    # ② defender — 정답이 무엇인지는 알려주되 오답을 변호하게 함
    with open(os.path.join(d, 'items_defend.md'), 'w', encoding='utf-8') as f:
        f.write("# 오답 변호 대상\n\n")
        for x in items:
            a = x['answer']
            f.write(f"## {x['id']}\n\n문항: {x['stem']}\n\n"
                    f"출제자가 정답으로 지정한 것: {CIR[a]} {x['choices'][a]}\n\n오답으로 지정된 선지:\n")
            for j, c in enumerate(x['choices']):
                if j != a:
                    f.write(f"  {CIR[j]} {c}\n")
            f.write("\n")
    # ③ factchecker — 해설만
    with open(os.path.join(d, 'items_solution.md'), 'w', encoding='utf-8') as f:
        for x in items:
            f.write(f"## {x['id']}\n\n{x['solution']}\n\n---\n\n")
    # ④ student-sim — solver 와 같은 정보(정답 모름)
    with open(os.path.join(d, 'items_sim.md'), 'w', encoding='utf-8') as f:
        f.write("# 가상 응시 대상\n\n")
        for x in items:
            f.write(f"## {x['id']}\n\n{x['stem']}\n\n")
            for j, c in enumerate(x['choices']):
                f.write(f"{CIR[j]} {c}\n")
            f.write("\n")


PROMPTS = {
 'solver': """당신은 한국 고등학교 화학 문항의 **독립 검증자**입니다. 출제자의 의도나 정답을 모르는 상태에서 직접 풀어, 출제자가 지정한 정답과 일치하는지 확인합니다.

읽을 파일: `{d}/items_solve.md`
{forbid}

문항마다: ①직접 풀어 답을 고른다 ②근거를 한두 문장 ③확신도(확실/보통/모호) ④모호하면 왜인지 구체적으로 — 답이 둘로 갈릴 여지가 있는가, 표현이 애매한가 ⑤**자족성** — stem 의 정보만으로 답이 유도되는가, 교재 밖 지식이나 암묵 가정이 필요한가.
편집상 흠(어미 불일치·표기 혼용 등)도 눈에 띄면 적어 주십시오.

단원: {theme}

보고: 표(문항|내 답|확신도|자족성) + 확실하지 않거나 자족성이 미흡한 것만 구체 서술.
문제가 없으면 없다고 명확히. 넘겨짚어 만들어내지 마십시오.""",

 'defender': """당신은 4지선다 화학 문항의 **적대적 검토자**입니다. 임무는 '오답'으로 지정된 선지를 **변호**하는 것입니다.

읽을 파일: `{d}/items_defend.md`
{forbid}

왜: 오답이 **그 자체로 사실인 진술**이면 잘 아는 학생일수록 끌려 변별도가 음수가 됩니다(실측에서 −0.026 관측). 오답은 '확실히 틀려야' 합니다.

오답마다 적극 변호하십시오. 특히 ①독립된 진술로 읽으면 참인가 ②특정 조건·해석에서 참이 되는가 ③정답 쪽이 "항상/모두/반드시"로 과잉 일반화는 아닌가 ④"~할 수 있다"로 끝나 가능성만으로 참이 되는가 ⑤부분적으로 옳은 요소가 섞였는가.

단원: {theme}

보고: **F2 실패 후보**를 심각도 순으로 먼저(문항ID·선지·변호 논거·왜 위험한지), 그다음 나머지는 "확실히 틀림" 한 줄 요약.
변호가 궁색하면 그건 좋은 오답이라는 뜻입니다 — 억지로 만들지 마십시오.""",

 'factchecker': """당신은 화학 해설문의 **사실 검증자**입니다.

읽을 파일: `{d}/items_solution.md`
{forbid}

해설마다 ①화학적 주장을 문장 단위로 참/거짓/과장/모호 판정 ②**곁가지 설명을 특히** — 본론은 검토되지만 "앞 단원에서 배웠듯…" 같은 부수 문장은 흘러가기 쉽다 ③수치는 표준값과 대조 ④"항상·절대·모두" 같은 단정이 실제로 성립하는가 ⑤틀리지는 않았으나 학생이 잘못 일반화할 서술.

단원: {theme}

보고: **사실 오류(✗)** 먼저(문항ID·문장·무엇이 틀렸는지·어떻게 고칠지), **과장·모호(△)** 그다음, 문제없는 것은 ID만 나열.
지적을 위한 지적을 만들지 마십시오.""",

 'student-sim': """당신은 문항의 **오답 매력도**를 예측합니다. 실제 학생 네 부류를 연기해 각 문항의 답을 고르십시오.

읽을 파일: `{d}/items_sim.md`
{forbid}

왜: 실측 479문항 분석 결과, 선택률 5% 미만인 '죽은 선지'가 늘수록 변별도가 무너집니다
(0개 0.446 → 1개 0.422 → 2개 0.264 → 3개 0.140). 아무도 안 고르는 오답은 문항을 무력화합니다.
실제 응시 전에 이를 미리 잡아내는 것이 목적입니다.

네 프로필 각각으로 **끝까지 연기해서** 답을 고르십시오. 정답을 아는 상태로 역산하지 말고, 그 학생이 실제로 어떻게 생각할지를 따라가십시오.
  A 개념 미형성 — 용어만 들어 봤고 원리는 모름. 그럴듯한 낱말이 겹치는 선지에 끌림
  B 흔한 오개념 보유 — 특정 오개념을 확신하고 있어 그에 맞는 선지를 고름
  C 부분 이해 — 절반쯤 알아 정답과 그럴듯한 오답 사이에서 흔들림
  D 숙달 — 정확히 앎

단원: {theme}

보고: 문항별 표(문항 | A | B | C | D | 아무도 안 고른 선지) + **죽은 선지 목록**(네 프로필 누구도 고르지 않은 오답)과, 그 선지를 어떻게 고치면 매력적이 될지 제안.
D(숙달)가 정답이 아닌 것을 골랐다면 그건 문항 결함이니 크게 표시하십시오.""",
}


def cmd_prep(lo, hi):
    items = load(lo, hi)
    if not items:
        print(f"⛔ {lo}~{hi} 에 해당하는 문항이 없습니다"); return
    theme = items[0]['theme']
    d = os.path.join(OUT_ROOT, f"{lo}_{hi}")
    write_inputs(items, d)
    print(f"═══ 층5 독립 패스 준비 · {lo}~{hi} ({len(items)}제 · {theme}) ═══")
    print(f"입력 생성 → {d}")
    for k in ('items_solve.md', 'items_defend.md', 'items_solution.md', 'items_sim.md'):
        p = os.path.join(d, k)
        print(f"   {k:<20} {os.path.getsize(p):>6,}B")
    print("\n※ 아래 4개를 **병렬로** 띄우십시오. 검증자끼리 결과를 공유하면 독립성이 깨집니다.\n")
    for name, tpl in PROMPTS.items():
        print("─" * 72)
        print(f"### agent: {name}")
        print(tpl.format(d=d, forbid=FORBID, theme=theme))
        print()


def cmd_record(lo, hi, note, at):
    bank = json.load(open(BANK, encoding='utf-8'))
    n = 0
    for x in bank:
        if lo <= x['id'] <= hi:
            x['verified'] = {"layer5": note, "at": at, "by": "독립 에이전트 패스"}
            n += 1
    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total = sum(1 for x in bank if (x.get('verified') or {}).get('layer5'))
    print(f"✅ {n}제 기록 · 누적 층5 통과 {total}/{len(bank)}제 ({total/len(bank):.1%})")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(0)
    c = sys.argv[1]
    if c == 'prep':
        cmd_prep(sys.argv[2], sys.argv[3])
    elif c == 'record':
        cmd_record(sys.argv[2], sys.argv[3],
                   sys.argv[4] if len(sys.argv) > 4 else "F1~F7 통과",
                   sys.argv[5] if len(sys.argv) > 5 else "미기재")
    else:
        print(__doc__)
