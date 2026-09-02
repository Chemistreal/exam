export const meta = {
  name: 'thin-explanations-verify',
  description: '이미 증보된 해설을 크롭과 대조해 적대적으로 반박하고 수리한다',
  phases: [
    { title: '검증', detail: '크롭을 직접 읽고 처음부터 풀어, 증보된 해설이 사실인지 반박한다' },
    { title: '수리', detail: '반박된 문항만 고쳐 쓴다' },
  ],
}

const SRC = '/tmp/claude-0/-home-user-study64-report/2113474c-4485-592e-912d-e7d09ec51ec8/scratchpad/thinsrc'
const OUT = '/home/user/exam/answers/_thick'
const KEYS = (args && args.keys) || []

const S_WRITE = {
  type: 'object', additionalProperties: false, required: ['written', 'notes'],
  properties: { written: { type: 'integer' }, notes: { type: 'string' } },
}
const S_PROBLEM = {
  type: 'object', additionalProperties: false, required: ['q', 'kind', 'what', 'fix'],
  properties: {
    q: { type: 'string' },
    kind: { type: 'string', enum: ['정답오류', '지문오독', '계산오류', '화학오류', '함정허구', '오답누락', '근거없음', '말투', '기타'] },
    what: { type: 'string' },
    fix: { type: 'string' },
  },
}
const S_VERDICT = {
  type: 'object', additionalProperties: false, required: ['verdict', 'problems'],
  properties: {
    verdict: { type: 'string', enum: ['clean', 'problems'] },
    problems: { type: 'array', items: S_PROBLEM },
  },
}
const S_FIX = {
  type: 'object', additionalProperties: false, required: ['fixed', 'remaining', 'note'],
  properties: { fixed: { type: 'integer' }, remaining: { type: 'integer' }, note: { type: 'string' } },
}

const WHY = [
  '왜 이 문항들인가',
  '',
  '여기 실린 문항은 모두 **응시자 절반 이상이 틀린** 것들이다(각 문항에 `_정답률` 로',
  '적혀 있다). 그런데 해설은 「사고과정 E° = 0.80 − (−0.76) = 1.56 V … → ④」 처럼',
  '메모 한 줄뿐이다. 이미 아는 사람에게는 충분하지만, **틀린 학생에게는 아무것도',
  '알려 주지 않는다.** 그 학생이 왜 틀렸는지, 어디서 갈렸는지가 없다.',
  '',
  '많이 틀린 문항일수록 해설이 두꺼워야 한다. 그 반대로 되어 있었다.',
  '',
  '앞선 아홉 덩어리에서는 **전부 결함이 나왔다.** 지문을 안 보고 옛 메모를 부풀린',
  '자리들이었다 — 「진한 황산(밀도 약 1.28 g/mL)」(1.28 은 전해액 밀도이고 진한',
  '황산은 1.84 다), 함정 설명대로 실수하면 다른 보기가 나오는 자리, 지문에 없는',
  '원자량을 「주어진 것」으로 적은 자리. 그래서 **그림을 직접 열라**고 시킨다.',
].join('\n')

