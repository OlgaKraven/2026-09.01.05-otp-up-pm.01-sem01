async (page) => {
 await page.setViewportSize({width:736,height:900});
 await page.getByRole('button',{name:'Обращения',exact:true}).click();
 await page.locator('body').ariaSnapshot();
 await page.getByRole('button',{name:/^DEMO-01 /}).click();
 if(!(await page.getByRole('textbox',{name:'Ответ пользователю',exact:true}).inputValue()).includes('устаревшую'))throw Error('Restored answer missing');
 await page.getByRole('button',{name:'Технологические карты',exact:true}).click();
 if(await page.getByRole('textbox',{name:'Тема карты',exact:true}).count()!==2)throw Error('Cards missing');
 if(!(await page.getByRole('textbox',{name:'Тема карты',exact:true}).nth(1).inputValue()).includes('сертификата'))throw Error('Second card not restored');
 await page.getByRole('textbox',{name:'Тема карты',exact:true}).first().scrollIntoViewIfNeeded();
 await page.screenshot({path:'site/assets/walkthrough/13-restored.png'});
 await page.getByLabel('Загрузить исходные обращения',{exact:true}).setInputFiles('output/playwright/wrong-schema.json');
 if(!(await page.getByRole('status').innerText()).includes('Прежняя работа сохранена'))throw Error('Schema failure not explained');
 await page.getByLabel('Восстановить выполненную работу',{exact:true}).setInputFiles('output/playwright/invalid.json');
 if(!(await page.getByRole('status').innerText()).includes('Прежняя работа сохранена'))throw Error('Invalid JSON not explained');
 await page.getByLabel('Восстановить выполненную работу',{exact:true}).setInputFiles('site/downloads/demo-tickets.json');
 if(!(await page.getByRole('status').innerText()).includes('Это не резервная копия'))throw Error('Initial data incorrectly accepted as a backup');
 await page.getByRole('status').scrollIntoViewIfNeeded();await page.screenshot({path:'site/assets/walkthrough/14-import-error.png'});
 const ev=page.waitForEvent('download');await page.getByRole('button',{name:'Экспорт резервной копии',exact:true}).click();await(await ev).saveAs('output/playwright/restored-result.json');
 return {restoredAnswer:true,restoredCards:2,invalidJsonPreservesWork:true,wrongSchemaPreservesWork:true,wrongBackupPreservesWork:true};
}
