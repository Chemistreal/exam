# -*- coding: utf-8 -*-
import re, json, chem1_data as D
def jstr(s): return json.dumps(s, ensure_ascii=False)
def js_rows(rows):
    out=[]
    for r in rows:
        out.append(" ["+",".join([str(r[0]),str(r[1]),str(r[2]),jstr(r[3]),jstr(r[4])])+"]")
    return "[\n"+",\n".join(out)+"\n]"
def js_order(at):
    o=D.present_area_order(at); return "["+",".join(jstr(a) for a in o)+"]"
def js_group(at):
    g=D.area_group_map(at); return "{"+",".join("%s:%s"%(jstr(a),jstr(v)) for a,v in g.items())+"}"

p="index.html"; s=open(p,encoding="utf-8").read()
def rep(o,n,c=1,t=""):
    global s; k=s.count(o); assert k==c,"FAIL[%s] exp %d got %d"%(t,c,k); s=s.replace(o,n); print("ok",t)

# 1. Q_KCH13B / Q_KCH12B 배열 정의 (CHEM21_OM 뒤, mkExam 앞)
arrays=('const Q_KCH13B='+js_rows(D.rows_k13b())+';\n'
        'const Q_KCH12B='+js_rows(D.rows_k12b())+';\n')
rep('function mkExam(meta,rows){', arrays+'function mkExam(meta,rows){',1,"동형 배열")

# 2. EXAMS에 2종 추가 (chem2-1 엔트리 뒤, ]; 앞)
anchor=('  questions:Q_CHEM21.map(r=>({n:r[0],ans:r[1],p:r[2],area:r[3],type:r[4],page:0,accept:r[5],misc:(typeof CHEM21_OM!=="undefined"?CHEM21_OM[r[0]]:null)||null}))}\n];')
newent=('  questions:Q_CHEM21.map(r=>({n:r[0],ans:r[1],p:r[2],area:r[3],type:r[4],page:0,accept:r[5],misc:(typeof CHEM21_OM!=="undefined"?CHEM21_OM[r[0]]:null)||null}))},\n'
 ' {id:"kch1to3-b",title:"화학1 1-3단원 모의고사 (동형)",range:"화학의 기초 ~ 분자의 극성 · 중등 화올",source:"조준모의고사 · 동형",N:0,estP:true,haeseol:"",\n'
 '  areaOrder:'+js_order(D.K13B_AT)+',\n'
 '  areaGroup:'+js_group(D.K13B_AT)+',\n'
 '  questions:Q_KCH13B.map(r=>({n:r[0],ans:r[1],p:r[2],area:r[3],type:r[4],page:0,misc:omFor(r[4])}))},\n'
 ' {id:"kch1to2-b",title:"화학1 1-2단원 모의고사 (동형)",range:"화학의 기초 ~ 주기율 · 원자의 세계",source:"조준모의고사 · 동형",N:0,estP:true,haeseol:"",\n'
 '  areaOrder:'+js_order(D.K12B_AT)+',\n'
 '  areaGroup:'+js_group(D.K12B_AT)+',\n'
 '  questions:Q_KCH12B.map(r=>({n:r[0],ans:r[1],p:r[2],area:r[3],type:r[4],page:0,misc:omFor(r[4])}))}\n];')
rep(anchor,newent,1,"동형 EXAMS")

# 3. 레이더 축 상한 가드: n>8 -> n>16 (9~13축 렌더, 회귀 수정)
rep("  if(n<3||n>8) return '';", "  if(n<3||n>16) return '';",1,"레이더 가드")

open(p,"w",encoding="utf-8").write(s)
print("index.html written, %d bytes"%len(s.encode("utf-8")))
