import math

import requests
from bs4 import BeautifulSoup

from constants import AO_SEARCH_URL, HEADERS

PAGE_SIZE_FIELD = "ctl0$CONTENU_PAGE$resultSearch$listePageSizeTop"
NEXT_PAGE_TARGET = "ctl0$CONTENU_PAGE$resultSearch$PagerTop$ctl2"


def _form_data(html):
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    data = {}

    for inp in form.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        itype = inp.get("type", "text")
        if itype in ("submit", "image", "button", "reset"):
            continue
        if itype in ("checkbox", "radio"):
            if inp.get("checked"):
                data[name] = inp.get("value", "on")
            continue
        data[name] = inp.get("value", "")

    for sel in form.find_all("select"):
        name = sel.get("name")
        if not name:
            continue
        opt = sel.find("option", selected=True) or sel.find("option")
        data[name] = opt.get("value", "") if opt else ""

    return data


def fetch_ao_search_range(date_start, date_end, max_records=None, page_size=50, deadline_start="01/01/2023", deadline_end="01/01/2027"):
    """date_start / date_end / deadline_start / deadline_end are DD/MM/YYYY strings.

    date_start/date_end filter on "Date de mise en ligne" (publication date).
    deadline_start/deadline_end widen "Date limite de remise des plis" so the
    site's hidden default (restricted to still-open consultations) doesn't
    silently narrow the results.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    r = session.get(AO_SEARCH_URL, timeout=30)
    data = _form_data(r.text)

    data["ctl0$CONTENU_PAGE$AdvancedSearch$dateMiseEnLigneStart"] = deadline_start
    data["ctl0$CONTENU_PAGE$AdvancedSearch$dateMiseEnLigneEnd"] = deadline_end
    data["ctl0$CONTENU_PAGE$AdvancedSearch$dateMiseEnLigneCalculeStart"] = date_start
    data["ctl0$CONTENU_PAGE$AdvancedSearch$dateMiseEnLigneCalculeEnd"] = date_end
    data["ctl0$CONTENU_PAGE$AdvancedSearch$lancerRecherche"] = "Lancer la recherche"

    r = session.post(AO_SEARCH_URL, data=data, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    nb_span = soup.find("span", id="ctl0_CONTENU_PAGE_resultSearch_nombreElement")
    nb_results = int(nb_span.get_text(strip=True)) if nb_span else 0

    data = _form_data(r.text)
    data[PAGE_SIZE_FIELD] = str(page_size)
    data["PRADO_POSTBACK_TARGET"] = PAGE_SIZE_FIELD
    data["PRADO_POSTBACK_PARAMETER"] = ""
    r = session.post(AO_SEARCH_URL, data=data, timeout=30)

    total_to_fetch = min(nb_results, max_records) if max_records else nb_results
    num_pages = math.ceil(total_to_fetch / page_size) if total_to_fetch else 0

    print(f"{nb_results} consultations found between {date_start} and {date_end}; fetching {total_to_fetch} ({num_pages} pages)")

    fetched = 0
    for _ in range(num_pages):
        yield r.text
        fetched += page_size
        if fetched >= total_to_fetch:
            break

        data = _form_data(r.text)
        data["PRADO_POSTBACK_TARGET"] = NEXT_PAGE_TARGET
        data["PRADO_POSTBACK_PARAMETER"] = ""
        r = session.post(AO_SEARCH_URL, data=data, timeout=30)


def fetch_ao_search_year(year, max_records=None, page_size=50, deadline_start="01/01/2023", deadline_end="01/01/2027"):
    yield from fetch_ao_search_range(
        f"01/01/{year}", f"31/12/{year}",
        max_records=max_records, page_size=page_size,
        deadline_start=deadline_start, deadline_end=deadline_end,
    )
