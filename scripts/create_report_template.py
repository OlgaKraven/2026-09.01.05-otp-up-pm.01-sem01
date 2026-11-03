"""Create the editable report form with the user's document formatting profile."""
from pathlib import Path
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1]
doc=Document();doc.core_properties.author='';doc.core_properties.last_modified_by='';s=doc.sections[0];s.page_width=Cm(21);s.page_height=Cm(29.7);s.left_margin=Cm(3);s.right_margin=s.top_margin=s.bottom_margin=Cm(2)
for name in ['Normal','Title','Heading 1','Heading 2','Heading 3','Caption']:
 st=doc.styles[name];st.font.name='Times New Roman';st.font.size=Pt(12 if name=='Caption' else 16 if name in ['Title','Heading 1'] else 14);st.font.color.rgb=RGBColor(0,0,0);st.paragraph_format.line_spacing=1 if name=='Caption' else 1.5;st.paragraph_format.first_line_indent=Cm(1.25 if name=='Normal' else 0);st.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER if name in ['Title','Heading 1','Caption'] else WD_ALIGN_PARAGRAPH.JUSTIFY
doc.styles['Heading 1'].font.all_caps=True
doc.styles['Title'].font.all_caps=True
for st in doc.styles:
 for border in list(st.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
 for auto in list(st.element.iter(qn('w:autoRedefine'))):auto.getparent().remove(auto)
 for fonts in st.element.iter(qn('w:rFonts')):
  for attr in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
   fonts.attrib.pop(qn('w:'+attr),None)
doc.add_paragraph('Отчёт по учебной практике ПМ.01',style='Title')
for t in ['ФИО: ____________________','Группа: ____________________','Код работы: ____________________','Номер и предметная область: ____________________','Дата: ____________________']:doc.add_paragraph(t)
doc.add_page_break();doc.add_paragraph('СОДЕРЖАНИЕ',style='Title');p=doc.add_paragraph();fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'TOC \\o "1-2" \\h \\z \\u');p._p.append(fld)
doc.add_page_break()
sections=[
('1. Исходные условия',['Указать область, исходные файлы, среду и границы доступных действий. Различить предоставленное досье и собственные проверки.','Приложить собственный снимок исходных обращений.']),
('2. Регистрация и консультации',['Приложить таблицу десяти обращений, пять ответов и две технологические карты отдельными документами. Объяснить неоднозначные категории, статусы и влияние.','Указать ID неполных обращений и конкретные уточняющие вопросы.']),
('3. Проверки и индивидуальные задачи',['Для каждой собственной проверки описать объект, исходное состояние, ожидание, действие, фактический результат и соседний сценарий. Вставить читаемые снимки с подписями.','Привести обе дополнительные задачи своей области, их исходные условия, решения и ограничения. Предоставленные сведения обозначать как досье.']),
('4. Сохранение и восстановление',['Указать имя JSON и порядок восстановления в новом сеансе. Подтвердить наличие десяти обращений, пяти ответов и обеих карт. Приложить снимок восстановленного собственного результата.']),
('5. Заключение',['Объяснить подтверждённые результаты, нерешённые вопросы и передачу специалистам. Приложить резервную копию и проверить согласованность всех документов.'])]
for title,paras in sections:
 doc.add_heading(title,1)
 for t in paras:
  paragraph=doc.add_paragraph(t);paragraph.paragraph_format.keep_with_next=True
 doc.add_paragraph('________________________________________')
footer=s.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER;field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
dest=ROOT/'site/downloads/report-template.docx';doc.save(dest)
text='# Отчёт по учебной практике ПМ.01\n\nФИО: ____________________\n\nГруппа: ____________________\n\nКод работы: ____________________\n\nПредметная область: ____________________\n\n'
for title,paras in sections:text+='## '+title+'\n\n'+'\n\n'.join(paras)+'\n\n'
(ROOT/'report-template.md').write_text(text,encoding='utf-8');(ROOT/'site/downloads/report-template.md').write_text(text,encoding='utf-8')
print('Created report form.')
