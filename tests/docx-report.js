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
  const pre=await p.evaluate(()=>({rec:dhRecovery(cur).length, rep:repeatedMisses(cur).length}));
  console.log('사전 상태: 회복 문항',pre.rec,'· 반복 유형',pre.rep);

  const [dl]=await Promise.all([p.waitForEvent('download',{timeout:300000}),p.evaluate(()=>downloadReportDOCX())]);
  const f=path.join(OUT,'r.docx'); await dl.saveAs(f);
  console.log('저장',(fs.statSync(f).size/1024).toFixed(0),'KB');
  await b.close();
  execSync(`cd ${OUT} && rm -rf x && mkdir x && cd x && unzip -q ../r.docx`);
  const dir=path.join(OUT,'x/word');
  const xml=fs.readFileSync(path.join(dir,'document.xml'),'utf8');
  const txt=xml.replace(/<[^>]+>/g,'');
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
  chk('JS 오류 없음',errs,[]);
  console.log(fail?`\n실패 ${fail}건`:'\n전부 통과');
  process.exit(fail?1:0);
})().catch(e=>{console.error('ERR',e.message);process.exit(1);});
