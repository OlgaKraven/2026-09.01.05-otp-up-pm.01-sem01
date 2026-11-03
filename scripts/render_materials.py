"""Render the complete teaching sources and package the verified offline stands."""
from __future__ import annotations
import html, json, os, shutil, zipfile
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from fontTools.ttLib import TTFont as Font
from fontTools.varLib.instancer import instantiateVariableFont
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';DL=SITE/'downloads';WIDTH=A4[0]-50*mm
BASE='https://olgakraven.github.io/2026-09.01.05-otp-up-pm.01-sem01/'
def read(name):return json.loads((ROOT/'content'/name).read_text(encoding='utf-8'))
def h(s):return html.escape(str(s)).replace('\n','<br/>')
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
fontdir=SITE/'assets/fonts'
for weight,name in [(400,'Golos'),(700,'GolosBold')]:
    dest=fontdir/(name+'.ttf')
    if not dest.exists():
        f=Font(fontdir/'GolosText.ttf');instantiateVariableFont(f,{'wght':weight},inplace=True).save(dest)
    pdfmetrics.registerFont(TTFont(name,str(dest)))
pdfmetrics.registerFontFamily('Golos',normal='Golos',bold='GolosBold')
times_candidates=[Path(os.environ.get('PM01_TIMES_FONT','')),Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/times.ttf',Path('/Library/Fonts/Microsoft/Times New Roman.ttf')]
times_path=next((p for p in times_candidates if p.is_file()),None)
if times_path is None:raise FileNotFoundError('Set PM01_TIMES_FONT to an installed Times New Roman TTF file.')
pdfmetrics.registerFont(TTFont('TimesCaption',str(times_path)))
body=ParagraphStyle('Body',fontName='Golos',fontSize=12,leading=18,spaceAfter=10,textColor=colors.HexColor('#1c1c1c'),splitLongWords=True)
small=ParagraphStyle('Small',parent=body,fontSize=10,leading=14)
sub=ParagraphStyle('Sub',parent=body,fontName='GolosBold',fontSize=15,leading=20,spaceBefore=12,keepWithNext=True)
caption=ParagraphStyle('Caption',fontName='TimesCaption',fontSize=12,leading=14,alignment=TA_CENTER,spaceBefore=8)
white=ParagraphStyle('White',fontName='GolosBold',fontSize=23,leading=29,textColor=colors.white)
class Doc(BaseDocTemplate):
    def __init__(self,path,label):
        super().__init__(str(path),pagesize=A4,leftMargin=30*mm,rightMargin=20*mm,topMargin=20*mm,bottomMargin=20*mm,title=label,author='',allowSplitting=True)
        self.label=label;self.sequence=0
        frame=Frame(self.leftMargin,self.bottomMargin,self.width,self.height,id='normal',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='normal',frames=[frame],onPageEnd=self.decorate))
    def beforeDocument(self):
        self.sequence=0
        self.running=self.label
    def decorate(self,c,doc):
        c.saveState();c.setFont('Golos',8);c.setFillColor(colors.HexColor('#606773'));c.drawString(30*mm,12*mm,self.running);c.drawRightString(A4[0]-20*mm,12*mm,str(doc.page));c.restoreState()
    def afterFlowable(self,f):
        if getattr(f,'_toc_title',None):
            if f._toc_title.startswith('Вариант '):self.running=f._toc_title
            self.sequence+=1;key='section-'+str(self.sequence);self.canv.bookmarkPage(key);self.canv.addOutlineEntry(f._toc_title,key,0,False);self.notify('TOCEntry',(0,f._toc_title,self.page,key))
