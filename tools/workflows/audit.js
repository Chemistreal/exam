export const meta = {
  name: 'unfinished-audit',
  description: '두 저장소에서 «하려다 만 것»을 여러 각도로 찾아내고 적대적으로 검증한다',
  phases: [
    { title: '훑기', detail: '열 가지 다른 각도로 미완·불일치·빈 자리를 찾는다' },
    { title: '반박', detail: '찾은 것마다 세 관점으로 «정말 미완인가»를 반박한다' },
    { title: '빠진 것', detail: '무엇을 못 봤는지 되묻는다' },
  ],
}

const EXAM = '/home/user/exam'
const DT = '/home/user/dt'
const MSGS = (args && args.usermsgs) || ''

const S_FINDINGS = {
  type: 'object', additionalProperties: false, required: ['findings', 'notes'],
  properties: {
    notes: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['what', 'where', 'evidence', 'kind', 'weight'],
        properties: {
          what: { type: 'string' },
          where: { type: 'string' },
          evidence: { type: 'string' },
          kind: { type: 'string', enum: ['빈자리', '불일치', '거짓말', '미배선', '검사구멍', '요청미이행', '선생님대기', '기타'] },
          weight: { type: 'string', enum: ['학생에게보임', '선생님에게보임', '안쪽만'] },
        },
      },
    },
  },
}

const S_VERDICT = {
  type: 'object', additionalProperties: false, required: ['real', 'why'],
  properties: {
    real: { type: 'boolean' },
    why: { type: 'string' },
    correction: { type: 'string' },
  },
}

const GROUND = [
  '두 저장소가 있다.',
  '  ' + EXAM + '  — 파이널·기출 성적표(chemistreal.github.io/exam). 답지 answers/, 동형문제',
  '     은행 donghyung/, 개념강의 lec-*.html 125편, 성적표 final.html, 통합 셸 hub.html.',
  '  ' + DT + '  — 주간 누적 OX 시험(chemistreal.github.io/DT). 성적표 report.html,',
  '     회차 자료 appdata/round_*.json, 서버 apps-script.gs.',
  '',
  '**이미 끝난 것으로 아는 것** (다시 찾아 보고할 필요 없다):',
  '  · 얇은 해설 증보 240문항 (정답률 50% 미만 + 해설 150자 미만 → 0개 남음)',
  '  · DT 오개념→개념강의 배선 718/792종 (못 이은 74종은 까닭이 적혀 있다)',
  '  · 공개 저장소 학생 실명 제거 + tools/name_guard.py 가드',
  '  · kch1to3·kch1to3-b 동형문제 은행 120문항',
  '',
  '**이미 알고 있는 빈 자리** (다시 찾을 필요 없다. 더 깊은 것을 찾아라):',
  '  · 선지별 오답 해설이 3,213/4,080 문항에 없다',
  '  · 동형문제 은행이 없는 회차 넷 — chem2-1 · kch2to3 · kch2final · j0',
  '  · lec-116 에 확인 문제가 0개',
  '  · answers/*.json 의 reviewNote 47개가 선생님 판단을 기다린다',
  '',
  '⚠ **이 저장소는 공개이고 학생은 미성년자다.** 어떤 보고서에도 실제 학생 이름을',
  '  적지 마라. 이름을 발견하면 그 자체가 결함이니 이름 없이 위치만 적어라.',
].join('\n')

const ASK = [
  '',
  '무엇이 «하려다 만 것» 인가',
  '',
  '  · **빈자리** — 자리는 만들어 두고 안 채운 것(빈 배열·빈 표·「준비 중」·자리표시자).',
  '  · **불일치** — 만들어 내는 자(생성기)와 만들어진 것이 어긋난 것. 원본을 고쳤는데',
  '    파생물을 다시 안 만든 자리.',
  '  · **거짓말** — 화면이나 문서가 사실과 다른 말을 하는 것. 「전부」라고 적었는데',
  '    일부인 자리, 「없다」고 적었는데 있는 자리.',
  '  · **미배선** — 지어 놓고 화면에서 못 가는 것. 파일은 있는데 링크가 없는 자리.',
  '  · **검사구멍** — 검사는 있는데 CI 에 안 걸린 것, 실패해도 경고로만 넘기는 것,',
  '    꺼져 있는 검사.',
  '  · **요청미이행** — 사람이 시켰는데 아직 안 한 것.',
  '  · **선생님대기** — 사람이 자료를 줘야 진행되는 것(원본 그림·명단·판단).',
  '',
  '무엇이 «하려다 만 것» 이 **아닌가**',
  '',
  '  · 일부러 비워 둔 자리. 까닭이 적혀 있으면 미완이 아니다.',
  '  · 앞으로 하면 좋을 새 기능. 이 감사는 **시작해 놓고 안 끝낸 것**을 찾는다.',
  '  · 취향 문제. 「이렇게 하면 더 좋겠다」는 결함이 아니다.',
  '',
  '어떻게 찾나',
  '',
  '  파일을 **실제로 열어 읽어라.** grep 으로 후보를 좁히고, 그 자리를 읽고,',
  '  가능하면 도구를 직접 돌려 봐라(`python3 tools/<이름>.py --check`).',
  '  증거(evidence)에는 **파일:줄** 과 **본 것 그대로**를 적어라. 짐작은 적지 마라.',
  '  찾은 것이 없으면 findings 를 빈 배열로 두고 notes 에 무엇을 어떻게 봤는지 적어라.',
].join('\n')

