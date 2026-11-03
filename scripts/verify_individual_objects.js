async (page) => {
 const results=[];
 const base='http://127.0.0.1:8767/stands/';
 const assert=(value,message)=>{if(!value)throw Error(message)};
 async function snapshot(){await page.locator('body').ariaSnapshot()}
 await page.setViewportSize({width:1100,height:950});
 for(let i=1;i<=30;i++){
  const v=String(i).padStart(2,'0'),code=String(i).padStart(3,'0')+'205';
  const folder='site/stands/v'+v+'/materials/'+v+'/';
  await page.goto(base+'v'+v+'/materials/'+v+'/csv-lab.html');await snapshot();
  await page.getByLabel('Файл CSV',{exact:true}).setInputFiles(folder+'sample.csv');
  await page.locator('#source').filter({hasText:code}).waitFor();
  const source=await page.locator('#source').innerText();
  assert(source.includes(code+';Учебная запись '+v+';2026-11-24;"Город, улица 1"'),'Wrong own source '+v);
  assert(await page.locator('th').count()===1,'Comma header '+v);
  await page.getByRole('combobox',{name:'Разделитель',exact:true}).selectOption(';');
  assert(await page.locator('th').count()===4,'Four columns '+v);
  assert(await page.locator('tr').count()===3,'Two rows '+v);
  assert(await page.locator('td').first().innerText()===String(Number(code)),'Numeric own code '+v);
  assert(await page.locator('td').nth(3).innerText()==='Город, улица 1','Quoted address '+v);
  await page.getByRole('combobox',{name:'Тип первого столбца',exact:true}).selectOption('text');
  assert(await page.locator('td').first().innerText()===code,'Text own code '+v);
  await page.getByRole('combobox',{name:'Кодировка',exact:true}).selectOption('windows-1251');
  assert(!(await page.locator('td').nth(1).innerText()).includes('Учебная'),'Wrong encoding detectable '+v);
  await page.getByRole('combobox',{name:'Кодировка',exact:true}).selectOption('utf-8');
  for(const [option,expected] of [['ru','24.11.2026'],['us','11/24/2026'],['iso','2026-11-24']]){
   await page.getByRole('combobox',{name:'Вид даты',exact:true}).selectOption(option);
   assert(await page.locator('td').nth(2).innerText()===expected,'Date '+option+' '+v);
   assert(await page.locator('#source').innerText()===source,'Date changed source '+v);
  }
  if(i===8)await page.screenshot({path:'output/playwright/individual/08-code.png',fullPage:true});
  const special={13:'swapped.csv',14:'headers.csv',25:'serial.csv',30:'duplicates.csv'}[i];
  let specialResult=null;
  if(special){
   await page.getByLabel('Файл CSV',{exact:true}).setInputFiles(folder+special);
   await page.waitForFunction(({i,code})=>{const text=document.querySelector('#source').textContent;return i===13?text.includes('Учебная запись 13;'+code):i===14?text.startsWith('Артикул;Наименование'):i===25?text.includes('SN-'+code):text.trim().split('\n').length===4},{i,code});
   const original=await page.locator('#source').innerText();
   if(i===13){assert(await page.locator('td').first().innerText()==='Учебная запись 13','Swapped value');assert(await page.locator('td').nth(1).innerText()===code,'Swapped own code');specialResult='title/code are under wrong headers; both rows read';}
   if(i===14){assert(await page.locator('th').first().innerText()==='Артикул','Original header');await page.getByRole('combobox',{name:'Сопоставление заголовков',exact:true}).selectOption('catalog');assert(await page.locator('th').first().innerText()==='code','Mapped code');assert(await page.locator('th').nth(1).innerText()==='title','Mapped title');assert(await page.locator('td').first().innerText()===code,'Mapped own code');assert(await page.locator('td').nth(2).innerText()===String(Number(code)+1).padStart(6,'0'),'Mapped second code');specialResult='two headers mapped; two own codes unchanged';}
   if(i===25){for(const mode of ['number','text']){await page.getByRole('combobox',{name:'Тип первого столбца',exact:true}).selectOption(mode);assert(await page.locator('td').first().innerText()==='SN-'+code,'Serial exact '+mode)}specialResult='SN-prefix, hyphen, leading zeroes remain strings';}
   if(i===30){assert(await page.locator('tr').count()===4,'Three duplicate rows');assert((await page.getByRole('status').innerText()).includes('уникальных строк: 2; повторов: 1'),'Duplicate detected');assert(await page.locator('tr').nth(1).innerText()===await page.locator('tr').nth(3).innerText(),'Full duplicate fields');specialResult='three source rows; two unique; one full duplicate';}
   assert(await page.locator('#source').innerText()===original,'Special source changed '+v);
   await page.screenshot({path:'output/playwright/individual/'+v+'-special.png',fullPage:true});
  }
  results.push({variant:v,code,numeric:String(Number(code)),rows:2,columns:4,dateViews:3,sourceUnchanged:true,special:specialResult});
 }
 const layouts=['02','03','06','07','08','12','13','16','20','21','24','26'];
 async function bounds(){return await page.evaluate(()=>{const f=document.querySelector('#frame').getBoundingClientRect();return Array.from(document.querySelectorAll('#scene>span')).map(el=>{const r=el.getBoundingClientRect();return {mark:el.textContent,inside:r.left>=f.left+1&&r.top>=f.top+1&&r.right<=f.right-1&&r.bottom<=f.bottom-1}})})}
 for(const v of layouts){
  await page.goto(base+'v'+v+'/materials/'+v+'/layout-lab.html');await snapshot();
  const before=await bounds();assert(before.some(x=>!x.inside),'Initial clipping '+v);
  await page.getByRole('combobox',{name:'Масштаб',exact:true}).selectOption('1');
  const fill=await bounds();
  await page.getByRole('combobox',{name:'Размещение',exact:true}).selectOption('fit');
  const after=await bounds();assert(after.every(x=>x.inside),'Fit bounds '+v);
  await page.getByRole('combobox',{name:'Масштаб',exact:true}).selectOption('1.1');
  await page.getByRole('combobox',{name:'Размещение',exact:true}).selectOption('fill');
  assert((await bounds()).some(x=>!x.inside),'Reproduce clipping '+v);
  await page.getByRole('combobox',{name:'Масштаб',exact:true}).selectOption('1');await page.getByRole('combobox',{name:'Размещение',exact:true}).selectOption('fit');
  assert((await bounds()).every(x=>x.inside),'Return fit '+v);
  await page.screenshot({path:'output/playwright/individual/'+v+'-layout.png',fullPage:true});
  results.push({variant:v,object:'layout',before,fill100:fill,fit100:after,repeated:true,returned:true});
 }
 await page.goto(base+'v28/materials/28/filter-lab.html');await snapshot();
 const original=await page.locator('#source').innerText();
 const counts=[];for(const mode of ['first','all','first','all']){await page.getByRole('combobox',{name:'Строки',exact:true}).selectOption(mode);const rows=await page.locator('#rows tr').count(),bars=await page.locator('#chart>div').count();assert(rows===(mode==='first'?1:2)&&bars===rows,'Filter rows/chart');assert(await page.locator('#source').innerText()===original,'Filter changed source');counts.push({mode,rows,bars})}
 assert((await page.locator('#rows').innerText()).includes('028206'),'Second measurement visible');await page.screenshot({path:'output/playwright/individual/28-filter.png',fullPage:true});results.push({variant:'28',object:'filter',counts,sourceUnchanged:true});
 for(const v of ['18','27']){await page.goto(base+'v'+v+'/materials/'+v+'/comparisons.html');await snapshot();const text=await page.locator('main').innerText();assert(text.includes('2026-11-20')&&text.includes('2026-11-24')&&text.includes('понедельник')&&text.includes('вторник'),'Version objects '+v);await page.screenshot({path:'output/playwright/individual/'+v+'-versions.png',fullPage:true});results.push({variant:v,object:'versions',differentText:true,datesPresent:true});}
 const download=page.waitForEvent('download');await page.evaluate(data=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='objects-result.json';a.click()},results);await(await download).saveAs('output/playwright/individual/objects-result.json');
 return {csv:30,special:4,layouts:12,filter:1,versions:2,results:results.length};
}
