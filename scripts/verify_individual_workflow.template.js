async (page) => {
 const [start,end]=/*RANGE*/;
 const response=await page.goto('http://127.0.0.1:8768/solutions.json');
 const solutions=JSON.parse(await response.text());
 const result=[];const assert=(value,message)=>{if(!value)throw Error(message)};
 const fields=[['topic','Тема карты'],['task','Задача и граница применения'],['materials','Материалы и совместимость'],['steps','Последовательность действий'],['check','Проверка и ожидаемый результат'],['problems','Возможные проблемы и передача специалисту']];
 const docs=[['таблицу 10 обращений','registry'],['пять ответов','answers'],['две технологические карты','cards'],['основу отчёта','report']];
 await page.setViewportSize({width:1000,height:950});
 for(const solution of solutions.slice(start-1,end)){
  const v=solution.variant,url='http://127.0.0.1:8767/stands/v'+v+'/index.html';
  await page.goto(url);await page.locator('body').ariaSnapshot();
  assert((await page.locator('#subject').innerText()).includes(solution.subject),'Wrong subject '+v);
  await page.getByRole('textbox',{name:'Код работы',exact:true}).fill('CHECK-'+v);await page.getByRole('textbox',{name:'Код работы',exact:true}).blur();
  const originalFacts=[];
  for(const t of solution.tickets){
   await page.getByRole('button',{name:new RegExp('^'+t.id+' ')}).click();await page.locator('body').ariaSnapshot();
   originalFacts.push(await page.locator('.note').innerText());
   for(const [key,label] of [['summary','Краткий пересказ обращения'],['category','Категория'],['impact','Влияние и обоснование'],['additional_info','Факты, вопросы и результаты проверок']])await page.getByRole('textbox',{name:label,exact:true}).fill(t[key]);
   await page.getByRole('combobox',{name:'Статус',exact:true}).selectOption(t.status);
   await page.getByRole('textbox',{name:'Ответ пользователю',exact:true}).fill(solution.answers[t.id]||'');
   await page.getByRole('button',{name:'Сохранить карточку',exact:true}).click();
  }
  await page.getByRole('button',{name:'Технологические карты',exact:true}).click();await page.locator('body').ariaSnapshot();
  for(let i=0;i<2;i++)for(const [key,label] of fields)await page.getByRole('textbox',{name:label,exact:true}).nth(i).fill(solution.cards[i][key]);
  await page.getByRole('button',{name:'Сохранить обе карты',exact:true}).click();
  await page.getByRole('button',{name:'Данные стенда',exact:true}).click();await page.locator('body').ariaSnapshot();
  const comparisons=page.getByRole('link',{name:'Условия и порядок индивидуальных сравнений',exact:true});assert(await comparisons.count()===1,'No individual method '+v);
  for(let i=0;i<2;i++)await page.getByRole('textbox',{name:'Решение и доказательство',exact:true}).nth(i).fill(solution.extra_answers[i]);
  await page.getByRole('button',{name:'Сохранить дополнительные задачи',exact:true}).click();
  await page.getByRole('button',{name:'Документы для сдачи',exact:true}).click();await page.locator('body').ariaSnapshot();
  for(const [label,key] of docs){const event=page.waitForEvent('download');await page.getByRole('button',{name:'Скачать '+label+' · DOCX',exact:true}).click();await(await event).saveAs('output/playwright/individual/v'+v+'-'+key+'.docx');}
  const backup=page.waitForEvent('download');await page.getByRole('button',{name:'Экспорт резервной копии',exact:true}).click();await(await backup).saveAs('output/playwright/individual/v'+v+'-result.json');
  const restored=await page.context().newPage();await restored.goto(url);await restored.locator('body').ariaSnapshot();
  assert(await restored.getByRole('textbox',{name:'Код работы',exact:true}).inputValue()==='','New session unexpectedly has old data '+v);
  restored.once('dialog',dialog=>dialog.accept());
  await restored.getByLabel('Восстановить выполненную работу',{exact:true}).setInputFiles('output/playwright/individual/v'+v+'-result.json');
  await restored.waitForFunction(value=>document.querySelector('#workcode').value===value,'CHECK-'+v);await restored.locator('body').ariaSnapshot();
  for(let i=0;i<10;i++){
   const t=solution.tickets[i];await restored.getByRole('button',{name:new RegExp('^'+t.id+' ')}).click();await restored.locator('body').ariaSnapshot();
   for(const [key,label] of [['summary','Краткий пересказ обращения'],['category','Категория'],['impact','Влияние и обоснование'],['additional_info','Факты, вопросы и результаты проверок']])assert(await restored.getByRole('textbox',{name:label,exact:true}).inputValue()===t[key],'Restored '+key+' '+t.id);
   assert(await restored.getByRole('combobox',{name:'Статус',exact:true}).inputValue()===t.status,'Restored status '+t.id);
   assert(await restored.getByRole('textbox',{name:'Ответ пользователю',exact:true}).inputValue()===(solution.answers[t.id]||''),'Restored answer '+t.id);
   assert(await restored.locator('.note').innerText()===originalFacts[i],'Source dossier replaced '+t.id);
  }
  await restored.getByRole('button',{name:'Технологические карты',exact:true}).click();await restored.locator('body').ariaSnapshot();
  for(let i=0;i<2;i++)for(const [key,label] of fields)assert(await restored.getByRole('textbox',{name:label,exact:true}).nth(i).inputValue()===solution.cards[i][key],'Restored card '+v+' '+i+' '+key);
  await restored.getByRole('button',{name:'Данные стенда',exact:true}).click();await restored.locator('body').ariaSnapshot();
  for(let i=0;i<2;i++)assert(await restored.getByRole('textbox',{name:'Решение и доказательство',exact:true}).nth(i).inputValue()===solution.extra_answers[i],'Restored extra '+v);
  await restored.getByRole('heading',{name:'Дополнительная задача 1',exact:true}).scrollIntoViewIfNeeded();
  await restored.screenshot({path:'output/playwright/individual/v'+v+'-restored.png'});
  const repeated=restored.waitForEvent('download');await restored.getByRole('button',{name:'Экспорт резервной копии',exact:true}).click();await(await repeated).saveAs('output/playwright/individual/v'+v+'-restored.json');
  await restored.close();
  result.push({variant:v,requests:10,answers:5,cards:2,extraTasks:2,documents:4,newSessionRestore:true,allFieldsChecked:true,sourceFactsPreserved:true});
 }
 const report=page.waitForEvent('download');await page.evaluate(data=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='workflow-result.json';a.click()},result);await(await report).saveAs('output/playwright/individual/workflow-'+start+'-'+end+'.json');
 return {start,end,completed:result.length};
}