const LENSES = [
  {
    key: '표시자',
    p: '두 저장소에서 **사람이 남긴 미완 표시**를 전수로 훑어라.\n'
      + 'TODO · FIXME · XXX · HACK · 아직 · 나중에 · 준비 중 · 임시 · 미완 · 추후 ·\n'
      + '「일단」 · 「우선」 · 「다음에」 · placeholder · WIP · stub 같은 말을 찾아라.\n'
      + '주석·문서·화면 글월을 모두 본다. 각 자리를 열어 읽고, **정말 안 끝난 것**인지\n'
      + '아니면 이미 끝났는데 표시만 남은 것인지 가려라.',
  },
  {
    key: '빈그릇',
    p: '**자리는 만들어 두고 안 채운 그릇**을 찾아라.\n'
      + 'JSON·JS 안의 빈 배열 `[]`·빈 객체 `{}`·빈 글자열이 「아직 없음」을 뜻하는 자리,\n'
      + '길이 0 인 표, 「없습니다」로만 그려지는 화면, 0 건으로 세어지는 목록.\n'
      + '특히 `answers/`·`appdata/`·`cohort/` 의 자료 구조와 `final.html`·`report.html`·\n'
      + '`hub.html` 안의 상수 표를 보아라(donghyung/ 의 빈 은행 넷은 이미 안다).\n'
      + '빈 것이 **일부러 비운 것**인지(까닭이 적혀 있는가) **아직 안 채운 것**인지 가려라.',
  },
  {
    key: '생성기',
    p: '**만들어 내는 자와 만들어진 것이 어긋난 자리**를 찾아라.\n'
      + '두 저장소의 `tools/*.py` 를 훑어 `--check` 를 받는 것을 모두 찾고, **직접 돌려라**\n'
      + '(`cd ' + EXAM + ' && python3 tools/<이름>.py --check`, DT 도 같다).\n'
      + '빨간불이 나는 것이 곧 어긋난 자리다. 어떤 검사가 있는지, 무엇이 실패하는지,\n'
      + '실패가 무슨 뜻인지 적어라. 검사가 없는 생성기도 적어라 — 그것은 어긋나도 모른다.',
  },
  {
    key: 'CI',
    p: '**검사가 있는데 안 걸린 자리**를 찾아라.\n'
      + '두 저장소의 `.github/workflows/*.yml` 을 읽고, `tools/` 와 `tests/` 에 있는\n'
      + '검사 가운데 **CI 에 안 실린 것**을 목록으로 만들어라.\n'
      + '또 CI 안에서 `|| true`·`|| echo`·`continue-on-error`·`warning` 으로 **실패를**\n'
      + '**넘기는 자리**를 찾아라 — 그것은 있으나 마나 한 검사다.\n'
      + '건너뛰거나 주석 처리된 검사도 찾아라.',
  },
  {
    key: '문서대조',
    p: '**문서·화면이 사실과 다른 자리**를 찾아라.\n'
      + '두 저장소의 `README*`·`docs/`·`tools/INDEX.md`·`AUTODEPLOY.md` 와 화면의 안내\n'
      + '글월을 읽고, 거기 적힌 숫자·주장·「전부」·「모두」·「없다」를 **실제 저장소 상태와**\n'
      + '**대조**해라. 몇 편·몇 문항·몇 회차라고 적힌 곳이 지금도 맞는지 세어 봐라.\n'
      + 'DT 의 `tools/lie_check.py` 가 무엇을 재는지도 읽고, 그것이 못 잡는 종류를 찾아라.',
  },
  {
    key: '자산배선',
    p: '**지어 놓고 화면에서 못 가는 자리**를 찾아라.\n'
      + '두 저장소의 파일 가운데 어디에서도 링크되지 않는 것(고아)을 찾고, 반대로\n'
      + '코드가 가리키는데 **없는 파일**도 찾아라(깨진 링크).\n'
      + 'exam 의 `lec-*.html` 125편·`sol-final-*.html`·`crops/`, DT 의 `munje_*`·`haeseol_*`·\n'
      + '`omr_*`·PDF 들이 화면에서 실제로 닿는지 보아라.\n'
      + '`tools/page_doors.py`·`asset_doors.py`·`dead-link` 검사가 있으면 돌려 보아라.',
  },
  {
    key: '자료구멍',
    p: '**자료가 군데군데 빈 자리**를 세어라. 세는 코드를 직접 짜서 돌려라.\n'
      + 'exam: `answers/*.json` 문항 가운데 stem·choices·area·type·concept·acceptableAnswers\n'
      + '같은 칸이 없는 것이 몇 개인가. `exams.json` 의 회차 목록과 실제 파일이 맞는가.\n'
      + '`cohort/baseline.json` 의 회차·인원과 실제 응시 기록이 맞는가.\n'
      + 'DT: `appdata/` 와 화면이 아는 회차 수가 같은가. 서버가 아는 과목과 화면이 아는\n'
      + '과목이 같은가.\n'
      + '숫자를 세어 적고, 그 빈 자리가 화면에서 어떻게 보이는지도 확인해라.',
  },
  {
    key: '사람대기',
    p: '**사람이 자료를 줘야 진행되는 자리**를 찾아라(answers 의 reviewNote 47개는 이미 안다).\n'
      + '두 저장소의 **코드와 문서**에서 「선생님」·「확인 필요」·「받으면」·「주시면」·\n'
      + '「원본」·「한 번 실행」·「직접 넣어」 같은 말이 든 자리를 찾아 읽어라.\n'
      + '특히 **앱스크립트에서 사람이 한 번 눌러야 하는 함수**(트리거 등록·시트 초기화·\n'
      + '속성 설정)를 모두 찾아, 그것이 실제로 눌렸는지 알 방법이 있는지 보아라.\n'
      + '각각 **무엇을 기다리는지**와 **그것이 없으면 지금 화면이 어떻게 되는지**를 적어라.',
  },
  {
    key: '요청대조',
    p: '**사람이 시켰는데 아직 안 한 것**을 찾아라.\n'
      + '`' + MSGS + '` 에 이 프로젝트에서 사람이 보낸 말 212개가 시간순으로 있다.\n'
      + '(학생 이름은 ○○○ 로 가려 두었다.)\n'
      + '**전부 읽어라.** 그 가운데 «해 달라» 는 요청을 뽑고, 각각이 지금 저장소에\n'
      + '실제로 들어가 있는지 **파일을 열어 확인**해라.\n'
      + '오래된 요청일수록 잊히기 쉬우니 앞쪽(i 가 작은 것)을 특히 꼼꼼히 보아라.\n'
      + '이미 된 것은 적지 말고, **안 된 것과 반쯤 된 것**만 적어라.',
  },
  {
    key: '반쯤한것',
    p: '**시작해 놓고 절반에서 멈춘 자리**를 찾아라.\n'
      + '한 종류의 일을 여러 대상에 하다가 일부만 한 자리다 — 예를 들어 어떤 회차에는\n'
      + '있는데 다른 회차에는 없는 자료, 어떤 화면에는 붙었는데 다른 화면에는 안 붙은 기능,\n'
      + '어떤 문항에만 채워진 칸.\n'
      + '두 저장소의 같은 갈래 파일들을 **서로 견주어** 무엇이 어디에만 있는지 세어라.\n'
      + '(예: 회차 자료 · 성적표 절 · 문자 서식 · 검사 · 도구 · 화면마다 붙은 단추)',
  },
]