const RULES = [
  '증보 규칙 — 반드시 지킨다.',
  '',
  '1. **지문을 먼저 읽어라.** 각 문항의 `_크롭` 이 원본 문제지 그림이다(저장소 상대 경로,',
  '   예: `/home/user/exam/crops/jmchc-10/12.png`). Read 로 그림을 열어 지문과 보기를',
  '   눈으로 읽어라. 지문을 안 보고 옛 해설만 부풀리면 틀린 해설이 길어질 뿐이다.',
  '2. **정답을 네가 직접 풀어 확인해라.** 옛 해설의 답과 다르면 고치지 말고 `notes` 에 적어라.',
  '   ⚠ **정답 키(answer·acceptableAnswers)는 절대 바꾸지 않는다.** 이 회차들은 이미',
  '   채점이 끝나 성적이 나갔다. 답이 틀렸다고 판단되면 `reviewNote` 에 적어 선생님께 넘긴다.',
  '3. **explanation 은 단계로 쓴다.** 무엇이 주어졌는지 → 어떤 법칙을 쓰는지 → 계산 →',
  '   결론. 계산은 중간값을 다 보인다. 「≈」 로 얼버무리지 않고 실제 수를 적는다.',
  '   판단형(옳은 것/옳지 않은 것)이면 **보기 네 개를 각각 판정**해서 적는다.',
  '4. **misconceptions 에 선지별 함정을 채운다.** 오답 번호마다, 그 번호를 고른 학생이',
  '   저지른 **구체적인 실수**를 적는다. 그 실수를 실제로 저질러 계산하면 그 보기 값이',
  '   나와야 한다. 안 나오면 지어낸 설명이니 쓰지 않는다.',
  '   (예: 「n 을 2 가 아니라 1 로 두고 네른스트 식을 세운 값」)',
  '5. **misconception(단수) 은 이 개념에서 흔한 실수 한 문장.** 선지별 설명과 같은 말을',
  '   되풀이하지 않는다.',
  '6. **지문에 없는 값을 「주어진 것」이라고 적지 않는다.** 표준 원자량처럼 밖에서',
  '   가져온 값은 그 출처를 밝혀 쓴다 — 「표준 원자량(H 1, O 16)으로 18」.',
  '7. **없는 것을 지어내지 않는다.** 크롭이 흐려서 못 읽는 대목이 있으면 그 문항은',
  '   건드리지 말고 `notes` 에 「N번 크롭을 못 읽었다」고 적어라. 추측으로 채우지 않는다.',
  '8. **평서체로 쓴다 — 모든 문장이 「~다.」로 끝난다.** 반말(「~어긋나.」)이나',
  '   해요체(「~어긋나요.」), 청유형(「~해 보자.」)으로 쓰지 않는다. 학생에게 말을 거는',
  '   투로 쓰지 않는다 — 이 글은 인쇄되어 학부모도 읽는다.',
  '9. **concept·area 는 글자까지 그대로 둔다.** 은행 색인이 이름으로 같은 개념을 찾는다.',
  '10. 한국어. 고등학교 화학/화학올림피아드 수준. 첨자는 유니코드(H₂O, Ca²⁺, ¹²C, E°).',
  '    온도는 °C 로 쓴다(℃ 한 글자를 쓰지 않는다).',
].join('\n')

const SHAPE = [
  '{',
  '  "<문항번호>": {',
  '    "explanation": "<단계별 풀이. 줄바꿈은 \\\\n>",',
  '    "misconception": "<이 개념에서 흔한 실수 한 문장>",',
  '    "misconceptions": { "<오답 번호>": "<그 번호를 고르게 만드는 구체적인 오류>" },',
  '    "reviewNote": "<선생님이 봐야 할 것이 있을 때만. 없으면 이 칸을 넣지 않는다>"',
  '  }',
  '}',
].join('\n')


/* ── 왜 「검증만」 대본이 따로 있나 ────────────────────────────────────
   집필은 끝났는데 검증·수리가 중간에 끊기는 일이 실제로 두 번 났다(세션
   한도). 그때 남는 것은 **아무도 확인하지 않은 원고**다. 처음부터 다시
   돌리면 이미 쓴 것을 버리게 되고, 그냥 넣으면 확인 안 한 글이 학생에게
   간다. 그래서 증보 단계만 떼어 낸 대본을 둔다.

   ⚠ 첫 독자가 누구인지 반박자에게 알려 준다 — 「앞선 실행이 끊겨 아무도
     이 글을 확인하지 않았다. 네가 첫 독자다」. 이 한 줄이 있고 없고가
     실제로 달랐다. */
phase('검증')

