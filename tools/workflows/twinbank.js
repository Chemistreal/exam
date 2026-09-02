export const meta = {
  name: 'twin-banks-batch',
  description: '동형문제 은행을 집필하고 적대적으로 검증한다 (이미 집필된 덩어리는 검증만)',
  phases: [
    { title: '집필', detail: '원문 10문항을 읽고 같은 개념의 새 문항 10개를 쓴다' },
    { title: '검증', detail: '집필한 문항을 처음부터 다시 풀어 정답·선지·오개념을 반박한다' },
    { title: '수리', detail: '반박된 문항만 고쳐 쓴다' },
  ],
}

const SRC = '/tmp/claude-0/-home-user-study64-report/2113474c-4485-592e-912d-e7d09ec51ec8/scratchpad/twinsrc'
const OUT = '/home/user/exam/donghyung/_wip'
const DONE = (args && args.done) || []
const TODO = (args && args.todo) || []
const ALL = DONE.map(k => ({ key: k, authored: true })).concat(TODO.map(k => ({ key: k, authored: false })))

const S_WRITE = {
  type: 'object', additionalProperties: false, required: ['written', 'notes'],
  properties: { written: { type: 'integer' }, notes: { type: 'string' } },
}
const S_PROBLEM = {
  type: 'object', additionalProperties: false,
  required: ['q', 'kind', 'what', 'fix'],
  properties: {
    q: { type: 'string' },
    kind: { type: 'string', enum: ['정답오류', '복수정답', '정답없음', '함정허구', '오답누락', '화학오류', '개념불일치', '개념이름', '복제', '기타'] },
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

const RULES = [
  '집필 규칙 — 반드시 지킨다.',
  '',
  '1. **같은 개념, 같은 사고과정, 다른 문제.** 원문의 숫자·물질·맥락을 바꾼 새 문항이다.',
  '   원문을 베끼지 않는다. 원문과 답이 같은 번호가 되도록 맞추지도 않는다.',
  '2. **정답 번호를 골고루.** 한 덩어리 10문항의 정답이 한 번호에 몰리지 않게 한다.',
  '3. **오답 세 개 모두 진짜 함정이어야 한다.** 각 오답은 학생이 실제로 저지르는 특정한',
  '   실수의 결과여야 하고, misconceptions 에 그 실수를 적는다.',
  '   (예: 「계수비 2:3 을 1:1 로 보고 계산한 값」, 「질량수에서 원자번호를 빼지 않은 값」)',
  '4. **정답은 하나뿐이어야 한다.** 보기 넷을 각각 검토해 둘 이상 맞는 일이 없게 한다.',
  '5. **화학이 맞아야 한다.** 원자량·상수는 문항 안에 밝혀 준다. 계산은 직접 끝까지 해 보고',
  '   explanation 에 그 계산을 그대로 적는다. 어림하지 않는다.',
  '6. **난도는 원문과 같게.** 원문이 한 줄 계산이면 한 줄, 다단계면 다단계로.',
  '7. **그림이 있어야만 풀리는 문항은 만들지 않는다.** 표는 텍스트로 그린다.',
  '8. **misconceptions 는 오답 번호만** 담는다. 오답 세 개 전부 채운다.',
  '9. **concept 는 원문의 것을 그대로 쓴다. 띄어쓰기도 바꾸지 않는다.**',
  '   은행 색인이 이름으로 같은 개념을 찾으므로, 「한계반응물」을 「한계 반응물」로 바꾸면',
  '   같은 개념이 두 이름으로 갈라져 앉아 서로를 못 본다. 다만 원문의 concept 가 개념이',
  '   아니라 소재·대상 이름이면(「납」「원자」「비율」「표기법」「면적」「종합비교」)',
  '   진짜 개념 이름으로 바꿔 쓴다(「납」 → 「중성자수」).',
  '10. **평서체로 쓴다 — 모든 문장이 「~다.」로 끝난다.** 반말(「~어긋나.」)이나',
  '    해요체(「~어긋나요.」), 청유형(「~해 보자.」)으로 쓰지 않는다.',
  '11. 한국어. 고등학교 화학/화학올림피아드 수준.',
].join('\n')

const SHAPE = [
  '{',
  '  "<원문 문항번호>": {',
  '    "concept": "<위 9번 규칙대로>",',
  '    "area": "<원문의 area 그대로>",',
  '    "learningPoint": "<이 문항으로 확인하는 것 한 마디>",',
  '    "origin": "authored",',
  '    "stem": "<새 문항의 지문. 줄바꿈은 \\\\n. 첨자는 유니코드(H₂O, Al₂O₃, ¹²C, Ca²⁺)>",',
  '    "choices": ["<보기1>", "<보기2>", "<보기3>", "<보기4>"],',
  '    "answer": <1~4 정수>,',
  '    "explanation": "<단계별 풀이. 계산·근거를 다 보인다>",',
  '    "misconception": "<이 개념에서 흔한 실수 한 문장>",',
  '    "misconceptions": { "<오답 번호>": "<그 번호를 고르게 만드는 구체적인 오류>" },',
  '    "verified": true',
  '  }',
  '}',
].join('\n')

phase('집필')

const results = await pipeline(
  ALL,

  function (it) {
    if (it.authored) return { key: it.key, written: -1, notes: '이미 집필돼 있음 — 검증부터' }
    const key = it.key
    const j0hint = key.indexOf('j0__') === 0
      ? '이 덩어리는 원문 지문이 없다. 대신 `' + SRC + '/j0q/blk-*.txt` 에 원문 시험의 상세\n'
        + '해설이 문항별로 잘려 있다. 「문제 N ·」 대목에 그 문항의 문제 요약·정답·판단 과정·\n'
        + '선지별 분석·핵심 오개념이 있다. 그것을 읽고 같은 개념의 새 문항을 집필한다.\n\n'
      : ''
    const p = '동형문제를 집필한다.\n\n'
      + '원문 문항이 `' + SRC + '/' + key + '.json` 에 있다. 먼저 그 파일을 통째로 읽어라.\n\n'
      + RULES + '\n\n' + j0hint
      + '완성하면 `' + OUT + '/' + key + '.json` 에 아래 모양 그대로 JSON 을 써라(파일 전체가 questions 맵 하나).\n\n'
      + SHAPE + '\n\n'
      + '문항 번호 키는 원문 파일의 questions 키와 정확히 같아야 한다 — 열 개 전부.\n'
      + '파일을 쓴 뒤 다시 읽어 JSON 이 유효하고 키가 열 개인지 확인해라.'
    return agent(p, { label: '집필:' + key, phase: '집필', schema: S_WRITE })
      .then(r => Object.assign({ key: key }, r || { written: 0, notes: '집필 실패' }))
  },

  function (_r, it) {
    const p = '집필된 동형문제를 **반박한다**. 통과시키는 것이 아니라 틀린 것을 찾는 것이 목적이다.\n\n'
      + '원문: `' + SRC + '/' + it.key + '.json`\n'
      + '집필본: `' + OUT + '/' + it.key + '.json`\n\n'
      + '집필본의 열 문항을 하나씩, **집필자의 해설을 믿지 말고 처음부터 직접 풀어라.**\n'
      + '그런 다음 일곱 가지를 따진다.\n\n'
      + 'A. **정답이 맞나.** 네가 푼 답과 answer 가 다르면 문제다.\n'
      + 'B. **정답이 하나뿐인가.** 보기 넷을 각각 판정해서 둘 이상 맞으면 문제다. 다 틀려도 문제다.\n'
      + 'C. **오답이 진짜 함정인가.** misconceptions 에 적힌 실수를 실제로 저질러 보면 그 보기 숫자가\n'
      + '   나오는가. 안 나오면 지어낸 설명이다. 오답 세 개가 다 채워져 있는가.\n'
      + 'D. **화학이 맞나.** 원자량·상수·단위·유효숫자, 반응식 균형, 주기성 서술, 평형·산염기·\n'
      + '   산화환원의 방향이 맞는가. 푸는 데 필요한 값이 지문에 다 주어져 있는가.\n'
      + 'E. **원문과 같은 개념을 묻는가, 그리고 원문의 복제가 아닌가.**\n'
      + '   원문의 정답이 지문에 그대로 적혀 있지는 않은가. 옆 문항의 정답을 흘리지 않는가.\n'
      + 'F. **concept 가 원문의 것과 글자까지 같은가.** 원문이 「한계반응물」인데 「한계 반응물」로\n'
      + '   띄어 썼다면 문제다 — 은행 색인이 이름으로 찾으므로 같은 개념이 두 이름으로 갈라진다.\n'
      + '   (원문 concept 가 「납」「원자」「비율」처럼 개념이 아닌 딱지였다면 바꾼 것이 맞다.)\n'
      + 'G. **모든 문장이 「~다.」로 끝나는 평서체인가.**\n\n'
      + '문제가 하나도 없으면 verdict 를 "clean" 으로 반환한다.\n'
      + '있으면 문항 번호와 무엇이 왜 틀렸는지, 그리고 **어떻게 고쳐야 하는지**를 구체적으로 적는다.\n'
      + '확신이 없으면 문제로 신고한다 — 놓치는 쪽이 더 나쁘다.'
    return agent(p, { label: '검증:' + it.key, phase: '검증', effort: 'high', schema: S_VERDICT })
  },

  function (report, it) {
    if (!report || report.verdict === 'clean' || !report.problems || !report.problems.length) {
      return { key: it.key, note: 'clean' }
    }
    const lines = report.problems.map(x => '- ' + x.q + '번 [' + x.kind + '] ' + x.what + '\n  고칠 방향: ' + x.fix).join('\n')
    const p = '집필된 동형문제에서 검토자가 아래 문제들을 찾았다. **고쳐 써라.**\n\n'
      + '파일: `' + OUT + '/' + it.key + '.json`\n'
      + '원문: `' + SRC + '/' + it.key + '.json`\n\n'
      + lines + '\n\n'
      + '각 지적을 먼저 **네가 직접 확인**해라. 검토자가 틀렸을 수도 있다 — 확인해 보고 검토자가\n'
      + '틀렸다면 고치지 말고 그 사실을 반환값에 적어라.\n\n'
      + '정말 틀린 것은 고친다. 고칠 때는 문항 전체를 다시 성립하게 만들어라 —\n'
      + '숫자 하나만 바꿔 놓고 해설·오개념이 옛 숫자를 가리키게 두지 않는다.\n'
      + '정답 번호를 바꿨으면 misconceptions 의 키도 새 오답 번호들로 맞춘다.\n\n'
      + RULES + '\n\n'
      + '고친 뒤 파일을 다시 읽어 JSON 이 유효하고 문항 키가 원문과 같은 열 개인지 확인해라.'
    return agent(p, { label: '수리:' + it.key, phase: '수리', schema: S_FIX })
      .then(r => Object.assign({ key: it.key }, r || { fixed: 0, remaining: -1, note: '수리 실패' }))
  },
)

const rows = results.filter(Boolean)
log('덩어리 ' + rows.length + '/' + ALL.length + ' 완료')
return {
  done: rows.length,
  asked: ALL.length,
  clean: rows.filter(r => r.note === 'clean').length,
  repaired: rows.filter(r => r.note !== 'clean'),
}
