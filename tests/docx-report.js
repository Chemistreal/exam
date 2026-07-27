/* ============================================================
   성적표 Word 문서 회귀 테스트 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   Word 성적표에 화면에는 있는 것들이 통째로 빠져 있었다.

   - **다원 로고**가 저장소에 있는데 성적표 어디에도 쓰이지 않았다
   - **수상 확률(베이지안 추정)** — 학부모가 가장 먼저 찾는 숫자인데 Word 에 없었다
   - **동형문제 회복률**과 **되풀이되는 오개념** — 화면에만 있었다

   계산은 화면과 같은 함수를 그대로 쓴다(winProb·dhRecovery·repeatedMisses).
   숫자가 갈라질 자리를 만들지 않는다.

   여기서 지키는 것:
   - 로고가 실제 문서에 박힌다(바이트 크기로 확인)
   - 수상 확률 섹션과 등급별 확률이 들어간다
   - 회복률·반복 오개념이 데이터가 있을 때 들어간다
   - 목차에도 반영된다(번호가 밀리지 않는다)
   - 기존 섹션과 부록 3종이 그대로 남는다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/docx-report.js
   ============================================================ */
'use strict';
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) { console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0); }
const fs=require('fs'),path=require('path'),{execSync}=require('child_process');
const OUT = require('os').tmpdir() + '/chemistreal-docx-test';
let fail=0; const chk=(n,g,w)=>{const ok=JSON.stringify(g)===JSON.stringify(w);
  console.log((ok?'  PASS  ':'  FAIL  ')+n+(ok?'':`  got=${JSON.stringify(g)} want=${JSON.stringify(w)}`));if(!ok)fail++;};
