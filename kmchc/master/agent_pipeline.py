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

설계 단계 에이전트 3종 (배치 **전** — design 하위 명령)
  textbook-miner       교재 쪽 판독 → 개념 목록. 490쪽을 한 컨텍스트에 담을 수 없으므로 쪽 범위 fan-out
  duplicate-hunter     후보 지식 ↔ 은행 의미 중복 탐색. 기계 R1~R5 는 의미 중복을 못 잡는다
  distractor-designer  오개념 기반 오답 후보 생성. '거짓이면서 매력적'을 만족하는 후보를 여러 개 받아 고른다

  ※ duplicate-hunter 만은 은행을 봐야 하므로 독립성 제약이 없다. 대신 테마 전량을
    한 파일로 뽑아 주어 은행을 헤매지 않게 한다.

사용
----
  python3 master/agent_pipeline.py prep M01817 M01826     검증 입력 4종 + 프롬프트
  python3 master/agent_pipeline.py design '원자 모형' 76 78   설계 단계 3종 + 테마 대조표
  python3 master/agent_pipeline.py record M01817 M01826 "F1~F7 통과" "감사36"
                                                          층5 통과를 verified 에 기록
"""
import glob, json, os, sys

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
    #    ★factchecker 에서 잡혔던 것과 같은 어긋남이 여기에도 있었다★ (T14 P16 1차에 잡힘)
    #    defender 에게 시킨 일 둘째 항은 ★해설의 반박이 그 오답을 정말로 죽이는지★ 보는
    #    것인데, 이 파일은 발문·선지·정답만 실었다. defender 가 "해설이 없어 출제자가
    #    의도했을 반박을 복원해 검증했다" 고 적고서야 드러났다 — 한 회차가 반쯤 헛돌았다.
    #    ▸ 독립성은 깨지지 않는다. defender 는 이미 정답을 받는 자리다.
    #    ▸ ★시킨 일에 없는 자료를 주지 않는 것과, 시킨 일에 필요한 자료를 빠뜨리는 것은
    #      다르다★ — 최소는 '그 검증자가 시킨 일을 할 수 있는 만큼' 이다(F2 와 같은 규약).
    #    ★★같은 어긋남이 세 번째다 — 이번엔 계산 줄★★ (T15 P3 6차에 잡힘). defender 가
    #    "계산줄 필드는 이 파일에 실려 있지 않습니다" 라고 적었다. 그 회차에 내가 고친
    #    세 자리가 모두 계산 줄을 포함했는데 defender 는 해설·단평만 보고 판정했다.
    #    ▸ ★검증자가 '무엇이 없어 못 봤다' 고 적으면 그것은 판정이 아니라 도구 결함의
    #      신고다★ — 세 번 다 그렇게 드러났다(해설 없음 · 발문 없음 · 계산 줄 없음).
    with open(os.path.join(d, 'items_defend.md'), 'w', encoding='utf-8') as f:
        f.write("# 오답 변호 대상\n\n")
        for x in items:
            a = x['answer']
            f.write(f"## {x['id']}\n\n문항: {x['stem']}\n\n"
                    f"출제자가 정답으로 지정한 것: {CIR[a]} {x['choices'][a]}\n\n오답으로 지정된 선지:\n")
            for j, c in enumerate(x['choices']):
                if j != a:
                    f.write(f"  {CIR[j]} {c}\n")
            f.write(f"\n출제자의 근거: {x.get('answer_proof', '')}\n\n"
                    f"출제자의 계산 줄: {x.get('calc_check', '')}\n\n"
                    f"출제자의 해설(반박·단평 포함):\n{x['solution']}\n\n")
    # ③ factchecker — 문항 전체(발문·선지·근거·계산 줄)와 해설
    #    ★검증자에게 시킨 일과 검증자에게 준 자료가 어긋나 있었다★ (T14 P6 2차에 잡힘)
    #    이 파일은 오래도록 x['solution'] 만 썼다. 그런데 factchecker 에게 시킨 일에는
    #    ★발문과 해설의 대조★ 와 ★발문·선지·해설·자가진단 사이의 낱말 어긋남 세기★ 가
    #    들어 있다 — 발문이 없으면 물리적으로 할 수 없는 일이다. factchecker 가 두
    #    회차에 걸쳐 "발문이 없어 판정 불가" 라고 적고서야 도구를 열어 보았다.
    #    ▸ 독립성은 깨지지 않는다. factchecker 는 이미 정답과 해설을 받는 자리라
    #      발문·선지를 더 준다고 새로 새는 것이 없다. 독립성 원칙 1('필요 최소 정보')의
    #      ★최소★ 는 ★그 검증자가 시킨 일을 할 수 있는 만큼★ 이지 무조건 적게가 아니다.
    #    ▸ 근거(answer_proof)와 계산 줄(calc_check)도 싣는다. 사실오류가 사는 자리이고
    #      학생에게 보이지는 않아도 문항의 열세 자리 가운데 둘이다.
    with open(os.path.join(d, 'items_solution.md'), 'w', encoding='utf-8') as f:
        for x in items:
            a = x['answer']
            f.write(f"## {x['id']}\n\n[발문] {x['stem']}\n\n[선지]\n")
            for j, c in enumerate(x['choices']):
                f.write(f"{CIR[j]} {c}{'   ← 정답' if j == a else ''}\n")
            f.write(f"\n[근거] {x.get('answer_proof', '')}\n\n"
                    f"[계산 줄] {x.get('calc_check', '')}\n\n"
                    f"[도입 줄·해설·오답 단평·자가진단]\n{x['solution']}\n\n---\n\n")
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


TEXTBOOK_DIR = os.environ.get('KMCHC_TEXTBOOK_DIR', '/tmp/tb')


def textbook_pages(lo, hi):
    """교재 이미지 실제 경로. unzip 이 한글 파일명을 #Uxxxx 로 망가뜨려 두므로 글롭으로 찾는다."""
    out = []
    for p in range(int(lo), int(hi) + 1):
        hit = glob.glob(os.path.join(TEXTBOOK_DIR, f"*_{p}.jpg"))
        if hit:
            out.append((p, hit[0]))
    return out


