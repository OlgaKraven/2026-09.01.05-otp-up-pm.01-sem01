"""Editable PM.01 report with data fields, repository link and figure spaces."""
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

REPOSITORY='https://github.com/OlgaKraven/2026-09.01.05-otp-up-pm.01-sem01'
SITE='https://olgakraven.github.io/2026-09.01.05-otp-up-pm.01-sem01/'

def build():
 root=Path(__file__).resolve().parents[1]
 doc=Document();doc.core_properties.author='';doc.core_properties.last_modified_by=''
 section=doc.sections[0];section.page_width=Cm(21);section.page_height=Cm(29.7)
 section.left_margin=Cm(3);section.right_margin=section.top_margin=section.bottom_margin=Cm(2)
 for name in ['Normal','Title','Heading 1','Heading 2','Heading 3','Caption']:
  style=doc.styles[name];style.font.name='Times New Roman';style.font.size=Pt(12 if name=='Caption' else 16 if name in ['Title','Heading 1'] else 14);style.font.color.rgb=RGBColor(0,0,0)
  pf=style.paragraph_format;pf.line_spacing=1 if name=='Caption' else 1.5;pf.first_line_indent=Cm(1.25 if name=='Normal' else 0)
  pf.alignment=WD_ALIGN_PARAGRAPH.CENTER if name in ['Title','Heading 1','Caption'] else WD_ALIGN_PARAGRAPH.JUSTIFY
  pf.space_after=Pt(6);pf.keep_with_next=name.startswith('Heading')
 doc.styles['Heading 1'].font.all_caps=True;doc.styles['Title'].font.all_caps=True
 for style in doc.styles:
  for element in list(style.element.iter(qn('w:pBdr')))+list(style.element.iter(qn('w:autoRedefine'))):element.getparent().remove(element)
  for fonts in style.element.iter(qn('w:rFonts')):
   for attr in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:fonts.attrib.pop(qn('w:'+attr),None)
 md=['# Отчёт по учебной практике ПМ.01','']
 def paragraph(text,style=None):
  p=doc.add_paragraph(text,style=style);md.extend([text,'']);return p
 def field(label,hint='Заполнить'):
  return paragraph(label+': ['+hint+'].' )
 def heading(text,level=1,new_page=False):
  p=doc.add_heading(text,level);p.paragraph_format.page_break_before=new_page;md.extend(['#'*(level+1)+' '+text,'']);return p
 def hyperlink(label,url):
  p=paragraph(label+':');p.paragraph_format.keep_with_next=True
  p=doc.add_paragraph();p.paragraph_format.first_line_indent=Cm(0)
  link=OxmlElement('w:hyperlink');link.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
  run=OxmlElement('w:r');props=OxmlElement('w:rPr');font=OxmlElement('w:rFonts');font.set(qn('w:ascii'),'Times New Roman');font.set(qn('w:hAnsi'),'Times New Roman');props.append(font)
  size=OxmlElement('w:sz');size.set(qn('w:val'),'28');props.append(size)
  underline=OxmlElement('w:u');underline.set(qn('w:val'),'single');props.append(underline)
  color=OxmlElement('w:color');color.set(qn('w:val'),'000000');props.append(color);run.append(props)
  text=OxmlElement('w:t');text.text=url;run.append(text);link.append(run);p._p.append(link);md.extend([url,''])
 figures=[]
 def figure(title,optional=False):
  number=len(figures)+1;figures.append(title)
  instruction=('При наличии цифрового результата заменить' if optional else 'Заменить')+' рамку собственным снимком: Вставка → Рисунки. Сохранить пропорции; подпись уточнить по фактическому результату.'
  p=paragraph(instruction);p.paragraph_format.keep_with_next=True
  p=doc.add_paragraph('[Место для рисунка '+str(number)+': '+title+']')
  pf=p.paragraph_format;pf.first_line_indent=Cm(0);pf.alignment=WD_ALIGN_PARAGRAPH.CENTER;pf.line_spacing_rule=WD_LINE_SPACING.EXACTLY;pf.line_spacing=Pt(105);pf.keep_with_next=True
  for run in p.runs:run.font.size=Pt(12)
  borders=OxmlElement('w:pBdr')
  for side in ['top','left','bottom','right']:
   edge=OxmlElement('w:'+side);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4');edge.set(qn('w:color'),'A6A6A6');edge.set(qn('w:space'),'6');borders.append(edge)
  p._p.get_or_add_pPr().append(borders)
  p=doc.add_paragraph(style='Caption');p.add_run('Рисунок ')
  fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'SEQ Рисунок \\* ARABIC');run=OxmlElement('w:r');text=OxmlElement('w:t');text.text=str(number);run.append(text);fld.append(run);p._p.append(fld);p.add_run(' — '+title)
  md.extend(['[Место для рисунка '+str(number)+']','', 'Рисунок '+str(number)+' — '+title,''])
 paragraph('Отчёт по учебной практике',style='Title')
 paragraph('ПМ.01 Поддержка клиентов по вопросам эксплуатации технологических компонентов инфокоммуникационных систем')
 for label,hint in [('ФИО обучающегося','ФИО'),('Группа','VДКО-11Х или ДКО-1ХХ'),('Код работы','назначенное преподавателем обозначение'),('Предметная область','номер и название'),('Период практики','даты'),('Дата оформления','дата')]:field(label,hint)
 paragraph('Заполнить поля в квадратных скобках собственными данными. Инструкции заменить описанием выполненной работы. Привести собственные доказательства; предоставленные сведения досье обозначить отдельно.')
 doc.add_page_break();paragraph('СОДЕРЖАНИЕ',style='Title');p=doc.add_paragraph();fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'TOC \\o "1-2" \\h \\z \\u');p._p.append(fld)
 heading('1. Исходные условия',new_page=True)
 field('Область и исходные обращения','номер, название и диапазон десяти ID')
 field('Файлы собственного стенда','имена ZIP, JSON, CSV и других предоставленных файлов')
 field('Среда','ОС, браузер и версии используемых программ')
 field('Доступные действия и ограничения','что выполняется самостоятельно, что разбирается по досье')
 hyperlink('Репозиторий учебных материалов',REPOSITORY);hyperlink('Учебный сайт и индивидуальные стенды',SITE)
 paragraph('Ссылка на репозиторий относится к исходным учебным материалам. Собственные документы результатов и резервная копия перечисляются в разделе 6.')
 figure('Исходные обращения собственной области')
 heading('2. Регистрация и консультации',new_page=True)
 for label,hint in [('Реестр десяти обращений','имя отдельного документа'),('Пять ответов','имя документа и ID 01, 04, 06, 08, 10'),('Две технологические карты','имя документа и две повторяющиеся темы'),('Обоснование классификации','категории, статусы, влияние и неоднозначные случаи'),('Уточнения и передача','ID, недостающие сведения, адресат и основание передачи')]:field(label,hint)
 figure('Заполненная карточка и собственный ответ')
 heading('3. Собственные проверки',new_page=True)
 paragraph('Для каждого объекта различить исходное состояние, действие и наблюдаемый результат. Для недоступного объекта описать анализ досье и план; план не заменяет результат опыта.')
 for index in [1,2]:
  heading('3.'+str(index)+'. Проверка '+str(index),2,new_page=index==2)
  for label,hint in [('Объект и источник','свой файл, модель или сведения досье'),('Исходное состояние и ожидание','значения до действия и критерий результата'),('Выполненные действия','последовательность и собственные значения'),('Фактический результат','наблюдение, сравнение с ожиданием, повтор и возврат'),('Ограничения','что не проверено и что требуется уточнить')]:field(label,hint)
  figure('Результат проверки '+str(index))
 heading('4. Индивидуальные задачи',new_page=True)
 for index in [1,2]:
  heading('4.'+str(index)+'. Дополнительная задача '+str(index),2)
  field('Условие','полный текст задачи своей области');field('Исходные данные и режим','данные своего файла, цифровая модель или анализ досье');field('Решение и проверка','ход решения, вывод и основание его подтверждения')
 figure('Доказательство индивидуального сравнения',optional=True)
 heading('5. Сохранение и восстановление',new_page=True)
 field('Резервная копия','имя собственного JSON')
 field('Порядок восстановления','закрытие сеанса, открытие новой сессии, выбор поля восстановления и своего файла')
 field('Результат сверки','десять карточек, пять ответов, две карты, обе дополнительные задачи и код работы')
 field('Повторный экспорт','имя файла и результат содержательного сравнения')
 figure('Собственные данные после восстановления')
 heading('6. Заключение и приложения',new_page=True)
 for label,hint in [('Подтверждённые результаты','что выполнено и чем подтверждено'),('Нерешённые вопросы','ID, недостающие данные и ограничения'),('Передача специалистам','основание и состав передаваемых сведений'),('Вывод','освоенные действия и результат собственной работы')]:field(label,hint)
 paragraph('Проверить согласованность приложений с областью и кодом работы, открыть все документы перед сдачей.')
 for label in ['Реестр десяти обращений','Пять ответов','Две карты','Резервная копия JSON','Собственные изображения и дополнительные материалы']:field(label,'имя файла')
 footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER;footer.paragraph_format.first_line_indent=Cm(0);fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
 dest=root/'site/downloads/report-template.docx';doc.save(dest)
 text='\n'.join(md).rstrip()+'\n';(root/'report-template.md').write_text(text,encoding='utf-8',newline='\n');(root/'site/downloads/report-template.md').write_text(text,encoding='utf-8',newline='\n')
 print('Created editable report: data fields, two active links and '+str(len(figures))+' figure spaces.')

if __name__=='__main__':build()