(async()=>{
  fs.mkdirSync(OUT,{recursive:true});
  const b=await chromium.launch({executablePath:CHROMIUM,args:['--no-sandbox']});
  const ctx=await b.newContext({acceptDownloads:true}); const p=await ctx.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto(`http://localhost:${PORT}/final.html`,{waitUntil:'networkidle'});
  await p.waitForTimeout(700);

  // 두 시험을 응시시켜 '되풀이되는 오개념'이 나오게 하고, 동형문제도 풀어 회복률을 만든다
  await p.evaluate(async()=>{
    localStorage.clear();
    // 두 시험에 공통으로 있는 유형을 하나 골라, 양쪽에서 그 유형만 틀리게 한다
    const setOf=id=>{const e=FINAL_EXAMS.find(x=>x.id===id);return new Set((e.type||[]).filter(Boolean));};
    const TY=[...setOf('hwol-2018')].find(t=>setOf('hwol-2019').has(t));
    window.__TY=TY;
    const e2=FINAL_EXAMS.find(x=>x.id==='hwol-2019');
    const ans2=[]; for(let q=1;q<=e2.nQ;q++){const acc=(e2.multi&&e2.multi[q])||[e2.key[q-1]];const g=acc[0]||1;
      ans2.push(((e2.type&&e2.type[q-1])===TY||q%4===0)?((g%4)+1):g);}
    let c=0,t=0; const m2=new Set(e2.miss||[]);
    for(let q=1;q<=e2.nQ;q++){if(m2.has(q))continue;t++;if(okq(e2,q,ans2[q-1]))c++;}
    saveSubs('hwol-2019',[{name:'전체본',ts:900,correct:c,total:t,wrong:t-c,ans:ans2}]);
    // 12명 누적(또래 통계 활성 → 한계 이득도 나오게)
    const ex=FINAL_EXAMS.find(x=>x.id==='hwol-2018'), nQ=ex.nQ;
    const mk=s=>{let x=(s*2654435761)>>>0,a=[];for(let i=0;i<nQ;i++){x=(x*1664525+1013904223)>>>0;a.push((x>>>16)%4+1);}return a;};
    const miss=new Set(ex.miss||[]), arr=[];
    for(let s=1;s<=12;s++){const a=mk(s);let cc=0,tt=0;
      for(let q=1;q<=nQ;q++){if(miss.has(q))continue;tt++;if(okq(ex,q,a[q-1]))cc++;}
      arr.push({name:'학생'+s,school:'X중',grade:'3',ts:1000+s,correct:cc,total:tt,wrong:tt-cc,ans:a});}
    saveSubs('hwol-2018',arr);
    openExam('hwol-2018'); document.getElementById('nm').value='전체본';
    document.getElementById('sch').value='X중';
    for(let q=1;q<=cur.nQ;q++){const acc=(cur.multi&&cur.multi[q])||[cur.key[q-1]];const g=acc[0]||1;
      setAns(q,((cur.type&&cur.type[q-1])===window.__TY||q%4===0)?((g%4)+1):g);}
    scoreAuto();
    await new Promise(r=>setTimeout(r,3000));
    // 동형문제 두 개 풀기 → 회복률 생성
    const ols=[].slice.call(document.querySelectorAll('.wb-card .wb-opts.is-live')).slice(0,2);
    ols.forEach(ol=>ol.querySelector('li[data-c="'+Number(ol.dataset.ans)+'"]').click());
  });
  await p.waitForTimeout(1200);
  const pre=await p.evaluate(()=>({rec:dhRecovery(cur).length, rep:repeatedMisses(cur).length,
    // 화면이 말하는 석차를 **모두** 모은다. 맨 위 요약(숫자 뒤에 '석차')과
    // '점수 분포 속 나의 위치'('석차' 뒤에 숫자) 두 곳이다. 아래에서 서로
    // 같은지, 그리고 Word 도 같은 숫자를 말하는지 대조한다.
    ranks:(function(){ var t=document.body.innerText.replace(/\s+/g,' '), out=[];
      (t.match(/석차\s*\d+\s*\/\s*\d+/g)||[]).forEach(function(m){ out.push(m.replace(/[^\d/]/g,'')); });
      (t.match(/\d+\s*\/\s*\d+\s*석차/g)||[]).forEach(function(m){ out.push(m.replace(/[^\d/]/g,'')); });
      return out; })()}));
  console.log('사전 상태: 회복 문항',pre.rec,'· 반복 유형',pre.rep,'· 화면 석차',pre.ranks.join(', ')||'(없음)');

  const [dl]=await Promise.all([p.waitForEvent('download',{timeout:300000}),p.evaluate(()=>downloadReportDOCX())]);
  const f=path.join(OUT,'r.docx'); await dl.saveAs(f);
  console.log('저장',(fs.statSync(f).size/1024).toFixed(0),'KB');
  await b.close();
  execSync(`cd ${OUT} && rm -rf x && mkdir x && cd x && unzip -q ../r.docx`);
  const dir=path.join(OUT,'x/word');
  const xml=fs.readFileSync(path.join(dir,'document.xml'),'utf8');
  const txt=xml.replace(/<[^>]+>/g,'');
  // 문단 단위로도 본다. 줄이 서로 붙어 버리는 사고는 통짜 텍스트로는 안 보인다.
  const lines=(xml.match(/<w:p[ >][\s\S]*?<\/w:p>/g)||[])
    .map(p=>(p.match(/<w:t[^>]*>([\s\S]*?)<\/w:t>/g)||[])
      .map(t=>t.replace(/<[^>]+>/g,'')).join('').trim()).filter(Boolean);
  const media=fs.readdirSync(path.join(dir,'media'));
  console.log('이미지 파일 수:',media.length);

  chk('수상 확률 섹션',/수상 확률/.test(txt),true);
  chk('베이지안 설명문',/각 등급 이상을 받을 확률/.test(txt),true);
  chk('수상 확률 수치',/수상\(장려상 이상\) 확률/.test(txt),true);
  chk('등급별 행 5개',(txt.match(/이상/g)||[]).length>=5,true);
  chk('동형문제 회복률 섹션',/동형문제 회복률/.test(txt),true);
  chk('회복 문항 표시',/회복한 문항/.test(txt),true);
  chk('되풀이되는 오개념 섹션',/되풀이되는 오개념/.test(txt),true);
  chk('목차에 수상 확률',/베이지안 추정/.test(txt),true);
  chk('기존 섹션 유지',/문항별 정오표/.test(txt)&&/영역별 성취/.test(txt),true);
  chk('부록 3종 유지',/오답 정리/.test(txt)&&/개념 강의/.test(txt)&&/동형 미니 시험지/.test(txt),true);
  // 로고가 실제로 문서에 박혔는지 — 표지·마무리 두 번 들어간다
  const logoBytes=fs.statSync(path.join(__dirname,'..','dawon_logo_trim.png')).size;
  const hasLogo=media.some(f=>{try{return fs.statSync(path.join(dir,'media',f)).size===logoBytes;}catch(e){return false;}});
  chk('다원 로고가 문서에 들어 있다',hasLogo,true);
  // ── 화면에만 있던 나머지 섹션들 (secToParas 로 옮긴 것) ──
  [['수상권 목표 정렬','ROADMAP'],['신호등 사분면','QUADRANT'],['개념 깊이','DEPTH'],
   ['선수 개념','PREREQUISITE'],['숙달','MASTERY'],
   ['성장 루프','LONG RUN']].forEach(([ko])=>{
    chk('섹션 · '+ko, new RegExp(ko).test(txt), true);
  });

  /* ── 읽을 수 있는가 ────────────────────────────────────────────────
     한때 신호등 사분면이 '47101218…맞음틀림강점최우선' 한 줄로 나왔다.
     그림 안쪽 좌표 글자가 문단으로 잡히고, 칸 제목과 번호가 붙은 탓이다.
     "섹션이 있다"만 보는 검사는 이걸 통과시킨다. 그래서 문단을 본다. */
  // 사분면 칸의 '4 6 8 12…'는 정상이다(띄어쓰기가 있다). 그림에서 샌 글자는
  // 좌표 순으로 붙어 나와 띄어쓰기가 없다 — 그 모양만 잡는다.
  const glued=lines.filter(l=>/맞음틀림|어려움쉬움|→\d+%[가-힣]/.test(l));
  chk('붙어 버린 줄이 없다',glued.slice(0,3),[]);
  chk('그림 속 글자가 새지 않는다',lines.some(l=>/^\d{16,}$/.test(l)),false);
  chk('화면 전용 상자가 안 넘어온다',/불러오는 중/.test(txt),false);
  chk('사분면 칸 제목이 제 줄에 있다',lines.some(l=>/^쉬움·틀림 \(최우선\) · \d+$/.test(l)),true);
  chk('선수 개념 지도가 표로 남는다',/먼저 알아야 할 것/.test(txt),true);

  /* ── 석차 ────────────────────────────────────────────────────────
     Word·인쇄 책자에는 처음부터 있었는데 화면에만 빠져 있었다. 백분위만
     적어 두면 "그래서 몇 등이냐"를 반드시 되묻는다. 두 곳이 같은 식으로
     세는지가 핵심이다 — 화면과 종이가 다른 등수를 말하면 안 된다. */
  chk('화면 두 곳에 석차가 나온다',pre.ranks.length>=2,true);
  chk('화면끼리 석차가 어긋나지 않는다',Array.from(new Set(pre.ranks)),pre.ranks.slice(0,1));
  chk('Word 에도 석차가 있다',/석차/.test(txt),true);
  chk('화면과 Word 의 석차가 같다',
      new RegExp('석차\\s*'+(pre.ranks[0]||'x').replace('/','\\s*/\\s*')).test(txt.replace(/\s+/g,' ')),true);

  // ── 뺀 것 (선생님 요청) ──
  chk('학습 유형 진단은 Word 에 없다',/학습 유형/.test(txt),false);
  chk('4주 학습 계획표는 Word 에 없다',/학습 계획표/.test(txt),false);
  // 목차 제목도 본문 제목도 '선택지 분석'을 지나가므로 이 한 줄이 둘 다 잡는다.
  // ('함정 선택지'는 오답 노트 부록과 한 장 요약에 그대로 남아 있으므로 쓰면 안 된다.)
  chk('누적 정답률·선택지 분석은 Word 에 없다',/선택지 분석/.test(txt),false);

  // ── Word 에만 넣은 것 ──
  chk('학부모 한 장 요약',/한 장 요약/.test(txt),true);
  chk('요약에 결론만 담는다는 안내',/이 장만 보셔도 됩니다/.test(txt),true);
  chk('미니 시험지 답안 기입란',/답안 기입란/.test(txt),true);

  // ── 배경 워터마크 ──
  const markBytes=fs.statSync(path.join(__dirname,'..','assets','report','logo-watermark.png')).size;
  const hasMark=media.some(f=>{try{return fs.statSync(path.join(dir,'media',f)).size===markBytes;}catch(e){return false;}});
  chk('배경 워터마크가 문서에 들어 있다',hasMark,true);

  chk('JS 오류 없음',errs,[]);
  console.log(fail?`\n실패 ${fail}건`:'\n전부 통과');
  process.exit(fail?1:0);
})().catch(e=>{console.error('ERR',e.message);process.exit(1);});