DESIGN_PROMPTS = {
 'textbook-miner': """당신은 한국 고등학교 화학 교재의 **판독자**입니다. 지정된 쪽 이미지를 읽고 개념 목록을 만듭니다.

읽을 파일(이미지):
{pages}

이 쪽들에 실제로 적혀 있는 것만 뽑으십시오. 배경지식으로 채우지 마십시오 — 교재에 없는데 있다고 하면
그 개념으로 만든 문항이 교재 범위를 벗어납니다.

개념마다: ①한 줄 진술 ②쪽 번호 ③유형(정의 / 실험과 그 결론 / 수식 / 표·그림 자료 / 한계·경계)
④선수 개념 ⑤교재가 명시한 수치·상수가 있으면 그대로 ⑥문항으로 물을 수 있는 서로 다른 각도를 2~3개.

특히 다음을 놓치지 마십시오 — 표와 그림 안의 수치, 각주, "주의"·"참고" 상자,
그리고 **한 실험이 무엇까지 말해 주고 무엇은 말해 주지 못하는가**(문항의 핵심 소재입니다).

단원: {theme}

보고: 개념 목록(위 6항목) + 쪽별 요약 한 줄. 판독이 불확실한 글자는 [?] 로 표시하십시오.""",

 'duplicate-hunter': """당신은 문항 은행의 **의미 중복 탐색자**입니다.

읽을 파일: `{d}/theme_bank.md` (이 테마의 기존 문항 전량 — 발문과 정답)
새로 만들려는 후보 지식 목록은 사용자가 함께 줍니다.

왜: 기계 검사(R1~R5)는 scenario·skill·계산 골격만 봅니다. **말만 바꾼 같은 지식은 못 잡습니다.**
실제로 은행에는 이런 부채가 119제 쌓여 있습니다.

후보마다 판정하십시오.
  ✗ 중복    기존 문항과 **묻는 지식이 같다**. 표현·소재가 달라도 학생이 쓰는 판단이 같으면 중복입니다
  △ 인접    지식은 다르나 같은 뿌리에서 갈라져 나온다. 어떻게 차별화할지 함께 제시
  ○ 신규    겹치지 않는다

판정 근거로 **반드시 기존 문항 ID를 대십시오.** ID 없는 지적은 채택하지 않습니다.

다음은 중복이 **아닙니다** — 잘못 걸러내지 마십시오.
  · 거울 관계이면서 정답 지식이 상반될 때(예: β⁻ 는 Z+1, β⁺ 는 Z−1)
  · 같은 실험이라도 결과가 달라 결론이 다를 때(음극선 4실험은 각기 다른 지식)

단원: {theme}

보고: 후보별 표(후보 | 판정 | 근거 문항 ID | 차별화 방안). ✗ 와 △ 를 먼저.""",

 'distractor-designer': """당신은 4지선다 화학 문항의 **오답 설계자**입니다.

사용자가 발문과 정답을 줍니다. 각 문항에 쓸 오답 후보를 **문항당 6개 이상** 만드십시오.

★절대 원칙★ **오답은 '거짓이면서 매력적'이어야 합니다. 둘 중 하나만 만족하면 실격입니다.**

| 오답의 상태 | 판정 |
|---|---|
| 거짓 + 매력적 | 이상적 |
| 거짓 + 아무도 안 고름 | 죽은 선지 — 변별도를 깎는다(실측: 2개면 0.446→0.264) |
| **참 + 매력적** | **최악 — 음(−)변별. 아는 학생일수록 틀린다** |

그러므로 후보마다 **①무엇이 거짓인지 한 줄로 증명**하고, ②어떤 학생이 왜 끌리는지 밝히십시오.
독립된 진술로 읽었을 때 참이 될 여지가 조금이라도 있으면 스스로 버리십시오.

겨냥할 대상을 나누어 주십시오.
  B 흔한 오개념 보유 — 특정 오개념을 확신하는 학생
  **C 부분 이해 — 절반쯤 아는 학생.** 여기가 가장 어렵고 가장 중요합니다.
     C 를 흔들지 못하면 상위권 변별도가 0 이 됩니다(가상 응시에서 C=D 10/10 일치 관측)

오답 유형은 다음 8종 안에서 고르고 표기하십시오:
  proc(절차·귀속 혼동) · sign(부호·방향) · surface(표면적 특징) · conserv(보존량)
  · unit(단위) · scale(크기 규모) · overgen(과잉 일반화) · causal(인과 뒤바꿈)

단원: {theme}

보고: 문항별로 후보 표(후보 문장 | type | 거짓인 이유 | 겨냥 프로필 | 매력도 상·중·하).
한 문항의 후보 6개가 서로 다른 type 이 되도록 하십시오.""",
}


