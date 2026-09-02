export const meta = {
  name: 'twin-dedupe',
  description: '회차를 넘나들며 겹친 동형문제를 다시 집필하고 적대적으로 검증한다',
  phases: [
    { title: '재집필', detail: '같은 개념을 다른 각도로 묻는 새 문항으로 갈아 쓴다' },
    { title: '검증', detail: '처음부터 다시 풀어 정답·선지·오개념을 반박하고, 겹침이 정말 사라졌는지 본다' },
    { title: '수리', detail: '반박된 문항만 고쳐 쓴다' },
  ],
}

const JOBS = (args && args.jobs) || []

const S_WRITE = {
  type: 'object', additionalProperties: false, required: ['ok', 'notes'],
  properties: { ok: { type: 'boolean' }, notes: { type: 'string' } },
}
const S_PROBLEM = {
  type: 'object', additionalProperties: false,
  required: ['kind', 'what', 'fix'],
  properties: {
    kind: { type: 'string', enum: ['정답오류', '복수정답', '정답없음', '함정허구', '오답누락', '화학오류', '개념불일치', '개념이름', '겹침잔존', '난도이탈', '기타'] },
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
  '왜 고치나',
  '',
  'kch1u1 · kch1to2 · kch1to2-b · kch1to3 · kch1to3-b 는 **같은 학생이 차례로 보는**',
  '진도별 시험이다. 그래서 개념이 겹치는 것은 당연하고, 겹쳐야 맞다.',
  '겹치면 안 되는 것은 **문항**이다. 앞 회차에서 이미 본 것과 거의 같은 동형문제가',
  '뒤 회차 오답노트에 다시 뜨면, 학생은 개념을 다시 세우는 대신 답을 기억해 낸다.',
  '그 순간 동형문제는 약점을 고치는 도구가 아니라 기억력 시험이 된다.',
].join('\n')

const RULES = [
  '집필 규칙 — 반드시 지킨다.',
  '',
  '1. **같은 개념, 다른 각도.** concept 와 area 는 그대로 두고, 묻는 방식을 바꾼다.',
  '   숫자만 바꾸는 것은 안 된다 — 그러면 겹침이 그대로 남는다.',
  '   (예: 「반지름이 가장 큰 것은?」 → 「반지름 순서로 옳게 배열한 것은?」,',
  '    「완전 연소했을 때 CO₂ 질량은?」 → 「생성된 CO₂ 질량으로부터 처음 시료의 화학식을 구하면?」)',
  '2. **정답은 하나뿐이어야 한다.** 보기 넷을 각각 검토해 둘 이상 맞는 일이 없게 한다.',
  '3. **오답 세 개 모두 진짜 함정이어야 한다.** 각 오답은 학생이 실제로 저지르는 특정한',
  '   실수의 결과여야 하고, misconceptions 에 그 실수를 적는다. 그 실수를 실제로 저질러',
  '   계산해 보면 그 보기 값이 나와야 한다.',
  '4. **화학이 맞아야 한다.** 원자량·상수는 문항 안에 밝혀 준다. 계산은 끝까지 직접 해 보고',
  '   explanation 에 그 계산을 그대로 적는다. 어림하지 않는다.',
  '5. **난도는 지금 문항과 같게.** 쉬워지거나 어려워지면 그 회차의 균형이 깨진다.',
  '6. **그림이 있어야만 풀리는 문항은 만들지 않는다.** 표는 텍스트로 그린다.',
  '7. **misconceptions 는 오답 번호만** 담는다. 오답 세 개 전부 채운다.',
  '8. **concept 와 area 는 글자까지 그대로 둔다.** 은행 색인이 이름으로 같은 개념을 찾으므로,',
  '   띄어쓰기 하나만 바뀌어도 같은 개념이 두 이름으로 갈라져 서로를 못 본다.',
  '9. **평서체로 쓴다 — 모든 문장이 「~다.」로 끝난다.** 반말·해요체·청유형으로 쓰지 않는다.',
  '10. 한국어. 고등학교 화학/화학올림피아드 수준.',
].join('\n')

const SHAPE = [
  '해당 문항 하나의 값만 통째로 갈아 끼운다. 다른 문항은 건드리지 않는다.',
  '',
  '{',
  '  "concept": "<그대로>",',
  '  "area": "<그대로>",',
  '  "learningPoint": "<이 문항으로 확인하는 것 한 마디>",',
  '  "origin": "authored",',
  '  "stem": "<새 문항의 지문. 줄바꿈은 \\\\n. 첨자는 유니코드(H₂O, Al₂O₃, ¹²C, Ca²⁺)>",',
  '  "choices": ["<보기1>", "<보기2>", "<보기3>", "<보기4>"],',
  '  "answer": <1~4 정수>,',
  '  "explanation": "<단계별 풀이. 계산·근거를 다 보인다>",',
  '  "misconception": "<이 개념에서 흔한 실수 한 문장>",',
  '  "misconceptions": { "<오답 번호>": "<그 번호를 고르게 만드는 구체적인 오류>" },',
  '  "verified": true',
  '}',
].join('\n')

function pathOf(job) { return '/home/user/exam/donghyung/' + job.exam + '.json' }

function facts(job) {
  return [
    '지금 문항 (' + job.exam + ' ' + job.no + '번) — 이것을 갈아 쓴다',
    '  지문: ' + String(job.mine.stem).replace(/\n/g, ' / '),
    '  보기: ' + job.mine.choices.join(' | '),
    '  정답: ' + job.mine.answer + '번',
    '  concept: ' + job.mine.concept + ' · area: ' + job.mine.area,
    '',
    '겹치는 상대 (' + job.other.exam + ' ' + job.other.no + '번, 지문 3-그램 유사도 ' + job.sim + ')',
    '  지문: ' + String(job.other.q.stem).replace(/\n/g, ' / '),
    '  보기: ' + job.other.q.choices.join(' | '),
    '  정답: ' + job.other.q.answer + '번',
    '',
    '⚠ 상대 문항은 이미 배포되어 학생들이 풀었다. **상대는 절대 건드리지 않는다.**',
    '  고치는 것은 ' + job.exam + ' ' + job.no + '번 하나뿐이다.',
  ].join('\n')
}

phase('재집필')

const results = await pipeline(
  JOBS,

  function (job) {
    const p = '겹친 동형문제를 다시 집필한다.\n\n' + WHY + '\n\n' + facts(job) + '\n\n' + RULES + '\n\n'
      + '은행 파일 `' + pathOf(job) + '` 의 questions["' + job.no + '"] 를 새 문항으로 통째로 갈아 끼워라.\n'
      + '먼저 그 파일을 읽어 지금 값과 이웃 문항들을 확인해라 — **같은 회차 안의 다른 문항과도**\n'
      + '겹치면 안 된다.\n\n' + SHAPE + '\n\n'
      + '쓴 뒤 파일을 다시 읽어 JSON 이 유효하고 문항 수가 그대로 60개인지 확인해라.'
    return agent(p, { label: '재집필:' + job.key, phase: '재집필', effort: 'high', schema: S_WRITE })
      .then(r => Object.assign({ key: job.key }, r || { ok: false, notes: '집필 실패' }))
  },

  function (_r, job) {
    const p = '다시 집필된 동형문제를 **반박한다**. 통과시키는 것이 아니라 틀린 것을 찾는 것이 목적이다.\n\n'
      + '파일: `' + pathOf(job) + '` 의 questions["' + job.no + '"]\n\n'
      + facts(job) + '\n\n'
      + '(위의 「지금 문항」은 **고치기 전**의 모습이다. 파일에는 이미 새 문항이 들어가 있다.)\n\n'
      + '새 문항을 **집필자의 해설을 믿지 말고 처음부터 직접 풀어라.** 그런 다음 따진다.\n\n'
      + 'A. **정답이 맞나.** 네가 푼 답과 answer 가 다르면 문제다.\n'
      + 'B. **정답이 하나뿐인가.** 보기 넷을 각각 판정해서 둘 이상 맞으면 문제다. 다 틀려도 문제다.\n'
      + 'C. **오답이 진짜 함정인가.** misconceptions 에 적힌 실수를 실제로 저질러 보면 그 보기 값이\n'
      + '   나오는가. 안 나오면 지어낸 설명이다. 오답 세 개가 다 채워져 있는가.\n'
      + 'D. **화학이 맞나.** 원자량·상수·단위, 반응식 균형, 주기성 서술의 방향이 맞는가.\n'
      + '   푸는 데 필요한 값이 지문에 다 주어져 있는가.\n'
      + 'E. **겹침이 정말 사라졌나.** 위의 상대 문항과 나란히 놓고 읽어라. 묻는 각도가 정말\n'
      + '   달라졌는가, 아니면 숫자와 물질만 바뀌고 같은 질문인가. 후자면 [겹침잔존] 이다.\n'
      + '   같은 회차 안의 다른 59문항과도 겹치지 않는지 파일을 읽어 확인해라.\n'
      + 'F. **concept·area 가 고치기 전과 글자까지 같은가.**\n'
      + 'G. **난도가 고치기 전과 같은가.** 한 줄 계산이 세 단계가 되었거나 그 반대면 문제다.\n'
      + 'H. **모든 문장이 「~다.」로 끝나는 평서체인가.**\n\n'
      + '문제가 하나도 없으면 verdict 를 "clean" 으로 반환한다.\n'
      + '있으면 무엇이 왜 틀렸는지, 그리고 **어떻게 고쳐야 하는지**를 구체적으로 적는다.\n'
      + '확신이 없으면 문제로 신고한다 — 놓치는 쪽이 더 나쁘다.'
    return agent(p, { label: '검증:' + job.key, phase: '검증', effort: 'high', schema: S_VERDICT })
  },

  function (report, job) {
    if (!report || report.verdict === 'clean' || !report.problems || !report.problems.length) {
      return { key: job.key, note: 'clean' }
    }
    const lines = report.problems.map(x => '- [' + x.kind + '] ' + x.what + '\n  고칠 방향: ' + x.fix).join('\n')
    const p = '다시 집필된 동형문제에서 검토자가 아래 문제들을 찾았다. **고쳐 써라.**\n\n'
      + '파일: `' + pathOf(job) + '` 의 questions["' + job.no + '"]\n\n'
      + facts(job) + '\n\n' + lines + '\n\n'
      + '각 지적을 먼저 **네가 직접 확인**해라. 검토자가 틀렸을 수도 있다 — 확인해 보고 검토자가\n'
      + '틀렸다면 고치지 말고 그 사실을 반환값에 적어라.\n\n'
      + '정말 틀린 것은 고친다. 고칠 때는 문항 전체를 다시 성립하게 만들어라 —\n'
      + '숫자 하나만 바꿔 놓고 해설·오개념이 옛 숫자를 가리키게 두지 않는다.\n'
      + '정답 번호를 바꿨으면 misconceptions 의 키도 새 오답 번호들로 맞춘다.\n\n'
      + RULES + '\n\n'
      + '고친 뒤 파일을 다시 읽어 JSON 이 유효하고 문항 수가 60개인지 확인해라.'
    return agent(p, { label: '수리:' + job.key, phase: '수리', effort: 'high', schema: S_FIX })
      .then(r => Object.assign({ key: job.key }, r || { fixed: 0, remaining: -1, note: '수리 실패' }))
  },
)

const rows = results.filter(Boolean)
log('겹친 문항 ' + rows.length + '/' + JOBS.length + ' 처리')
return {
  done: rows.length,
  asked: JOBS.length,
  clean: rows.filter(r => r.note === 'clean').length,
  repaired: rows.filter(r => r.note !== 'clean'),
}
