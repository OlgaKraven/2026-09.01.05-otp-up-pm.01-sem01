"""Specialize the shared report master without redefining its styles."""
from pathlib import Path
import shutil
from docx import Document
from docx.shared import Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from report_master import text_control, response, heading, field, figure_slot

REPOSITORY='https://github.com/OlgaKraven/2026-09.01.05-otp-up-pm.01-sem01'
SITE='https://olgakraven.github.io/2026-09.01.05-otp-up-pm.01-sem01/'
NAME='Отчет о выполнении.docx'

def build():
 root=Path(__file__).resolve().parents[1];doc=Document(root/'templates'/NAME)
 doc.core_properties.author='';doc.core_properties.last_modified_by=''
 for item in list(doc.element.body):
  if item.tag!=qn('w:sectPr'):doc.element.body.remove(item)
 md=['# Отчет о выполнении','', 'Учебная практика ПМ.01','']
 def p(text,style=None):doc.add_paragraph(text,style=style);md.extend([text,''])
 def answer(label,tag,lines=2):response(doc,label,tag,lines);md.extend([label+': [Заполнить собственными данными]',''])
 def link(label,url):
  p(label,style='Field label');paragraph=doc.add_paragraph();paragraph.paragraph_format.first_line_indent=Mm(0)
  element=OxmlElement('w:hyperlink');element.set(qn('r:id'),paragraph.part.relate_to(url,RT.HYPERLINK,is_external=True));run=OxmlElement('w:r');text=OxmlElement('w:t');text.text=url;run.append(text);element.append(run);paragraph._p.append(element);md.extend([url,''])
 p('АНО ВО «СИНЕРГИЯ»',style='Cover field');p('Отчет о выполнении',style='Title')
 values=[('practice_type','Вид практики','Учебная практика'),('discipline','Дисциплина или ПМ','ПМ.01'),('topic','Тема','Поддержка клиентов по вопросам эксплуатации технологических компонентов инфокоммуникационных систем'),('student','ФИО студента',None),('group','Группа',None),('variant','Номер варианта',None),('domain','Предметная область',None),('period','Период практики',None)]
 for tag,label,value in values:
  para=doc.add_paragraph(style='Cover field');para.add_run(label+': ');text_control(para,tag,label,value or '____________________')
 p('Группа: VДКО-11Х или ДКО-1ХХ. Заполнить редактируемые поля собственными сведениями; подсказки заменить описанием выполненных действий. После заполнения обновить содержание и поля документа.')
 doc.add_page_break();p('Содержание',style='TOC title');para=doc.add_paragraph();field(para,r'TOC \o "1-2" \h \z \u','')
 heading(doc,'Исходные условия',new_page=True)
 answer('Цель и ожидаемый итог собственной работы','goal')
 answer('Предметная область, исходные обращения и рабочие файлы','inputs',3)
 answer('Среда выполнения и необходимые параметры','environment')
 answer('Замены данных DEMO на данные своей области','mapping',3)
 link('Репозиторий учебных материалов',REPOSITORY);link('Учебный сайт и отдельные стенды',SITE)
 heading(doc,'Выполнение и проверка',new_page=True)
 p('Записывать отдельно: предоставлено по досье, выполнено самостоятельно, требуется уточнить. План недоступной проверки обозначать как план. Для цифрового сравнения сохранять исходное и итоговое состояния. Неиспользуемое место рисунка удалить с объяснением, если этап выполняется только анализом досье. Изображения сохранять читаемыми; при необходимости размещать на отдельной странице.')
 steps=[
  ('Подготовка индивидуального стенда','Показать номер области, собственные десять ID и код. Указать, как открыт новый стенд или восстановлена прежняя работа.',['Исходные обращения собственной области']),
  ('Регистрация десяти обращений','Подготовить самостоятельные пересказы, категории, статусы, влияние, вопросы и основания передачи. Не объединять разные случаи по одинаковой теме.',['Заполненная карточка собственной области']),
  ('Пять ответов и две технологические карты','Сверить ответы для ID 01, 04, 06, 08, 10, два выбранных повторяющихся случая и все разделы карт. Приложить документы результатов.',['Собственный ответ пользователю','Собственная технологическая карта']),
  ('Собственные сравнения','Разобрать два случая своей области. Для каждого назвать объект, собственные значения и ожидаемый результат, действие, результат, повтор и возврат. Недоступное действие разбирать по досье; ремонт не имитировать.',['Сравнение 1 — исходное состояние','Сравнение 1 — итоговое состояние','Сравнение 2 — исходное состояние','Сравнение 2 — итоговое состояние']),
  ('Обе дополнительные задачи','Привести полный текст обеих задач своей области, собственные входные данные, ход решения и критерий. Разделить вывод, предположение и вопрос.',['Индивидуальное сравнение при наличии цифровой проверки']),
  ('Сохранение и восстановление','Экспортировать собственный JSON, восстановить в новом сеансе, сверить код работы, десять карточек, пять ответов, две карты и оба дополнительных решения.',['Собственная работа до закрытия сеанса','Собственная работа после восстановления'])
 ]
 figure_number=0
 for index,(title,hint,pictures) in enumerate(steps,1):
  heading(doc,title,2,new_page=index>1);md.extend(['## 2.'+str(index)+'. '+title,'',hint,'']);p(hint)
  answer('Исходные данные и ожидаемый результат','stage'+str(index)+'_initial')
  answer('Выполненные действия','stage'+str(index)+'_actions',3)
  answer('Фактический результат и проверка','stage'+str(index)+'_actual')
  answer('Вывод по этапу и объяснение расхождений','stage'+str(index)+'_conclusion')
  if index==5:
   answer('Задача 1 — собственное условие, решение и проверка','extra1',3);answer('Задача 2 — собственное условие, решение и проверка','extra2',3)
  for title in pictures:
   figure_number+=1
   para=doc.add_paragraph();para.add_run('Подтверждение этапа привести на рис. ');field(para,'REF PM01Figure'+str(figure_number)+' \\h',str(figure_number));para.add_run('. Заменить подсказку в рамке собственным изображением, сохраняя пропорции. Область допускает увеличение.')
   figure_slot(doc,title,'picture_'+str(figure_number),figure_number,'PM01Figure'+str(figure_number));md.extend(['[Место для рисунка '+str(figure_number)+'; не менее 60 мм]','', 'Рисунок '+str(figure_number)+' — '+title,''])
 heading(doc,'Итоговая проверка и сдача',new_page=True)
 para=doc.add_paragraph(style='Caption');para.add_run('Таблица ');field(para,r'SEQ Таблица \* ARABIC','1');para.add_run(' — итоговые результаты проверки')
 table=doc.add_table(rows=1,cols=4);table.autofit=False
 for i,title in enumerate(['Проверяемый результат','Ожидаемый результат','Фактический результат','Вывод']):table.cell(0,i).text=title
 for row_index,label in enumerate(['Десять обращений','Пять ответов','Две карты','Обе дополнительные задачи','Собственные сравнения','Восстановление и согласованность файлов'],1):
  cells=table.add_row().cells;cells[0].text=label
  for col in range(1,4):text_control(cells[col].paragraphs[0],f'check_{row_index}_{col}',label,'________________',multiline=True)
 for row in table.rows:
  for cell in row.cells:
   cell.width=Mm(40)
   for para in cell.paragraphs:para.style='Table text'
 table.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
 answer('Состав передаваемых материалов — имена файлов','submission',3)
 answer('Ссылка на репозиторий проекта','repository')
 p('Если самостоятельный репозиторий заданием не предусмотрен, указать неприменимость. В ПМ.01 собственный программный проект не требуется; ссылка на учебные материалы приведена ниже.')
 link('Репозиторий учебных материалов ПМ.01',REPOSITORY)
 answer('Невыполненные требования и причины при наличии','limitations')
 heading(doc,'Заключение',new_page=True);answer('Что выполнено, что получено, какие затруднения возникли и как устранены','conclusion',6)
 heading(doc,'Использованные источники')
 for index in range(1,4):
  para=doc.add_paragraph();para.add_run(str(index)+') ');text_control(para,'source_'+str(index),'Использованный источник','____________________________________________',multiline=True)
 p('Указать только использованные материалы. Для интернет-источника привести название, полный URL и дату обращения.')
 target=root/'site/downloads'/NAME;doc.save(target);shutil.copyfile(target,root/'site/downloads/report-template.docx')
 text='\n'.join(md).rstrip()+'\n';(root/'report-template.md').write_text(text,encoding='utf-8',newline='\n');(root/'site/downloads/report-template.md').write_text(text,encoding='utf-8',newline='\n')
 print('Prepared shared-master report with 6 stages and '+str(figure_number)+' expandable figure areas of at least 60 mm.')

if __name__=='__main__':build()
