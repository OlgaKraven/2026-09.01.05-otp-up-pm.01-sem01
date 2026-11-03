async (page) => {
 const results=[];
 for(const width of [1366,900,736,390]){
  await page.setViewportSize({width,height:900});
  await page.goto('http://127.0.0.1:8767/stands/v08/index.html');
  await page.locator('body').ariaSnapshot();
  for(const tab of ['Обращения','Технологические карты','Данные стенда','Документы для сдачи']){
   await page.getByRole('button',{name:tab,exact:true}).click();await page.locator('body').ariaSnapshot();
   const metrics=await page.evaluate(()=>({viewport:innerWidth,content:document.documentElement.scrollWidth}));
   if(metrics.content>metrics.viewport+1)throw Error('Overflow at '+width+' in '+tab+': '+metrics.content);
   results.push({width,tab,...metrics});
  }
 }
 return results;
}
