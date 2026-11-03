async (page) => {
 const solution=/*SOLUTION*/;
 await page.setViewportSize({width:900,height:900});
 async function shot(name){await page.setViewportSize({width:736,height:900});if(name.startsWith('09'))await page.getByRole('textbox',{name:'Категория',exact:true}).scrollIntoViewIfNeeded();if(name.startsWith('10'))await page.getByRole('textbox',{name:'Ответ пользователю',exact:true}).scrollIntoViewIfNeeded();if(name.startsWith('11'))await page.getByRole('textbox',{name:'Тема карты',exact:true}).first().scrollIntoViewIfNeeded();if(name.startsWith('12'))await page.getByRole('heading',{name:'Документы для сдачи',exact:true}).scrollIntoViewIfNeeded();if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow before screenshot '+name);await page.screenshot({path:'site/assets/walkthrough/'+name})}
 await page.getByRole('textbox',{name:'Код работы',exact:true}).fill('DEMO');
 await page.getByRole('textbox',{name:'Код работы',exact:true}).blur();
 for(let i=0;i<10;i++){
  const id='DEMO-'+String(i+1).padStart(2,'0');
  await page.getByRole('button',{name:new RegExp('^'+id+' ')}).click();
  await page.locator('body').ariaSnapshot();
  const [category,status,summary,info]=solution.classifications[i];
  await page.getByRole('textbox',{name:'Краткий пересказ обращения',exact:true}).fill(summary);
  await page.getByRole('textbox',{name:'Категория',exact:true}).fill(category);
  await page.getByRole('combobox',{name:'Статус',exact:true}).selectOption(status);
  await page.getByRole('textbox',{name:'Влияние и обоснование',exact:true}).fill('Подтверждён один заявитель; влияние на остальных не установлено.');
  await page.getByRole('textbox',{name:'Факты, вопросы и результаты проверок',exact:true}).fill(info);
  if(solution.answers[id])await page.getByRole('textbox',{name:'Ответ пользователю',exact:true}).fill(solution.answers[id]);
  await page.getByRole('button',{name:'Сохранить карточку',exact:true}).click();
 }
 await page.getByRole('button',{name:/^DEMO-01 /}).click();
 await page.getByRole('textbox',{name:'Категория',exact:true}).scrollIntoViewIfNeeded();
 await shot('09-registry.png');
 await page.getByRole('textbox',{name:'Ответ пользователю',exact:true}).scrollIntoViewIfNeeded();
 await shot('10-response.png');
 await page.getByRole('button',{name:'Технологические карты',exact:true}).click();
 await page.locator('body').ariaSnapshot();
 const fields=[['topic','Тема карты'],['task','Задача и граница применения'],['materials','Материалы и совместимость'],['steps','Последовательность действий'],['check','Проверка и ожидаемый результат'],['problems','Возможные проблемы и передача специалисту']];
 for(let i=0;i<2;i++)for(const [key,label] of fields)await page.getByRole('textbox',{name:label,exact:true}).nth(i).fill(solution.cards[i][key]);
 await page.getByRole('button',{name:'Сохранить обе карты',exact:true}).click();
 await page.getByRole('textbox',{name:'Тема карты',exact:true}).first().scrollIntoViewIfNeeded();
 await shot('11-cards.png');
 await page.getByRole('button',{name:'Данные стенда',exact:true}).click();
 await page.locator('body').ariaSnapshot();
 for(let i=0;i<2;i++)await page.getByRole('textbox',{name:'Решение и доказательство',exact:true}).nth(i).fill(solution.extra_answers[i]);
 await page.getByRole('button',{name:'Сохранить дополнительные задачи',exact:true}).click();
 await page.getByRole('button',{name:'Документы для сдачи',exact:true}).click();
 await page.locator('body').ariaSnapshot();
 await shot('12-documents.png');
 const buttons=[['таблицу 10 обращений','registry'],['пять ответов','answers'],['две технологические карты','cards'],['основу отчёта','report']];
 for(const [label,key] of buttons){const event=page.waitForEvent('download');await page.getByRole('button',{name:'Скачать '+label+' · DOCX',exact:true}).click();await (await event).saveAs('output/playwright/demo-'+key+'.docx');}
 const backup=page.waitForEvent('download');await page.getByRole('button',{name:'Экспорт резервной копии',exact:true}).click();await(await backup).saveAs('output/playwright/demo-result.json');
 return {completed:10,answers:5,cards:2,documents:4,backup:'output/playwright/demo-result.json'};
}
