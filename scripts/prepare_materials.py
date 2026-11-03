"""Build individual offline stands from the retained assignment and authored case inputs."""
from __future__ import annotations
import copy, html, json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'; DL=SITE/'downloads'
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def dump(p,d):write(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def h(s):return html.escape(str(s))
course=json.loads((ROOT/'content/course.json').read_text(encoding='utf-8'))
profiles=json.loads((ROOT/'content/case-inputs.json').read_text(encoding='utf-8'))
STYLE='''@font-face{font-family:Golos;src:url("fonts/GolosText.ttf")}*{box-sizing:border-box}body{margin:0;font:16px/1.65 Golos,Arial,sans-serif;color:#1c1c1c}header{background:#1c1c1c;color:white;border-bottom:6px solid #ed131c;padding:30px}h1{font-size:36px;line-height:1.2}h2{font-size:23px}main{max-width:1080px;margin:auto;padding:30px}.block{background:#f4f4f6;border-radius:14px;padding:24px;margin:20px 0}.route{border-left:2px solid #ddd;padding-left:25px}.check{border-top:1px solid #dfe1e5;padding-top:12px}a{color:#a40d14}header a{color:white}nav,.links{display:flex;gap:24px;flex-wrap:wrap}.button{padding:12px 18px;border:1px solid #aaa;border-radius:6px;display:inline-block;text-decoration:none}td,th{border:1px solid #ddd;padding:12px;text-align:left}table{border-collapse:collapse}img{max-width:100%}pre,code{white-space:pre-wrap;overflow-wrap:anywhere}@media print{nav,.screen{display:none}@page{size:A4;margin:20mm 20mm 20mm 30mm}body{font-size:12pt}.block{break-inside:avoid}header{background:white;color:black;padding:0}h1{font-size:24pt}main{padding:0}}'''
write(SITE/'assets/materials.css',STYLE)
assert (SITE/'assets/fonts/GolosText.ttf').is_file(), 'The bundled Golos Text font is required.'
assert (SITE/'assets/fonts/OFL.txt').is_file(), 'The font license must accompany the source.'
def page(title,body,nav=True):
    return f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}</title><link rel="stylesheet" href="assets/materials.css"></head><body><header><p>Учебная практика · ПМ.01</p><h1>{h(title)}</h1>'+('<nav><a href="index.html">Задание</a><a href="lessons.html">Методические рекомендации</a><a href="areas.html">Предметные области</a></nav>' if nav else '')+f'</header><main>{body}</main></body></html>'
def standalone(title,body):return page(title,body,False).replace('<link rel="stylesheet" href="assets/materials.css">','<style>'+STYLE[STYLE.index('*{'):].replace('Golos,Arial','Arial')+'</style>')
def block(title,text,check=''):
    return f'<section class="block"><h2>{h(title)}</h2>{text}'+(f'<p class="check"><b>Результат:</b> {h(check)}</p>' if check else '')+'</section>'
def other_fact(topic,n):
    t=topic.lower()
    if n==9:return 'Подтверждения полномочий на чужие данные, изменение прав или отключение защиты нет. Действие не выполнять; сформулировать границу и передачу уполномоченному специалисту.'
    if n==10:return 'Существенное условие намеренно не сообщено: '+topic+'. Уточнить его до вывода о причине. Объяснить, как полученный ответ повлияет на дальнейшую проверку.'
    if any(k in t for k in ['csv','нул','кодиров','символ','дат']):return 'Сверить sample.csv своей области: UTF-8, разделитель «;», код 001205, дата 2026-11-24, четыре столбца. Исходник не изменять. Если тема относится к другому файлу, это аналогичный приём, а не подтверждённая причина исходного случая.'
    if any(k in t for k in ['печат','этикет','масштаб']):return 'Досье: исходный документ содержит нижнюю строку; масштаб 110 %, формат вывода меньше макета. Физическая печать не проверялась. Модель print-lab.html показывает только влияние масштаба на границы страницы.'
    if any(k in t for k in ['письм','уведом','приглаш']):return 'Учебный журнал: M-01 «Учебное подтверждение», папка «Спам»; M-02 «Приглашение», папка «Рассылки». Реальная доставка не проверялась. Сформулировать безопасный поиск и условие передачи без запроса пароля.'
    if any(k in t for k in ['архив']):return 'Досье: archive-A — 0 байт, archive-B — 120 КБ. Это сведения реестра, архивы не предоставлены для восстановления. Зафиксировать ограничение и запросить неповреждённую копию у владельца.'
    if any(k in t for k in ['фото','вложен','изображ']):return 'Досье: форма принимает PDF/JPG/PNG до 2 МБ, photo.heic — 1 МБ, large.pdf — 3 МБ. Сопоставить формат и размер. Эти имена обозначают условия случая; реальный контрольный файл комплекта — control.svg.'
    if any(k in t for k in ['фильтр','поиск','не вид','не найден','не наход']):return 'Досье: активная запись 001205 скрыта фильтром «Архив». Отдельно сверить исходный код и условия поиска. Для другого пользователя этот результат не считать проверенным.'
    if any(k in t for k in ['язык','клавиатур']):return 'Досье: выбрана раскладка EN, ожидается RU. Разрешён выбор языка текущего ввода; системные политики не меняются.'
    if 'черновик' in t:return 'Досье: использовано приватное окно, после закрытия черновик отсутствует. Условия сохранения уточнить, восстановление не обещать.'
    return 'Досье: доступны только исходное сообщение и учебный контакт. Уточнить точный файл или адрес, версию программы, действие и сообщение. Проверку чужого устройства или внешней системы без доступа не объявлять выполненной.'
