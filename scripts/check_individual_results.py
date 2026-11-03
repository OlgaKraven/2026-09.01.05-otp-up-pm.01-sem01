import json,pathlib,zipfile,xml.etree.ElementTree as ET,hashlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];F=ROOT/'output/playwright/individual'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
norm=lambda s:re.sub(r'\s+','',s)
def doc_text(path):
 with zipfile.ZipFile(path) as z:
  for name in z.namelist():
   if name.endswith('.xml'):ET.fromstring(z.read(name))
  doc=ET.fromstring(z.read('word/document.xml'))
  assert not doc.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}br'), 'Forced line breaks stretch justified paragraphs: '+str(path)
  return ''.join(doc.itertext())
results=[]
for s in read(F/'solutions.json'):
 v=s['variant'];initial=read(ROOT/f'site/stands/v{v}/initial.json');a=read(F/f'v{v}-result.json');b=read(F/f'v{v}-restored.json')
 assert a==b,('backup mismatch',v)
 assert a['variant']==v and a['subject']==s['subject'] and a['workcode']=='CHECK-'+v
 assert [(t['id'],t['description'],t['topic'],t['dossier']) for t in a['tickets']]==[(t['id'],t['description'],t['topic'],t['dossier']) for t in initial['tickets']]
 for expected,actual in zip(s['tickets'],a['tickets']):
  for k in ['summary','category','status','impact','additional_info']:assert expected[k]==actual[k],(v,k)
 assert {k:value for k,value in a['answers'].items() if value}==s['answers'] and len(s['answers'])==5
 assert a['cards']==s['cards'] and a['extra_answers']==s['extra_answers'] and len(a['extra_answers'])==2
 docs={kind:doc_text(F/f'v{v}-{kind}.docx') for kind in ['registry','answers','cards','report']}
 for kind,text in docs.items():
  assert s['subject'] in text and 'CHECK-'+v in text and 'DEMO-' not in text,(v,kind)
 for t in s['tickets']:
  for key in ['id','summary','category','impact','additional_info']:assert norm(t[key]) in norm(docs['registry']),(v,'registry',key,t['id'])
 for key,text in s['answers'].items():assert key in docs['answers'] and norm(text) in norm(docs['answers']),(v,'answer',key)
 for card in s['cards']:
  for key,text in card.items():assert norm(text) in norm(docs['cards']),(v,'card',key)
 for text in s['extra_answers']:assert norm(text) in norm(docs['report']),(v,'extra')
 results.append({'variant':v,'sourceDataUnchanged':True,'allSavedFieldsMatch':True,'restoredJsonEqual':True,'documentsParsed':4,'allRegistryRowsInDocx':True,'allRepliesInDocx':True,'allCardFieldsInDocx':True,'extraResultsInReportBase':True,'backupSha256':hashlib.sha256((F/f'v{v}-result.json').read_bytes()).hexdigest()})
objects=read(F/'objects-result.json')
assert len([r for r in objects if 'numeric' in r])==30 and len(objects)==45
assert len(list(F.glob('v*-registry.docx')))==30 and len(list(F.glob('v*-cards.docx')))==30
(F/'content-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: all 30 complete states, 300 dossiers and classifications, 150 replies, 60 maps, 60 tasks, 120 DOCX exports and 30 independent restores; actual objects checked separately.')
