import re

from bs4 import BeautifulSoup
from constants import BASE_URL


def extract_ao_links(html):
    soup = BeautifulSoup(html, "html.parser")
    urls = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("?page=entreprise.EntrepriseDetailConsultation"):
            urls.add(BASE_URL + "/index.php" + href)

    return sorted(urls)


def _text_after_strong(div):
    strong = div.find("strong") if div else None
    if strong is None:
        return None

    parts = []
    for sibling in strong.next_siblings:
        if getattr(sibling, "name", None) == "span":
            break
        if isinstance(sibling, str):
            parts.append(sibling)

    return " ".join("".join(parts).split())


def _visible_text(tag):
    if tag is None:
        return None
    return " ".join(tag.get_text(" ", strip=True).split()) or None


def extract_ao_records(html):
    soup = BeautifulSoup(html, "html.parser")
    records = []

    for ref_input in soup.find_all("input", id=re.compile(r"_refCons$")):
        row = ref_input.find_parent("tr")
        if row is None:
            continue

        prefix = ref_input["id"][: -len("_refCons")]
        ref_consultation = ref_input["value"]

        org_input = row.find("input", id=f"{prefix}_orgCons")
        org_acronyme = org_input["value"] if org_input else None

        ref_td = row.find("td", attrs={"headers": "cons_ref"})
        abbrev = None
        if ref_td is not None:
            bulle_div = ref_td.find("div", class_="line-info-bulle")
            first_text = bulle_div.find(string=True, recursive=False) if bulle_div else None
            abbrev = first_text.strip() if first_text else None

        type_procedure = _visible_text(
            row.find("div", id=lambda x: x and x.endswith("_panelBlocTypesProc"))
        )
        categorie_div = row.find("div", id=lambda x: x and x.endswith("_panelBlocCategorie"))
        categorie = _visible_text(categorie_div)
        date_publication = _visible_text(categorie_div.find_next_sibling("div")) if categorie_div is not None else None

        reference = _visible_text(row.find("span", id=f"{prefix}_reference"))

        objet_tooltip = _visible_text(row.find("div", id=f"{prefix}_infosBullesObjet"))
        objet = objet_tooltip or _text_after_strong(row.find("div", id=f"{prefix}_panelBlocObjet"))

        acheteur = _text_after_strong(row.find("div", id=f"{prefix}_panelBlocDenomination"))

        lieux_div = row.find("div", id=f"{prefix}_panelBlocLieuxExec")
        lieu_execution = None
        if lieux_div is not None:
            first_text = lieux_div.find(string=True, recursive=False)
            lieu_execution = first_text.strip() if first_text else None

        date_end_td = row.find("td", attrs={"headers": "cons_dateEnd"})
        date_limite = None
        if date_end_td is not None:
            for cloture in date_end_td.find_all("div", class_="cloture-line"):
                parent = cloture.parent
                if parent is not None and "display:none" in (parent.get("style") or ""):
                    continue
                date_limite = _visible_text(cloture)
                if date_limite:
                    break

        statuts = []
        lieu_exe_td = row.find("td", attrs={"headers": "cons_lieuExe"})
        if lieu_exe_td is not None:
            for img in lieu_exe_td.find_all("img"):
                label = img.get("title") or img.get("alt")
                if label and label not in statuts and "Détail des lots" not in label:
                    statuts.append(label)

        records.append({
            "ref_consultation": ref_consultation,
            "org_acronyme": org_acronyme,
            "reference": reference,
            "type_procedure": type_procedure,
            "type_procedure_abbrev": abbrev,
            "categorie": categorie,
            "objet": objet,
            "acheteur": acheteur,
            "lieu_execution": lieu_execution,
            "date_publication": date_publication,
            "date_limite": date_limite,
            "statut": "; ".join(statuts),
            "url": (
                f"{BASE_URL}/index.php?page=entreprise.EntrepriseDetailConsultation"
                f"&refConsultation={ref_consultation}&orgAcronyme={org_acronyme}"
            ),
        })

    return records


def _extract_estimation_bundle(soup, base):
    estimation_ttc = _visible_text(soup.find(
        "span",
        id=re.compile(rf"^{re.escape(base)}_idReferentielZoneText(?:Lot)?_RepeaterReferentielZoneText_ctl\d+_labelReferentielZoneText$"),
    ))
    caution_provisoire = _visible_text(soup.find("span", id=f"{base}_cautionProvisoire"))
    qualifications = _visible_text(soup.find("span", id=f"{base}_qualification"))
    agrements = _visible_text(soup.find("span", id=f"{base}_agrements"))
    variante = _visible_text(soup.find("span", id=f"{base}_varianteValeur"))
    reserve_pme = _visible_text(soup.find(
        "span",
        id=re.compile(rf"^{re.escape(base)}_idRefRadio_RepeaterReferentielRadio_ctl\d+_labelReferentielRadio$"),
    ))

    return {
        "estimation_ttc": estimation_ttc,
        "caution_provisoire": caution_provisoire,
        "qualifications": qualifications,
        "agrements": agrements,
        "variante": variante,
        "reserve_pme": reserve_pme,
    }


def extract_ao_lots(html):
    soup = BeautifulSoup(html, "html.parser")
    lots = []

    lot_headers = soup.find_all("span", class_="blue bold")
    qualification_divs = soup.find_all("div", id=re.compile(r"^ctl0_CONTENU_PAGE_repeaterLots_ctl\d+_panelQualification$"))

    for lot_header, qualification_div in zip(lot_headers, qualification_divs):
        base = qualification_div["id"][: -len("_panelQualification")]

        lot_number = "".join(c for c in lot_header.get_text(" ", strip=True) if c.isdigit())

        intitule_div = lot_header.find_parent("div")
        siblings = intitule_div.find_next_siblings("div", limit=7) if intitule_div else []

        lot_intitule = _visible_text(siblings[0]) if len(siblings) > 0 else None
        categorie = _visible_text(siblings[3]) if len(siblings) > 3 else None
        description = _visible_text(siblings[6]) if len(siblings) > 6 else None

        lots.append({
            "lot_numero": lot_number,
            "lot_intitule": lot_intitule,
            "categorie": categorie,
            "description": description,
            **_extract_estimation_bundle(soup, base),
        })

    return lots


def extract_ao_nbr_lots(html):
    soup = BeautifulSoup(html, "html.parser")
    text = _visible_text(soup.find("span", id="ctl0_CONTENU_PAGE_idEntrepriseConsultationSummary_nbrLots"))
    digits = "".join(c for c in (text or "") if c.isdigit())
    return int(digits) if digits else None


def extract_ao_single_estimation(html):
    soup = BeautifulSoup(html, "html.parser")
    return {
        "lot_numero": "1",
        "lot_intitule": None,
        "categorie": None,
        "description": None,
        **_extract_estimation_bundle(soup, "ctl0_CONTENU_PAGE_idEntrepriseConsultationSummary"),
    }