"""Validate the PM.01 publication without network access."""
from __future__ import annotations

import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DL = SITE / "downloads"


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("href", "src", "data"):
            if values.get(key):
                self.links.append(values[key] or "")


def check_local_links() -> None:
    for page in SITE.rglob("*.html"):
        parser = Links()
        parser.feed(page.read_text(encoding="utf-8"))
        for link in parser.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or link.startswith("#"):
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            assert target.is_file(), f"broken link in {page.name}: {link}"


def main() -> None:
    course = json.loads((ROOT / "content/course.json").read_text(encoding="utf-8"))
    stands = {item['variant']: item for item in json.loads((ROOT / 'content/stands.json').read_text(encoding='utf-8'))}
    assert course["meta"] == {
        "title": "ПМ.01 Поддержка клиентов по вопросам эксплуатации технологических компонентов",
        "organization": "Университет «Синергия»",
        "academic_year": "2026",
        "semester": 1,
        "specialty": "09.01.05 Оператор технической поддержки",
        "qualification": "Оператор технической поддержки",
        "environment": "Автономный браузерный стенд",
    }
    assert len(course["areas"]) == 30
    assert [a["variant"] for a in course["areas"]] == [f"{i:02d}" for i in range(1, 31)]
    assert len({a["subject"] for a in course["areas"]}) == 30
    for area in course["areas"]:
        assert len(area["tickets"]) == 10
        assert len({t["id"] for t in area["tickets"]}) == 10
        assert area["reply_ticket_numbers"] == [1, 4, 6, 8, 10]
        assert len(area["knowledge_card_topics"]) == 2
        assert len(area["additional_tasks"]) == 2
        assert (DL / f"variant-{area['variant']}.json").is_file()
        variant = area['variant']
        initial = json.loads((DL / f'variant-{variant}.json').read_text(encoding='utf-8'))
        assert initial == stands[variant], 'PDF source and individual stand metadata differ: '+variant
        assert [(t['id'], t['topic'], t['description']) for t in initial['tickets']] == [(t['id'], t['topic'], t['description']) for t in area['tickets']]
        assert initial['additional_tasks'] == area['additional_tasks']
        assert initial['knowledge_card_topics'] == area['knowledge_card_topics']
        assert len(initial['additional_inputs']) == 2 and all(t['dossier'] for t in initial['tickets'])
        assert all('Проверка:' in text for text in initial['additional_inputs']), variant
        assert 'Условия и порядок индивидуальных сравнений' in initial['materials'], variant
        if variant == '01':
            assert 'завершающий символ не указаны' in initial['tickets'][3]['dossier']
            assert 'Scan-A' in initial['tickets'][4]['dossier']
            assert 'панель поиска' in initial['tickets'][6]['dossier']
        if variant == '08':
            assert '1205' not in initial['tickets'][0]['dossier'], 'stale numeric demo value'
        if variant == '04':
            assert 'двоеточие' in initial['tickets'][6]['dossier']
            assert 'sample.csv' not in initial['tickets'][6]['dossier'], 'filename is not a CSV encoding case'
        assert initial['controls']['code'] == f'{int(variant):03d}205'
        assert (DL / f'variant-{variant}.pdf').read_bytes().startswith(b'%PDF-')
        with zipfile.ZipFile(DL / f'stand-{variant}.zip') as package:
            zipped = json.loads(package.read('initial.json').decode('utf-8'))
            assert zipped == initial
            assert all(path in package.namelist() for path in initial['materials'].values())
            assert package.read(f'materials/{variant}/sample.csv').decode('utf-8').splitlines()[1].startswith(initial['controls']['code']+';')
            if variant in ['13', '14', '25', '30']:
                name = {'13': 'swapped.csv', '14': 'headers.csv', '25': 'serial.csv', '30': 'duplicates.csv'}[variant]
                text = package.read(f'materials/{variant}/{name}').decode('utf-8')
                assert initial['controls']['code'] in text
                if variant == '14': assert text.startswith('Артикул;Наименование\n')
                if variant == '25': assert 'SN-'+initial['controls']['code'] in text
                if variant == '30':
                    rows = text.splitlines()[1:]
                    assert len(rows) == 3 and len(set(rows)) == 2 and rows[0] == rows[2]

    required = {
        "assignment.pdf", "guide.pdf", "report-template.md", "report-template.docx",
        "support-desk.zip", "demo-tickets.json", "demo-result.zip",
        *{f"variant-{i:02d}.json" for i in range(1, 31)},
    }
    assert required <= {p.name for p in DL.iterdir() if p.is_file()}
    for name in ("assignment.pdf", "guide.pdf"):
        assert (DL / name).read_bytes().startswith(b"%PDF-")
    assert zipfile.is_zipfile(DL / "report-template.docx")
    assert zipfile.is_zipfile(DL / "support-desk.zip")
    assert zipfile.is_zipfile(DL / "demo-result.zip")

    areas_html = (SITE / "areas.html").read_text(encoding="utf-8")
    assert areas_html.count('class="card area-card"') == 31
    assert areas_html.count("Вариант ") == 30
    for i in range(1, 31):
        assert f"downloads/variant-{i:02d}.json" in areas_html
    assert "Демонстрационная область" in areas_html
    check_local_links()

    searchable = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in [ROOT / "README.md", ROOT / "report-template.md", *SITE.glob("*.html")]
    ).lower()
    forbidden = ("балльная шкала", "количество баллов", "общий объём практики", "перечень файлов для сдачи", "chatgpt", "нейросет")
    assert not any(term in searchable for term in forbidden)
    assert not re.search(r"\b[А-Я]{2,4}\.\d+(?:\.\d+)+\b", searchable, re.I)
    print("PASS: passport, 30 variants, demo, links, downloads, PDFs, DOCX, archives and restrictions")


if __name__ == "__main__":
    main()