const results = await pipeline(
  KEYS,

  function (key) {
    const p = '증보된 해설을 **반박한다**. 통과시키는 것이 아니라 틀린 것을 찾는 것이 목적이다.\n\n'
      + '⚠ 이 증보본은 **검증을 못 거친 채 남아 있는 원고**다(앞선 실행이 중간에 끊겼다).\n'
      + '  아무도 아직 이 글을 확인하지 않았다. 네가 첫 독자다.\n\n'
      + '원본(지문·보기·정답·옛 해설): `' + SRC + '/' + key + '.json`\n'
      + '증보본: `' + OUT + '/' + key + '.json`\n\n'
      + '⚠ **크롭 그림을 네가 직접 열어 읽어라.** 원본 파일의 `_크롭` 경로를 Read 로 연다\n'
      + '(저장소 뿌리는 `/home/user/exam`). 지문을 안 보고는 해설이 맞는지 알 수 없다.\n'
      + '그림에서 수치를 읽어야 하는 문항이면 눈금과 견주어 **값을 직접 재라** — 앞선\n'
      + '실행에서 「첫 봉우리 약 200으로 가장 높다」가 실제로는 195였고 가장 높은 것은\n'
      + '다른 도표였던 자리가 그렇게 잡혔다.\n\n'
      + '문항마다 **증보자의 글을 믿지 말고 그림을 보고 처음부터 직접 풀어라.** 그런 다음 따진다.\n\n'
      + 'A. **해설이 낸 답이 정답 키와 같은가.** 다르면 문제다.\n'
      + 'B. **해설의 계산이 맞나.** 중간값을 하나씩 다시 계산해 봐라. 단위·유효숫자·부호,\n'
      + '   반응식 균형, 상수 값이 맞는가.\n'
      + 'C. **해설이 지문을 제대로 읽었나.** 그림에 있는 조건을 빠뜨렸거나, 그림에 없는\n'
      + '   조건을 지어내지는 않았는가. 판단형이면 보기 넷을 다 판정했는가.\n'
      + '   **지문에 없는 값을 「주어진 것」이라고 적지는 않았는가.**\n'
      + 'D. **선지별 함정이 진짜인가.** misconceptions 에 적힌 실수를 실제로 저질러 계산하면\n'
      + '   그 보기 값이 나오는가. 안 나오면 [함정허구] 다. 오답 전부가 채워져 있는가.\n'
      + 'E. **근거 없는 단정이 없는가.** 「일반적으로」「보통」 으로 넘어간 자리가 있으면\n'
      + '   그것이 이 문항에서 실제로 성립하는지 따져라.\n'
      + 'F. **모든 문장이 「~다.」로 끝나는 평서체인가.** 반말·해요체·청유형이 섞였으면 [말투] 다.\n\n'
      + '문제가 하나도 없으면 verdict 를 "clean" 으로 반환한다.\n'
      + '있으면 문항 번호와 무엇이 왜 틀렸는지, **어떻게 고쳐야 하는지**를 구체적으로 적는다.\n'
      + '확신이 없으면 문제로 신고한다 — 놓치는 쪽이 더 나쁘다.'
    return agent(p, { label: '검증:' + key, phase: '검증', effort: 'high', schema: S_VERDICT })
  },

  function (report, key) {
    if (!report || report.verdict === 'clean' || !report.problems || !report.problems.length) {
      return { key: key, note: 'clean' }
    }
    const lines = report.problems.map(x => '- ' + x.q + '번 [' + x.kind + '] ' + x.what + '\n  고칠 방향: ' + x.fix).join('\n')
    const p = '증보된 해설에서 검토자가 아래 문제들을 찾았다. **고쳐 써라.**\n\n'
      + '증보본: `' + OUT + '/' + key + '.json`\n'
      + '원본: `' + SRC + '/' + key + '.json` (각 문항의 `_크롭` 이 원본 그림, 뿌리는 `/home/user/exam`)\n\n'
      + lines + '\n\n'
      + '각 지적을 먼저 **네가 직접 확인**해라 — 크롭을 열어 보고, 계산을 다시 해 봐라.\n'
      + '검토자가 틀렸을 수도 있다. 확인해 보고 검토자가 틀렸다면 고치지 말고 그 사실을\n'
      + '반환값에 적어라.\n\n'
      + '정말 틀린 것은 고친다. 고칠 때는 해설 전체를 다시 성립하게 만들어라 —\n'
      + '숫자 하나만 바꿔 놓고 뒷 문장이 옛 숫자를 가리키게 두지 않는다.\n\n'
      + RULES + '\n\n'
      + '고친 뒤 파일을 다시 읽어 JSON 이 유효한지 확인해라.'
    return agent(p, { label: '수리:' + key, phase: '수리', effort: 'high', schema: S_FIX })
      .then(r => Object.assign({ key: key }, r || { fixed: 0, remaining: -1, note: '수리 실패' }))
  },
)

const rows = results.filter(Boolean)
log('덩어리 ' + rows.length + '/' + KEYS.length + ' 완료')
return {
  done: rows.length,
  asked: KEYS.length,
  clean: rows.filter(r => r.note === 'clean').length,
  repaired: rows.filter(r => r.note !== 'clean'),
}
