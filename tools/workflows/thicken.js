export const meta = {
  name: 'thin-explanations',
  description: '정답률이 낮은데 해설이 얇은 문항의 해설을 증보하고 적대적으로 검증한다',
  phases: [
    { title: '증보', detail: '크롭에서 지문을 읽고 해설·오개념·선지별 함정을 다시 쓴다' },
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
].join('\n')

const RULES = [
  '증보 규칙 — 반드시 지킨다.',
  '',
  '1. **지문을 먼저 읽어라.** 각 문항의 `_크롭` 이 원본 문제지 그림이다(저장소 상대 경로,',
  '   예: `/home/user/exam/crops/donghyung-4/54.png`). Read 로 그림을 열어 지문과 보기를',
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
  '6. **없는 것을 지어내지 않는다.** 크롭이 흐려서 못 읽는 대목이 있으면 그 문항은',
  '   건드리지 말고 `notes` 에 「N번 크롭을 못 읽었다」고 적어라. 추측으로 채우지 않는다.',
  '7. **평서체로 쓴다 — 모든 문장이 「~다.」로 끝난다.** 반말(「~어긋나.」)이나',
  '   해요체(「~어긋나요.」), 청유형(「~해 보자.」)으로 쓰지 않는다. 학생에게 말을 거는',
  '   투로 쓰지 않는다 — 이 글은 인쇄되어 학부모도 읽는다.',
  '8. **concept·area 는 글자까지 그대로 둔다.** 은행 색인이 이름으로 같은 개념을 찾는다.',
  '9. 한국어. 고등학교 화학/화학올림피아드 수준. 첨자는 유니코드(H₂O, Ca²⁺, ¹²C, E°).',
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

phase('증보')

const results = await pipeline(
  KEYS,

  function (key) {
    const p = '정답률이 낮은데 해설이 얇은 문항의 해설을 증보한다.\n\n' + WHY + '\n\n'
      + '문항이 `' + SRC + '/' + key + '.json` 에 있다. 먼저 그 파일을 통째로 읽어라.\n'
      + '각 문항의 `_크롭` 이 원본 그림 경로다 — **저장소 뿌리는 `/home/user/exam` 이다.**\n\n'
      + RULES + '\n\n'
      + '완성하면 `' + OUT + '/' + key + '.json` 에 아래 모양 그대로 JSON 을 써라.\n'
      + '**바꾸는 칸만 담는다** — stem·choices·answer·concept·area 는 담지 않는다.\n\n'
      + SHAPE + '\n\n'
      + '문항 번호 키는 원본 파일의 questions 키와 정확히 같아야 한다(크롭을 못 읽어\n'
      + '건드리지 않기로 한 문항은 빼고, 그 사실을 notes 에 적는다).\n'
      + '파일을 쓴 뒤 다시 읽어 JSON 이 유효한지 확인해라.'
    return agent(p, { label: '증보:' + key, phase: '증보', effort: 'high', schema: S_WRITE })
      .then(r => Object.assign({ key: key }, r || { written: 0, notes: '증보 실패' }))
  },

  function (_r, key) {
    const p = '증보된 해설을 **반박한다**. 통과시키는 것이 아니라 틀린 것을 찾는 것이 목적이다.\n\n'
      + '원본(지문·보기·정답·옛 해설): `' + SRC + '/' + key + '.json`\n'
      + '증보본: `' + OUT + '/' + key + '.json`\n\n'
      + '⚠ **크롭 그림을 네가 직접 열어 읽어라.** 원본 파일의 `_크롭` 경로를 Read 로 연다\n'
      + '(저장소 뿌리는 `/home/user/exam`). 지문을 안 보고는 해설이 맞는지 알 수 없다.\n\n'
      + '문항마다 **증보자의 글을 믿지 말고 그림을 보고 처음부터 직접 풀어라.** 그런 다음 따진다.\n\n'
      + 'A. **해설이 낸 답이 정답 키와 같은가.** 다르면 문제다.\n'
      + 'B. **해설의 계산이 맞나.** 중간값을 하나씩 다시 계산해 봐라. 단위·유효숫자·부호,\n'
      + '   반응식 균형, 상수 값이 맞는가.\n'
      + 'C. **해설이 지문을 제대로 읽었나.** 그림에 있는 조건을 빠뜨렸거나, 그림에 없는\n'
      + '   조건을 지어내지는 않았는가. 판단형이면 보기 넷을 다 판정했는가.\n'
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