phase('훑기')

const rounds = await parallel(LENSES.map(L => () =>
  agent(GROUND + '\n\n' + L.p + '\n' + ASK, {
    label: '훑기:' + L.key, phase: '훑기', effort: 'high', schema: S_FINDINGS,
  }).then(r => ({ lens: L.key, r: r }))))

const all = []
rounds.filter(Boolean).forEach(x => {
  ((x.r && x.r.findings) || []).forEach(f => all.push(Object.assign({ lens: x.lens }, f)))
})

const seen = new Map()
all.forEach(f => {
  const k = (f.where || '').replace(/\s+/g, '').toLowerCase() + '|' + (f.what || '').slice(0, 40)
  if (!seen.has(k)) seen.set(k, f)
  else seen.get(k).lens += '·' + f.lens
})
const uniq = Array.from(seen.values())
log('훑기에서 ' + all.length + '건 · 같은 자리를 합쳐 ' + uniq.length + '건')

phase('반박')

const LENS3 = [
  ['사실', '이 주장이 **사실인가**. 적힌 파일과 줄을 네가 직접 열어 확인해라.\n'
         + '증거가 실제로 그 자리에 있는가. 숫자가 맞는가. 도구를 돌려야 하면 돌려라.\n'
         + '증거가 틀렸으면 real=false 다.'],
  ['의도', '이것이 **일부러 그렇게 둔 것**은 아닌가. 그 자리와 그 둘레의 주석·문서·\n'
         + '커밋 기록(`git log -S`)을 읽어라. 까닭이 적혀 있으면 미완이 아니라 판단이다.\n'
         + '(예: 「강의가 없는 개념은 비워 둔다」·「선생님이 정할 일이라 안 했다」)\n'
         + '일부러 둔 것이면 real=false 다.'],
  ['영향', '이것이 **지금 누군가에게 보이는가**. 학생 성적표·학부모 문자·선생님 화면\n'
         + '가운데 어디에 나타나는지, 아니면 안쪽에만 있는지 확인해라.\n'
         + '아무 화면에도 안 나타나고 앞으로도 안 나타날 것이면 real=false 다.\n'
         + '보인다면 **어디에 어떻게 보이는지** correction 에 적어라.'],
]

