async (page) => {
 const results=[];
 for(const v of [...Array.from({length:30},(_,i)=>String(i+1).padStart(2,'0')),'DEMO']){
  const demo=v==='DEMO',folder=demo?'demo':'v'+v;
  await page.goto('http://127.0.0.1:8767/stands/'+folder+'/index.html?export=paragraphs');await page.locator('body').ariaSnapshot();
  page.once('dialog',dialog=>dialog.accept());
  await page.getByLabel('Восстановить выполненную работу',{exact:true}).setInputFiles(demo?'output/playwright/demo-result.json':'output/playwright/individual/v'+v+'-result.json');
  await page.waitForFunction(value=>document.querySelector('#workcode').value===value,demo?'DEMO':'CHECK-'+v);await page.locator('body').ariaSnapshot();
  await page.getByRole('button',{name:'Документы для сдачи',exact:true}).click();await page.locator('body').ariaSnapshot();
  for(const [label,key] of [['таблицу 10 обращений','registry'],['пять ответов','answers'],['две технологические карты','cards'],['основу отчёта','report']]){
   const download=page.waitForEvent('download');await page.getByRole('button',{name:'Скачать '+label+' · DOCX',exact:true}).click();await(await download).saveAs(demo?'output/playwright/demo-'+key+'.docx':'output/playwright/individual/v'+v+'-'+key+'.docx');
  }
  results.push({variant:v,documentsReexported:4,backupRestored:true});
 }
 const download=page.waitForEvent('download');await page.evaluate(data=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='reexport-result.json';a.click()},results);await(await download).saveAs('output/playwright/individual/reexport-result.json');
 return {variants:31,documents:124};
}
