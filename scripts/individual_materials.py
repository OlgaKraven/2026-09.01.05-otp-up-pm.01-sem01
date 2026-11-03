"""Additional student inputs and observable models for the individual cases."""
import html, json

LAYOUTS = {
 '02':('Ведомость · шесть столбцов',180,120,180,120,6),
 '03':('Презентация 16:9 в области 4:3',160,90,120,90,0),
 '06':('Контрольный макет · отрезок 100 мм',120,80,120,80,0),
 '07':('Этикетка 58×40 мм в области 40×30 мм',58,40,40,30,0),
 '08':('Этикетка 58×40 мм в области 40×30 мм',58,40,40,30,0),
 '12':('Сводка · восемь столбцов',180,120,180,120,8),
 '13':('Талон · Учебная запись R-013',90,60,90,60,0),
 '16':('Наклейка 58×40 мм в области 40×30 мм',58,40,40,30,0),
 '20':('Бейдж 90×60 мм · E-020',90,60,90,60,0),
 '21':('Учебный документ абонемента',120,80,120,80,0),
 '24':('Контрольная отметка · отрезок 100 мм',120,80,120,80,0),
 '26':('Фотография 3:2 в области 1:1',150,100,100,100,0)
}

def create_individual_materials(d, mat, standalone, write):
    v=d['variant'];code=d['controls']['code'];next_code=d['controls']['next_code']
    if v=='DEMO':return
    h=html.escape
    rows=''.join('<section class="plain-card"><h2>'+h(t)+'</h2><p>'+h(i)+'</p></section>' for t,i in zip(d['additional_tasks'],d['additional_inputs']))
    if v in ('18','27'):
        prefix='editor' if v=='18' else 'contract'
        rows+='<h2>Выданные редакции учебного документа</h2><p>Это тексты условия, а не документы реального заказчика. Изменять их для совпадения результатов нельзя.</p>'
        for revision,date,body in [('v1','2026-11-20','Учебная редакция. Проверка выполняется в понедельник.'),('v2','2026-11-24','Учебная редакция. Проверка выполняется во вторник.')]:
            rows+='<article class="plain-card"><h3>'+prefix+'-'+revision+'</h3><p>Дата: '+date+'</p><p>'+body+'</p><p>Журнал: '+('исходная редакция, правок нет' if revision=='v1' else 'замена «понедельник» на «вторник»; комментарий C-18 только для editor-v2')+'</p></article>'
        if v=='18':rows+='<h2>Контрольная страница для плана экспорта</h2><div style="border:1px solid #606773;padding:20mm;min-height:90mm;box-sizing:border-box"><p>ВЕРХ · editor-v2 · одна страница</p><p>Содержание контрольного документа. Целевые поля — 20 мм; ошибочная настройка экспорта — 5 мм.</p><p>НИЗ · editor-v2</p></div><p>Экранное представление не подтверждает реальные поля экспортированного PDF; требуется отдельный экспорт для такого вывода.</p>'
    write(mat/'comparisons.html',standalone('Сравнения · '+d['subject'],rows))
    d['materials']['Условия и порядок индивидуальных сравнений']=f'materials/{v}/comparisons.html'
    special = {
      '13':('swapped.csv',f'code;title;date;address\nУчебная запись {v};{code};2026-11-24;"Город, улица 1"\nВторая запись {v};{next_code};2026-11-25;"Город, улица 2"\n'),
      '14':('headers.csv',f'Артикул;Наименование\n{code};Учебная запись {v}\n{next_code};Вторая запись {v}\n'),
      '25':('serial.csv',f'code;title;date;address\nSN-{code};Учебная запись {v};2026-11-24;"Город, улица 1"\nSN-{next_code};Вторая запись {v};2026-11-25;"Город, улица 2"\n'),
      '30':('duplicates.csv',f'code;title;date;address\n{code};Учебная запись {v};2026-11-24;"Город, улица 1"\n{next_code};Вторая запись {v};2026-11-25;"Город, улица 2"\n{code};Учебная запись {v};2026-11-24;"Город, улица 1"\n')
    }
    if v in special:
        name,text=special[v];write(mat/name,text);d['materials']['Файл индивидуального случая · '+name]=f'materials/{v}/{name}'
    if v in LAYOUTS:
        title,sw,sh,fw,fh,columns=LAYOUTS[v]
        config={'sw':sw,'sh':sh,'fw':fw,'fh':fh}
        table=''
        if columns:table='<div style="display:flex;position:absolute;top:25%;left:0;width:100%;height:45%">'+''.join(f'<div style="width:{100/columns}%;border:1px solid #606773;box-sizing:border-box;text-align:center">{i+1}<br/>{i+3}</div>' for i in range(columns))+'</div>'
        body='<p>Цифровая модель показывает геометрию. Она не выполняет физическую печать, не декодирует QR и не изменяет документ пользователя. Размеры указаны в условных единицах модели, соответствующих обозначенным размерам исходника.</p><p>Сравнить исходное заполнение 110 %, затем 100 % и режим «Вписать». Повторить исходное состояние и вернуть итог. Сохранить снимки и число видимых крайних отметок; экран не заменяет измерение на бумаге.</p><label>Масштаб <select id="scale"><option value="1.1">110 %</option><option value="1">100 %</option></select></label><label>Размещение <select id="fit"><option value="fill">Заполнить</option><option value="fit">Вписать</option></select></label><div style="overflow:auto;padding:20px 0"><div id="frame" style="box-sizing:content-box;position:relative;overflow:hidden;border:2px solid #606773;background:#f4f4f6"><div id="scene" style="position:absolute;transform-origin:top left;box-sizing:border-box;background:white;border:2px solid #ed131c"><span style="position:absolute;left:1%;top:1%">A</span><span style="position:absolute;right:1%;top:1%">B</span><span style="position:absolute;left:1%;bottom:1%">C</span><span style="position:absolute;right:1%;bottom:1%">D</span><p style="position:absolute;top:9%;left:8%;right:8%;font-size:13px">'+h(title)+'</p>'+table+'<p style="position:absolute;left:8%;bottom:6%;font-size:12px">Нижняя строка · '+h(v)+'</p></div></div></div><p id="geometry" role="status"></p>'
        if v in ('06','24'):body+='<p>Исходный отрезок control.svg — 100 мм. Расчётный размер при 110 % равен 100×1,1; это расчёт, а не замер напечатанного листа.</p><img src="control.svg" alt="Исходная контрольная отметка 100 мм" style="max-width:100%">'
        body+='<script>const cfg='+json.dumps(config)+';const factor=Math.min(4,600/cfg.fw);const frame=document.querySelector("#frame"),scene=document.querySelector("#scene");frame.style.width=cfg.fw*factor+"px";frame.style.height=cfg.fh*factor+"px";scene.style.width=cfg.sw*factor+"px";scene.style.height=cfg.sh*factor+"px";function render(){const ratios=[cfg.fw/cfg.sw,cfg.fh/cfg.sh];const base=document.querySelector("#fit").value==="fit"?Math.min(...ratios):Math.max(...ratios);const scale=base*Number(document.querySelector("#scale").value);scene.style.transform="scale("+scale+")";scene.style.left=(cfg.fw*factor-cfg.sw*factor*scale)/2+"px";scene.style.top=(cfg.fh*factor-cfg.sh*factor*scale)/2+"px";document.querySelector("#geometry").textContent="Источник "+cfg.sw+"×"+cfg.sh+"; область "+cfg.fw+"×"+cfg.fh+"; коэффициент "+scale.toFixed(4)}for(const id of ["scale","fit"])document.querySelector("#"+id).onchange=render;render()</script>'
        write(mat/'layout-lab.html',standalone(title,body))
        d['materials']['Модель макета своей области']=f'materials/{v}/layout-lab.html'
    if v=='28':
        body='<p>Исходные измерения не меняются. Сравнить число исходных и видимых строк, график и коды. Затем повторить фильтр и вернуться ко всем строкам.</p><pre id="source"></pre><label>Строки <select id="filter"><option value="first">Только первая</option><option value="all">Все строки</option></select></label><table><thead><tr><th>Код</th><th>Значение</th></tr></thead><tbody id="rows"></tbody></table><div id="chart" aria-label="График видимых измерений"></div><p id="status" role="status"></p><script>const data='+json.dumps([{'code':code,'value':10},{'code':next_code,'value':20}])+';document.querySelector("#source").textContent=JSON.stringify(data,null,2);function render(){const shown=document.querySelector("#filter").value==="first"?data.slice(0,1):data;document.querySelector("#rows").innerHTML=shown.map(r=>"<tr><td>"+r.code+"</td><td>"+r.value+"</td></tr>").join("");document.querySelector("#chart").replaceChildren(...shown.map(r=>{const bar=document.createElement("div");bar.textContent=r.code+": "+r.value;Object.assign(bar.style,{width:r.value*10+"px",background:"#ed131c",color:"white",padding:"8px",margin:"8px 0"});return bar}));document.querySelector("#status").textContent="Исходных строк: "+data.length+"; видимых: "+shown.length}document.querySelector("#filter").onchange=render;render()</script>'
        write(mat/'filter-lab.html',standalone('График и фильтр · '+d['subject'],body));d['materials']['Модель фильтра и графика']=f'materials/{v}/filter-lab.html'