const judged = await parallel(uniq.map(f => () =>
  parallel(LENS3.map(([lens, ask]) => () =>
    agent('저장소 감사에서 아래를 「하려다 만 것」으로 신고했다. **' + lens + '** 관점에서 따져라.\n\n'
      + '  무엇: ' + f.what + '\n'
      + '  어디: ' + f.where + '\n'
      + '  증거: ' + f.evidence + '\n'
      + '  갈래: ' + f.kind + ' · 무게: ' + f.weight + '\n\n'
      + ask + '\n\n'
      + '저장소는 ' + EXAM + ' 와 ' + DT + ' 다.\n'
      + '**통과시키는 것이 목적이 아니라 틀린 신고를 걸러 내는 것이 목적이다.**\n'
      + '헷갈리면 real=false 로 두어라 — 없는 일을 있다고 하는 쪽이 더 나쁘다.',
      { label: '반박:' + lens + ':' + (f.where || '').slice(0, 24), phase: '반박', effort: 'high', schema: S_VERDICT })))
    .then(vs => {
      const ok = vs.filter(Boolean)
      const yes = ok.filter(v => v.real).length
      return Object.assign({}, f, {
        votes: ok.length, real: yes,
        why: ok.map((v, i) => LENS3[i][0] + ': ' + v.why).join(' / '),
        correction: ok.map(v => v.correction).filter(Boolean).join(' / '),
      })
    })))

const kept = judged.filter(Boolean).filter(x => x.votes >= 2 && x.real >= 2)
const dropped = judged.filter(Boolean).filter(x => !(x.votes >= 2 && x.real >= 2))
log('반박을 이겨 낸 것 ' + kept.length + '건 · 걸러진 것 ' + dropped.length + '건')

phase('빠진 것')

const gaps = await agent(
  GROUND + '\n\n'
  + '방금 열 가지 각도로 두 저장소를 훑어 「하려다 만 것」 ' + kept.length + '건을 확인했다.\n\n'
  + kept.map((f, i) => (i + 1) + '. [' + f.kind + '] ' + f.what + ' — ' + f.where).join('\n') + '\n\n'
  + '훑은 각도는 이랬다: ' + LENSES.map(l => l.key).join(' · ') + '.\n\n'
  + '**무엇을 못 봤는지 되물어라.**\n\n'
  + '  · 이 열 각도가 **구조적으로 놓치는 것**은 무엇인가.\n'
  + '  · 위 목록이 한 갈래에 몰려 있지는 않은가(예: 전부 exam 이고 DT 는 없다).\n'
  + '  · 두 저장소가 **서로 어긋난 자리**는 아무도 안 봤을 수 있다 — 한쪽이 다른 쪽의\n'
  + '    파일·이름·규칙을 가리키는 자리들을 대조해 봐라.\n'
  + '  · 사람이 자주 쓰는 길(채점 → 성적표 → 문자 → 재도전)을 처음부터 끝까지 따라가며\n'
  + '    끊긴 데가 없는지 보아라.\n\n'
  + '새로 찾은 것만 findings 에 담아라. 파일을 열어 확인한 것만 담는다.\n'
  + '못 찾았으면 빈 배열로 두고 notes 에 무엇을 어떻게 봤는지 적어라.',
  { label: '빠진 것', phase: '빠진 것', effort: 'high', schema: S_FINDINGS })

return {
  확인된것: kept.map(f => ({
    갈래: f.kind, 무게: f.weight, 무엇: f.what, 어디: f.where,
    증거: f.evidence, 표: f.real + '/' + f.votes, 관점: f.why, 덧붙임: f.correction,
  })),
  걸러진것: dropped.map(f => ({ 무엇: f.what, 어디: f.where, 표: f.real + '/' + f.votes, 까닭: f.why })),
  빠진것: (gaps && gaps.findings) || [],
  빠진것메모: (gaps && gaps.notes) || '',
}