demo=json.loads((ROOT/'content/demo-source.json').read_text(encoding='utf-8')) if (ROOT/'content/demo-source.json').exists() else json.loads((DL/'demo-tickets.json').read_text(encoding='utf-8'))
demo['reply_ticket_numbers']=[1,4,6,8,10];demo['knowledge_card_topics']=[demo['tickets'][0]['topic'],demo['tickets'][3]['topic']]
demo['additional_tasks']=['Сопоставить старый и актуальный маршрут расписания','Проверить сохранение кода и даты при чтении CSV']
demo['additional_inputs']=['На портале даны старый маршрут и действующие группы A/B. Проверить обе группы после смены маршрута.','sample.csv: код 001205, дата 2026-11-24, UTF-8, разделитель «;». Сначала прочитать исходник.']
demo_facts=['Старый маршрут portal/old.html больше не используется. Действующий вход portal/index.html; сравнение выполнить на предоставленных страницах.','Роль «Слушатель» не имеет права на административное расписание. Согласование доступа не предоставлено.','Тот же симптом, но адрес и группа не сообщены. Причина не установлена.','В print-lab.html масштаб 110 %: нижняя строка выходит за границу модели страницы. Проверить 100 %.','Досье: использована старая редакция сертификата v1 без нижней строки. Изменение масштаба не добавит отсутствующий текст.','В учебном журнале M-01 «Учебное подтверждение» находится в «Спам». Реальная почта не используется.','В реестре archive-A — 0 байт, archive-B — 120 КБ. Восстановление не выполнялось.','sample.csv содержит код 001205 и дату 2026-11-24. Сравнить чтение при разных разделителях и типах кода.','Запрошен журнал другой группы. Подтверждённых полномочий нет. Доступ не менять.','Версия браузера не указана. Запросить название и версию, адрес, время и текст ошибки; причина пока неизвестна.']
data=[]
for source in [demo]+course['areas']:
    d=copy.deepcopy(source);v=d['variant'];pr=profiles.get(v)
    d['stand_id']='pm01-'+v.lower()
    for i,t in enumerate(d['tickets'],1):
        if v=='DEMO':t['dossier']=demo_facts[i-1]
        elif i==1:t['dossier']=pr[0]
        elif i==2:t['dossier']='Отдельный случай второго пользователя. '+pr[0]+' Самостоятельная проверка на его рабочем месте ещё не выполнена.'
        elif i==3:t['dossier']='Отдельный случай третьего пользователя. Причина из обращения 01 для него не подтверждена. Уточнить объект, время появления и недавнее изменение; одинаковая тема не доказывает одинаковую причину.'
        elif i in (4,5):t['dossier']=pr[1]+(' Проверка на рабочем месте пользователя 05 отдельно не выполнена.' if i==5 else '')
        else:t['dossier']=other_fact(t['topic'],i)
    if pr:d['additional_inputs']=pr[2:]
    code='001205' if v=='DEMO' else f'{int(v):03d}205'
    d['controls']={'code':code,'next_code':str(int(code)+1).zfill(6),'date':'2026-11-24','rows':2,'columns':4}
    if v!='DEMO':
        for t in d['tickets']:t['dossier']=t['dossier'].replace('001205',code).replace('001206',d['controls']['next_code'])
        d['additional_inputs']=[s.replace('001205',code).replace('001206',d['controls']['next_code']) for s in d['additional_inputs']]
    d['materials']={title:f'materials/{v}/{path}' for title,path in [('Досье десяти обращений','dossier.html'),('Исходные данные и реестр','raw-data.html'),('CSV своей области','sample.csv'),('Проверка CSV','csv-lab.html'),('Контрольная рамка и отрезок','control.svg'),('Модель страницы печати','print-lab.html')]}
    if v=='DEMO':d['materials']['Учебный портал расписания']='materials/DEMO/portal/index.html'
    data.append(d)