def P(s,style=body):return Paragraph(h(s),style)
def link(label,url):return Paragraph('<link href="'+html.escape(url,quote=True)+'" color="#a40d14"><u>'+h(label)+'</u></link>',body)
def heading(title,kicker=''):
    flows=[]
    if kicker:flows.append(Paragraph(h(kicker),ParagraphStyle('Kicker',parent=small,textColor=colors.white)))
    flows.append(Paragraph(h(title),white))
    t=Table([[flows]],colWidths=[WIDTH]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#1c1c1c')),('BOX',(0,0),(-1,-1),0,colors.white),('LINEBELOW',(0,0),(-1,-1),4,colors.HexColor('#ed131c')),('LEFTPADDING',(0,0),(-1,-1),18),('RIGHTPADDING',(0,0),(-1,-1),18),('TOPPADDING',(0,0),(-1,-1),16),('BOTTOMPADDING',(0,0),(-1,-1),18)]));t._toc_title=title
    return [t,Spacer(1,16)]
def block(title,paras,check='',number=''):
    def make(texts,continued=False,with_check=False):
        content=[P(title+(' · продолжение' if continued else ''),sub)]+[P(p) for p in texts]
        if with_check and check:content+=[P('Проверка: '+check,ParagraphStyle('Check',parent=body,fontName='GolosBold',spaceBefore=8))]
        t=Table([[P(number,sub),content]],colWidths=[24,WIDTH-24])
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(1,0),(1,0),colors.HexColor('#f4f4f6')),('LEFTPADDING',(1,0),(1,0),14),('RIGHTPADDING',(1,0),(1,0),14),('TOPPADDING',(1,0),(1,0),10),('BOTTOMPADDING',(1,0),(1,0),10),('LEFTPADDING',(0,0),(0,0),0)]))
        return t
    chunks=[];chunk=[]
    for para in paras:
        test=make(chunk+[para],bool(chunks),False)
        if chunk and test.wrap(WIDTH,10000)[1]>490:chunks.append(chunk);chunk=[]
        chunk.append(para)
    chunks.append(chunk)
    if make(chunks[-1],len(chunks)>1,True).wrap(WIDTH,10000)[1]>580 and len(chunks[-1])>1:
        last=chunks[-1].pop();chunks.append([last])
    return [KeepTogether([make(c,i>0,i==len(chunks)-1),Spacer(1,15)]) for i,c in enumerate(chunks)]
def toc():
    t=TableOfContents();t.levelStyles=[ParagraphStyle('TOC',parent=body,fontSize=11,leading=16,spaceBefore=6,rightIndent=22)];return t
data=read('stands.json');guide=read('guide.json');assignment=read('assignment-sections.json');solution=read('demo-solution.json')
def full_assignment():
    out=heading('1. Полное задание','Учебная практика · семестр 1')
    out+=[P('Обработать поток обращений учебной службы поддержки в назначенной предметной области. Образец показывает способ выполнения; самостоятельный результат создаётся на данных индивидуального стенда.')]
    for i,s in enumerate(assignment,1):out+=block(s['title'],[s['text']],number=str(i))
    return out
def area_story(d,include_toc=False):
    v=d['variant'];out=heading('Вариант '+v+'. '+d['subject'],'Предметная область · ПМ.01')
    out+=[P(d.get('context','')),P('Индивидуальный стенд '+d['stand_id']+'. Использовать собственную папку и код работы, назначенный преподавателем. Образец DEMO служит только объяснением способа.')]
    out+=[link('Открыть стенд области',BASE+'stands/v'+v+'/index.html'),link('Скачать автономный стенд области',BASE+'downloads/stand-'+v+'.zip')]
    out+=block('1. Подготовить собственные данные',[f'Распаковать stand-{v}.zip и открыть index.html. Для новой работы проверить десять ID своего варианта. Для продолжения использовать поле восстановления и свой JSON; это альтернативные пути, а не два обязательных импорта.',f'Собственный контрольный код {d["controls"]["code"]}, дата {d["controls"]["date"]}; в CSV две строки и четыре столбца. Файлы лежат в materials/{v}.'],f'В заголовке «{d["subject"]}», ID от {d["tickets"][0]["id"]} до {d["tickets"][-1]["id"]}.')
    out+=block('2. Обработать обращения',['Зарегистрировать десять карточек, подготовить ответы 01, 04, 06, 08, 10 и две карты. Метод действий раскрыт в общей методичке.','Повторяющиеся темы карт: '+'; '.join(d['knowledge_card_topics'])+'.','Досье — предоставленные условия задачи. Собственные результаты цифровых проверок записывать отдельно. Анализ отсутствующего внешнего объекта не объявлять выполненным ремонтом.'],'Заполнены пересказы, категории, статусы, влияние и уточняющие вопросы.')
    out+=[link('Методические рекомендации с разбором',BASE+'downloads/guide.pdf')]
    for i,t in enumerate(d['tickets'],1):
        out+=block(t['id']+' · '+t['topic'],['Источник: '+t['channel']+'. Контакт: '+t['requester']+'.',t['description'],'Досье учебного случая: '+t['dossier']],number=str(i))
    out+=heading('Индивидуальные условия · '+v+' · '+d['subject'])
    for i,(task,inp) in enumerate(zip(d['additional_tasks'],d['additional_inputs']),1):out+=block('Дополнительная задача '+str(i),[task,inp],'Названы исходные факты, сравниваемые условия, вывод и ограничение.')
    out+=block('3. Проверить и сохранить результат',['Для предоставленного файла сохранить исходное состояние, действие, ожидаемый и фактический результат. После изменения проверить исходный и соседний безопасный сценарий. Для анализа досье указать источник каждого вывода.','Скачать таблицу десяти обращений, пять ответов, две карты и основу отчёта. Добавить доказательства и решения обеих задач. Экспортировать JSON, открыть новый сеанс и восстановить его.'],'Документы и резервная копия относятся к своей области, а обе карты доступны после восстановления.')
    out+=[P('Файлы стенда: dossier.html — полное досье; raw-data.html — роли, реестр и условия; sample.csv — собственные данные; csv-lab.html — проверка чтения; control.svg — рамка и отрезок 100 мм; print-lab.html — модель масштаба. Имена иных файлов в досье не означают, что они предоставлены для испытания.')]
    return out
