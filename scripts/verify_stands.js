async (page) => {
 const results=[];
 for(let i=1;i<=30;i++){
  const variant=String(i).padStart(2,'0');
  await page.goto('http://127.0.0.1:8767/stands/v'+variant+'/index.html');
  await page.locator('body').ariaSnapshot();
  if(await page.locator('#list button').count()!==10)throw Error('Wrong ticket count '+variant);
  if(!(await page.locator('#list button').first().innerText()).includes('V'+variant+'-01'))throw Error('Wrong first ID '+variant);
  await page.getByRole('button',{name:'Данные стенда',exact:true}).click();
  await page.locator('body').ariaSnapshot();
  if(await page.getByRole('textbox',{name:'Решение и доказательство',exact:true}).count()!==2)throw Error('Missing individual tasks '+variant);
  if(!(await page.locator('#card').innerText()).includes('pm01-'+variant))throw Error('Wrong stand identifier '+variant);
  const href=await page.getByRole('link',{name:'CSV своей области',exact:true}).getAttribute('href');
  if(href!=='materials/'+variant+'/sample.csv')throw Error('Wrong CSV path '+variant);
  results.push({variant,tickets:10,individualTasks:2,csv:href});
 }
 return results;
}