dump(ROOT/'content/demo-source.json',data[0]);dump(ROOT/'content/stands.json',data)
CSVLAB='''<!doctype html><html lang="ru"><meta charset="utf-8"><title>Проверка CSV</title><style>body{font:18px/1.6 Arial;max-width:1000px;margin:30px auto;padding:20px}label{display:block;margin:15px}td,th{border:1px solid #999;padding:15px}table{border-collapse:collapse}pre{background:#f4f4f6;padding:20px}</style><h1>Проверка CSV своей области</h1><p>Выбрать sample.csv этого комплекта. Исходный файл не изменяется.</p><label>Файл CSV <input id="file" type="file" accept=".csv"></label><label>Кодировка <select id="encoding"><option value="utf-8">UTF-8</option><option value="windows-1251">Windows-1251</option></select></label><label>Разделитель <select id="delimiter"><option value=",">Запятая</option><option value=";">Точка с запятой</option></select></label><label>Тип первого столбца <select id="type"><option value="number">Число</option><option value="text">Текст</option></select></label><h2>Исходный текст</h2><pre id="source"></pre><h2>Результат чтения</h2><div id="result"></div><p id="status" role="status"></p><script>
const $=s=>document.querySelector(s),esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));let bytes;
function parse(s,del){let rows=[],row=[],v='',quoted=false;for(let i=0;i<s.length;i++){let c=s[i];if(c==='"'){if(quoted&&s[i+1]==='"'){v+='"';i++}else quoted=!quoted}else if(!quoted&&c===del){row.push(v);v=''}else if(!quoted&&c==='\\n'){row.push(v.replace(/\\r$/,''));rows.push(row);row=[];v=''}else v+=c}if(v||row.length){row.push(v);rows.push(row)}return rows}
function render(){if(!bytes)return;const text=new TextDecoder($('#encoding').value).decode(bytes);$('#source').textContent=text;const rows=parse(text,$('#delimiter').value);$('#result').innerHTML='<table>'+rows.map((r,i)=>'<tr>'+r.map((v,j)=>{if(i&&j===0&&$('#type').value==='number'&&/^\\d+$/.test(v))v=String(Number(v));return '<'+(i?'td':'th')+'>'+esc(v)+'</'+(i?'td':'th')+'>'}).join('')+'</tr>').join('')+'</table>';$('#status').textContent='Строк данных: '+(rows.length-1)+'; столбцов в заголовке: '+rows[0].length}
$('#file').onchange=async e=>{bytes=await e.target.files[0].arrayBuffer();render()};for(const id of ['encoding','delimiter','type'])$('#'+id).onchange=render;</script></html>'''
PRINTLAB='''<!doctype html><html lang="ru"><meta charset="utf-8"><title>Проверка макета печати</title><style>body{font:18px/1.5 Arial;margin:25px}#page{width:600px;height:430px;border:2px solid #333;overflow:hidden;background:#f4f4f6;margin:20px 0}#sheet{box-sizing:border-box;width:596px;height:425px;border:3px solid #ed131c;position:relative;transform-origin:top left;background:white;padding:35px}#bottom{position:absolute;bottom:10px;left:30px}select{font:inherit}</style><h1>Учебный макет сертификата</h1><p>Модель границы страницы показывает влияние масштаба. Она не подтверждает физическую печать.</p><label>Масштаб <select id="scale"><option value="1.1">110 %</option><option value="1">100 %</option></select></label><div id="page"><article id="sheet"><h2>СЕРТИФИКАТ</h2><p>Учебный курс технической поддержки</p><p>Контроль: четыре стороны рамки и нижняя строка.</p><p id="bottom">Нижняя строка · учебный образец</p></article></div><p id="result" role="status"></p><script>const s=document.querySelector('#scale');function render(){document.querySelector('#sheet').style.transform='scale('+s.value+')';document.querySelector('#result').textContent=Number(s.value)>1?'Часть рамки и нижняя строка выходят за границу страницы.':'Четыре стороны рамки и нижняя строка находятся внутри страницы.'}s.onchange=render;render()</script></html>'''
for d in data:
    v=d['variant'];target=SITE/'stands'/('demo' if v=='DEMO' else 'v'+v);target.mkdir(parents=True,exist_ok=True)
    for f in (ROOT/'support-desk').glob('*'):
        if f.is_file():shutil.copy2(f,target/f.name)
    write(target/'stand.js','window.INIT_DATA='+json.dumps(d,ensure_ascii=False)+';\n')
    mat=target/'materials'/v;mat.mkdir(parents=True,exist_ok=True)
    write(mat/'sample.csv','code;title;date;address\n'+d['controls']['code']+';Учебная запись '+v+';2026-11-24;"Город, улица 1"\n'+d['controls']['next_code']+';Вторая запись '+v+';2026-11-25;"Город, улица 2"\n')
    write(mat/'csv-lab.html',CSVLAB);write(mat/'print-lab.html',PRINTLAB)
    write(mat/'control.svg','<svg xmlns="http://www.w3.org/2000/svg" width="120mm" height="80mm" viewBox="0 0 120 80"><rect x="1" y="1" width="118" height="78" fill="white" stroke="black"/><path d="M10 40H110 M10 35V45 M110 35V45" stroke="black"/><text x="60" y="30" text-anchor="middle" font-size="7">100 mm</text><text x="60" y="65" text-anchor="middle" font-size="5">'+v+'</text></svg>')
    raw=f'<h2>Область {h(v)} · {h(d["subject"])}</h2><p>Это исходные сведения учебного случая. Собственные измерения отмечаются отдельно.</p><h2>Контрольная строка CSV</h2><pre>001205;Учебная запись {v};2026-11-24;"Город, улица 1"</pre><p>UTF-8, разделитель «;», четыре столбца, первая колонка — текстовый код. Две строки данных.</p><h2>Реестр</h2><p>Учебные записи 001205 и 001206; действующая редакция документов v2. M-01 «Учебное подтверждение» — «Спам»; M-02 «Приглашение» — «Рассылки».</p><p>Имена archive-A (0 байт), archive-B (120 КБ), small.pdf (1 МБ), large.pdf (3 МБ), photo.heic (1 МБ) обозначают сведения досье. Эти файлы не выдаются за предоставленные или восстановленные. Реальные файлы: sample.csv и control.svg; цифровые проверки: csv-lab.html и print-lab.html.</p><h2>Полномочия</h2><p>Пользователь — собственные объекты; оператор — назначенные обращения; администратор — согласованные изменения прав. Реальные пароли и персональные данные не используются.</p>'+''.join(f'<h3>{h(t)}</h3><p>{h(i)}</p>' for t,i in zip(d['additional_tasks'],d['additional_inputs']))
    raw=raw.replace('001205',d['controls']['code']).replace('001206',d['controls']['next_code'])
    write(mat/'raw-data.html',standalone('Исходные данные',raw))
    write(mat/'dossier.html',standalone('Досье · '+d['subject'],''.join(block(t['id']+' · '+t['topic'],f'<p>{h(t["description"])}</p><p>Канал: {h(t["channel"])}. Контакт: {h(t["requester"])}.</p><p><b>Предоставлено:</b> {h(t["dossier"])}</p>') for t in d['tickets'])))
    if v=='DEMO':
        portal=mat/'portal'
        write(portal/'old.html',standalone('Устаревший маршрут','<p>Сохранённый маршрут больше не используется.</p><a href="index.html">Открыть главную страницу учебного портала</a>'))
        write(portal/'index.html',standalone('Учебный портал · расписание','<p><a href="schedule-a.html">Группа A</a></p><p><a href="schedule-b.html">Группа B</a></p><p><a href="old.html">Старая сохранённая ссылка</a></p>'))
        for group,time in [('a','10:00'),('b','12:00')]:write(portal/('schedule-'+group+'.html'),standalone('Расписание группы '+group.upper(),f'<p>Учебный курс · 24.11.2026 · {time}</p><a href="index.html">К выбору группы</a>'))
    dump(DL/('demo-tickets.json' if v=='DEMO' else 'variant-'+v+'.json'),d);dump(target/'initial.json',d)
    shutil.copytree(mat,SITE/'support-desk'/'materials'/v,dirs_exist_ok=True)
