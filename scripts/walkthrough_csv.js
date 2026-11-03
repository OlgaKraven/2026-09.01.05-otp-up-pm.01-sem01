async (page) => {
  await page.setViewportSize({width:850,height:1000});
  await page.getByLabel('Файл CSV').setInputFiles('site/stands/demo/materials/DEMO/sample.csv');
  await page.getByRole('combobox',{name:'Разделитель'}).selectOption(';');
  await page.screenshot({path:'site/assets/walkthrough/07-csv-number.png',fullPage:true});
  if(!(await page.locator('#result').innerText()).includes('1205')) throw Error('Numeric conversion not observed');
  await page.getByRole('combobox',{name:'Тип первого столбца'}).selectOption('text');
  await page.getByRole('combobox',{name:'Кодировка'}).selectOption('windows-1251');
  await page.getByRole('combobox',{name:'Кодировка'}).selectOption('utf-8');
  if(!(await page.locator('#result').innerText()).includes('001205')) throw Error('Text code not preserved');
  if((await page.getByRole('status').innerText())!=='Строк данных: 2; столбцов в заголовке: 4') throw Error('CSV dimensions incorrect');
  await page.screenshot({path:'site/assets/walkthrough/08-csv-text.png',fullPage:true});
  return {status:await page.getByRole('status').innerText(),source:await page.locator('#source').innerText(),result:await page.locator('#result').innerText()};
}
