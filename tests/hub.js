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
const ctx = { console };
vm.createContext(ctx);
vm.runInContext([
  cut('normName'), cut('normSchool'), cut('normGrade'),
  cut('unifyKey'), cut('looseKey'), cut('mergeRosters'),
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
  chk('localStorage 에 쓰지 않는다', /localStorage\.setItem/.test(body), false);
  chk('localStorage 를 비우지 않는다', /localStorage\.(clear|removeItem)/.test(body), false);
  chk('앱스크립트에 POST 하지 않는다', /method\s*:\s*['"]POST/i.test(body), false);
  chk('읽기 액션만 부른다',
      (body.match(/action\s*:\s*'(\w+)'/g) || []).sort(),
      ["action:'names'", "action:'pending'"]);

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

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
