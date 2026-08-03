/* ============================================================
   통합 셸 회귀 테스트 (브라우저 불필요 — CI 에서 돈다)
   ------------------------------------------------------------
   파이널·DT·KMChC 가 각자 다르게 학생을 식별한다. 셋을 한 명단으로
   합칠 때 두 가지가 잘못되기 쉽다.

     너무 헐겁게 합치면  동명이인 둘이 한 사람이 된다
     너무 빡빡하게 합치면 같은 학생이 앱마다 따로 뜬다 — 명단이 세 배가 된다

   학교 표기가 흔들리는 것이 화근이다('휘문중' / '휘문중학교' / 빈칸).
   학년은 한쪽에만 적혀 있는 일이 흔해서 갈라놓는 근거로 쓰지 않는다.

   여기서 지키는 것:
   - 학교 표기가 달라도 같은 학생으로 붙는다
   - 학교가 다르면 동명이인으로 갈라진다
   - 정보가 더 많은 쪽(학교·학년이 적힌 쪽)이 남는다
   - 어느 앱에서 왔는지가 지워지지 않는다
   - 한 앱이 죽어도 나머지 명단은 나온다
   - 셸이 기존 앱의 데이터를 건드리지 않는다
   - 회차 집계(인원·평균·안 본 학생)가 맞는다
   - 성적표 링크 규칙을 베끼지 않고 파이널 앱에서 빌린다
   - 채점하면 스스로 따라온다(다시 읽는다)
   - 시트와 얼마나 묵었는지 늘 보여 주고, 오래되면 스스로 맞춘다
   - 망을 기다리느라 손에 쥔 것을 못 내주지 않는다
   - 학생 카드 한 장에 세 앱이 모인다(파이널 회차 · DT 미응시·재시·통과 · KMChC 진단)
   - 대시보드와 학생 카드가 **같은 배열의 같은 번호**를 가리킨다
     (어긋나면 카드에서 누른 문자가 엉뚱한 학생 것이 되어 그대로 나간다)
   - 틀리게 붙이느니 안 붙인다(동명이인·학교 표기가 흔들릴 때)
   - 화면에서 자른 것은 자른다고 말하고, 복사는 자르지 않는다

   실행:  node tests/hub.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'hub.html'), 'utf8');
/* 주석에 적어 둔 말이 검사를 속인 적이 여러 번 있었다('재시 안내' 라고 설명해
   놓은 주석이 "문구를 베꼈다"로 잡혔다). 코드만 보는 사본을 한 곳에서 만든다. */
const CODE_ONLY = (SRC.split('<script>')[1] || '')
  .replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');

/* 브라우저용 한 덩어리라 통째로 못 돌린다. 명단 합치는 함수만 오려 낸다. */
function cut(name) {
  const at = SRC.search(new RegExp(`^function ${name}\\(`, 'm'));
  if (at < 0) throw new Error(`hub.html 에서 ${name} 을 못 찾았다`);
  let depth = 0, end = -1;
  for (let j = SRC.indexOf('{', at); j < SRC.length; j++) {
    if (SRC[j] === '{') depth++;
    else if (SRC[j] === '}') { depth--; if (!depth) { end = j + 1; break; } }
  }
  return SRC.slice(at, end);
}
const ctx = { console, Date };
vm.createContext(ctx);
vm.runInContext([
  cut('normName'), cut('normSchool'), cut('normGrade'),
  ((SRC.match(/^const CHO = \[[\s\S]*?\];$/m) || [''])[0]).replace(/^const /, 'var '),
  cut('choOf'), cut('isCho'), cut('koHit'),
  cut('lesFill'),
  "var LES_ALL=[], LES_HEAD=null; const LES_HEAD_DEFAULT='{이름} 학생 학부모님께';" +
  ' function lesAll(){return LES_ALL;} function lesHead(){return LES_HEAD==null?LES_HEAD_DEFAULT:LES_HEAD;}',
  cut('lesText'),
  cut('unifyKey'), cut('looseKey'), cut('mergeRosters'),
  cut('allRounds'), cut('misTally'),
  /* 기간 기준은 소스에서 그대로 읽는다. 여기 손으로 적어 두면 소스만 바뀌었을 때
     검사가 옛 기준으로 통과한다. */
  'const DAY = 86400000;',
  (SRC.match(/^const RECENT_ROUND = .*$/m) || ['']) [0],
  cut('roundStats'),
  cut('schoolCore'), cut('schoolType'), cut('schoolAkin'),
  cut('sameStudent'), cut('nameIsUnique'), cut('dtForStudent'), cut('kmForStudent'),
  cut('dtCached'), cut('syncWorkRows'), cut('mergeCandidates'),
  cut('esc'), cut('stackBar'), cut('legendOf'), cut('donut'), cut('histo'), cut('dotsOf'),
  cut('dtClassList'), cut('finFor'), cut('classRows'), cut('clsCounts'),
  cut('sentKey'), cut('bulkBar'), cut('readHash'), cut('deltaOf'), cut('dayCounts'),
  cut('rosterCount'), cut('wonOf'),
  cut('dayKey'), cut('snoozedTill'), cut('isSnoozed'), cut('snzCls'), cut('snzBtn'),
  cut('viewName'), cut('prMis'), cut('median'), cut('madOutliers'), cut('ndgKey'), cut('nudges'), cut('snzBar'), cut('conEntry'), cut('conPut'), cut('conHits'), cut('conTags'),
  cut('conFor'), cut('conClassOf'), cut('conByClass'), cut('conRounds'),
  ((SRC.match(/^const FEE_PER = \d+;.*$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const DT_COURSE = \{[^}]*\};?$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const NDG_SENT_DAYS = \d+;.*$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const NDG_MAX = \d+;.*$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const MAD_N = \d+, MAD_Z = \d+;.*$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const SNZ_DAYS = \d+;.*$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const NDG_PEND_DAYS = \d+;.*$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const NDG_ABS_RUN = \d+;.*$/m) || [''])[0]).replace(/^const /, 'var '),
  cut('lesRoundsOf'), cut('lesSentKey'), cut('lesSentAt'),
  'var LES_SENT={}; var DT_MAT=null;',
  'var SNZ=new Map(), SNZ_SHOW=false;',
  ((SRC.match(/^const TAB_NAME = \{[^}]*\};?$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const CLS_LABEL = \{[^}]*\};?$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const MAT_GROUPS = \[[\s\S]*?^\];$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const STU_FILTERS = \[[\s\S]*?^\];$/m) || [''])[0]).replace(/^const /, 'var '),
  ((SRC.match(/^const SNZ_DAYS = \d+;.*$/m) || [''])[0]).replace(/^const /, 'var '),
  'var SENT=new Set(), TABS=["dash","stu","cls","rnd","mat","inc","exam","dt","dtp","dtr","km"], location={hash:""};',
  'var FIN=null, ROSTER=[];',
  'var PASS_ROWS=[], PEND_ROWS=[], ABS_ROWS=[], MIS_TOP=[], KM_ROWS=null, DT_CACHE={};',
].join('\n'), ctx);

console.log('── 이름표를 다듬는다 ──');
{
  chk('공백을 없앤다', ctx.normName(' 김 지 성 '), '김지성');
  chk('학교 꼬리를 뗀다', ctx.normSchool('휘문중학교'), '휘문중');
  chk('고등학교도', ctx.normSchool('한성과학고등학교'), '한성과학고');
  chk('이미 짧으면 그대로', ctx.normSchool('휘문중'), '휘문중');
  chk('학년에서 숫자만', ctx.normGrade('2학년'), '2');
  chk('학년이 없으면 빈칸', ctx.normGrade(''), '');
  chk('빈 값에도 안 죽는다', [ctx.normName(null), ctx.normSchool(undefined)], ['', '']);
}

console.log('\n── 같은 학생은 하나로 ──');
{
  const merged = ctx.mergeRosters([
    { app: 'exam', students: [{ name: '김지성', school: '휘문중', grade: '2', count: 3 }] },
    { app: 'dt',   students: [{ name: '김지성', school: '휘문중학교', grade: '' }] },
  ]);
  chk('학교 표기가 달라도 한 사람', merged.length, 1);
  chk('두 앱 모두에서 왔다고 남는다', Object.keys(merged[0].apps).sort(), ['dt', 'exam']);
  chk('파이널 응시 횟수가 보존된다', merged[0].apps.exam, 3);
  chk('학년은 적힌 쪽을 남긴다', merged[0].grade, '2');
}
{
  // 학년이 한쪽만 비어 있다고 갈라놓으면 명단이 두 배가 된다
  const merged = ctx.mergeRosters([
    { app: 'exam', students: [{ name: '이도현', school: 'A중', grade: '3' }] },
    { app: 'dt',   students: [{ name: '이도현', school: 'A중', grade: '' }] },
  ]);
  chk('학년이 비어도 갈라지지 않는다', merged.length, 1);
}

console.log('\n── 동명이인은 둘로 ──');
{
  const merged = ctx.mergeRosters([
    { app: 'exam', students: [
      { name: '김민준', school: '휘문중', grade: '2' },
      { name: '김민준', school: '대원국제중', grade: '2' },
    ] },
  ]);
  chk('학교가 다르면 두 사람', merged.length, 2);
  chk('학교가 둘 다 남는다',
      merged.map(r => r.school).sort(), ['대원국제중', '휘문중']);
}
{
  // 학교가 비어 있는 쪽은 정보가 없다 — 있는 쪽에 붙이지 않는다
  const merged = ctx.mergeRosters([
    { app: 'exam', students: [{ name: '박서준', school: '', grade: '' }] },
    { app: 'dt',   students: [{ name: '박서준', school: 'B중', grade: '1' }] },
  ]);
  chk('학교 없는 쪽은 따로 센다', merged.length, 2);
}

console.log('\n── 정보가 많은 쪽이 남는다 ──');
{
  const merged = ctx.mergeRosters([
    { app: 'exam', students: [{ name: '최유진', school: 'C중', grade: '' }] },
    { app: 'dt',   students: [{ name: '최유진', school: 'C중학교', grade: '2' }] },
  ]);
  chk('한 사람', merged.length, 1);
  chk('빈 학년이 채워진다', merged[0].grade, '2');
  chk('학교는 먼저 온 표기를 지킨다', merged[0].school, 'C중');
}

console.log('\n── 한 앱이 없어도 나온다 ──');
{
  chk('빈 목록', ctx.mergeRosters([]), []);
  chk('한 앱만 있어도', ctx.mergeRosters([
    { app: 'exam', students: [{ name: '가', school: 'X중', grade: '1' }] }]).length, 1);
  chk('이름 없는 줄은 버린다', ctx.mergeRosters([
    { app: 'dt', students: [{ name: '', school: 'X중' }, { name: '나', school: 'X중' }] }]).length, 1);
  chk('students 가 없어도 안 죽는다', ctx.mergeRosters([{ app: 'dt' }]), []);
}

console.log('\n── 이름 순으로 나온다 ──');
{
  const merged = ctx.mergeRosters([{ app: 'exam', students: [
    { name: '한지민', school: 'X중' }, { name: '강도윤', school: 'X중' }, { name: '박서연', school: 'X중' },
  ] }]);
  chk('가나다순', merged.map(r => r.name), ['강도윤', '박서연', '한지민']);
}