for f in (ROOT/'support-desk').glob('*'):
    if f.is_file():shutil.copy2(f,SITE/'support-desk'/f.name)
assignment=[
('Обработать десять обращений','Зарегистрировать все обращения назначенной области, сохранить исходные факты, написать краткий пересказ, выбрать категорию и статус, обосновать влияние. Для неполных сообщений сформулировать вопросы. Не объединять разные случаи только из-за одинаковой темы.'),
('Подготовить пять ответов','Оформить ответы по обращениям 01, 04, 06, 08 и 10. Включить понятные действия, проверку результата, профилактику при применимости и условие передачи специалисту. Не обещать невыполненное исправление.'),
('Разработать две технологические карты','Выбрать две повторяющиеся темы. Раскрыть задачу, материалы и совместимость, действия, проверку и возможные проблемы. Скачивание и установка требуются только при наличии такого действия в выбранном случае.'),
('Проверить факты и границы','Использовать досье и файлы собственного стенда. Для предоставленных цифровых объектов сохранить исходное состояние, действие, ожидаемый и фактический результат. После изменения повторить исходный и соседний безопасный сценарий. Для внешних устройств без доступа выполнить анализ досье и план проверки, не объявлять ремонт выполненным.'),
('Выполнить дополнительные задачи','Выполнить обе задачи своей области с её исходными данными. Обосновать выводы. Запрос чужих прав, данных, паролей или отключения защиты передать уполномоченному специалисту без выполнения.'),
('Сохранить и представить результат','Подготовить таблицу десяти обращений DOCX, файл пяти ответов DOCX, файл двух карт DOCX, общий отчёт по форме и резервную копию JSON. В отчёт включить собственные доказательства проверок и восстановления, решения дополнительных задач, ограничения и вывод. Две карты разместить на отдельных страницах.')]
dump(ROOT/'content/assignment-sections.json',[{'title':t,'text':s} for t,s in assignment])
write(SITE/'index.html',page('Поддержка клиентов по вопросам эксплуатации технологических компонентов','<p>09.01.05 «Оператор технической поддержки» · семестр 1.</p>'+''.join(block(str(i)+'. '+t,'<p>'+h(s)+'</p>') for i,(t,s) in enumerate(assignment,1))+'<p class="links"><a href="areas.html">Выбрать предметную область</a><a href="lessons.html">Методические рекомендации</a><a href="downloads/assignment.pdf">Предметные области · PDF</a></p>'))
areas='<article class="card area-card">'+block('Демонстрационная область','<p>Центр дополнительного образования. Образец показывает способ работы; отдельная полная сдача демонстрации не требуется.</p><p><a href="stands/demo/index.html">Открыть образец</a> · <a href="downloads/stand-demo.zip">Скачать автономно</a> · <a href="downloads/demo-result.zip">Готовый результат для сверки</a></p>')+'</article>'
for d in data[1:]:
    v=d['variant'];areas+=f'<article class="card area-card" id="v{v}">'+block('Вариант '+v+'. '+d['subject'],f'<p>{h(d.get("context",""))}</p><p>Индивидуальная работа {h(d["stand_id"])}: обращения {h(d["tickets"][0]["id"])}–{h(d["tickets"][-1]["id"])}. Код работы назначается преподавателем; имён студентов в исходных данных нет.</p><p><a href="stands/v{v}/index.html">Открыть свой стенд</a> · <a href="downloads/stand-{v}.zip">Скачать свой стенд</a> · <a href="downloads/variant-{v}.pdf">Карточка области · PDF</a> · <a href="downloads/variant-{v}.json">Исходные обращения · JSON</a></p>')+'<div class="route">'
    for title,text,check in [('1. Подготовить собственные данные',f'Распаковать stand-{v}.zip в отдельную папку, открыть index.html. Для продолжения восстановить собственный JSON вместо загрузки исходника.',f'В заголовке «{d["subject"]}», десять ID своего варианта.'),('2. Обработать обращения','Выполнить общее задание: десять карточек, пять ответов и две карты. Темы карт: '+'; '.join(d['knowledge_card_topics'])+'.','Обоснованы категории, статусы, влияние, уточнения и границы.'),('3. Выполнить индивидуальные условия','\n'.join(t+'. '+i for t,i in zip(d['additional_tasks'],d['additional_inputs'])),'В разделе «Данные стенда» сохранены решения обеих задач.'),('4. Подготовить сдачу','Скачать документы, добавить доказательства в отчёт. Экспортировать JSON, закрыть сеанс, восстановить работу и проверить собственный ответ и обе карты.','Документы относятся к своей области; данные демонстрации не перенесены автоматически.')]:areas+=block(title,'<p>'+h(text).replace('\n','</p><p>')+'</p>',check)
    areas+='</div></article>'
write(SITE/'areas.html',page('Предметные области',areas))
print('Prepared 30 personal stands and a separate demonstration.')
