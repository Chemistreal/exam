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
  /* 딱 하나 예외가 있다: 첫 화면 잠금의 열쇠칸. 그건 남의 데이터가 아니라
     파이널·홈과 **나눠 쓰는 문고리**다 — 따로 두면 셸에서 넣고 iframe 안의
     파이널에서 또 물어 화면이 두 겹으로 잠긴다. 그 한 곳만 허용한다. */
  chk('저장하는 곳은 잠금 열쇠칸 하나뿐',
      (CODE_ONLY.match(/localStorage\.setItem\(\s*([A-Za-z_$][\w$]*)/g) || []),
      ['localStorage.setItem(KEY']);
  chk('그 칸은 파이널과 같은 칸', /var KEY = 'chemistreal:gate'/.test(body), true);
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
       "readOnce('dt', 'cohortmis'", "readOnce('dt', 'passed'", "readOnce('km', 'names'"]);

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
  chk('한 창구로만 부른다', /function readOnce\(app, action, shape, force\)/.test(body), true);
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
  const nKeys = ((body.match(/const n = '(\d+)'\.indexOf/) || ['',''])[1] || '').length;
  chk('탭이 열 개', nTabs, 10);
  chk('탭 수와 숫자키 수가 맞는다', nKeys, nTabs);
  /* 앞 다섯은 셸이 그리는 화면, 뒤 다섯은 앱을 얹은 화면. 머리의 두 줄과
     같은 차례여야 숫자키가 눈에 보이는 차례와 맞는다. */
  chk('보는 화면이 앞, 앱이 뒤',
      /const TABS = \['dash','stu','cls','rnd','mat','exam','dt','dtp','dtr','km'\]/.test(body), true);
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
  chk('반에서 학생 카드로 넘어간다', /openStudent\(hit\.length===1/.test(body), true);
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
  // 칩과 그림이 따로 그려지면 두 숫자가 어긋난다
  chk('칩과 그림이 같은 숫자를 본다', /function renderJump\(\)\{\s*\n\s*renderFig\(\);/.test(body), true);
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

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
