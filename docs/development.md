# Подготовка комплекта

Редактируемые требования находятся в `content/course.json`. Его 30 областей, исходные обращения и дополнительные задачи сохраняются при сборке. `content/case-inputs.json` содержит специально подготовленные условия учебных случаев, а не результаты экспериментов студентов. Действия общего разбора находятся в `content/guide.json`, значения демонстрационного прохода — в `content/demo-solution.json`.

Общий интерфейс находится в `support-desk/`. Индивидуальные автономные папки и ZIP создаются из него. У каждой области собственный код, CSV, досье и дополнительные условия. Код работы в интерфейсе предназначен для назначенного преподавателем обозначения, без включения имён в публичные исходники.

Порядок обновления:

1. Установить зависимости `requirements.txt` в среду Python.
2. Выполнить `python scripts/prepare_materials.py`.
3. Открыть локальную копию сайта и пройти демонстрацию через интерфейс. Использовать `scripts/walkthrough_csv.js`, `scripts/walkthrough_demo.template.js` и `scripts/verify_restore.js` с Playwright CLI. Сначала изучить актуальный снимок страницы; шаблон демонстрации дополнить JSON из `content/demo-solution.json` вместо `/*SOLUTION*/`.
4. Сохранить настоящий экспорт в `output/playwright/demo-result.json`, четыре DOCX с именами `demo-registry`, `demo-answers`, `demo-cards`, `demo-report`, а повторный экспорт после восстановления — в `restored-result.json`. Снимки действий сохраняются в `site/assets/walkthrough/`.
5. Выполнить `python scripts/create_report_template.py` и `python scripts/render_materials.py`.
6. Обновить содержание формы в Word/LibreOffice. На Windows `scripts/render_docx_windows.ps1 -InputFolder site/downloads -SaveUpdatedFields` обновляет поля и экспортирует собственные документы указанной папки; окно Word не показывается. Проверить PDF и снимки страниц, затем итоговые DOCX.
7. Выполнить `python scripts/build.py` и `python scripts/check.py`.

PDF используют профиль «маршрут + крупные блоки», локальный Golos Text и поля A4 30/20/20/20 мм. Подписи рисунков используют Times New Roman. На Windows шрифт берётся из системной папки; для другой системы требуется установленный Times New Roman. DOCX используют пользовательский профиль: Times New Roman, основной текст 14 пт, интервал 1,5.

`check.py` сопоставляет все исходные темы, описания и дополнительные задачи, проверяет 30 индивидуальных архивов и локальные ссылки. Он не заменяет фактический проход, просмотр PDF и проверку документов. Публикация выполняется существующим workflow GitHub Pages из `main`; её успех проверяется отдельно от push. История аудита хранится в BrainM.
