"""Publish the retained practice data through EatDoners' declarative page schema."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda name:json.loads((ROOT/'content'/name).read_text(encoding='utf-8-sig'))
course=read('course.json');stands=read('stands.json');guide=read('guide.json');solution=read('demo-solution.json')
site='https://olgakraven.github.io/2026-09.01.05-otp-up-pm.01-sem01/'
if isinstance(course['assignment'],dict):course['assignment_requirements']=course['assignment']
assert course['assignment_requirements']=={'tickets':10,'responses':[1,4,6,8,10],'knowledge_cards':2}
course['schema_version']=2
course['assignment']=[{'title':'Общее задание ПМ.01','blocks':[{'title':s['title'],'text':s['text']} for s in read('assignment-sections.json')]}]
course['guide']=[]
for item in guide:
 blocks=[{'title':'Порядок работы','text':'\n\n'.join(item['paragraphs'])}]
 key=item.get('solution')
 if key in ['registry','classifications']:
  for i,values in enumerate(solution['classifications'],1):
   blocks.append({'title':f'DEMO-{i:02d}','text':'\n'.join(label+': '+value for label,value in zip(['Категория','Статус','Пересказ','Факты и проверка'],values))})
 elif key=='answers':blocks.extend({'title':name,'text':value} for name,value in solution['answers'].items())
 elif key=='cards':
  for i,card in enumerate(solution['cards'],1):blocks.append({'title':'Карта '+str(i)+'. '+card['topic'],'text':'\n\n'.join(label+': '+card[k] for k,label in [('task','Задача'),('materials','Материалы'),('steps','Действия'),('check','Проверка'),('problems','Проблемы и передача')])})
 elif key=='extra_answers':blocks.extend({'title':'Решение задачи '+str(i),'text':value} for i,value in enumerate(solution['extra_answers'],1))
 elif key:raise ValueError('Unknown example solution '+key)
 blocks.append({'title':'Проверка результата','text':item['check']})
 for image in item.get('images',[])+([item['image']] if item.get('image') else []):
  path='site/assets/walkthrough/'+image;assert (ROOT/path).is_file()
  blocks.append({'kind':'image','title':item['title'],'text':item['title'],'path':path})
 course['guide'].append({'title':item['title'],'blocks':blocks})
by_variant={s['variant']:s for s in stands}
for area in course['areas']:
 v=area['variant'];stand=by_variant[v]
 area['title']='Вариант '+v+' · '+area['subject']
 area['blocks']=[{'title':'Индивидуальные данные','text':area['context']+'\nСобственный стенд: '+site+'stands/v'+v+'/index.html\nАвтономный комплект: '+site+'downloads/stand-'+v+'.zip\nКонтрольный код: '+stand['controls']['code']+'. Сведения досье отделять от самостоятельно выполненных проверок.'}]
 for t in stand['tickets']:
  area['blocks'].append({'title':t['id']+' · '+t['topic'],'text':'Канал: '+t['channel']+'. Контакт: '+t['requester']+'.\n'+t['description']+'\nПредоставлено по досье: '+t['dossier']})
 for i,(task,inputs) in enumerate(zip(stand['additional_tasks'],stand['additional_inputs']),1):area['blocks'].append({'title':'Дополнительная задача '+str(i),'text':task+'\n'+inputs})
 area['blocks'].append({'title':'Файлы своей области','text':'\n'.join('['+label+']('+site+'stands/v'+v+'/'+path+')' for label,path in stand['materials'].items())})
(ROOT/'content/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Prepared declarative assignment, guide and 30 areas; all retained request data preserved.')