console.log('\n── 셸이 남의 데이터를 건드리지 않는다 ──');
{
  /* 이 파일은 읽어서 보여 주기만 한다. 쓰기가 섞이면 앱 하나가 깨질 때
     원인을 셸에서도 찾아야 한다 — 그 순간 "지워도 안전한 파일"이 아니게 된다. */
  const body = SRC.split('<script>')[1] || '';
  /* 쓰는 자리는 **적어 둔 것만** 허용한다. 늘어날 수는 있지만, 늘 때마다
     여기를 고치게 만들어 "이건 앱 자료가 아니라 이 브라우저의 취향인가" 를
     한 번은 묻게 한다. 지금 둘 다 취향 쪽이다:

       KEY      첫 화면 잠금. 남의 데이터가 아니라 파이널·홈과 **나눠 쓰는
                문고리**다 — 따로 두면 셸에서 넣고 iframe 안의 파이널에서 또
                물어 화면이 두 겹으로 잠긴다.
       VIEW_KEY 저장된 보기(주소 + 이름). 통째로 지워도 잃는 것이 없다 —
                세 번 눌러 다시 만든다.
       PAL_KEY  빠른 이동에서 방금 본 것(갈래 + 이름 여덟 개). 이것도 취향이다 —
                지워도 다음에 한 번 더 치면 된다. 학생 이름이 들어가지만 명단은
                이미 이 브라우저가 들고 있는 것이고, 여기 적힌 이름은 열 때
                지금 명단에서 되찾아야만 줄이 된다(없으면 사라진다).
       LES_KEY  수업 문자 회차 글. ⚠ 여기 셋 중 **유일하게 남의 것이 아니라
                선생님이 여기서 짓는 것**이고, 지우면 다시 못 만든다. 그래서
                이것만은 파일로 내보내기를 나란히 둔다 — 브라우저를 비우면
                사라지는 것을 유일한 사본으로 두면 안 된다.
                저장소에는 안 넣는다(공개 저장소라 수업 내용과 전화번호가
                그대로 인터넷에 남는다).

     앱 자료(파이널 기록·DT 명단)를 쓰는 것은 여전히 금지다. 아래 검사들이 본다. */
  chk('쓰는 곳은 적어 둔 네 칸뿐',
      (CODE_ONLY.match(/localStorage\.setItem\(\s*([A-Za-z_$][\w$]*)/g) || []).sort(),
      ['localStorage.setItem(KEY', 'localStorage.setItem(LES_KEY',
       'localStorage.setItem(PAL_KEY', 'localStorage.setItem(VIEW_KEY']);
  chk('그 칸은 파이널과 같은 칸', /var KEY = 'chemistreal:gate'/.test(body), true);
  /* 셸이 쓰는 칸은 셸 것임이 이름에서 보여야 한다 — 앱 칸을 덮어쓰면
     앱 하나가 깨질 때 원인을 셸에서도 찾아야 한다. */
  chk('셸 칸은 셸 이름표를 단다', /const VIEW_KEY = 'chemistreal:views'/.test(body), true);
  chk('파이널 기록은 건드리지 않는다',
      /localStorage\.setItem\(\s*(FIN_PFX|['"]final:)/.test(CODE_ONLY), false);
  chk('localStorage 를 비우지 않는다', /localStorage\.(clear|removeItem)/.test(CODE_ONLY), false);
  chk('앱스크립트에 POST 하지 않는다', /method\s*:\s*['"]POST/i.test(body), false);
  /* 남의 앱스크립트를 부르는 곳은 readOnce 한 곳뿐이고, 거기 넘기는 것은 읽기
     액션뿐이다. 한 곳으로 모으기 전에는 action 문자열을 그대로 세면 됐는데,
     이제는 부르는 쪽을 세야 같은 것을 지킨다 — 지키는 것은 그대로다. */
  chk('남의 앱을 부르는 곳은 한 곳뿐', (body.match(/jsonp\(APPS\[?\w*\]?\.?\w*\.ep/g) || []), ['jsonp(APPS[app].ep']);
  chk('읽기 액션만 부른다',
      (body.match(/readOnce\('\w+', '(\w+)'|dtOnce\('(\w+)'/g) || []).sort(),
      ["dtOnce('names'", "dtOnce('pending'", "readOnce('dt', 'absentees'",
       "readOnce('dt', 'cohortmis'", "readOnce('dt', 'income'", "readOnce('dt', 'mistags'",
       "readOnce('dt', 'passed'", "readOnce('dt', 'sentlog'", "readOnce('dt', 'snoozelog'",
       "readOnce('dt', 'views'", "readOnce('km', 'names'"]);

  /* 한 앱이 응답하지 않아도 화면이 비면 안 된다. 앱스크립트는 그냥 안 돌아올
     때가 있어서, 타임아웃이 없으면 셸이 영원히 '불러오는 중'에 멈춘다. */
  const jp = cut('jsonp');
  chk('JSONP 에 시간 제한이 있다', /setTimeout\(/.test(jp) && /reject\(/.test(jp), true);
  chk('응답이 오면 타이머를 끈다', /clearTimeout\(/.test(jp), true);
  chk('끝나면 콜백을 치운다', /delete window\[cb\]/.test(jp), true);
  chk('실패해도 나머지를 그린다', /catch\(function\(e\)\{[\s\S]{0,200}note\(/.test(body), true);

  // 같은 오리진이라는 전제가 코드에 남아 있어야 나중에 옮길 때 걸린다
  chk('DT 를 상대 경로로 얹는다', /path\s*:\s*'\.\.\/DT\//.test(body), true);
  chk('KMChC 도 상대 경로', /path\s*:\s*'\.\.\/KMChC\//.test(body), true);

  // 모달이 화면을 막은 채 안 닫히면 앱 전체가 멈춘 것처럼 보인다
  chk('모달 바깥을 눌러도 닫힌다', /e\.target===DLG\) DLG\.close\(\)/.test(body), true);
  // 저장 키 순서에 기대면 학교 표기가 열 때마다 달라진다
  chk('저장 키 순서를 고정한다', /keys\.sort\(\)/.test(body), true);
}

console.log('\n── 회차 집계 ──');
{
  /* 채점하는 날 가장 자주 묻는 둘: "이 회차 몇 명 했지", "누가 아직 안 봤지". */
  const st = ts => ts;
  const mk = (name, school, rounds) => {
    const rec = { name, school, grade:'2', count:rounds.length, rounds:[] };
    rounds.forEach(r => rec.rounds.push({ exam:r[0], correct:r[1], total:60, ts:st(r[2]), ans:null, who:rec }));
    return rec;
  };
  const NOW = Date.now(), D = 86400000;
  // 지금 채점 중인 회차다(며칠 전). 여기서만 '안 본 학생' 을 센다.
  const a = mk('김지성','휘문중',[['jmchc-1',48,NOW-3*D],['jmchc-2',54,NOW-2*D]]);
  const b = mk('이도현','대원국제중',[['jmchc-1',30,NOW-3*D]]);
  ctx.FIN = { students:[a,b] };
  // 명단에는 셋이 있다 — 박서준은 아무 회차도 안 봤지만 지금 반(DT)에 있다.
  ctx.ROSTER = [
    { name:'김지성', school:'휘문중학교', grade:'2', apps:{} },
    { name:'이도현', school:'대원국제중', grade:'2', apps:{} },
    { name:'박서준', school:'휘문중', grade:'1', apps:{dt:1} },
  ];
  const rs = ctx.roundStats();
  chk('회차 수', rs.length, 2);
  chk('최근 채점한 회차가 위에', rs.map(g => g.id), ['jmchc-2','jmchc-1']);

  const r1 = rs.filter(g => g.id==='jmchc-1')[0];
  chk('1회 채점 인원', r1.n, 2);
  chk('1회 평균 정답률', r1.avg, 65);          // (80+50)/2
  chk('1회 최고', r1.best, 80);
  chk('점수 높은 순으로 선다', r1.rows.map(r => r.who.name), ['김지성','이도현']);
  /* 학교 표기가 '휘문중' / '휘문중학교' 로 갈려도 같은 사람이다. 여기서
     갈라지면 이미 본 학생이 '안 본 학생'에 뜬다 — 헛걸음을 시킨다. */
  chk('1회 안 본 학생', r1.missing.map(r => r.name), ['박서준']);

  const r2 = rs.filter(g => g.id==='jmchc-2')[0];
  chk('2회는 한 명만 봤다', r2.n, 1);
  chk('2회 안 본 학생 둘', r2.missing.map(r => r.name).sort(), ['박서준','이도현']);

  /* ── 옛 회차에는 지금 반을 견주지 않는다 ─────────────────────────────
     예전에는 합친 명단 전체를 견줬다. 그래서 2018년 회차를 열면 올해 반
     학생이 통째로 '안 본 학생' 으로 떴다 — 그 해에는 있지도 않던 아이들이다.
     숫자만 크고 뜻이 없으니 아무도 안 봤다. */
  {
    const old = mk('옛학생','옛중',[['hwol-2018',40,NOW-400*D]]);
    ctx.FIN = { students:[old] };
    ctx.ROSTER = [
      { name:'옛학생', school:'옛중', grade:'3', apps:{} },
      { name:'올해학생', school:'휘문중', grade:'2', apps:{dt:1} },
    ];
    const g = ctx.roundStats()[0];
    chk('옛 회차는 아예 세지 않는다', g.missing, null);
  }

  /* 지금 배우는 학생만 센다: DT 반 명단에 있거나, 최근에 채점한 학생. */
  {
    const now1 = mk('요즘학생','A중',[['jmchc-3',50,NOW-5*D]]);
    ctx.FIN = { students:[now1] };
    ctx.ROSTER = [
      { name:'요즘학생', school:'A중', grade:'2', apps:{} },
      { name:'반학생',   school:'B중', grade:'2', apps:{dt:1} },   // 지금 반
      { name:'떠난학생', school:'C중', grade:'3', apps:{} },       // 기록도 반도 없다
    ];
    const g = ctx.roundStats()[0];
    chk('지금 반 학생은 센다', g.missing.map(r => r.name), ['반학생']);
    chk('떠난 학생은 안 센다', g.missing.map(r => r.name).indexOf('떠난학생'), -1);
  }

  ctx.FIN = { students:[a,b] };
  ctx.ROSTER = [];
  chk('명단이 없으면 안 본 학생도 없다', ctx.roundStats()[0].missing, []);
  ctx.FIN = { students:[] };
  chk('기록이 없으면 빈 목록', ctx.roundStats(), []);
}

console.log('\n── 최근 채점 ──');
{
  const who = { name:'가', school:'X중' };
  ctx.FIN = { students:[{ rounds:[
    { exam:'a', ts:100, who }, { exam:'b', ts:300, who }, { exam:'c', ts:200, who }] }] };
  chk('최근 것이 먼저', ctx.allRounds(ctx.FIN).map(r => r.exam), ['b','c','a']);
  chk('빈 것에도 안 죽는다', ctx.allRounds({}), []);
}

console.log('\n── 링크 규칙을 베끼지 않는다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* #r= 링크를 만드는 규칙을 여기에 옮겨 적으면, 저쪽이 규칙을 바꾸는 날
     학부모가 받은 주소가 조용히 깨진다. 같은 오리진이니 원본을 부른다. */
  chk('해시를 직접 조립하지 않는다', /'r='|"r="|`r=`/.test(body), false);
  chk('encName 을 베끼지 않았다', /function encName/.test(body), false);
  chk('파이널의 함수를 빌린다',
      /w\.hashStrFinal\(/.test(body) && /w\.shareLinkFinal\(/.test(body), true);
  chk('빌릴 창을 기다린다', /typeof w\.hashStrFinal==='function'/.test(body), true);
  chk('안 뜨면 포기한다(영영 기다리지 않는다)', /n > 80/.test(body), true);

  /* 파이널은 hashchange 로 화면을 다시 그린다. 주소를 바꾸자마자 무엇을 열면
     뒤늦게 온 hashchange 가 그것을 덮는다. */
  const nav = cut('finalNav');
  chk('해시를 바꾸면 한 번 기다린다', /addEventListener\('hashchange'/.test(nav), true);
  chk('기다린 뒤 리스너를 뗀다', /removeEventListener\('hashchange'/.test(nav), true);
  chk('주소가 그대로면 직접 부른다', /w\.boot\(\)/.test(nav), true);
}

console.log('\n── 갈라진 이름표를 짚어 준다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 셸은 공백을 지우고 묶으므로 '박하람'·'박 하람' 이 한 사람으로 온다. 파이널
     성적표는 정확히 같은 이름만 한 사람으로 보므로 저기서는 회차가 갈라진다.
     두 화면의 숫자가 다른 이유를 셸이 말해 줘야 선생님이 합칠 수 있다. */
  chk('저장된 이름표를 모아 둔다', /rec\.names\.indexOf\(raw\)<0/.test(body), true);
  chk('둘 이상이면 알려 준다', /mine\.names\.length>1/.test(body), true);
  chk('무엇을 해야 하는지 적는다', /명단 관리<\/b>에서 합쳐 주세요/.test(body), true);
  chk('눈에 띄게 그린다', /class="note err"/.test(body), true);
}

console.log('\n── 채점하면 스스로 따라온다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 셸은 열 때 한 번 읽고 캐시했다. 채점하고 돌아와도 '오늘 채점' 이 그대로라
     새로고침해야 맞았다 — 그러면 셸의 숫자를 믿을 수 없다.
     채점은 iframe 안에서 일어나고, 같은 오리진이라 그 저장이 부모에게 온다. */
  chk('저장이 바뀌면 알아차린다', /addEventListener\('storage'/.test(body), true);
  chk('파이널 기록이 바뀔 때만 움직인다', /e\.key\.indexOf\(FIN_PFX\)!==0/.test(body), true);
  chk('연달아 오면 한 번만 그린다', /function refreshSoon\(\)\{ clearTimeout/.test(body), true);
  chk('화면으로 돌아올 때도 다시 읽는다', /visibilitychange/.test(body), true);
  chk('셸 탭으로 올 때도 다시 읽는다', /if\(!app\) refreshSoon\(\);/.test(body), true);
  chk('다시 읽으면 모든 화면을 맞춘다',
      /renderStudents\(\); renderRounds\(\); renderQuick\(\); renderDash\(\); renderMerge\(\); renderSyncBar\(\);/.test(body), true);
  // 다시 읽을 때마다 앱스크립트를 또 부르면 채점할 때마다 DT 를 두드린다
  chk('DT 명단은 기억해 두고 다시 안 부른다', /if\(DT_ROWS\) sources\.push/.test(body), true);
}

console.log('\n── 시트와 스스로 맞춘다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 진짜 원본은 시트다. 이 브라우저 기록은 사본이라 다른 기기에서 채점한
     회차는 여기 없는데, 화면이 그 말을 안 하면 '안 봤나 보다' 로 넘어간다. */
  chk('언제 맞췄는지 보여 준다', /function renderSyncBar\(\)/.test(body), true);
  chk('맞춘 적 없으면 그렇게 말한다', /아직 시트와 맞춘 적이 없습니다/.test(body), true);
  chk('오래되면 눈에 띄게 한다', /classList\.toggle\('err', stale\)/.test(body), true);
  chk('반나절 넘으면 스스로 맞춘다',
      /if\(!at \|\| \(Date\.now\(\)-at\) > SYNC_STALE\) syncSheet\(\);/.test(body), true);
  chk('맞춘 뒤 화면을 다시 그린다', /SYNCING=false;\s*\n\s*refreshLocal\(\);/.test(body), true);
  chk('겹쳐서 돌지 않는다', /if\(SYNCING\) return Promise\.resolve\(null\);/.test(body), true);

  /* 쓰기는 파이널 앱이 자기 데이터에 한다. 셸이 직접 쓰기 시작하면
     "지워도 안전한 파일" 이 아니게 된다 — 위의 '남의 데이터' 검사와 한 쌍이다. */
  chk('셸은 시키기만 한다', /w\.syncAllFromSheet\(res, true\)/.test(body), true);
  chk('셸이 파이널 기록을 직접 쓰지 않는다',
      /localStorage\.setItem\(\s*(FIN_PFX|['"]final:)/.test(CODE_ONLY), false);
}

console.log('\n── 망을 기다리느라 화면을 비워 두지 않는다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 앱스크립트가 조용하면 12초를 기다린다. 그동안 파이널 기록은 손에 있는데도
     명단·회차·합칠 이름이 통째로 비어 있었다. */
  const lr = cut('loadRoster');
  chk('DT 를 부르기 전에 먼저 그린다',
      lr.indexOf('refreshLocal();') < lr.indexOf('dtRoster()'), true);
  chk('실패해도 다시 그린다', /\]\)\.then\(function\(\)\{[\s\S]{0,200}refreshLocal\(\);/.test(lr), true);
  /* 한쪽이 조용해도 다른 쪽은 얹혀야 한다. 하나를 기다리다 둘 다 못 보여 주면
     앱스크립트가 느린 날 명단이 통째로 빈다. */
  chk('두 앱을 함께 부른다', /Promise\.all\(\[/.test(lr), true);
  chk('한쪽이 죽어도 나머지는 얹는다',
      (lr.match(/\.catch\(function\(e\)\{ miss\.push\(/g) || []).length, 2);
  chk('못 받은 것을 말해 준다', /note\('stuNote', miss\.join/.test(lr), true);
}

console.log('\n── DT 를 다시 그릴 때마다 두드리지 않는다 ──');
{
  /* 화면을 다시 그릴 때마다 DT 를 새로 불렀다. 그런데 다시 그리는 일은 채점할
     때마다·창을 볼 때마다·탭을 옮길 때마다 일어난다. 재어 보니 셸을 여는 것만으로
     13번, 탭 다섯 번 오가면 10번이 더 나갔다. 앱스크립트는 실행을 한 줄로 세우니
     뒤엣것은 한참을 기다리고, 그동안 화면의 DT 숫자는 '…' 로 돌아가 있다. */
  const body = SRC.split('<script>')[1] || '';
  const once = cut('readOnce');
  chk('한 창구로만 부른다', /function readOnce\(app, action, shape, force, extra\)/.test(body), true);
  chk('받아 둔 것을 쓴다', /if\(!force && c\.val && \(Date\.now\(\)-c\.at\) < DT_TTL\)/.test(once), true);
  chk('동시에 물으면 하나로 합친다', /if\(c\.inflight\) return c\.inflight;/.test(once), true);
  // 실패한 것을 담아 두면 다음에도 계속 틀린 값을 쓴다
  // 실패한 것을 val 에 담아 두면 다음에도 계속 틀린 값을 쓴다(다시 물어야 한다)
  chk('실패는 담아 두지 않는다',
      /catch\(function\(e\)\{[\s\S]{0,160}c\.inflight = null;[\s\S]{0,160}throw e;/.test(once) &&
      !/c\.val = /.test(once.split('catch(function(e){')[1] || ''), true);
  // 앱마다 열쇠가 갈려야 한다 — 'names' 하나로 묶으면 DT 명단이 KMChC 를 덮는다
  chk('앱별로 따로 담는다', /const key = app\+':'\+action;/.test(once), true);
  chk('명단·미완료 모두 그 창구를 쓴다',
      /function dtRoster\(force\)\{ return dtOnce\('names', force\); \}/.test(body) &&
      /function dtPending\(force\)\{ return dtOnce\('pending', force\); \}/.test(body), true);
  // 이미 아는 숫자를 물음표로 되돌리면 채점하는 날 내내 '…' 만 보인다
  const rd = cut('renderDash');
  chk('아는 숫자를 …로 되돌리지 않는다', /dtKnown\? dtKnown\.length : '…'/.test(rd), true);
}

console.log('\n── KMChC 도 명단에 합친다 ──');
{
  /* 여기만 읽을 창구가 없어서, KMChC 를 본 학생은 셸에 아예 안 나왔다.
     같은 학생인데 파이널·DT 에서만 보이니 '전 과목 기록' 이 반쪽이었다. */
  const body = SRC.split('<script>')[1] || '';
  chk('설문 앱 주소가 채워졌다', /km:\s*\{[\s\S]{0,300}ep:'https:\/\/script\.google\.com/.test(body), true);
  /* 이름이 둘인 것은 자리 때문이다 — 배지에 긴 이름을 넣으면 줄이 통째로 밀린다.
     둘 다 있어야 하고, 폴더 이름(주소)은 바뀌지 않는다. */
  chk('긴 이름과 짧은 이름이 함께 있다',
      /name:'화학 정밀 학습진단', short:'학습진단'/.test(body), true);
  chk('주소는 그대로 KMChC 폴더', /path:'\.\.\/KMChC\/index\.html'/.test(body), true);
  chk('KMChC 명단을 읽는 길이 있다', /function kmRoster\(force\)/.test(body), true);
  const km = cut('kmRoster');
  chk('같은 캐시를 쓴다', /readOnce\('km', 'names'/.test(km), true);
  // 이 시트에는 학교 열이 없다. 없는 것을 지어내면 안 된다
  chk('학교는 빈칸으로 둔다', /school:''/.test(km), true);
  chk('리포트 주소를 들고 온다', /kmLink:s\.link/.test(km), true);
  chk('명단에 얹는다', /if\(KM_ROWS\) sources\.push\(\{ app:'km', students: KM_ROWS/.test(body), true);
  /* ⚠ 아래 검사들은 noSchool 깃발을 **검사가 직접 세워** 부른다. 그래서 셸이
     그 깃발을 안 세워도 다 통과했고, 실제로 한 번도 안 세우고 있었다 —
     KMChC 학생이 같은 이름의 파이널 학생과 안 붙어 셸에 두 줄로 떴다.
     깃발을 세우는지 소스에서 직접 본다. */
  chk('학교 열이 없는 앱이라고 말해 준다',
      /sources\.push\(\{ app:'km', students: KM_ROWS, noSchool:true \}\)/.test(body), true);

  /* 학교 열이 없는 앱은 이름만으로 붙여 준다 — 안 그러면 같은 아이가 두 줄이다. */
  const merged = ctx.mergeRosters([
    { app:'exam', students:[{ name:'홍길동', school:'휘문중', grade:'2', count:3 }] },
    { app:'km',   students:[{ name:'홍길동', school:'', grade:'2', count:1 }], noSchool:true },
  ]);
  chk('학교 없는 앱은 한 사람으로 붙는다', merged.length, 1);
  chk('붙으면 학교가 남는다', merged[0].school, '휘문중');
  chk('두 앱에서 왔다고 남는다', Object.keys(merged[0].apps).sort(), ['exam','km']);
  chk('횟수가 더해진다', merged[0].n, 4);

  /* 그래도 동명이인이면 붙이지 않는다. 기계가 골라 붙이면 남의 성적이 남의
     이름 밑에 들어가고, 그건 되돌릴 수 없다. */
  const two = ctx.mergeRosters([
    { app:'exam', students:[{ name:'김민준', school:'휘문중', grade:'2' },
                            { name:'김민준', school:'대원국제중', grade:'2' }] },
    { app:'km',   students:[{ name:'김민준', school:'', grade:'2' }], noSchool:true },
  ]);
  chk('동명이인이면 그냥 둔다', two.length, 3);

  // 파이널에서 학교를 안 적은 줄은 예전대로 따로 둔다(모르는 것이지 없는 것이 아니다)
  const blank = ctx.mergeRosters([
    { app:'exam', students:[{ name:'박서준', school:'', grade:'' }] },
    { app:'dt',   students:[{ name:'박서준', school:'B중', grade:'1' }] },
  ]);
  chk('학교를 안 적은 줄은 그대로 따로', blank.length, 2);

  chk('임시 표시가 명단에 새지 않는다', merged[0].noSch, undefined);
}

console.log('\n── DT 오개념을 셸로 끌어온다 ──');
{
  /* DT 는 틀린 문항의 오개념 태그를 남기는데 그 집계가 DT 안에서만 보였다.
     다음 회차를 짤 때 제일 알고 싶은 것이 "요즘 반이 뭘 어려워하나" 인데. */
  const body = SRC.split('<script>')[1] || '';
  chk('집계를 읽는 길이 있다', /function dtMisRows\(force\)/.test(body), true);
  chk('같은 캐시를 쓴다', /readOnce\('dt', 'cohortmis'/.test(cut('dtMisRows')), true);
  chk('화면에 자리가 있다', /id="misWrap"/.test(SRC) && /id="misList"/.test(SRC), true);

  const D = 86400000, now = Date.now();
  const rows = [
    { studentKey:'s1', date:new Date(now-2*D).toISOString(), wrongMis:['몰농도','완충'] },
    { studentKey:'s2', date:new Date(now-3*D).toISOString(), wrongMis:['몰농도'] },
    // 같은 학생이 같은 태그를 또 틀렸다 — 두 명으로 세면 안 된다
    { studentKey:'s1', date:new Date(now-1*D).toISOString(), wrongMis:['몰농도'] },
    // 한 달이 넘은 것은 '요즘' 이 아니다
    { studentKey:'s3', date:new Date(now-90*D).toISOString(), wrongMis:['몰농도','산화수'] },
    { studentKey:'s4', date:'', wrongMis:['날짜없음'] },
    { studentKey:'s5', date:new Date(now-4*D).toISOString(), wrongMis:['', '  '] },
  ];
  const top = ctx.misTally(rows, 30);
  chk('많이 걸린 것부터', top.map(t => t.tag), ['몰농도','완충']);
  chk('한 학생을 두 번 세지 않는다', top[0].n, 2);
  chk('오래된 것은 빼고 센다', top.map(t => t.tag).indexOf('산화수'), -1);
  chk('날짜 없는 줄은 뺀다', top.map(t => t.tag).indexOf('날짜없음'), -1);
  chk('빈 태그는 세지 않는다', top.length, 2);
  chk('빈 입력에도 안 죽는다', [ctx.misTally(null), ctx.misTally([])], [[], []]);
}

console.log('\n── DT 문자를 셸에서 바로 복사한다 ──');
{
  /* 문자를 복사하려면 DT 의 pending.html 로 넘어가야 했다. 채점하다 말고
     페이지를 옮기는 일이라, 셸에서 다 볼 수 있는데도 거기서 끝나지 않았다. */
  const body = SRC.split('<script>')[1] || '';
  chk('통과 목록을 읽는 길이 있다', /function dtPassed\(force\)/.test(body), true);
  chk('같은 캐시를 쓴다', /readOnce\('dt', 'passed'/.test(cut('dtPassed')), true);
  chk('통과 자리가 화면에 있다', /id="passWrap"/.test(SRC) && /id="passList"/.test(SRC), true);
  chk('문자 단추가 두 목록에 다 있다',
      /data-pend="/.test(body) && /data-pass="/.test(body), true);

  /* 문구를 여기에 베껴 두면 언젠가 두 벌이 갈라지고, 학부모는 같은 상황에서
     서로 다른 문자를 받는다. 성적표 링크를 파이널에서 빌리는 것과 같은 규칙. */
  // 주석에 '재시 안내' 를 적어 두는 것은 베낀 것이 아니다. 코드만 본다.
  const code = body.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
  chk('문구를 베끼지 않는다',
      /안녕하세요, 화학 조준모입니다|조준모 드림|통과선\(80점\)/.test(code), false);
  chk('DT 화면에서 빌린다', /function dtPendWindow\(\)/.test(body), true);
  const dw = cut('dtPendWindow');
  chk('빌릴 창을 기다린다', /setInterval\(/.test(dw), true);
  chk('안 뜨면 포기한다(영영 기다리지 않는다)', /n > 80[\s\S]{0,80}rej\(/.test(dw), true);
  /* 이 화면은 탭으로도 얹힌다. 문자를 만들기 전에 그 탭을 먼저 지나갔는데 그때
     망이 끊겨 빈 화면을 물었다면, 그 창을 아무리 빌려도 함수가 안 생긴다. */
  chk('빈 화면을 물었으면 한 번 다시 띄운다', /if\(n === 40\)\{ try\{ f\.src = f\.src; \}/.test(dw), true);
  /* 예전에는 화면 밖(left:-9999px)에 숨겨 띄웠다. 어차피 띄우는 화면이니
     **탭으로 내놓는다** — 선생님이 그 화면을 그대로 쓰고, 한 장만 뜬다.
     따로 만들면 같은 화면이 두 번 떠서 앱스크립트를 두 번 두드린다. */
  chk('탭의 그 창을 빌린다', /mountFrame\('dtp'\)/.test(dw), true);
  chk('몰래 한 장 더 만들지 않는다', /left:-9999px/.test(dw), false);
  chk('재시·문자 화면에 탭 자리가 있다',
      /id="t-dtp"/.test(SRC) && /id="p-dtp"/.test(SRC), true);
  chk('명단 화면에도 탭 자리가 있다',
      /id="t-dtr"/.test(SRC) && /id="p-dtr"/.test(SRC), true);
  chk('두 화면 모두 DT 의 상대 경로', /'\.\.\/DT\/pending\.html'/.test(body) &&
      /'\.\.\/DT\/roster\.html'/.test(body), true);
  chk('빌린 함수를 그대로 부른다',
      /w\.shareMsg\(\{/.test(body) && /w\.passMsg\(\{/.test(body), true);

  /* DT 는 {active, stale, …} 객체로 준다. 배열로 알고 .length 를 읽어서
     'DT 미완료' 칸에 undefined 가 찍히고 있었다. */
  const dOnce = cut('dtOnce');
  chk('미완료는 active 만 센다', /\(p && p\.active\) \|\| \[\]/.test(dOnce), true);
  chk('배열로 와도 받는다', /Array\.isArray\(p\)/.test(dOnce), true);
}

console.log('\n── 하루 일을 셸 안에서 끝낸다 ──');
{
  /* 시험 미응시만 셸에 없어서, 채점하다 말고 DT 화면으로 넘어가야 했다.
     하루 흐름에서 거기만 끊겼다. */
  const body = SRC.split('<script>')[1] || '';
  chk('미응시를 읽는 길이 있다', /function dtAbsentees\(force\)/.test(body), true);
  chk('같은 캐시를 쓴다', /readOnce\('dt', 'absentees'/.test(cut('dtAbsentees')), true);
  chk('미응시 자리가 화면에 있다', /id="absWrap"/.test(SRC) && /id="absList"/.test(SRC), true);
  chk('반 전체 공지와 개별 안내가 다 있다',
      /data-stage="bc"/.test(body) && /data-stage="1"/.test(body) && /data-stage="2"/.test(body), true);
  /* 응시 링크를 셸이 지어내면 저쪽이 경로를 바꿀 때 조용히 어긋난다.
     문구도 주소도 DT 에서 빌린다. */
  chk('응시 주소도 DT 에서 빌린다', /w\.examLink\(c\.course, c\.round\)/.test(body), true);
  chk('미응시 문구도 빌린다', /w\.absentMsg\(\{/.test(body), true);
  chk('셸이 exam.html 주소를 짜지 않는다', /exam\.html\?c=/.test(body), false);

  /* 화면 차례가 하루 흐름이어야 한다: 급한 것 → 챙길 것 → 방금 한 것 → 참고.
     예전에는 '합쳐야 할 이름'(거의 빌 일) 이 맨 위였다. */
  const order = ['absWrap','pendWrap','passWrap','recentWrap','misWrap','mergeWrap']
    .map(id => SRC.indexOf('id="' + id + '"'));
  chk('모든 자리가 있다', order.every(i => i > 0), true);
  chk('급한 것부터 선다', order.slice().sort((a,b) => a-b), order);

  // 채점하는 날 제일 급한 숫자
  chk('미응시가 숫자 칸에도 뜬다', /id="abCnt"/.test(body), true);
}

console.log('\n── 어느 앱이 대답하는지 보여 준다 ──');
{
  /* DT 는 **한 해 내내 대답하지 않고 있었다.** 셸이 JSONP 로 부르는데 저쪽이
     콜백을 무시하고 순수 JSON 을 줘서, 받는 쪽이 그걸 자바스크립트로 실행하려다
     죽었다. 화면에는 '…' 와 '—' 만 남았고, '아직 불러오는 중' 인지 '고장' 인지
     구별할 길이 없어 아무도 눈치채지 못했다. */
  const body = SRC.split('<script>')[1] || '';
  chk('연결 줄 자리가 있다', /id="connBar"/.test(SRC), true);
  chk('연결 줄을 그린다', /function renderConn\(\)/.test(body), true);
  const conn = cut('renderConn');
  chk('앱마다 한 칸씩', /const CONN = \[/.test(body), true);
  chk('시트·DT·KMChC 를 다 본다',
      /'sheet'[\s\S]{0,400}'dt:names'[\s\S]{0,200}'dt:pending'[\s\S]{0,200}'dt:passed'[\s\S]{0,200}'km:names'/.test(body), true);
  // '아직' 과 '고장' 을 구별해야 눈치챌 수 있다
  chk('부르는 중과 실패를 가른다',
      /inflight && !s\.val\) return chip\(c\.name, 'wait'/.test(conn) &&
      /s\.err && !s\.val\) return chip\(c\.name, 'bad'/.test(conn), true);
  chk('왜 안 되는지 적는다', /chip\(c\.name, 'bad', s\.err\)/.test(conn), true);
  // 읽기가 끝나거나 엎어질 때마다 다시 그려야 실시간으로 보인다
  const once = cut('readOnce');
  chk('성공해도 실패해도 다시 그린다',
      (once.match(/renderConn\(\);/g) || []).length, 2);
  chk('실패 사유를 남긴다', /c\.err = e\.message/.test(once), true);
}

console.log('\n── 이 숫자가 어디까지의 숫자인지 적는다 ──');
{
  /* "파이널 누적 학생 42" 를 보면 42명이 전부라고 읽는다. 시트와 맞추기 전이라면
     그것은 이 브라우저에서 채점한 42명일 뿐이다. */
  const body = SRC.split('<script>')[1] || '';
  const sl = cut('sourceLine');
  chk('숫자 밑에 적을 자리가 있다', /id="srcNote"/.test(SRC), true);
  chk('맞춘 적 없으면 이 브라우저 기록만이라고 한다',
      /if\(!at\) return \{warn:true[\s\S]{0,120}이 브라우저 기록만/.test(sl), true);
  chk('묵었어도 그렇게 말한다', /stale\s*\n?\s*\? \{warn:true[\s\S]{0,80}이 브라우저 기록만/.test(sl), true);
  chk('맞춘 뒤에는 시트까지라고 한다', /시트까지 반영된 숫자입니다/.test(sl), true);
  chk('동기화 줄을 그릴 때 같이 그린다',
      /function renderSyncBar\(\)\{\s*\n\s*renderSourceNote\(\);/.test(body), true);
}

console.log('\n── 갈라진 이름을 매일 보여 준다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  chk('후보를 골라낸다', /function mergeCandidates\(\)/.test(body), true);
  chk('이름표가 둘 이상인 학생만', /s\.names && s\.names\.length>1/.test(body), true);
  chk('많이 본 학생부터', /return b\.n-a\.n;/.test(body), true);
  /* 기계가 합치면 동명이인을 되돌릴 수 없게 묶는다. 찾아만 준다. */
  chk('셸이 스스로 합치지 않는다', /rosterMerge|mergeNames\(/.test(body), false);
}

console.log('\n── 단축키가 글자 입력을 가로채지 않는다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  // 주석으로 죽여 놓아도 통과하지 않도록 줄 첫머리에서 본다
  chk('입력 중에는 비켜선다', /^\s*if\(typing\) return;/m.test(body), true);
  chk('조합키는 건드리지 않는다', /if\(e\.metaKey\|\|e\.ctrlKey\|\|e\.altKey\) return;/.test(body), true);
  /* 숫자를 손으로 적어 두면 탭을 늘릴 때마다 여기가 낡는다. 둘 다 소스에서
     읽어 길이를 견준다 — 탭이 늘었는데 키가 그대로면 마지막 탭에 못 간다. */
  const nTabs = ((body.match(/const TABS = \[([^\]]+)\]/) || ['',''])[1].match(/'/g) || []).length / 2;
  const nKeys = ((body.match(/const n = '([\d\-=]+)'\.indexOf/) || ['',''])[1] || '').length;
  chk('탭이 열두 개', nTabs, 12);
  chk('탭 수와 숫자키 수가 맞는다', nKeys, nTabs);
  /* 앞 일곱은 셸이 그리는 화면, 뒤 다섯은 앱을 얹은 화면. 머리의 두 줄과
     같은 차례여야 숫자키가 눈에 보이는 차례와 맞는다. */
  chk('보는 화면이 앞, 앱이 뒤',
      /const TABS = \['dash','stu','cls','rnd','con','mat','inc','exam','dt','dtp','dtr','km'\]/.test(body), true);
}

console.log('\n── 학교 표기가 앱마다 흔들린다 ──');
{
  /* 같은 학생을 DT 는 미완료 목록에서 '휘문', 통과 목록에서 '휘문중', 반 명단에서
     '휘문중학교' 로 준다. 표기로 가르면 학생 카드에 아무것도 안 붙는다. */
  chk('꼬리가 없어도 같은 학교', ctx.schoolAkin('휘문', '휘문중'), true);
  chk('긴 표기도 같은 학교', ctx.schoolAkin('휘문중학교', '휘문중'), true);
  /* 몸통이 같아도 종류가 다르면 다른 학교다. 여기서 붙으면 중학생 카드에
     고등학생 기록이 뜨고, 그 이름으로 문자가 나간다. */
  chk('중학교와 고등학교는 다르다', ctx.schoolAkin('대곡중', '대곡고'), false);
  chk('학교가 다르면 남이다', ctx.schoolAkin('휘문중', '도곡중'), false);
  chk('한쪽을 모르면 가르지 않는다', ctx.schoolAkin('', '휘문중'), true);
  chk('둘 다 몰라도 안 죽는다', ctx.schoolAkin(null, undefined), true);
}

console.log('\n── 학생 카드에 다른 앱 기록을 붙인다 ──');
{
  /* 여태 학생 카드는 파이널 회차만 보여 주고 DT·KMChC 는 "명단에도 있습니다"
     한 줄로 끝났다. 정작 물어보고 싶은 것은 그쪽인데. */
  ctx.ROSTER = [
    { name:'김지성', school:'휘문중',     grade:'2', apps:{exam:2, dt:1} },
    { name:'이도현', school:'대원국제중', grade:'2', apps:{dt:1} },
    { name:'박서준', school:'A중',        grade:'1', apps:{dt:1} },
    { name:'박서준', school:'B중',        grade:'2', apps:{dt:1} },   // 동명이인
  ];
  ctx.PASS_ROWS = [
    { name:'김지성', school:'휘문',       course:'ch2', round:7, score:91.7, tries:1 },  // 표기가 짧다
    { name:'이도현', school:'대원국제중', course:'ch1', round:6, score:85,   tries:2 },
  ];
  ctx.PEND_ROWS = [
    { name:'김지성', school:'휘문중학교', course:'gc', round:7, score:55, nextNeeded:'재시', days:13 },
  ];
  ctx.ABS_ROWS = [{ label:'화학1 일6-10', course:'ch1', round:6, absent:['김지성','박서준'], total:26 }];
  ctx.KM_ROWS = [
    { name:'김지성', school:'', grade:'중2', kmLink:'https://x/report?id=1' },
    { name:'박서준', school:'', grade:'중1', kmLink:'https://x/report?id=2' },
    { name:'박서준', school:'', grade:'중2', kmLink:'https://x/report?id=3' },
  ];

  const a = ctx.dtForStudent(ctx.ROSTER[0]);
  chk('표기가 짧아도 통과가 붙는다', a.passed, [0]);
  chk('표기가 길어도 재시가 붙는다', a.pending, [0]);
  chk('미응시도 붙는다', a.absent, [{ i:0, j:0 }]);
  /* 붙는 것은 값이 아니라 **원래 배열의 번호**다. 대시보드의 문자 단추와 같은
     번호를 써야 카드에서 누른 문자가 그 학생 것이 된다. */
  chk('번호는 원래 배열의 번호', ctx.PASS_ROWS[a.passed[0]].name, '김지성');

  const b = ctx.dtForStudent(ctx.ROSTER[1]);
  chk('남의 통과가 안 붙는다', b.passed, [1]);
  chk('없는 것은 빈 목록', b.pending, []);

  /* 미응시 목록에는 이름만 있다(학교가 없다). 동명이인이면 누구 것인지 알 길이
     없다 — 붙이면 남의 문자가 나가고, 나간 문자는 되돌릴 수 없다. */
  const c = ctx.dtForStudent(ctx.ROSTER[2]);
  chk('동명이인이면 미응시를 안 붙인다', c.absent, []);
  chk('이름이 유일해야 붙인다',
      [ctx.nameIsUnique('김지성'), ctx.nameIsUnique('박서준')], [true, false]);

  chk('KMChC 는 이름이 하나뿐일 때만', ctx.kmForStudent(ctx.ROSTER[0]).kmLink, 'https://x/report?id=1');
  chk('KMChC 동명이인은 고르지 않는다', ctx.kmForStudent(ctx.ROSTER[2]), null);
  chk('명단에 없는 학생에도 안 죽는다',
      ctx.dtForStudent({ name:'없는사람', school:'', apps:{} }),
      { passed:[], pending:[], absent:[] });
  chk('이름이 빈 줄에 붙지 않는다', ctx.sameStudent(ctx.ROSTER[0], {}), false);
}

console.log('\n── 대시보드와 학생 카드가 같은 줄을 가리킨다 ──');
{
  /* 두 곳에서 따로 잘라 담으면 학생 카드의 '문자 복사' 가 엉뚱한 학생 문구를
     만든다. 그 문자는 그대로 학부모에게 나가고, 되돌릴 수 없다. */
  ctx.DT_CACHE = {
    'dt:passed':    { val:[{ name:'가' }, { name:'나' }] },
    'dt:pending':   { val:[{ name:'다' }] },
    'dt:absentees': { val:[{ label:'A', absent:['라'] }, { label:'B', absent:[] }] },
  };
  ctx.syncWorkRows();
  chk('통과는 캐시 그대로', ctx.PASS_ROWS.length, 2);
  chk('미완료도 그대로', ctx.PEND_ROWS.length, 1);
  chk('아무도 안 빠진 반은 뺀다', ctx.ABS_ROWS.map(c => c.label), ['A']);
  ctx.DT_CACHE = {};
  ctx.syncWorkRows();
  chk('캐시가 비면 빈 목록', [ctx.PASS_ROWS, ctx.PEND_ROWS, ctx.ABS_ROWS], [[], [], []]);

  const body = SRC.split('<script>')[1] || '';
  chk('담는 곳은 한 곳뿐', /function syncWorkRows\(\)/.test(body), true);
  chk('대시보드가 따로 잘라 담지 않는다',
      /(PASS_ROWS|PEND_ROWS|ABS_ROWS)\s*=\s*[^;]*\.slice\(/.test(body), false);
  // 조용히 자르면 그 아래가 없는 줄 알고 넘어간다 — 그게 아직 안 끝난 학생이다
  chk('자를 때는 자른 것을 말한다',
      /function capNote\(rows\)/.test(body) && /앞 '\+DASH_MAX\+'명만/.test(body), true);
  chk('학생 카드에도 문자 단추가 있다',
      /data-pend="'\+i\+'" data-orig="재시 안내"/.test(body) &&
      /data-pass="'\+i\+'" data-orig="통과 문자"/.test(body) &&
      /data-abs="'\+a\.i\+'"/.test(body), true);
  // 뒤늦게 온 DT 응답이 이미 닫힌 카드를 그리면 안 된다
  chk('닫은 카드는 놓는다', /DLG\.addEventListener\('close'/.test(body), true);
  // 카드가 열리는 것을 망이 붙잡으면, 이름을 눌러도 아무 일이 없는 것처럼 보인다
  chk('망을 기다리며 카드를 붙잡지 않는다',
      /renderStuOther\(\);[\s\S]{0,400}Promise\.all\(\[[\s\S]{0,200}renderStuOther\(\); \}\);/.test(body), true);
  // 문자 복사가 실패하면 누른 자리 근처에 적어야 보인다(카드가 대시보드를 가린다)
  chk('실패를 누른 자리에 적는다', /btn\.closest\('\.dlg__b'\) \? 'dlgNote'/.test(body), true);
}

console.log('\n── 오늘 할 일을 한 줄에 세운다 ──');
{
  /* 급한 것이 아래로 다섯 섹션에 흩어져 있어, 무엇이 얼마나 남았는지 알려면
     스크롤하며 세야 했다. 그래서 아래쪽 섹션은 잘 안 보게 된다. */
  const jumpSrc = (SRC.match(/^const JUMPS = \[[\s\S]*?^\];$/m) || [''])[0];
  chk('목록이 있다', !!jumpSrc, true);
  vm.runInContext(jumpSrc.replace(/^const /, 'var '), ctx);   // const 는 컨텍스트에 안 붙는다
  ctx.PASS_ROWS = [{}, {}, {}]; ctx.PEND_ROWS = [{}]; ctx.MIS_TOP = [{}, {}];
  ctx.ABS_ROWS = [{ absent:['가','나'] }, { absent:['다'] }];
  ctx.FIN = { students:[] };
  const n = ctx.JUMPS.map(j => j.n());
  chk('미응시는 반이 아니라 사람 수로 센다', n[0], 3);
  chk('재시·통과·개념도 센다', [n[1], n[2], n[3]], [1, 3, 2]);
  chk('합칠 이름도 센다', n[4], 0);

  const body = SRC.split('<script>')[1] || '';
  chk('자리가 있다', /id="jump"/.test(SRC), true);
  chk('빈 것은 안 세운다', /JUMPS\.filter\(function\(j\)\{ return j\.n\(\) > 0; \}\)/.test(body), true);
  chk('누르면 그 자리로 간다', /scrollIntoView/.test(body), true);
  // 스크롤만 되면 무엇이 바뀌었는지 모른다
  chk('어디로 왔는지 표시한다', /classList\.add\('flashed'\)/.test(body), true);
}

console.log('\n── 학생을 걸러 본다 ──');
{
  /* "DT 반에는 있는데 파이널을 한 번도 안 본 학생" 은 검색으로 낼 수 없는
     물음인데, 다음 회차를 누구에게 돌릴지 정할 때 가장 먼저 나온다. */
  const fSrc = (SRC.match(/^const STU_FILTERS = \[[\s\S]*?^\];$/m) || [''])[0];
  chk('목록이 있다', !!fSrc, true);
  vm.runInContext(fSrc.replace(/^const /, 'var '), ctx);
  const R = [
    { name:'가', apps:{ exam:2 } },
    { name:'나', apps:{ dt:1 } },
    { name:'다', apps:{ exam:1, dt:1, km:1 } },
  ];
  const by = k => ctx.STU_FILTERS.filter(f => f.key === k)[0].fn;
  chk('전체', R.filter(by('all')).length, 3);
  chk('파이널', R.filter(by('exam')).map(r => r.name), ['가','다']);
  chk('DT', R.filter(by('dt')).map(r => r.name), ['나','다']);
  chk('KMChC', R.filter(by('km')).map(r => r.name), ['다']);
  chk('파이널을 한 번도 안 본 학생', R.filter(by('noexam')).map(r => r.name), ['나']);
  chk('자리가 있다', /id="stuFilter"/.test(SRC), true);
}

console.log('\n── 회차에서 바로 들고 나간다 ──');
{
  /* 회차를 열어 놓고 하는 일은 둘이다: 반 성적을 엑셀로 옮기거나, 아직 안 본
     아이들에게 공지를 돌리거나. 둘 다 화면을 보고 손으로 옮겨 적어야 했다. */
  const body = SRC.split('<script>')[1] || '';
  chk('표 복사 단추가 있다', /data-rnd="table"/.test(body), true);
  chk('이름 복사 단추가 있다', /data-rnd="names"/.test(body), true);
  chk('엑셀에 붙게 탭으로 나눈다', /join\('\\t'\)/.test(body), true);
  /* 화면은 120명만 보여 준다. 복사까지 잘리면 공지에서 아이가 빠지는데,
     빠진 줄도 모른다. */
  chk('이름 복사는 전부를 담는다',
      /copyText\(b, \(g\.missing\|\|\[\]\)\.map\(function\(r\)\{ return r\.name; \}\)\.join\(', '\)/.test(body), true);
  chk('잘랐다는 것을 말한다', /이름 복사는 '\+g\.missing\.length\+'명 전부를 담습니다/.test(body), true);
  chk('닫으면 회차를 놓는다', /RND_OPEN = null/.test(body), true);
  /* 남의 앱 주소를 셸이 지어내면 저쪽이 경로를 바꾸는 날 조용히 어긋난다.
     DT·KMChC 가 준 주소를 그대로 연다. */
  chk('주소를 지어내지 않는다', /data-url="'\+esc\(url\)\+'"/.test(body), true);
  chk('report\\.html 주소를 짜지 않는다', /['"`]report\.html\?/.test(body), false);
}

console.log('\n── 반으로도 물을 수 있다 ──');
{
  /* 셸은 사람(학생 탭)과 시험(회차 탭)으로만 물을 수 있었다. 그런데 수업은
     반으로 돈다 — "오늘 이 반, 누가 안 왔고 누가 재시가 밀렸나". 그걸 보려면
     DT 의 미응시·재시·통과 화면을 따로 열어 이름을 눈으로 맞춰야 했다. */
  const body = SRC.split('<script>')[1] || '';
  chk('반 탭 자리가 있다',
      /id="t-cls"/.test(SRC) && /id="clsTabs"/.test(SRC) && /id="clsList"/.test(SRC), true);
  /* 반 구조를 잃지 않아야 반째로 물을 수 있다. 창구를 한 번 더 두드리지
     않으려고 펴 놓은 줄에 원본을 달아 둔다. */
  chk('반 구조를 들고 있다', /rows\.classes = d\.classes \|\| \[\]/.test(body), true);
  chk('그 원본을 읽는 길이 있다', /function dtClassList\(\)/.test(body), true);

  ctx.ROSTER = [
    { name:'가', school:'A중', apps:{dt:1} }, { name:'나', school:'A중', apps:{dt:1} },
    { name:'다', school:'A중', apps:{dt:1} }, { name:'라', school:'A중', apps:{dt:1} },
  ];
  ctx.ABS_ROWS = [
    { label:'화학1 토', course:'ch1', round:12, absent:['가'], total:4 },
    // 같은 아이('라')가 다른 반에서도 미응시다. 이 줄이 이 반에 새면 안 된다.
    { label:'화학2 일', course:'ch2', round:7,  absent:['라'], total:4 },
  ];
  ctx.PEND_ROWS = [
    { name:'나', school:'A중', course:'ch1', round:12, score:55 },
    { name:'라', school:'A중', course:'ch2', round:7,  score:60 },   // 다른 과목
  ];
  ctx.PASS_ROWS = [
    { name:'다', school:'A중', course:'ch1', round:12, score:91 },
    { name:'가', school:'A중', course:'ch1', round:11, score:88 },   // 지난 회차 통과
  ];
  ctx.FIN = { students:[{ name:'다', school:'A중', rounds:[{correct:40,total:60,ts:1}] }] };
  const cls = { label:'화학1 토', course:'ch1', students:[
    {name:'가',school:'A중',year:'2'},{name:'나',school:'A중',year:'2'},
    {name:'다',school:'A중',year:'2'},{name:'라',school:'A중',year:'2'}] };
  const rows = ctx.classRows(cls);
  /* 급한 것이 이긴다. '가' 는 지난 회차를 통과했지만 이번 회차를 안 봤다 —
     지금 손이 필요한 쪽을 말해야 한다. */
  chk('상태는 급한 것이 이긴다', rows.map(r => r.st), ['miss','wait','ok','none']);
  /* '라' 는 화학2 반에서 미응시이고 화학2 재시도 밀렸다. 그 줄들이 이 반으로
     새면 '아직' 이어야 할 아이가 '미응시'·'재시 대기' 로 뜨고, 이 반에 없는
     일이 할 일 목록에 오른다. */
  chk('다른 반 미응시를 끌어오지 않는다', rows[3].abs.length, 0);
  chk('다른 과목 재시를 끌어오지 않는다', rows[3].pend.length, 0);
  chk('사람 수와 줄 수가 같다', rows.length, cls.students.length);
  const cnt = ctx.clsCounts(rows);
  chk('센 것의 합이 반 인원', cnt.reduce((t,p) => t + p.n, 0), 4);
  chk('미응시·재시·통과·아직 한 명씩', cnt.map(p => p.n), [1,1,1,1]);
  /* 파이널 기록은 이름이 하나뿐일 때만 붙인다(학교 표기가 흔들려도 붙는다). */
  chk('파이널 기록이 붙는다', !!rows[2].fin, true);
  chk('없는 사람은 안 붙는다', rows[3].fin, null);
  chk('빈 반에도 안 죽는다', ctx.classRows({label:'X',course:'ch1'}), []);

  chk('반에서도 문자를 바로 복사한다',
      /data-abs="'\+r\.abs\[0\]\.i\+'"/.test(body) &&
      /data-pend="'\+r\.pend\[0\]\+'"/.test(body) &&
      /data-pass="'\+r\.pass\[0\]\+'"/.test(body), true);
  /* 명단에 이미 있는 학생이면 그 줄을 쓴다(파이널 회차까지 붙은 카드가 열린다).
     같은 이름이 둘이면 붙이지 않는다 — 반쪽 카드가 남의 기록보다 낫다. */
  chk('명단에 있으면 그 줄로 연다', /hit\.length===1 \? hit\[0\]/.test(cut('rosterRow')), true);
  chk('반에서 학생 카드로 넘어간다', /openStudent\(list\[i\], list, i\)/.test(body), true);
}

/* 상담 주간에는 한 반을 이름 순서대로 훑는다. 카드를 닫고 다음 이름을 찾아
   다시 여는 일이 스무 번 되풀이됐다. */
console.log('\n── 학생 카드에서 옆 사람으로 ──');
{
  const body = SRC.split('<script>')[1] || '';
  chk('넘김 자리가 있다', /id="dlgNav"/.test(SRC) && /id="dlgPrev"/.test(SRC) &&
                          /id="dlgNext"/.test(SRC), true);
  /* 목록 없이 연 카드(알림에서 이름을 누른 것)에는 넘길 곳이 없다 —
     눌러도 아무 일이 없는 단추를 두지 않는다. */
  chk('혼자 열면 단추가 안 보인다', /nav\.hidden = n < 2 \|\| DLG_AT < 0;/.test(cut('dlgNavShow')), true);
  chk('끝에서는 못 누른다', /disabled = DLG_AT <= 0/.test(cut('dlgNavShow')) &&
                            /disabled = DLG_AT >= n-1/.test(cut('dlgNavShow')), true);
  chk('범위를 넘지 않는다', /at < 0 \|\| at >= DLG_LIST\.length/.test(cut('dlgStep')), true);
  /* 이미 열린 창에 showModal 을 또 부르면 브라우저가 예외를 던진다. */
  chk('열린 창을 다시 열지 않는다', /if\(!dlg\.open\) dlg\.showModal\(\);/.test(body), true);
  /* 같은 창을 회차와 학생이 나눠 쓴다. 회차 창에 학생용 단추가 남으면
     누를 때 엉뚱한 학생이 열린다. */
  chk('회차 창에는 안 남는다', /DLG_LIST = null; DLG_AT = -1; dlgNavShow\(\);/.test(cut('openRound')), true);
  chk('닫으면 잊는다', /DLG_LIST = null; DLG_AT = -1;/.test(body.slice(body.indexOf("DLG.addEventListener('close'"))), true);
  const kb = body.slice(body.indexOf("document.addEventListener('keydown'"));
  chk('← → 로도 넘긴다', /ArrowLeft.*dlgStep|dlgStep\(e\.key==='ArrowLeft'/.test(kb), true);
}

console.log('\n── 그림은 한 벌의 어휘를 쓴다 ──');
{
  /* 화면마다 다른 그림을 쓰면 그림마다 읽는 법을 새로 배워야 한다.
     넷만 쓰고, 색도 한 벌이다(초록 끝남 · 주황 진행 · 빨강 손이 필요). */
  const parts = [{n:2,tone:'bad',label:'미응시'},{n:0,tone:'warn',label:'재시'},
                 {n:6,tone:'ok',label:'통과'},{n:2,tone:'none',label:'아직'}];
  const bar = ctx.stackBar(parts);
  // 0 인 칸이 1px 로 남으면 없는 것을 있다고 읽는다
  chk('0 인 칸은 그리지 않는다', (bar.match(/<i /g)||[]).length, 3);
  const w = (bar.match(/width:([\d.]+)%/g)||[]).map(x => parseFloat(x.slice(6)));
  chk('너비의 합이 100%', Math.round(w.reduce((a,b) => a+b, 0)), 100);
  chk('빈 것에도 안 죽는다', /class="stack"><\/div>/.test(ctx.stackBar([])), true);
  // 색만 있고 이름이 없으면 무슨 색이 무엇인지 물어야 한다
  const lg = ctx.legendOf(parts);
  chk('범례가 색마다 이름을 붙인다',
      /미응시 2/.test(lg) && /통과 6/.test(lg) && !/재시/.test(lg), true);
  const h = ctx.histo([5, 15, 55, 95, 95]);
  chk('분포는 열 칸', (h.match(/<i /g)||[]).length, 10);
  chk('50% 미만은 붉게', (h.match(/class="hot"/g)||[]).length, 5);
  chk('점은 있는 것만 켠다',
      (ctx.dotsOf([{on:true,label:'ㄱ'},{on:false,label:'ㄴ'},{on:'half',label:'ㄷ'}])
        .match(/dot (on|half)/g)||[]).length, 2);
  chk('비율은 0~100 을 벗어나지 않는다',
      [/(\d+)%<\/span>/.exec(ctx.donut(-5))[1], /(\d+)%<\/span>/.exec(ctx.donut(140))[1]], ['0','100']);
  const body = SRC.split('<script>')[1] || '';
  chk('대시보드에도 그림 자리가 있다', /id="dashFig"/.test(SRC), true);
  /* 칩과 그림이 따로 그려지면 두 숫자가 어긋난다. 같은 배열을 같은 순간에 본다.
     다른 것은 하나뿐이다 — 칩은 미룬 것을 빼고(오늘 할 일), 그림은 넣는다(반 상태).
     그래서 그림 쪽에 미룬 수를 적는다. 안 적으면 둘이 틀린 것처럼 보인다. */
  chk('칩과 그림이 같은 순간에 그려진다',
      /function renderJump\(\)\{[\s\S]{0,400}?renderFig\(\);/.test(body), true);
  chk('그림은 미룬 것도 세고, 몇 명인지 적는다', /미룬 '\+snz\+'명 포함/.test(body), true);
}

console.log('\n── 자료는 실제로 있는 것만 건다 ──');
{
  /* 화학Ⅱ 는 문제지·OMR 이 18회까지 있는데 해설 HTML 은 7회까지뿐이다.
     회차 번호로 주소를 지어내면 눌러 본 뒤에야 404 를 만난다. */
  const body = SRC.split('<script>')[1] || '';
  chk('DT 가 만든 목록을 읽는다', /fetch\('\.\.\/DT\/materials\.json'/.test(body), true);
  chk('주소를 지어내지 않는다',
      /['"](munje|haeseol|omr)_['"]?\s*\+|['"](munje|haeseol|omr)_\$\{/.test(CODE_ONLY), false);
  chk('못 읽으면 이유를 적는다', /materials\.json\)을 못 읽었습니다/.test(body), true);
  chk('강의 목차도 베끼지 않고 읽는다', /fetch\('lecture-index\.html'/.test(body), true);
  chk('갈래가 여섯', ((body.match(/const MAT_GROUPS = \[([\s\S]*?)\];/)||['',''])[1]
      .match(/key:'/g)||[]).length, 6);

  /* 도구 목록은 손으로 적은 유일한 곳이다. 그 파일이 실제로 있는지 본다 —
     페이지 이름이 바뀌거나 지워지면 셸에서 404 로 이어진다. */
  const tools = ((SRC.match(/const MAT_TOOLS = \[([\s\S]*?)\n\];/)||['',''])[1]
    .match(/path:'([^']+)'/g)||[]).map(x => x.slice(6, -1));
  chk('도구를 스무 개쯤 걸어 뒀다', tools.length >= 15, true);
  const gone = tools.filter(t => !fs.existsSync(path.join(ROOT, t)));
  chk('거는 파일이 실제로 있다', gone, []);
}

console.log('\n── 첫 화면 잠금 ──');
{
  /* 주소만 알면 아무나 들어와 반 명단과 점수를 볼 수 있다. 지나가다 눌러 보는
     사람을 막는 문고리다 — 암호가 아니다(소스에 코드가 그대로 있다). */
  const body = SRC.split('<script>')[1] || '';
  const FIN_SRC = fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8');
  chk('셸도 코드를 묻는다', /function hubGate\(then\)/.test(body), true);
  const key = (body.match(/var KEY = '([^']+)', CODE = '([^']+)'/) || []).slice(1, 3);
  const fkey = (FIN_SRC.match(/var KEY = '([^']+)', CODE = '([^']+)'/) || []).slice(1, 3);
  /* 열쇠칸과 코드가 갈라지면 셸에서 넣고 iframe 안의 파이널에서 또 묻는다 —
     화면이 두 겹으로 잠겨 아무것도 못 한다. */
  chk('열쇠칸과 코드가 파이널과 같다', key, fkey);
  chk('코드는 0000', key[1], '0000');
  /* 못 들어올 사람 때문에 앱스크립트를 두드릴 이유가 없고, 잠긴 화면에 반
     명단이 잠깐 스치는 것도 안 된다. */
  chk('맞히기 전에는 아무것도 안 부른다', /hubGate\(boot\);/.test(body), true);
  chk('부르는 것은 모두 boot 안에 있다',
      /function boot\(\)\{[\s\S]*?loadRoster\(\);[\s\S]*?\n\}/.test(body), true);
  chk('시험 목록이 늦게 와도 잠금을 넘지 않는다', /if\(!BOOTED\) return;/.test(body), true);
}

console.log('\n── 반별 인원 · 수입 ──');
{
  /* "이번 달 몇 명이지" 는 매일 나오는 물음인데 반 탭까지 들어가야 알 수 있었다. */
  const body = SRC.split('<script>')[1] || '';
  chk('대시보드에 반별 인원 자리가 있다', /id="dashRoster"/.test(SRC), true);
  chk('수입 탭 자리가 있다', /id="t-inc"/.test(SRC) && /id="p-inc"/.test(SRC), true);

  /* 한 학생이 화학Ⅰ·Ⅱ 를 다 들으면 **자리는 2, 사람은 1** 이다. 수업료는 반
     단위라 총액은 자리로 세지만, 둘을 뭉뚱그리면 "42명인데 왜 44명분이지" 를
     매달 다시 헤아리게 된다. */
  ctx.DT_CACHE = { 'dt:names': { val: Object.assign([], { classes: [
    { label:'화학1 토', course:'ch1', students:[{name:'가'},{name:'나'},{name:'다'}] },
    { label:'화학2 일', course:'ch2', students:[{name:'가'},{name:'라'}] },
  ] }) } };
  const d = ctx.rosterCount();
  chk('자리는 반 등록 수', d.seats, 5);
  chk('사람은 겹치는 이름을 지운다', d.heads, 4);
  chk('반마다 인원이 나온다', d.rows.map(r => [r.label, r.n]), [['화학1 토',3],['화학2 일',2]]);
  chk('총액은 자리 × 수업료', d.monthly, 5 * ctx.FEE_PER);
  chk('수업료는 16만원', ctx.FEE_PER, 160000);
  chk('빈 이름은 사람으로 안 센다', (function(){
    ctx.DT_CACHE = { 'dt:names': { val: Object.assign([], { classes:[
      { label:'X', course:'ch1', students:[{name:''},{name:'  '},{name:'마'}] }] }) } };
    return ctx.rosterCount().heads; })(), 1);
  chk('명단이 없으면 0', (function(){ ctx.DT_CACHE = {}; const x = ctx.rosterCount();
    return [x.seats, x.heads, x.monthly]; })(), [0, 0, 0]);
  chk('돈은 세 자리마다 끊는다', ctx.wonOf(160000), '160,000원');

  /* 추정을 결산으로 읽으면 사고가 난다 — 화면이 그렇게 말해야 한다. */
  chk('추정이라고 적는다', /추정치입니다\. 실제 수납·미납은 반영되지 않습니다/.test(SRC), true);
  chk('자리와 사람의 차이를 적는다', /한 학생이 두 반을 들으면[\s\S]{0,80}자리<\/b>는 2/.test(SRC), true);

  /* ── 수입 탭만 한 번 더 묻는다 ────────────────────────────────────
     셸 잠금(0000)은 채점하는 날 내내 열려 있다. 화면을 켜 둔 채 자리를 비우거나
     학생이 옆에 서 있으면 금액이 그대로 보인다. */
  chk('수입 탭에 따로 코드가 걸린다', /const INC_CODE = '1233';/.test(body), true);
  chk('셸 잠금과 다른 코드', /var KEY = 'chemistreal:gate', CODE = '0000'/.test(body) &&
      /const INC_CODE = '1233'/.test(body), true);
  chk('통과 전에는 숫자를 안 그린다', /if\(!INC_OPEN\)\{[\s\S]{0,200}cards\.innerHTML = '';/.test(body), true);
  /* 90일을 기억해 두면 문고리를 다는 뜻이 없어진다 — 새로고침하면 다시 묻는다. */
  chk('통과 표시를 저장하지 않는다', /localStorage[\s\S]{0,60}INC_OPEN/.test(CODE_ONLY), false);
  chk('탭에 들어올 때마다 다시 그린다', /if\(id === 'inc'\) renderIncome\(\);/.test(body), true);

  /* 수입은 명단·점수와 종류가 다르다. 그 창구만 토큰을 받고, 토큰은 공개
     페이지에 적어 두지 않는다(적어 두면 토큰을 두는 뜻이 없다). */
  chk('수입 창구는 토큰을 받는다', /readOnce\('dt', 'income'[\s\S]{0,80}t:INC_TOKEN/.test(body), true);
  chk('토큰을 저장하지 않는다', /localStorage[\s\S]{0,60}INC_TOKEN/.test(CODE_ONLY), false);
  chk('토큰이 없으면 부르지 않는다', /if\(!INC_TOKEN\) return Promise\.reject/.test(body), true);

  /* 지난달 인원은 명단이 덮이는 순간 사라진다 — 추이는 지나간 뒤에 못 만든다. */
  chk('추이는 시트가 남긴다고 적는다', /매달 1일에 한 줄씩 남깁니다/.test(SRC), true);
}

console.log('\n── 색이 실제로 읽히는가 (눈이 아니라 재서) ──');
{
  /* "괜찮아 보인다"는 근거가 아니다. 밝기를 낮춘 화면·나이든 눈·색약에서
     무너지는 것은 재 봐야 안다. 예전 --muted 는 3.52:1 로 본문 기준(4.5)에
     못 미쳤고, 그 색이 힌트·카드 라벨·목록 부연 등 작은 글씨 전부에 쓰였다. */
  const V = {};
  (SRC.match(/--[a-zA-Z0-9-]+:\s*#[0-9A-Fa-f]{6}/g) || []).forEach(m => {
    const i = m.indexOf(':'); V[m.slice(2, i).trim()] = m.slice(i + 1).trim();
  });
  const lin = c => (c /= 255) <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  const lum = h => { h = h.replace('#', '');
    const p = i => lin(parseInt(h.slice(i, i + 2), 16));
    return 0.2126 * p(0) + 0.7152 * p(2) + 0.0722 * p(4); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b);
    return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const bg = V.bg;
  chk('색 이름을 읽어 왔다', [!!bg, !!V.muted, !!V.warnG].every(Boolean), true);
  chk('작은 글씨가 본문 기준(4.5)을 넘는다', ratio(V.muted, bg) >= 4.5, true);
  chk('본문색도 넉넉하다', ratio(V['ink-2'], bg) >= 4.5, true);
  // 막대·점은 글자가 아니라 그림이다 — 3:1 이 최소다
  chk('그림용 주황이 그래픽 기준(3.0)을 넘는다', ratio(V.warnG, bg) >= 3, true);
  chk('초록도 넘는다', ratio(V.ok, bg) >= 3, true);
  chk('빨강도 넘는다', ratio(V.ms, bg) >= 3, true);
  /* ⚠ 여기가 핵심이다. 주황을 아무리 어둡게 해도 초록·빨강과의 명도 차는
     1.0~1.2 밖에 안 된다 — 적록색약에게는 여전히 같은 색이다. 색조를 만지는
     것으로는 못 고친다. 그래서 색이 아닌 단서가 반드시 있어야 한다. */
  chk('색만으로는 못 가른다(그래서 아래가 필요하다)',
      ratio(V.warnG, V.ok) < 2 && ratio(V.warnG, V.ms) < 2, true);
  chk('막대 칸 사이에 흰 구분선이 있다',
      /box-shadow:1px 0 0 var\(--paper\) inset/.test(SRC), true);
  chk('진행 중 칸에 빗금이 있다',
      /\.stack i\.warn\{[\s\S]{0,200}repeating-linear-gradient/.test(SRC), true);
  chk('점은 채움·반채움·빈칸으로 갈린다',
      /\.dot\.half\{[\s\S]{0,160}linear-gradient/.test(SRC) &&
      /\.dot\{[\s\S]{0,200}background:transparent/.test(SRC), true);
  chk('범례에도 같은 빗금을 쓴다',
      /\.legend b\.warn\{[\s\S]{0,200}repeating-linear-gradient/.test(SRC), true);
  /* 숫자 여덟 개가 모두 강조색이면 색이 강조가 아니라 배경이 된다. */
  chk('평상시 숫자는 먹빛', /\.card b\{[^}]*color:var\(--ink\)/.test(SRC), true);
  chk('급한 숫자만 색', /\.card\.warn b\{color:var\(--ms\)\}/.test(SRC), true);
}

console.log('\n── 주소가 곧 상태 ──');
{
  const body = SRC.split('<script>')[1] || '';
  chk('주소를 쓰는 길이 있다', /function writeHash\(\)/.test(body), true);
  chk('주소를 읽는 길이 있다', /function applyHash\(\)/.test(body), true);
  // 탭을 옮길 때마다 기록이 쌓이면 뒤로가기가 브라우저를 못 빠져나간다
  chk('뒤로가기 기록을 쌓지 않는다',
      /history\.replaceState/.test(body) && !/history\.pushState/.test(body), true);
  chk('되돌려 읽는 동안은 안 쓴다', /if\(HASH_LOCK\) return;/.test(body), true);

  ctx.location = { hash:'#stu?f=noexam&q=%ED%9C%98%EB%AC%B8' };
  chk('탭과 조건을 되읽는다', ctx.readHash(), { tab:'stu', p:{ f:'noexam', q:'휘문' } });
  ctx.location = { hash:'#cls?c=%ED%99%94%ED%95%992%20%EC%9D%BC' };
  chk('반 이름의 빈칸도 살아 돌아온다', ctx.readHash().p.c, '화학2 일');
  ctx.location = { hash:'#nope?x=1' };
  chk('모르는 탭은 무시한다', ctx.readHash(), null);
  ctx.location = { hash:'' };
  chk('빈 주소도 안 죽는다', ctx.readHash(), null);
  chk('고른 것이 바뀌면 주소도 바뀐다', (body.match(/writeHash\(\);/g) || []).length >= 6, true);
}

console.log('\n── 보낸 것은 눈에서 내려간다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  chk('보낸 줄을 기억한다', /const SENT = new Set\(\);/.test(body), true);
  /* 열쇠는 목록 **번호**가 아니라 사람이다 — 번호로 만들면 다시 불러올 때
     밀려서 엉뚱한 줄이 흐려진다. */
  chk('열쇠는 번호가 아니라 사람', ctx.sentKey('pend', '김 지성', 'ch1', 12), 'pend|김지성|ch1|12');
  chk('빈 값에도 안 죽는다', ctx.sentKey('abs', null), 'abs|||');
  chk('누르면 그 줄에 표시한다', /row\.classList\.add\('sent'\)/.test(body), true);
  chk('다시 그려도 남는다', /function sentCls\(k\)/.test(body) && /SENT\.has\(k\)/.test(body), true);
  chk('브라우저에 남기지 않는다', /localStorage[\s\S]{0,40}SENT/.test(CODE_ONLY), false);

  /* ── 기기를 넘어 남는다 ────────────────────────────────────────────
     화면에서만 살면 새로고침에 사라지고 다른 기기에서는 안 보인다. 브라우저에
     적으면 기기마다 답이 달라진다 — 이 시스템이 피하려는 바로 그 모양이다.
     그래서 시트다. 그런데 **셸은 여전히 쓰지 않는다** — DT 화면에 시킨다. */
  chk('시트에서 읽어 온다', /function dtSentLog\(force\)/.test(body) &&
      /readOnce\('dt', 'sentlog'/.test(body), true);
  chk('받은 것을 화면에 입힌다', /function seedSent\(rows\)/.test(body), true);
  /* 시트 응답은 늦게 온다. 그 사이에 누른 것이 있으면 비우는 순간 사라진다 —
     방금 보낸 사람이 안 보낸 것처럼 되돌아온다. */
  chk('늦게 온 시트가 방금 누른 것을 지우지 않는다',
      /function seedSent\(rows\)\{\s*\n\s*\(rows\|\|\[\]\)\.forEach/.test(body), true);
  chk('셸이 직접 쓰지 않는다 — DT 에 시킨다',
      /w\.markSent\(\{ kind:p\[0\]/.test(body), true);
  chk('일괄로 보낸 것도 적는다',
      /left\.forEach\(function\(r\)\{[\s\S]{0,200}w\.markSent\(/.test(body), true);
  chk('앱스크립트에 POST 하지 않는다', /method\s*:\s*['"]POST/i.test(body), false);
  /* 잘못 눌렀으면 무를 수 있다. 보낸 표시는 로그라 지울 수 있으므로, 5초
     기다리게 하는 것보다 되돌릴 수 있게 두는 편이 낫다. */
  chk('무르는 길이 있다', /function sentUndo\(k\)/.test(body) &&
      /w\.unmarkSent\(/.test(body), true);
  chk('보낸 줄에만 무르기가 뜬다',
      /return SENT\.has\(k\) \? '<button class="mini undo"/.test(body), true);
  /* ⚠ 앱스크립트는 실행을 한 줄로 세운다. 꾸미는 창구까지 한꺼번에 부르면
     줄이 30초까지 길어지고 그동안 **다른 화면이 실패한다** — 실제로 명단
     화면이 기본 명단으로 되돌아가 덮어쓸 뻔했다. 뒤에 하나씩 세운다. */
  chk('꾸미는 창구는 줄 뒤에', /function laterOnce\(\)/.test(body) &&
      /dtSentLog\(\)\.then\(function\(rows\)\{ seedSent\(rows\); refreshSoon\(\); \}/.test(body), true);
  chk('한꺼번에 안 부른다', /steps\.reduce\(function\(p, f\)\{/.test(body), true);
  chk('한 번만 건다', /if\(LATER_DONE\) return;/.test(body), true);
  chk('못 받아도 화면은 산다', /f\(\)\.catch\(function\(\)\{\}\)/.test(body), true);
}

console.log('\n── 안 한 것이 떠오르게 (넛지) ──');
{
  const body = SRC.split('<script>')[1] || '';
  const D = 86400000, now = Date.now();
  /* 미루기는 선생님이 **누른** 것만 미룬다. 그런데 잊은 것은 대개 누른 적이
     없다 — 아무도 안 누른 것을 짚는 자리가 없었다. */
  chk('자리가 있다', /id="nudge"/.test(SRC), true);

  ctx.SENT.clear(); ctx.SNZ.clear();
  ctx.PEND_ROWS = [
    { name:'최예린', course:'ch1', round:12, days:9, score:68 },   // 오래됐고 안 보냄
    { name:'박서준', course:'ch1', round:12, days:2, score:70 },   // 아직 이르다
    { name:'김도윤', course:'ch1', round:11, days:20, score:55 },  // 오래됐지만 보냈다
  ];
  ctx.SENT.add(ctx.sentKey('pend', '김도윤', 'ch1', 11));
  ctx.DT_CACHE = {
    'dt:sentlog': { val: [
      /* 보낸 지 오래인데 아직 안 열어 봤다 */
      { kind:'pass', name:'김지성', course:'ch2', round:7, ts: now - 5*D },
      /* 보내고 나서 열어 봤다 — 짚을 것이 없다 */
      { kind:'pend', name:'한지우', course:'ch1', round:9, ts: now - 6*D },
      /* 어제 보냈다 — 아직 기다릴 때다 */
      { kind:'pend', name:'오승민', course:'ch1', round:9, ts: now - 1*D },
    ] },
    'dt:views': { val: [ { name:'한지우', ts: now - 2*D } ] },
  };
  const n = ctx.nudges();
  console.log('  ' + JSON.stringify(n.map(function(x){ return [x.kind, x.name, x.days]; })));
  chk('보냈는데 안 열어 본 사람을 짚는다',
      n.some(function(x){ return x.name==='김지성' && x.kind==='안 열어 봄'; }), true);
  /* 보낸 **뒤에** 열었어야 한다 — 지난달에 한 번 열어 본 것으로 이번 문자를
     읽었다고 칠 수는 없다. 여기서는 보낸 뒤에 열었으니 짚지 않는다. */
  chk('열어 본 사람은 안 짚는다', n.some(function(x){ return x.name==='한지우'; }), false);
  chk('어제 보낸 것은 아직 안 짚는다', n.some(function(x){ return x.name==='오승민'; }), false);
  chk('오래 밀린 재시를 짚는다',
      n.some(function(x){ return x.name==='최예린' && x.kind==='아직 안 보냄'; }), true);
  chk('며칠 안 된 것은 안 짚는다', n.some(function(x){ return x.name==='박서준'; }), false);
  /* 이미 보낸 것을 다시 짚으면 넛지를 안 믿게 된다. */
  chk('이미 보낸 것은 안 짚는다', n.some(function(x){ return x.name==='김도윤'; }), false);
  chk('오래된 것이 위에 선다', n.map(function(x){ return x.days; }),
      n.map(function(x){ return x.days; }).slice().sort(function(a,b){ return b-a; }));

  /* 보낸 **뒤에** 열었는지로 가린다. 이 규칙이 없으면 "지난달에 열어 봤으니
     됐다" 가 되어 이번 문자를 안 읽은 집을 놓친다. */
  ctx.DT_CACHE['dt:views'] = { val: [ { name:'김지성', ts: now - 9*D } ] };
  chk('보내기 전에 열어 본 것은 안 친다',
      ctx.nudges().some(function(x){ return x.name==='김지성'; }), true);

  /* '무시' 는 미루기를 그대로 쓴다 — 새로 저장할 곳을 만들지 않는다. */
  chk('무시는 미루기를 쓴다', /w\.snoozeStu\(\{ kind:p\[0\], name:p\[1\], course:p\[2\], round:p\[3\], until:until \}\)/.test(body), true);
  chk('무시한 것은 내려간다', (function(){
    const k = ctx.ndgKey('pend', '최예린', 'ch1', 12);
    ctx.SNZ.set(k, ctx.dayKey(7));
    return ctx.nudges().some(function(x){ return x.name==='최예린'; }); })(), false);
  /* 열쇠가 보낸 표시와 겹치면, 넛지를 무시했다고 문자까지 미룬 것이 된다. */
  chk('열쇠가 보낸 표시와 겹치지 않는다',
      ctx.ndgKey('pend','최예린','ch1',12) !== ctx.sentKey('pend','최예린','ch1',12), true);
  /* 여섯 줄이 넘으면 그것도 훑고 만다. */
  chk('너무 많으면 줄이고 몇 건인지 적는다',
      /all\.slice\(0, NDG_MAX\)/.test(body) && /외 '\+\(all\.length-NDG_MAX\)\+'건/.test(body), true);
  /* 이 창구는 진작 열려 있었는데 셸이 안 읽고 있었다 — 아침 메일만 쓰고 있었다. */
  chk('열람 창구를 읽는다', /function dtViews\(force\)/.test(body) &&
      /readOnce\('dt', 'views'/.test(body), true);
  chk('못 받아도 나머지는 뜬다', /dtViews\(\)\.then\(function\(\)\{ renderNudge\(\); \}\)/.test(body) &&
      /f\(\)\.catch\(function\(\)\{\}\)/.test(body), true);
  /* 급한 것이 실패해도 기다림은 끝나야 한다 — 여기서 멈추면 보낸 표시가
     영영 안 붙는다. */
  chk('급한 것이 실패해도 이어 간다',
      /dtRoster\(\)\.catch\(function\(\)\{\}\), dtPending\(\)\.catch/.test(body), true);
  ctx.SNZ.clear(); ctx.SENT.clear(); ctx.DT_CACHE = {}; ctx.PEND_ROWS = [];
}

console.log('\n── 어느 오답으로 쏠렸나 (문항 분석) ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 화학은 오답 선택지가 곧 오개념이다(몰 vs 질량, 산화수 부호). 정답률은
     '틀렸다' 를 말하지만 어느 오답을 골랐는지는 '왜' 를 말한다. */
  chk('회차에서 들어가는 길이 있다', /data-rnd="ana"/.test(body), true);
  /* ⚠ 그 계산은 **파이널 앱이 이미 하고 있다**(성적표의 '누적 정답률 · 선택지
     분석'). 여기에 다시 만들면 두 벌이 갈라지고 어느 쪽이 맞는지 물어야 한다.
     없던 것은 계산이 아니라 들어가는 길이었다. */
  chk('여기서 다시 계산하지 않는다',
      /qopt|qdisc|선택지 분포를 센다/.test(CODE_ONLY), false);
  chk('이미 있는 길을 그대로 탄다',
      /const r = RND_OPEN\.rows\.filter\(function\(x\)\{ return x\.ans; \}\)\[0\];[\s\S]{0,120}openReport\(r, b\)/.test(body), true);
  /* 답안이 없으면 성적표를 못 연다 — 단추를 내놓고 눌러도 아무 일이 없으면
     고장으로 읽는다. */
  chk('답안이 있을 때만 내놓는다',
      /const anaOK = g\.rows\.some\(function\(r\)\{ return r\.ans; \}\);/.test(body) &&
      /\(anaOK \? '<div class="note2">/.test(body), true);
  chk('없으면 그렇게 말한다', /flash\(b, '답안 없음'\)/.test(body), true);
  /* 누구 성적표로 열든 같은 그림이라는 것을 안 적으면, 그 학생 개인 분석으로
     읽고 "왜 얘 걸로 보지" 가 된다. */
  chk('반 전체 기록임을 적는다', /반 전체 기록<\/b>으로 그리므로/.test(body), true);
}

console.log('\n── 상담지 한 장 ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 학부모 상담은 매주 돌아온다. 자료는 이미 셸이 다 들고 있는데 **종이로
     나가는 길만** 없어서, 그때마다 세 앱을 오가며 손으로 옮겨 적었다. */
  chk('자리가 있다', /id="print"/.test(SRC), true);
  chk('단추가 카드에 있다', /id="dlgPrint"/.test(SRC), true);
  /* 화면 것을 그대로 인쇄하면 잉크만 먹고 안 읽힌다. <dialog> 는 브라우저마다
     다르게 잘린다 — 인쇄할 것만 따로 짓는다. */
  chk('화면에는 안 보인다', /#print\{display:none\}/.test(SRC), true);
  chk('인쇄할 때만 나온다',
      /@media print\{[\s\S]{0,400}body > \*\{display:none !important\}[\s\S]{0,120}#print\{display:block !important\}/.test(SRC), true);
  chk('A4 한 장', /@page\{size:A4/.test(SRC), true);
  chk('검정 글씨로', /#print \*\{color:#000 !important/.test(SRC), true);
  /* 상담은 말로 한다. 적을 자리가 없으면 종이 뒤에 적게 된다. */
  chk('적을 자리를 남긴다', /상담 메모<\/h2><div class="memo">/.test(body), true);
  /* 언제·무엇을 바탕으로 한 종이인지 안 적으면, 나중에 숫자가 달라졌을 때
     어느 시점 기록인지 알 길이 없다. */
  chk('무엇을 바탕으로 했는지 적는다',
      /파이널 채점 기록 · DT 시트 기준/.test(body) && /최근 2주/.test(body), true);

  /* 상담지에만 있는 계산을 두면 화면과 종이가 어긋나고, 어긋나면 어느 쪽이
     맞는지 물어야 한다. 화면이 쓰는 것을 그대로 쓴다. */
  chk('화면이 쓰는 것을 그대로 쓴다',
      /const fin = finFor\(r\), d = dtForStudent\(r\), km = kmForStudent\(r\);/.test(body), true);

  ctx.DT_CACHE = { 'dt:mistags': { val: [
    { name:'김지성', school:'휘문중', course:'ch1', round:5, tags:['몰농도','완충'] },
    { name:'김지성', school:'휘문',   course:'ch2', round:7, tags:['몰농도'] },
    { name:'박서준', school:'과천중', course:'ch1', round:5, tags:['산화수'] },
  ] } };
  const m = ctx.prMis({ name:'김지성', school:'휘문중' });
  chk('이 학생 것만 모은다', m.map(function(x){ return [x.tag, x.n]; }), [['몰농도',2],['완충',1]]);
  /* 학교 표기가 '휘문' 과 '휘문중' 으로 흔들려도 같은 아이다. */
  chk('학교 표기가 흔들려도 센다', (m.filter(function(x){ return x.tag==='몰농도'; })[0]||{}).n, 2);
  chk('남의 개념은 안 붙인다', m.some(function(x){ return x.tag==='산화수'; }), false);
  chk('기록이 없으면 빈 목록', ctx.prMis({ name:'없는학생', school:'X중' }), []);
  ctx.DT_CACHE = {};
}

console.log('\n── 또래 대비 크게 벗어난 점수 (MAD) ──');
{
  /* "60점 밑" 같은 고정 기준은 늘 같은 아이만 부른다 — 그 아이가 이번에
     잘 봤는지 못 봤는지는 말해 주지 않는다. */
  chk('가운데 값', [ctx.median([1,2,3]), ctx.median([1,2,3,4]), ctx.median([])], [2, 2.5, null]);
  const cls = [88,90,86,92,89,41].map(function(v,i){
    return { name:'학생'+i, score:v, course:'ch1', round:5 }; });
  const o = ctx.madOutliers(cls);
  console.log('  ' + JSON.stringify(o.map(function(x){ return [x.name, x.score, x.mid, x.z]; })));
  chk('또래에서 크게 벗어난 사람을 짚는다', o.map(function(x){ return x.name; }), ['학생5']);
  chk('중앙값도 같이 말해 준다', o[0].mid, 88.5);
  chk('몇 명과 견줬는지 말해 준다', o[0].n, 6);

  /* 평균·표준편차로 재면 크게 낮은 한 명이 기준선을 같이 끌어내려 **자기
     자신을 못 잡는다.** 중앙값·MAD 는 그렇지 않다 — 그게 이 방법을 쓰는 이유다. */
  chk('한 명 때문에 기준이 흔들리지 않는다', (function(){
    const avg = cls.reduce(function(t,x){ return t+x.score; },0)/cls.length;
    const sd = Math.sqrt(cls.reduce(function(t,x){ return t+(x.score-avg)*(x.score-avg); },0)/cls.length);
    return Math.abs((41-avg)/sd) < 3;      // 평균 기준으로는 3을 못 넘는다
  })(), true);

  /* 사람이 적으면 중앙값 자체가 흔들린다. */
  chk('사람이 적으면 안 부른다', ctx.madOutliers([
    { name:'ㄱ', score:90, course:'ch1', round:9 }, { name:'ㄴ', score:20, course:'ch1', round:9 },
  ]), []);
  /* MAD 가 0 이면(다 같은 점수) 나눌 수가 없다 — 한 명만 달라도 무한대가 된다. */
  chk('다 같은 점수면 안 부른다', ctx.madOutliers(
    [90,90,90,90,90,30].map(function(v,i){ return { name:'x'+i, score:v, course:'ch1', round:9 }; })), []);
  /* 잘 본 것은 챙길 일이 아니다. */
  chk('위로 벗어난 것은 안 부른다', ctx.madOutliers(
    [40,42,38,41,39,99].map(function(v,i){ return { name:'y'+i, score:v, course:'ch1', round:9 }; })), []);
  /* 회차가 다르면 다른 시험이다 — 섞어서 재면 아무 뜻이 없다. */
  chk('회차를 섞지 않는다', ctx.madOutliers(
    [90,91,89,92,88].map(function(v,i){ return { name:'a'+i, score:v, course:'ch1', round:1 }; })
    .concat([30,31,29].map(function(v,i){ return { name:'b'+i, score:v, course:'ch1', round:2 }; }))), []);
  chk('점수가 없는 줄은 건너뛴다', ctx.madOutliers(
    [{ name:'ㄱ', course:'ch1', round:3 }, { name:'ㄴ', score:'', course:'ch1', round:3 }]), []);

  /* 넛지 자리에 함께 선다 — '무시' 도 그대로 쓴다. */
  const body = SRC.split('<script>')[1] || '';
  chk('넛지로 함께 세운다', /kind: '또래 대비'/.test(body), true);
}

console.log('\n── 막대에서 목록으로 파고든다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 여태 막대는 보기만 하는 것이었다. "미응시 4명" 을 보고 나서 그 넷이
     누구인지 알려면 목록을 눈으로 훑어야 했다. */
  const parts = ctx.clsCounts([{ st:'miss' },{ st:'miss' },{ st:'wait' },{ st:'ok' }]);
  chk('조각마다 열쇠가 붙는다', parts.map(function(p){ return p.key; }),
      ['miss','wait','ok','none']);
  /* 이름(label)으로 걸면 이름을 고치는 날 저장해 둔 주소가 깨진다. */
  chk('열쇠는 이름이 아니다', parts[0].key !== parts[0].label, true);

  /* 서른 명 중 하나짜리 조각은 폭이 10px 도 안 된다 — 손가락으로 못 짚는다.
     이름이 붙은 범례가 훨씬 크다. */
  const lg = ctx.legendOf(parts, 'cls', 'miss');
  chk('범례를 누를 수 있다', /<button class="lg on" data-seg="cls" data-segv="miss"/.test(lg), true);
  chk('지금 고른 것을 알려 준다', /aria-pressed="true"/.test(lg), true);
  chk('안 고른 것은 눌린 티가 없다', (lg.match(/aria-pressed="false"/g)||[]).length, 2);
  /* 열쇠가 없는 막대(예: 반 상태 그림)는 그냥 보는 것으로 둔다. */
  chk('열쇠가 없으면 못 누른다', /<button/.test(ctx.legendOf([{n:1,tone:'ok',label:'통과'}])), false);
  chk('손가락 자리를 넓힌다', /\.legend button\.lg\{[\s\S]{0,400}?min-height:32px/.test(SRC), true);
  /* 마우스로는 조각도 되게 한다. */
  chk('막대 조각에도 같은 열쇠', /data-seg="cls" data-segv="miss"/.test(ctx.stackBar(parts)), true);

  /* 같은 것을 다시 누르면 풀린다 — 끄는 길을 따로 찾게 하지 않는다. */
  chk('다시 누르면 풀린다', /CLS_ST = \(CLS_ST === v\) \? '' : v/.test(body) &&
      /CON_CLS = \(CON_CLS === v\) \? '' : v/.test(body), true);
  /* 걸러 놓은 것을 안 적으면 "왜 애가 넷밖에 없지" 가 된다. */
  chk('걸러 놓은 것을 적는다', /만 보는 중 · <b>/.test(body), true);
  chk('푸는 길을 그 자리에 둔다', /data-seg="cls" data-segv=""/.test(body), true);
  /* 다른 반·다른 개념에서 넘어온 주소면 걸린 것이 그 자리에 없을 수 있다.
     빈 목록을 놓고 "왜 아무도 없지" 하게 두지 않는다. */
  chk('없는 것을 걸었으면 스스로 푼다',
      /if\(CLS_ST && !all\.some\(function\(r\)\{ return r\.st===CLS_ST; \}\)\) CLS_ST = '';/.test(body) &&
      /if\(CON_CLS && !parts\.some\(function\(x\)\{ return x\.key===CON_CLS; \}\)\) CON_CLS = '';/.test(body), true);

  /* 주소가 곧 상태라, 걸러 놓은 채로 저장·공유가 된다. */
  chk('주소에 남는다', /p\.push\('s='\+CLS_ST\)/.test(body) &&
      /p\.push\('c='\+encodeURIComponent\(CON_CLS\)\)/.test(body), true);
  chk('주소에서 되살린다', /CLS_ST = st\.p\.s \|\| '';/.test(body) &&
      /CON_CLS = st\.p\.c \|\| '';/.test(body), true);
  chk('저장한 보기 이름에도 들어간다',
      ctx.viewName({ tab:'cls', p:{ c:'화학1 토1:30', s:'miss' } }), '반 · 화학1 토1:30 · 미응시');
}

console.log('\n── 늘 묻는 것은 칩 하나로 (저장된 보기) ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 선생님이 묻는 것은 매번 새롭지 않다 — "3반 지금 어때", "몰농도 못 잡은
     애들". 그런데 매번 탭 옮기고 고르고 거르는 여섯 번을 되풀이한다. */
  chk('자리가 있다', /id="views"/.test(SRC), true);
  /* 주소가 이미 상태다. 저장할 것은 주소 한 줄, 되살리는 길도 이미 있다. */
  chk('만들 그릇이 없다 — 주소를 적는다',
      /v\.unshift\(\{ name: viewName\(\), hash: h \}\)/.test(body), true);
  chk('되살리는 길도 이미 있는 것을 쓴다',
      /history\.replaceState\(null, '', t\.dataset\.view\);[\s\S]{0,60}applyHash\(\)/.test(body), true);

  /* 물어보면(prompt) 저장이 귀찮아지고, 귀찮으면 안 쓴다. 지금 화면에서 짓는다.
     셸에는 prompt 가 한 군데 더 있다(클립보드가 막힌 브라우저의 마지막 수단)
     — 그건 그대로 두고 이 함수 안만 본다. */
  const vadd = (body.match(/function viewAdd\(\)\{[\s\S]*?\n\}/) || [''])[0];
  chk('이름을 안 묻는다', /prompt\(/.test(vadd), false);
  chk('이름은 지금 화면에서 짓는다', /name: viewName\(\)/.test(vadd), true);
  chk('대시보드는 그냥 대시보드', ctx.viewName({ tab:'dash', p:{} }), '대시보드');
  chk('반은 반 이름까지', ctx.viewName({ tab:'cls', p:{ c:'화학1 토1:30' } }), '반 · 화학1 토1:30');
  chk('개념은 개념 이름까지', ctx.viewName({ tab:'con', p:{ tag:'몰농도' } }), '개념 · 몰농도');
  chk('거른 것도 이름에 넣는다', ctx.viewName({ tab:'stu', p:{ f:'noexam' } }), '학생 · 파이널 기록 없음');
  chk('찾던 말도 넣는다', ctx.viewName({ tab:'rnd', p:{ q:'12회' } }), '회차 · "12회"');
  chk('둘 다면 둘 다', ctx.viewName({ tab:'mat', p:{ g:'ch2', q:'해설' } }), '자료 · DT 화학Ⅱ · "해설"');
  /* '전체' 는 거른 것이 아니다 — 이름에 붙으면 저장한 보기가 다 길어진다. */
  chk('전체는 이름에 안 붙인다', ctx.viewName({ tab:'stu', p:{ f:'all' } }), '학생');

  /* 앱 화면(iframe)은 저장해도 뜻이 없다 — 그 안의 상태는 주소에 안 담긴다. */
  chk('앱 화면은 저장 못 한다', /function viewSavable\(\)\{ return !frameOf\(curTab\(\)\); \}/.test(body), true);
  /* 같은 주소를 두 번 저장하면 칩이 두 개가 되고, 어느 것이 최신인지 모른다. */
  chk('같은 화면을 두 번 안 담는다',
      /if\(v\.some\(function\(x\)\{ return x\.hash === h; \}\)\) return 'dup';/.test(body), true);
  /* 끝없이 쌓이면 칩 줄이 화면을 다 먹는다. */
  chk('끝없이 쌓이지 않는다', /v\.slice\(0, VIEW_MAX\)/.test(body), true);
  /* 지우기에 확인을 안 붙인다 — 세 번 눌러 다시 만들 수 있는 것이라,
     확인창이 지키는 것보다 걸리적거리는 값이 크다.
     ⚠ 예전에는 파일 전체에 confirm 이 없는지 봤는데, 그건 이 뜻보다 넓다.
     되돌릴 수 없는 것(손으로 적은 수업 문자를 파일로 덮어쓰기)에는 물어야
     한다. 여기서 지키려는 것은 **보기 지우기**뿐이므로 그 자리만 본다. */
  chk('보기 지우기에 확인창을 안 세운다', /\bconfirm\(/.test(cut('viewDel')), false);
  chk('열두 탭 밑에 묻히지 않는다 — 팔레트에도 오른다',
      /kind:'보기', label:v\.name/.test(body), true);
  chk('탭을 옮기면 어느 보기인지도 따라온다',
      /navReveal\(id\); navEdges\(\); renderViews\(\);/.test(body), true);
  /* 재어 보니 이 줄이 휴대폰 머리를 118 → 162px 로 되돌려 놨다. 세로가 가장
     아쉬운 화면에서, 아직 저장한 것도 없는 빈 줄에 44px 을 내주는 셈이었다. */
  chk('휴대폰에서는 쓰고 있을 때만 자리를 낸다',
      /function viewsNarrow\(\)/.test(body) &&
      /if\(!v\.length && !canAdd\)\{ el\.innerHTML = ''; el\.hidden = true; return; \}/.test(body), true);
  /* 클래스 선택자가 브라우저 기본 [hidden] 규칙을 이긴다. 이 한 줄이 없으면
     숨긴 줄이 그대로 서서 머리가 11px 도로 늘어난다 — 재어 보고 알았다. */
  chk('숨긴 줄이 진짜로 숨는다', /\.views\[hidden\]\{display:none\}/.test(SRC), true);
  chk('폭이 바뀌면 다시 그린다',
      /window\.addEventListener\('resize', function\(\)\{ navEdges\(\); renderViews\(\); \}\)/.test(body), true);
}

console.log('\n── 휴대폰에서도 탭이 다 보인다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 390px 에서 재어 보니 열두 탭 중 여섯만 보였다. 가로로 밀 수는 있는데
     막대를 숨겨 놔서 **더 있다는 표시가 아예 없었다** — 자료·수입·학습진단은
     있는 줄도 모르고 지나간다. */
  chk('잘린 쪽을 흐린다', /nav\.scr-l\{/.test(SRC) && /nav\.scr-r\{/.test(SRC), true);
  chk('양쪽 다 잘릴 수 있다', /nav\.scr-l\.scr-r\{/.test(SRC), true);
  /* 마스크는 스크롤되는 내용이 아니라 상자에 걸려야 가장자리에 머문다. */
  chk('사파리도 본다', /-webkit-mask-image:linear-gradient\(to right/.test(SRC), true);
  chk('잘리지 않으면 안 흐린다', /max > 2 && n\.scrollLeft > 4/.test(body), true);

  /* Cmd+K 로 '수입' 에 가면 화면은 바뀌는데 밑줄 그어진 탭이 화면 밖이라
     아무 일도 안 일어난 것처럼 보인다. */
  const nrv = (body.match(/function navReveal\(id\)\{[\s\S]*?\n\}/) || [''])[0];
  chk('고른 탭을 보이는 자리로', /function navReveal\(id\)/.test(body) &&
      /navReveal\(id\); navEdges\(\);/.test(body), true);
  /* 페이지까지 같이 밀면 보고 있던 자리를 잃는다 — 탭 줄만 민다.
     scrollIntoView 는 셸의 다른 자리에서도 쓰므로 이 함수 안만 본다. */
  chk('탭 줄만 민다', /scrollIntoView/.test(nrv), false);
  chk('탭 줄의 scrollLeft 만 건드린다', /n\.scrollLeft =/.test(nrv), true);
  /* 붙이는 기준은 밀고 난 결과(scrollLeft)가 아니다. 결과로 재면 마지막 탭을
     보이려고 13px 밀어 놓은 것을 도로 0 으로 되돌려 그 탭이 영영 안 보인다 —
     실제로 그렇게 깨져 있었고 브라우저 검사가 잡았다.
     ⚠ 그렇다고 `l < 40` 같은 상수로 재도 안 된다. 그 40 은 '보기' 라벨의 너비를
     손으로 옮겨 적은 숫자였고, 라벨 글씨를 10px→11.5px 로 올리자마자 첫 탭이
     40 을 넘겨 조용히 안 붙었다. 그래서 여기서는 **상수가 아니라 줄의 실제
     너비로 재는지**를 본다 — 라벨을 바꿔도 따라오는 조건이어야 한다. */
  chk('처음으로 붙일지를 줄 너비로 잰다', /n\.clientWidth[^)]*\) n\.scrollLeft = 0;/.test(nrv), true);
  chk('라벨 너비를 상수로 베껴 적지 않는다', /if\(l < \d+\)/.test(nrv), false);
  chk('밀고 난 결과로 재지 않는다', /if\(n\.scrollLeft < \d+\)/.test(nrv), false);
  chk('잠금이 풀린 뒤에 잰다', /navEdges\(\);\s*\/\/ 잠금이 풀린 뒤/.test(body), true);

  /* 재어 보니 390px 화면에서 머리만 163px — 세로의 5분의 1을 숫자 하나 보기
     전에 쓴다. 부제는 탭에 이미 다 적혀 있다. */
  chk('휴대폰에서 머리를 줄인다', /@media \(max-width:560px\)\{[\s\S]{0,400}\.brand \.sub\{display:none\}/.test(SRC), true);
  chk('탭도 같이 줄인다', /@media \(max-width:560px\)\{[\s\S]{0,600}nav button\{padding:9px 11px/.test(SRC), true);
}

console.log('\n── 개념 하나로 아이들을 부른다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 익명본(cohortmis)은 "몰농도 7명" 까지만 말해 준다. 그걸 보고 나서 할 수
     있는 일이 없었다 — 누구인지를 모르니까. 보충을 앉히려면 이름이 필요하다. */
  chk('이름 붙은 창구를 따로 읽는다', /function dtMisNamed\(force\)/.test(body) &&
      /readOnce\('dt', 'mistags'/.test(body), true);
  /* 익명본은 그대로 익명이어야 한다 — 반 패널은 개인을 되짚을 이유가 없다. */
  chk('익명본은 그대로 쓴다', /readOnce\('dt', 'cohortmis'/.test(body), true);

  const R = [
    { name:'김지성', school:'휘문중', course:'ch1', round:5, attempt:'재시', pass:true,
      score:92, days:1, tags:['완충','몰농도'] },
    { name:'김지성', school:'휘문',   course:'ch1', round:4, attempt:'정시', pass:false,
      score:60, days:9, tags:['몰농도'] },
    { name:'이도현', school:'과천중', course:'ch2', round:7, attempt:'정시', pass:false,
      score:55, days:3, tags:['몰농도'] },
    { name:'박서준', school:'과천중', course:'ch1', round:5, attempt:'정시', pass:false,
      score:48, days:2, tags:['완충'] },
  ];
  const tags = ctx.conTags(R);
  chk('많이 걸린 개념이 앞에 선다', tags.map(function(t){ return [t.tag, t.n]; }),
      [['몰농도',2],['완충',2]]);
  /* 같은 학생이 여러 회차에서 같은 태그에 걸린다. 사람으로 묶지 않으면 한 아이가
     셋으로 보여 보충 인원을 잘못 센다. */
  chk('한 사람은 한 번만 센다', (tags.filter(function(t){ return t.tag==='몰농도'; })[0]||{}).n, 2);
  /* 학교 표기가 '휘문' 과 '휘문중' 으로 흔들려도 같은 사람이다. */
  /* DT 는 같은 아이를 '휘문' 과 '휘문중' 으로 섞어서 준다. 글자로 비교하면 한
     아이가 둘로 서고, 보충 인원이 부푼 채로 믿게 된다. */
  chk('학교 표기가 흔들려도 한 사람', ctx.conPut([], R[0]).length === 1 &&
      ctx.conPut([R[0]], R[1]).length === 1, true);
  /* 대곡중과 대곡고는 다른 사람이다 — 여기서까지 합치면 남의 성적이 섞인다. */
  chk('중·고가 다르면 다른 사람',
      ctx.conPut([{ name:'한지우', school:'대곡중', days:1 }],
                 { name:'한지우', school:'대곡고', days:2, tags:[] }).length, 2);

  const who = ctx.conFor(R, '몰농도');
  chk('그 개념 못 잡은 사람만 선다', who.map(function(r){ return r.name; }), ['김지성','이도현']);
  /* 오래된 회차를 보여 주면 "이거 벌써 했는데" 가 된다 — 가장 최근 것을 남긴다. */
  chk('같은 사람은 최근 것으로', (who.filter(function(r){ return r.name==='김지성'; })[0]||{}).round, 5);
  chk('급한 것이 위에 선다', who.map(function(r){ return r.days; }), [1,3]);
  chk('없는 개념이면 빈 목록', ctx.conFor(R, '없는개념'), []);

  /* 통과했는데도 이 개념은 틀렸다는 것을 안 적으면, "얘는 통과했는데 왜 여기
     있지" 하고 목록 전체를 못 믿게 된다. */
  chk('통과했지만 틀린 것을 적는다', /통과 · 이 개념은 틀림/.test(body), true);

  /* 보충을 짤 때 반이 섞이면 시간을 못 잡는다. */
  ctx.DT_CACHE = { 'dt:names': { val: { classes: [
    { label:'화학1 토1:30', course:'ch1', students:[{ name:'김지성', school:'휘문중' }] } ] } } };
  chk('어느 반인지 붙인다', ctx.conClassOf(R[0]), '화학1 토1:30');
  chk('모르면 모른다고 한다', ctx.conClassOf(R[2]), '');
  chk('반별로 센다', ctx.conByClass(who).map(function(x){ return [x.label, x.n]; }),
      [['화학1 토1:30',1],['반 모름',1]]);
  ctx.DT_CACHE = {};

  /* 대시보드 숫자를 보고 나서 할 수 있는 일이 있어야 한다. */
  /* ── 한 번 틀린 아이와 세 회차 내리 걸린 아이는 다른 아이다 ──────────
     목록에 섞여 있으면 둘이 똑같아 보이고, 보충은 대개 뒤엣아이 몫이다. */
  const rep = ctx.conFor(R, '몰농도').filter(function(e){ return e.name==='김지성'; })[0];
  chk('몇 회차에서 걸렸는지 센다', ctx.conHits(rep), 2);
  chk('한 회차뿐이면 1', ctx.conHits(ctx.conFor(R,'몰농도')[1]), 1);
  /* 같은 회차의 정시·재시를 둘로 세면 "두 번 걸렸다" 가 거짓이 된다. */
  chk('같은 회차를 두 번 세지 않는다',
      ctx.conHits(ctx.conFor([
        { name:'한지우', school:'X중', course:'ch1', round:3, attempt:'정시', days:5, tags:['몰농도'] },
        { name:'한지우', school:'X중', course:'ch1', round:3, attempt:'재시', days:4, tags:['몰농도'] },
      ], '몰농도')[0]), 1);
  chk('줄 하나가 망가져도 화면이 안 죽는다',
      ctx.conPut([{ name:'한지우', school:'X중', course:'ch1', round:3, days:1 }],
                 { name:'한지우', school:'X중', course:'ch1', round:4, days:2 }).length, 1);
  chk('되풀이를 화면에 적는다', /회차 걸림</.test(body), true);
  chk('되풀이만 따로 볼 수 있다', /data-conact="repeat"/.test(body) &&
      /CON_REPEAT = !CON_REPEAT/.test(body), true);
  /* 되풀이가 없는데 '되풀이만' 이 켜져 있으면 빈 화면이 뜬다. */
  chk('되풀이가 없으면 스스로 내린다', /if\(CON_REPEAT && !rep\.length\) CON_REPEAT = false;/.test(body), true);

  /* ── 명단만 뽑고 자료를 다시 찾아 헤매면 보충 준비가 두 번 일이 된다 ── */
  chk('이 개념이 나온 회차를 모은다',
      ctx.conRounds(ctx.conFor(R, '몰농도')).map(function(c){ return c.course+c.round; }),
      ['ch14','ch15','ch27']);
  chk('같은 회차는 한 번만', ctx.conRounds([
      { course:'ch1', round:5, seen:['ch1#5'] }, { course:'ch1', round:5, seen:['ch1#5'] }]).length, 1);
  /* 주소를 지어내면 404 로 끝난다 — 화학Ⅱ 는 해설 HTML 이 7회까지밖에 없다.
     DT 자료 목록에 실제로 있는 것만 건다. */
  chk('없는 자료는 안 건다', /if\(!DT_MAT\) return '';/.test(body) &&
      /if\(f\.munje\)/.test(body) && /if\(f\.haeseol\)/.test(body), true);
  chk('자료를 못 읽어도 명단은 뜬다',
      /if\(!DT_MAT\) dtMaterials\(\)\.then\(function\(\)\{ renderConcept\(\); \}\)\.catch/.test(body), true);

  chk('대시보드에서 바로 넘어간다', /data-mistag=/.test(body) &&
      /CON_PICK = m\.dataset\.mistag; show\('con'\)/.test(body), true);
  /* 열지도 않은 창구를 미리 두드리면 앱스크립트가 줄을 세워 다른 숫자가 늦어진다. */
  chk('들어올 때 부른다', /if\(id === 'con'\)\{\s*\n\s*renderConcept\(\);/.test(body), true);
  chk('주소가 곧 상태', /p\.push\('tag='\+encodeURIComponent\(CON_PICK\)\)/.test(body) &&
      /if\(st\.p\.tag\) CON_PICK = st\.p\.tag/.test(body), true);
  chk('탭 자리가 있다', /id="p-con"/.test(SRC) && /id="t-con"/.test(SRC), true);
}

console.log('\n── 오늘 못 하는 줄은 미룬다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  /* 지운 것은 돌아오지 않는다. 미룬 것은 날짜가 지나면 저절로 돌아와야 한다 —
     그래야 잊어버려도 된다. 그 '저절로' 가 이 검사의 전부다. */
  ctx.SNZ.clear(); ctx.SNZ_SHOW = false;
  const k = ctx.sentKey('pend', '김지성', 'ch1', 12);
  chk('아직 안 미뤘으면 비어 있다', ctx.snoozedTill(k), '');
  ctx.SNZ.set(k, ctx.dayKey(7));
  chk('미루면 날짜가 잡힌다', ctx.isSnoozed(k), true);
  chk('오늘까지는 아직 미룬 것', (ctx.SNZ.set(k, ctx.dayKey(0)), ctx.isSnoozed(k)), true);
  /* 어제까지였던 것은 오늘 목록에 **다시 올라와야** 한다. 안 돌아오면 미루기가
     아니라 삭제다 — 그 학생은 영영 안 보인다. */
  chk('어제까지였으면 오늘 돌아온다', (ctx.SNZ.set(k, ctx.dayKey(-1)), ctx.isSnoozed(k)), false);
  chk('돌아온 줄은 접히지 않는다', ctx.snzCls(k), '');
  chk('빈 날짜는 미룬 것이 아니다', (ctx.SNZ.set(k, ''), ctx.isSnoozed(k)), false);
  chk('날짜는 글자 차례로 비교한다', ctx.dayKey(0).length === 10 && /^\d{4}-\d{2}-\d{2}$/.test(ctx.dayKey(0)), true);

  ctx.SNZ.set(k, ctx.dayKey(7));
  chk('미룬 줄은 접는다', ctx.snzCls(k), ' snz');
  chk('단추가 언제까지인지 말해 준다', /지금 보기<\/button>$/.test(ctx.snzBtn(k)), true);
  chk('안 미룬 줄에는 미루기가 뜬다', (ctx.SNZ.clear(), /">미루기<\/button>/.test(ctx.snzBtn(k))), true);

  /* 몇이 사라졌는지 안 보이면 "아까보다 왜 줄었지" 가 된다. */
  ctx.SNZ.set(k, ctx.dayKey(7));
  chk('미룬 수를 세어 보여 준다', /미룬 것 <b>1명/.test(ctx.snzBar([{key:k},{key:'x'}])), true);
  chk('미룬 것이 없으면 줄도 없다', ctx.snzBar([{key:'x'}]), '');
  chk('펼칠 수 있다', /data-snzshow="1"/.test(ctx.snzBar([{key:k}])), true);
  chk('접혀 있을 땐 "보기"', />보기</.test(ctx.snzBar([{key:k}])), true);
  chk('펼쳐 있을 땐 "다시 접기"',
      (ctx.SNZ_SHOW = true, />다시 접기</.test(ctx.snzBar([{key:k}]))), true);
  ctx.SNZ_SHOW = false;

  /* 오늘 안 할 사람 문구를 같이 만들면 붙여 넣고 손으로 지워야 한다. */
  chk('일괄에서도 미룬 사람은 뺀다',
      /!SENT\.has\(r\.key\) && !isSnoozed\(r\.key\)/.test(body), true);
  chk('남은 수에서도 뺀다',
      ctx.bulkBar('pend', [{key:k},{key:'x'}], 'y').indexOf('남은 <b>1명') >= 0, true);
  ctx.SNZ.clear();

  /* 열쇠는 보낸 표시와 **같은 규칙**이다. 다르면 같은 줄을 두 이름으로 부르게 된다. */
  chk('열쇠 규칙은 보낸 표시와 같다', /function snzBtn\(k\)/.test(body) &&
      /SNZ\.set\(k, until\)/.test(body), true);
  chk('시트에서 읽어 온다', /function dtSnoozeLog\(force\)/.test(body) &&
      /readOnce\('dt', 'snoozelog'/.test(body), true);
  /* 보낸 표시와 같은 이유로 더한다 — 늦게 온 시트가 방금 미룬 것을 되살리면 안 된다. */
  chk('늦게 온 시트가 방금 미룬 것을 되살리지 않는다',
      /function seedSnooze\(rows\)\{\s*\n\s*\(rows\|\|\[\]\)\.forEach/.test(body), true);
  chk('셸이 직접 쓰지 않는다 — DT 에 시킨다', /w\.snoozeStu\(\{ kind:p\[0\]/.test(body), true);
  chk('앱스크립트에 POST 하지 않는다', /method\s*:\s*['"]POST/i.test(body), false);
  chk('브라우저에 남기지 않는다', /localStorage[\s\S]{0,40}SNZ/.test(CODE_ONLY), false);
  /* 오늘 할 일 칩에서는 빼고, 반 상태 그림에는 넣는다(빼면 학생이 사라진 것처럼
     보인다). 대신 그림 쪽에 몇 명을 미뤘는지 적는다. */
  chk('오늘 할 일에서는 뺀다', /isSnoozed\(sentKey\('pend'/.test(body) &&
      /isSnoozed\(sentKey\('abs'/.test(body), true);
  chk('반 상태 그림에는 넣고 몇 명인지 적는다', /미룬 '\+snz\+'명 포함/.test(body), true);
  /* 색과 투명도만 쓰면 색을 못 가리는 눈에는 아무 차이가 없다. */
  chk('빗금과 글자로도 알린다', /\.row\.snz \.nm::after\{content:' 미룸'/.test(SRC) &&
      /repeating-linear-gradient\(45deg,rgba\(0,0,0,\.045\)/.test(SRC), true);
  /* 카드는 "이 학생 전부" 를 보는 자리다. 접으면 한 건뿐인 학생의 카드가 빈다. */
  chk('학생 카드에서는 접지 않는다',
      /body:not\(\.snzshow\) \.row\.snz\{display:none\}/.test(SRC) &&
      !/body:not\(\.snzshow\)[^\n]*\.trk__i\.snz\{display:none\}/.test(SRC), true);
  chk('통과한 학생은 미루지 않는다', /st !== 'ok'/.test(body), true);
}

console.log('\n── 여덟 명이면 여덟 번 눌렀다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  chk('한 번에 만드는 길이 있다', /function copyBulk\(btn, kind, rows\)/.test(body), true);
  chk('이미 보낸 사람은 뺀다', /!SENT\.has\(r\.key\) && !isSnoozed\(r\.key\)/.test(body), true);
  chk('누구 것인지 머리를 붙인다', /'── ' \+ r\.name \+ ' ──/.test(body), true);
  /* 문구 규칙이 낱개와 일괄 두 곳에 흩어지면 갈라지고, 학부모는 같은 상황에서
     서로 다른 문자를 받는다. */
  chk('문구는 한 곳에서만 만든다', /function makerFor\(kind, i, j\)/.test(body), true);
  chk('일괄도 DT 에서 빌린다', /copyBulk[\s\S]{0,400}dtPendWindow\(\)/.test(body), true);
  chk('한 명뿐이면 안 내놓는다', ctx.bulkBar('pend', [{key:'a'}], '한 번에'), '');
  chk('둘부터 내놓는다', /data-bulk="pend"/.test(ctx.bulkBar('pend', [{key:'a'},{key:'b'}], '한 번에')), true);
  chk('남은 사람 수를 적는다',
      /남은 <b>1명/.test((ctx.SENT.add('a'), ctx.bulkBar('pend', [{key:'a'},{key:'b'}], 'x'))), true);
  ctx.SENT.clear();
}

console.log('\n── 어디 있더라 (Cmd+K) ──');
{
  const body = SRC.split('<script>')[1] || '';
  chk('팔레트 자리가 있다', /id="pal"/.test(SRC) && /id="palIn"/.test(SRC), true);
  chk('학생·반·회차·자료·화면을 모두 담는다',
      /kind:'화면'/.test(body) && /kind:'학생'/.test(body) && /kind:'반'/.test(body) &&
      /kind:'회차'/.test(body) && /kind:'자료'/.test(body), true);
  /* 팔레트를 열 때마다 창구를 두드리면 앱스크립트가 줄을 선다. */
  chk('창구를 새로 두드리지 않는다',
      /readOnce|jsonp\(|dtRoster\(|kmRoster\(/.test(cut('palSources')), false);
  /* 빈 칸으로 열었을 때 탭만 나오면 팔레트를 열 이유가 없다(탭은 숫자키 한 번).
     방금 본 학생·반·회차가 먼저 와야 한다. */
  chk('방금 본 것을 적어 둔다', /PAL_KEY|palRemember/.test(body), true);
  chk('고르면 적는다', /palRemember\(r\);/.test(cut('palRun')), true);
  chk('탭은 안 적는다', /kind === '화면'/.test(cut('palRemember')), true);
  chk('빈 칸이면 방금 본 것이 먼저', /rec\.concat\(/.test(cut('renderPal')), true);
  /* 이름만 적어 두고 열 때 되찾는다 — 명단에서 빠진 학생이 남으면 안 된다. */
  chk('없어진 줄은 저절로 사라진다', /if\(hit\) out\.push\(hit\);/.test(cut('palRecentRows')), true);
  const kb = body.slice(body.indexOf("document.addEventListener('keydown'"));
  chk('입력 중에도 열린다', kb.indexOf('openPal();') < kb.indexOf('if(typing) return;'), true);
  chk('위아래로 고르고 엔터로 연다',
      /ArrowDown/.test(body) && /ArrowUp/.test(body) && /palRun\(PAL_AT\)/.test(body), true);
}

/* 명단이 300명을 넘는다. 이름을 통째로 치는 것과 초성 세 번은 매번 다르다. */
console.log('\n── 초성으로 찾는다 ──');
{
  chk('초성을 뽑는다', [ctx.choOf('김'), ctx.choOf('유'), ctx.choOf('정')], ['ㄱ','ㅇ','ㅈ']);
  chk('한글이 아니면 빈칸', [ctx.choOf('A'), ctx.choOf('7'), ctx.choOf('')], ['','','']);
  chk('겹자음도 제자리', [ctx.choOf('까'), ctx.choOf('빵')], ['ㄲ','ㅃ']);
  chk('초성 셋으로 찾는다', ctx.koHit('김유정', 'ㄱㅇㅈ'), true);
  chk('순서가 다르면 안 걸린다', ctx.koHit('김유정', 'ㅈㅇㄱ'), false);
  chk('가운데부터도 걸린다', ctx.koHit('남궁유정', 'ㅇㅈ'), true);
  chk('조합 중인 글자도 걸린다', ctx.koHit('김준', '김ㅈ'), true);
  chk('통짜 찾기는 그대로', [ctx.koHit('김유정','김유'), ctx.koHit('김유정','박')], [true, false]);
  chk('빈 물음은 다 걸린다', ctx.koHit('김유정', ''), true);
  /* 모음만 친 것은 초성이 아니다. 'ㅏ' 가 아무 글자에나 붙으면 목록이 안 줄어든다. */
  chk('모음은 초성으로 안 본다', ctx.koHit('김유정', 'ㅏ'), false);
  chk('물음이 이름보다 길면 안 걸린다', ctx.koHit('김유', 'ㄱㅇㅈㅎ'), false);
  chk('학교도 초성으로', ctx.koHit(ctx.normSchool('휘문중학교'), 'ㅎㅁㅈ'), true);
  /* 세 찾기 칸이 모두 같은 자를 쓴다 — 한 곳만 고치면 나머지가 뒤처진다. */
  const body = SRC.split('<script>')[1] || '';
  chk('학생·바로 찾기·빠른 이동이 모두 쓴다',
      (body.match(/koHit\(/g) || []).length >= 6, true);
}

/* 수업이 끝나면 반마다 "오늘 뭘 배웠다" 를 보낸다. 열두 명이면 열두 번,
   이름만 바꿔 가며 손으로 붙여 넣었다. 한 반에 5분, 여섯 반이면 30분이다. */
console.log('\n── 수업 문자 ──');
{
  const body = SRC.split('<script>')[1] || '';
  const cls = { label:'화학1 일3-7', course:'ch1' };
  const who = { name:'김유정', school:'휘문중', grade:'2' };

  chk('이름이 채워진다', ctx.lesFill('{이름} 학생', who, cls, 1), '김유정 학생');

  /* 본문에 {이름} 을 손으로 넣게 하면 잊는다 — 잊으면 열두 통이 모두 같은
     글이 되고, 붙여 넣고 나서야 안다. 머리말로 저절로 붙는다. */
  ctx.LES_HEAD = null;
  chk('본문에 이름이 없으면 머리말이 붙는다',
      ctx.lesText({ body: '안녕하세요. 조준모입니다.', round: 1 }, who, cls),
      '김유정 학생 학부모님께\n\n안녕하세요. 조준모입니다.');
  /* 본문에 직접 넣었으면 안 붙인다 — 두 번 나오면 어색하다. */
  chk('본문에 이름이 있으면 안 붙인다',
      ctx.lesText({ body: '{이름} 학생, 안녕하세요.', round: 1 }, who, cls),
      '김유정 학생, 안녕하세요.');
  ctx.LES_HEAD = '[{과목} {회차}회] {이름} 학부모님';
  chk('머리말을 바꿀 수 있다',
      ctx.lesText({ body: '본문', round: 3 }, who, cls),
      '[화학Ⅰ 3회] 김유정 학부모님\n\n본문');
  ctx.LES_HEAD = '';
  chk('머리말을 비우면 안 붙는다', ctx.lesText({ body: '본문', round: 1 }, who, cls), '본문');
  ctx.LES_HEAD = null;
  /* 학생이 없으면 이름 자리는 빈 칸이 된다 — 자리표시자가 그대로 남는 것보다 낫다. */
  chk('빈 회차에도 안 죽는다', [ctx.lesText(null, who, cls), ctx.lesText({}, null, null)],
      ['', ' 학생 학부모님께\n\n']);
  chk('과목도', ctx.lesFill('{과목}', who, cls, 1), '화학Ⅰ');
  /* 학교·학년·반은 뺐다(선생님 결정). 남아 있으면 그대로 글자로 나가야 한다 —
     조용히 빈칸이 되면 문장이 깨진 채로 학부모에게 간다. */
  chk('뺀 것은 글자 그대로', ctx.lesFill('{학교} {학년} {반}', who, cls, 1), '{학교} {학년} {반}');
  chk('넣을 수 있는 것은 셋뿐', /const LES_MARKS = \['\{이름\}','\{과목\}','\{회차\}'\];/.test(SRC), true);
  chk('회차도', ctx.lesFill('조준모의고사 {회차}회', who, cls, 3), '조준모의고사 3회');
  chk('여러 번 나와도 다 바꾼다', ctx.lesFill('{이름}·{이름}', who, cls, 1), '김유정·김유정');
  /* 학년이 없는 학생이 흔하다(DT 명단에 안 적힌다). '학년' 이라는 글자만
     덩그러니 남으면 그대로 학부모에게 나간다. */
  chk('빈 값은 빈 칸으로', ctx.lesFill('[{이름}]', {}, cls, 1), '[]');
  chk('모르는 자리표시자는 그대로', ctx.lesFill('{선생님}', who, cls, 1), '{선생님}');
  chk('본문이 없어도 안 죽는다', [ctx.lesFill(null, who, cls, 1), ctx.lesFill('', null, null, null)], ['', '']);
  /* 회차 번호가 0 일 수 있다(오리엔테이션). null 과 0 을 섞으면 '0회' 가 빈칸이 된다. */
  chk('0회차도 0으로', ctx.lesFill('{회차}', who, cls, 0), '0');

  chk('반에서 여는 단추가 있다', /data-clsact="lesson"/.test(body), true);
  /* 수업 안내는 걸러 놓은 목록이 아니라 **반 전체**에게 간다. */
  chk('걸러 놓은 목록이 아니라 반 전체', /return LES_CLS \? \(LES_CLS\.students \|\| \[\]\) : \[\];/.test(cut('lesWho')), true);
  chk('과목이 맞는 회차만 보인다', /!x\.course \|\| x\.course === course/.test(cut('lesFor')), true);
  chk('회차 번호 차례로', /\(Number\(a\.round\)\|\|0\)-\(Number\(b\.round\)\|\|0\)/.test(cut('lesFor').replace(/\s/g,'')), true);
  /* {이름} 이 없으면 열두 통이 모두 같은 글이 된다 — 붙여 넣고 나서 알면 늦다. */
  chk('이름이 자동으로 붙는다고 적는다', /머리말로 이름이 자동으로/.test(body), true);
  chk('머리말도 비면 그때는 짚어 준다', /통이 모두 같은 글이 됩니다/.test(body), true);
  chk('머리말을 고칠 수 있다', /data-les="head"/.test(body), true);
  chk('미리보기는 나가는 것 그대로', /lesText\(cur, first, LES_CLS\)/.test(body), true);
  /* 미리보기와 복사가 다른 것을 쓰면 화면에서 본 것과 나간 것이 달라진다. */
  chk('복사도 같은 것을 쓴다',
      (body.match(/lesText\(cur, /g) || []).length >= 3, true);
  /* 브라우저를 비우면 사라지는 것을 유일한 사본으로 두지 않는다. */
  chk('파일로 내보낼 수 있다', /data-les="export"/.test(body) && /수업문자\.json/.test(body), true);
  chk('파일에서 가져올 수 있다', /data-les="import"/.test(body) && /id="lesFile"/.test(SRC), true);
  /* 덮어쓰기는 되돌릴 수 없다 — 손으로 적은 것이라 다시 못 만든다. */
  chk('덮어쓰기 전에 묻는다', /!confirm\('지금 있는 회차/.test(body), true);
  chk('수업 문자 파일이 아니면 거른다', /lessons 목록이 없습니다/.test(body), true);
  /* 화면에 보이는 목록은 걸러 낸 사본이다. 사본을 고치면 다음에 열 때 돌아온다. */
  chk('원본에서 찾아 고친다', /const at = all\.indexOf\(cur\);/.test(body), true);
  /* 이 셸은 앱 자료를 쓰지 않는다. 회차 글은 앱 자료가 아니라 여기서 짓는 것이다. */
  chk('앱스크립트에 올리지 않는다', /lesSave[\s\S]{0,200}jsonp\(/.test(body), false);

  /* '＋ 새 회차' 를 열여덟 번 누르게 하면 안 된다. DT 자료가 그 과목에 몇
     회차가 있는지 이미 안다(화학Ⅰ 18 · 화학Ⅱ 18 · 일반화학 10). */
  chk('DT 회차 수를 읽어 온다', /function lesRoundsOf/.test(body), true);
  chk('회차 번호만 골라 차례로', /r\.round\) \|\| 0/.test(cut('lesRoundsOf')), true);
  chk('그 수만큼 빈 칸을 세운다', /blank: true/.test(cut('lesList')), true);
  /* 적어 둔 것이 이긴다 — 빈 칸이 내용을 덮으면 글이 사라진 것처럼 보인다. */
  chk('적어 둔 것이 이긴다', /out\.push\(by\[n\] \|\| \{/.test(cut('lesList')), true);
  /* DT 회차에 없는 것(손으로 더한 회차)도 사라지면 안 된다. */
  chk('DT 에 없는 회차도 남는다', /mine\.forEach\(function\(x\)\{ const k = Number\(x\.round\); if\(!k \|\| by\[k\]\) out\.push\(x\); \}\);/.test(cut('lesList')), true);
  /* 빈 칸은 아직 담긴 것이 아니다 — 처음 적을 때 넣어야 한다. */
  chk('빈 칸은 처음 적을 때 담는다', /if\(at < 0\) all\.push\(row\); else all\[at\] = row;/.test(body), true);
  chk('빈 칸은 지울 것이 없다', /아직 안 적은 칸은 지울 것이 없다/.test(SRC), true);
  /* 몇 칸을 채웠는지 보여야 "어디까지 적었더라" 를 안 센다. */
  chk('몇 칸 적었는지 적는다', /' 적음<\/span>'/.test(body), true);
  chk('빈 칸이라고 알려 준다', /아직 안 적음/.test(body), true);
  /* 회차 수는 DT 자료에서 온다 — 자료 탭에 안 들어갔으면 아직 안 읽었다. */
  chk('창을 열 때 자료를 부른다', /if\(!DT_MAT\) dtMaterials\(\)\.then\(function\(\)\{ lesRender\(\); \}\)/.test(body), true);
}

/* 한 번 빠진 것은 넘어가도 여러 회차 연속이면 다른 신호다. 지금은 회차별로만
   보여서 누적이 안 보였다 — 회차 목록을 아무리 봐도 세어야만 알 수 있었다. */
console.log('\n── 자꾸 빠지는 학생 ──');
{
  const body = SRC.split('<script>')[1] || '';
  chk('몇 회차부터인지 한 곳에 적는다', ctx.NDG_ABS_RUN, 3);
  chk('회차를 가로질러 센다', /const absN = \{\};/.test(body), true);
  chk('기준 미만은 안 부른다', /if\(a\.n < NDG_ABS_RUN\) return;/.test(body), true);
  chk('어느 회차였는지 적는다', /a\.where\.slice\(0, 3\)/.test(body), true);
  /* 이름이 같은 줄이 여러 번 나오면 한 사람으로 세야 한다. */
  chk('이름을 다듬어 센다', /const k = normName\(nm\); if\(!k\) return;/.test(body), true);
  /* 미루기는 다른 넛지와 같은 길을 쓴다 — 따로 만들면 한쪽만 조용해진다. */
  chk('미루기가 걸린다', /ndgKey\('absrun'/.test(body), true);
}

/* 카드·칩·넛지·명단이 다 펼쳐져 있어 어디부터 볼지 눈으로 정해야 했다. */
console.log('\n── 오늘 할 일 한 줄 ──');
{
  const body = SRC.split('<script>')[1] || '';
  chk('자리가 있다', /id="todo"/.test(SRC), true);
  /* 숫자가 칩과 다르면 어느 쪽이 맞는지 알 수 없다 — 같은 배열에서 나와야 한다. */
  chk('칩과 같은 배열에서 센다', /JUMPS\.filter\(function\(j\)\{ return j\.n\(\) > 0; \}\)/.test(cut('renderTodo')), true);
  chk('칩과 같은 순간에 그려진다', /renderTodo\(\);/.test(cut('renderJump')), true);
  chk('할 일이 없으면 없다고 말한다', /남은 것이 없습니다/.test(body), true);
  chk('수업 문자 안 보낸 반도 센다', /data-todocls/.test(body), true);
}

/* 반이 여섯이면 "이 반 보냈던가?" 를 매주 헷갈린다. */
console.log('\n── 수업 문자를 보냈는지 남는다 ──');
{
  const body = SRC.split('<script>')[1] || '';
  const cls = { course:'ch1', label:'화학1 일3-7' };
  chk('열쇠는 과목+회차+반', ctx.lesSentKey(cls, 3), 'ch1|3|화학1 일3-7');
  chk('빈 것에도 안 죽는다', ctx.lesSentKey(null, null), '||');
  ctx.LES_SENT = { 'ch1|3|화학1 일3-7': '2026-08-03' };
  chk('보낸 날을 돌려준다', ctx.lesSentAt(cls, 3), '2026-08-03');
  chk('다른 반은 안 걸린다', ctx.lesSentAt({ course:'ch1', label:'딴반' }, 3), '');
  ctx.LES_SENT = {};
  chk('고르개에 표시한다', /lesSentAt\(LES_CLS, x\.round\) \? '✓ ' : ''/.test(body), true);
  chk('무를 수 있다', /data-les="unsend"/.test(body), true);
  /* 복사한 순간이 이쪽에서 아는 마지막 순간이다(붙여넣기는 문자 앱에서 한다). */
  chk('복사하면 보낸 것으로', /lesMarkSent\(LES_CLS, cur\.round, true\)/.test(body), true);
}

/* 상담 중에 "이 학생한테만 다시 보내 주세요" 는 흔한 부탁이다. */
console.log('\n── 학생 카드에서 바로 ──');
{
  const body = SRC.split('<script>')[1] || '';
  chk('그 학생이 든 반을 찾는다', /function lesClassOf/.test(body), true);
  chk('마지막으로 적어 둔 회차', /function lesLatestFor/.test(body), true);
  chk('안 적은 회차는 뺀다', /filter\(function\(x\)\{ return x\.body; \}\)/.test(cut('lesLatestFor')), true);
  chk('카드에 단추가 붙는다', /data-lesstu="1"/.test(body), true);
  /* 반 탭과 다른 글이 나오면 안 된다 — 같은 함수를 써야 한다. */
  chk('반 탭과 같은 함수를 쓴다', /copyText\(b, lesText\(cur, DLG_STU, cls\)/.test(body), true);
  /* 회차 창에서 안 본 학생을 눌러 카드로. 거기에 문자가 다 있다. */
  chk('회차에서 카드로 간다', /data-rndstu=/.test(body), true);
  chk('이웃으로도 넘어간다', /openStudent\(list\[\+b\.dataset\.rndstu\], list/.test(body), true);
}

console.log('\n── 모든 반 한눈에 ──');
{
  const body = SRC.split('<script>')[1] || '';
  chk('자리가 있다', /id="clsMult"/.test(SRC), true);
  chk('반이 하나면 안 그린다', /\(list\.length < 2\) \? '' :/.test(body), true);
  chk('누르면 그 반으로 간다', /data-clsjump/.test(body), true);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