def cmd_design(theme, pg_lo=None, pg_hi=None):
    bank = json.load(open(BANK, encoding='utf-8'))
    items = [x for x in bank if x.get('theme') == theme]
    d = os.path.join(OUT_ROOT, 'design_' + theme.replace(' ', '_'))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'theme_bank.md'), 'w', encoding='utf-8') as f:
        f.write(f"# {theme} — 기존 문항 전량 ({len(items)}제)\n\n"
                "발문과 정답만 싣는다. 묻는 지식이 같은지를 보라.\n\n")
        for x in items:
            f.write(f"- **{x['id']}** {x['stem']}\n  → 정답 {CIR[x['answer']]} {x['choices'][x['answer']]}\n")
    print(f"═══ 설계 단계 · {theme} (기존 {len(items)}제) ═══")
    print(f"대조표 → {os.path.join(d, 'theme_bank.md')} "
          f"({os.path.getsize(os.path.join(d, 'theme_bank.md')):,}B)")

    pages = textbook_pages(pg_lo, pg_hi) if pg_lo else []
    if pg_lo and not pages:
        print(f"⚠ 교재 이미지를 찾지 못함 — {TEXTBOOK_DIR} 확인 "
              "(컨테이너 리셋 시 handoff 아카이브의 textbook/t.zip 재해동 필요)")
    plist = "\n".join(f"  {p}쪽  `{f}`" for p, f in pages) or "  (쪽 범위 미지정)"
    print("\n※ textbook-miner 는 쪽 범위를 나눠 **병렬**로. duplicate-hunter 는 후보 목록이 나온 뒤.\n")
    for name, tpl in DESIGN_PROMPTS.items():
        print("─" * 72)
        print(f"### agent: {name}")
        print(tpl.format(d=d, theme=theme, pages=plist))
        print()


def cmd_record(lo, hi, note, at):
    bank = json.load(open(BANK, encoding='utf-8'))
    n = 0
    for x in bank:
        if lo <= x['id'] <= hi:
            # ★watch 는 반드시 보존한다★ 검증 회차를 돌며 쌓인 '이 자리를 이렇게 되돌리지 말 것'
            #   기록이 여기에 들어 있다. 예전에는 통째로 덮어써서 T12 P3 의 10제 분량을
            #   한 번에 날렸다 — 그 기록이 없으면 다음 사람이 같은 결함을 다시 만든다.
            watch = (x.get('verified') or {}).get('watch')
            x['verified'] = {"layer5": note, "at": at, "by": "독립 에이전트 패스"}
            if watch:
                x['verified']['watch'] = watch
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
    elif c == 'design':
        cmd_design(sys.argv[2], *sys.argv[3:5])
    elif c == 'record':
        cmd_record(sys.argv[2], sys.argv[3],
                   sys.argv[4] if len(sys.argv) > 4 else "F1~F7 통과",
                   sys.argv[5] if len(sys.argv) > 5 else "미기재")
    else:
        print(__doc__)
