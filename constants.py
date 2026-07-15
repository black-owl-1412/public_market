BASE_URL = "https://www.marchespublics.gov.ma"

AO_LISTING_URL = (
    "https://www.marchespublics.gov.ma/index.php"
    "?page=entreprise.EntrepriseAdvancedSearch&AllCons"
)

AO_SEARCH_URL = (
    "https://www.marchespublics.gov.ma/index.php"
    "?page=entreprise.EntrepriseAdvancedSearch&searchAnnCons"
)

AO_LOTS_URL = (
    "https://www.marchespublics.gov.ma/index.php"
    "?page=commun.PopUpDetailLots&orgAccronyme={org_acronyme}&refConsultation={ref_consultation}&lang="
)

HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
}