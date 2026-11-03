async (page) => {
 const base='http://127.0.0.1:8767/stands/demo/materials/DEMO/';
 await page.setViewportSize({width:736,height:560});
 await page.goto(base+'portal/old.html');await page.locator('body').ariaSnapshot();
 await page.screenshot({path:'site/assets/walkthrough/02-old-route.png',fullPage:true});
 await page.getByRole('link',{name:'Открыть главную страницу учебного портала',exact:true}).click();await page.locator('body').ariaSnapshot();
 await page.getByRole('link',{name:'Группа A',exact:true}).click();await page.locator('body').ariaSnapshot();
 if(!(await page.locator('body').innerText()).includes('10:00'))throw Error('Group A failed');
 await page.screenshot({path:'site/assets/walkthrough/03-schedule-a.png',fullPage:true});
 await page.getByRole('link',{name:'К выбору группы',exact:true}).click();await page.locator('body').ariaSnapshot();
 await page.getByRole('link',{name:'Группа B',exact:true}).click();await page.locator('body').ariaSnapshot();
 if(!(await page.locator('body').innerText()).includes('12:00'))throw Error('Group B failed');
 await page.screenshot({path:'site/assets/walkthrough/04-schedule-b.png',fullPage:true});
 await page.setViewportSize({width:736,height:800});
 await page.goto(base+'print-lab.html');await page.locator('body').ariaSnapshot();
 await page.screenshot({path:'site/assets/walkthrough/05-print-before.png',fullPage:true});
 await page.getByRole('combobox',{name:'Масштаб',exact:true}).selectOption('1');
 if(!(await page.getByRole('status').innerText()).includes('внутри'))throw Error('Scale failed');
 await page.screenshot({path:'site/assets/walkthrough/06-print-after.png',fullPage:true});
 return {portalA:true,portalB:true,printModel:true};
}