story=heading('Список предметных областей','ПМ.01 · 09.01.05 · семестр 1')+[P('Общее задание и индивидуальные стенды. Для работы можно скачать отдельную карточку назначенной области и её автономный комплект.'),PageBreak()]+heading('Содержание')+[toc(),PageBreak()]+full_assignment()
for d in data[1:]:
    story+=[PageBreak()]+area_story(d)
    Doc(DL/('variant-'+d['variant']+'.pdf'),'ПМ.01 · '+d['subject']).build(area_story(d))
Doc(DL/'assignment.pdf','ПМ.01 · Список предметных областей').multiBuild(story)
# Guide: the complete assignment precedes files, which precede the walkthrough.
story=heading('Методические рекомендации','Обработка обращений · ПМ.01')+[P('Пошаговый разбор на центре дополнительного образования и перенос на индивидуальную предметную область. Снимки показывают выполненный проход учебного комплекта.'),PageBreak()]+heading('Содержание')+[toc(),PageBreak()]+full_assignment()+[PageBreak()]+heading('2. Файлы для работы')
files=[('Демонстрационный стенд — распаковать до разбора','stand-demo.zip'),('Демонстрационные исходные обращения — для общего сервиса','demo-tickets.json'),('Готовый результат — только для сверки','demo-result.zip'),('Пустая форма отчёта','report-template.docx'),('Предметные области и индивидуальные данные','assignment.pdf'),('Общий сервис для импорта JSON','support-desk.zip')]
for label,file in files:story+=[link(label,BASE+'downloads/'+file)]
story+=[P('В карточке своей области находятся её отдельный стенд, JSON и PDF. Архив стенда содержит реестр, файлы и досье; готовый демонстрационный результат не используется вместо собственных исходных данных.'),PageBreak()]
figure=0;html_sections=[]
for n,s in enumerate(guide,1):
    title='3.'+str(n)+'. '+s['title'];story+=heading(title,'Разбор на демонстрационной области')
    story+=block(s['title'],s['paragraphs'],s['check'],str(n))
    extra=''
    if s.get('solution')=='classifications':
        for i,(cat,status,summary,info) in enumerate(solution['classifications'],1):
            story+=block('DEMO-'+str(i).zfill(2),[summary,'Категория: '+cat+'. Статус: '+status+'.','Влияние: подтверждён один заявитель, остальные не установлены.',info])
            extra+=f'<div class="block"><h3>DEMO-{i:02d}</h3><p>{h(cat)} · {h(status)}</p><p>{h(summary)}</p><p>{h(info)}</p></div>'
    if s.get('solution')=='answers':
        for key,val in solution['answers'].items():story+=block(key,[val]);extra+=f'<h3>{h(key)}</h3><p>{h(val)}</p>'
    if s.get('solution')=='cards':
        for i,c in enumerate(solution['cards'],1):
            story+=[PageBreak()]+heading('Карта '+str(i)+'. '+c['topic'])
            story+=block('Порядок выполнения',[label+': '+c[key] for key,label in [('task','Задача'),('materials','Материалы и совместимость'),('steps','Действия'),('check','Проверка'),('problems','Возможные проблемы')]])
            labels={'task':'Задача','materials':'Материалы и совместимость','steps':'Действия','check':'Проверка','problems':'Возможные проблемы'}
            extra+='<div class="block"><h3>'+h(c['topic'])+'</h3>'+''.join('<p><b>'+h(labels[k])+':</b> '+h(v)+'</p>' for k,v in c.items() if k!='topic')+'</div>'
    if s.get('solution')=='extra_answers':
        for i,val in enumerate(solution['extra_answers'],1):story+=block('Результат задачи '+str(i),[val]);extra+='<p>'+h(val)+'</p>'
    images=s.get('images',[])+([s['image']] if s.get('image') else [])
    html_images=''
    for img in images:
        source=SITE/'assets/walkthrough'/img
        if not source.is_file():raise FileNotFoundError('Capture the actual walkthrough first: '+str(source))
        figure+=1;image=Image(str(source));scale=min(WIDTH/image.imageWidth,570/image.imageHeight);image.drawWidth=image.imageWidth*scale;image.drawHeight=image.imageHeight*scale
        story+=[PageBreak()]+heading(s['title'],'Снимок выполненного действия')+[image,P('Рисунок '+str(figure)+' — '+s['title']+' ('+str(images.index(img)+1)+')',caption)]
        html_images+=f'<figure><img loading="lazy" src="assets/walkthrough/{img}" alt="{h(s["title"])}"><figcaption>Рисунок {figure} — {h(s["title"])}</figcaption></figure>'
    html_sections.append(f'<section id="step-{n}"><h2>{h(title)}</h2>'+''.join('<p>'+h(p)+'</p>' for p in s['paragraphs'])+'<p class="check"><b>Проверка:</b> '+h(s['check'])+'</p>'+extra+html_images+'</section>')
    story+=[PageBreak()]
if isinstance(story[-1],PageBreak):story.pop()
Doc(DL/'guide.pdf','ПМ.01 · Методические рекомендации').multiBuild(story)
nav='<p><a href="downloads/guide.pdf">Скачать методические рекомендации · PDF</a></p><ol>'+''.join(f'<li><a href="#step-{i}">{h(s["title"])}</a></li>' for i,s in enumerate(guide,1))+'</ol>'
html_start='<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Методические рекомендации ПМ.01</title><link rel="stylesheet" href="assets/materials.css"><header><h1>Методические рекомендации</h1><nav><a href="index.html">Задание</a><a href="areas.html">Предметные области</a></nav></header><main>'
write(SITE/'lessons.html',html_start+'<h2>1. Полное задание</h2>'+''.join('<div class="block"><h3>'+h(s['title'])+'</h3><p>'+h(s['text'])+'</p></div>' for s in assignment)+'<h2>2. Файлы для работы</h2>'+''.join('<p><a href="downloads/'+f+'">'+h(l)+'</a></p>' for l,f in files)+'<h2>3. Разбор образца</h2>'+nav+''.join(html_sections)+'</main></html>')
# Use actual UI exports, including the restored JSON, as the comparison package.
result=ROOT/'output/playwright/demo-result.json';restored=ROOT/'output/playwright/restored-result.json'
if json.loads(result.read_text(encoding='utf-8'))!=json.loads(restored.read_text(encoding='utf-8')):raise ValueError('Restored state differs from the exported walkthrough')
with zipfile.ZipFile(DL/'demo-result.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.write(result,'demo-result.json')
    for name in ['registry','answers','cards','report']:z.write(ROOT/f'output/playwright/demo-{name}.docx','demo-'+name+'.docx')
    for f in sorted((SITE/'assets/walkthrough').glob('*.png')):z.write(f,'evidence/'+f.name)
for d in data:
    v=d['variant'];folder=SITE/'stands'/('demo' if v=='DEMO' else 'v'+v);fname='stand-demo.zip' if v=='DEMO' else 'stand-'+v+'.zip'
    with zipfile.ZipFile(DL/fname,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(folder.rglob('*')):
            if f.is_file():z.write(f,f.relative_to(folder))
with zipfile.ZipFile(DL/'support-desk.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted((SITE/'support-desk').rglob('*')):
        if f.is_file():z.write(f,f.relative_to(SITE/'support-desk'))
print('Rendered complete assignment, 30 area PDFs, guide with '+str(figure)+' genuine screenshots; packaged all stands.')
