"""
Central registry of sources used by the dashboard.

IMPORTANT:
- This app is for *pre-dimensioning / early-stage sizing only*.
- Always verify with the official (often paywalled) standard text and local requirements.
"""

from dataclasses import dataclass
from typing import Dict, List

ACCESS_DATE = "2026-02-14"
@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    accessed: str
    kind: str  # "Standard/Law" | "Guideline/Recommendation" | "Context"

SOURCES: Dict[str, Source] = {
    # Electrical (VDE/IEC, plus public summaries)
    "ELEC_VDROP_LAPP_PDF": Source(
        id="ELEC_VDROP_LAPP_PDF",
        title="LAPP technical paper (mentions TAB/NAV/VDE-AR-N 4100 and voltage drop guidance; references DIN VDE 0100-520 and DIN 18015-1-10)",
        url="https://contentmedia.lappcdn.com/e/lapp/IUrE4SbY1_k-zREx5E0xtQ~~",
        accessed=ACCESS_DATE,
        kind="Guideline/Recommendation",
    ),
    "IEC60364_G52_WIK": Source(
        id="IEC60364_G52_WIK",
        title="Electrical Installation Guide (summary of IEC 60364-5-52 voltage drop typical limits)",
        url="https://www.electrical-installation.org/enwiki/Maximum_voltage_drop_limit",
        accessed=ACCESS_DATE,
        kind="Guideline/Recommendation",
    ),
    "DIN18015_OVERVIEW_SIS": Source(
        id="DIN18015_OVERVIEW_SIS",
        title="DIN 18015-1 overview (scope: electrical installations in residential buildings; info page)",
        url="https://www.sis.se/en/produkter/construction-materials-and-building/installations-in-buildings/electricity-supply-systems/din-18015-1/",
        accessed=ACCESS_DATE,
        kind="Context",
    ),

    # HVAC / ventilation / energy law
    "REHVA_EN16798_PDF": Source(
        id="REHVA_EN16798_PDF",
        title="REHVA presentation on EN 16798-1 revision (example outdoor air rates by category)",
        url="https://www.rehva.eu/fileadmin/user_upload/2024/2_Jarek.pdf",
        accessed=ACCESS_DATE,
        kind="Guideline/Recommendation",
    ),
    "DIN_TR_16789_DRAFT": Source(
        id="DIN_TR_16789_DRAFT",
        title="DIN draft TR 16789-2 (input parameters, includes ventilation rate examples for EN 16798 categories)",
        url="https://www.din.de/resource/blob/66392/911886c68e3d0917dc03085dcc35f144/tr-16789-2-draft-data.pdf",
        accessed=ACCESS_DATE,
        kind="Guideline/Recommendation",
    ),
    "VDI_2078_PAGE": Source(
        id="VDI_2078_PAGE",
        title="VDI 2078 standard page (cooling load calculation scope)",
        url="https://www.vdi.de/en/home/vdi-standards/details/vdi-2078-calculation-of-thermal-loads-and-room-temperatures-design-cooling-load-and-annual-simulation",
        accessed=ACCESS_DATE,
        kind="Context",
    ),
    "BWP_KLIMAKARTE": Source(
        id="BWP_KLIMAKARTE",
        title="BWP Klimakarte (Norm-Außentemperaturen according to DIN/TS 12831-1, map by postal code)",
        url="https://www.waermepumpe.de/werkzeuge/klimakarte/",
        accessed=ACCESS_DATE,
        kind="Guideline/Recommendation",
    ),

    "DWD_TRY_PAGE": Source(
        id="DWD_TRY_PAGE",
        title="German Weather Service (DWD): Test Reference Years (TRY) — official overview and downloads",
        url="https://www.dwd.de/DE/leistungen/testreferenzjahre/testreferenzjahre.html",
        accessed=ACCESS_DATE,
        kind="Context",
    ),
    "VDI_2078_AMENDMENT_PDF": Source(
        id="VDI_2078_AMENDMENT_PDF",
        title="VDI 2078 amendment text (mentions deriving variable values from DIN 4710 or suitable TRY evaluation)",
        url="https://www.vdi.de/fileadmin/pages/vdi_de/redakteure/richtlinien/dateien/2020-01-28_Aenderung_VDI_2078_Text.pdf_-_ersetzt_-_2018-11-01_Aenderung_VDI_2078_Text.pdf",
        accessed=ACCESS_DATE,
        kind="Guideline/Recommendation",
    ),
    "EU_GEG_OVERVIEW": Source(
        id="EU_GEG_OVERVIEW",
        title="EU Clean Energy Islands: Germany legal overview — Building Energy Act (GEG) replaces previous laws (overview page)",
        url="https://clean-energy-islands.ec.europa.eu/countries/germany/legal/heating-cooling-support/heating-cooling-support-building-obligations",
        accessed=ACCESS_DATE,
        kind="Context",
    ),
    "DINMEDIA_GEG_TOPIC": Source(
        id="DINMEDIA_GEG_TOPIC",
        title="DIN Media topic page: Energy efficiency / GEG (context and references)",
        url="https://www.dinmedia.de/en/topics/energy-efficiency",
        accessed=ACCESS_DATE,
        kind="Context",
    ),

    # Water / plumbing
    "DIN1988_300_PDF": Source(
        id="DIN1988_300_PDF",
        title="Educational PDF: dimensioning steps per DIN 1988-300 (Trinkwasser installation pipe sizing workflow)",
        url="https://c.wgr.de/f/buchlinks/978-3-14-235039-4/217_DIN_1988-300_Bemessung_der_Trinkwasserinstallation.pdf",
        accessed=ACCESS_DATE,
        kind="Guideline/Recommendation",
    ),
    "ZVSHK_T110_PDF": Source(
        id="ZVSHK_T110_PDF",
        title="ZVSHK index/table of contents: DIN EN 806-3 and DIN 1988-300 referenced for pipe diameter calculation",
        url="https://www.zvshk.de/uploads/tx_ccshopgdi/product_files/index_of_content/Inhaltsverzeichnis-T110-DIN-1988-300.pdf",
        accessed=ACCESS_DATE,
        kind="Context",
    ),
    "EN806_3_CATALOG": Source(
        id="EN806_3_CATALOG",
        title="EN 806-3 catalog entry (scope: pipe sizing simplified method for drinking water installations)",
        url="https://ecommerce.sist.si/catalog/standards/cen/c600c378-b062-40b9-a0fa-f6a8b719ead1/en-806-3-2006",
        accessed=ACCESS_DATE,
        kind="Context",
    ),

    # Drainage / rainwater
    "DIN1986_100_OVERVIEW_AENOR": Source(
        id="DIN1986_100_OVERVIEW_AENOR",
        title="DIN 1986-100 summary (scope: private ground drainage; in addition to DIN EN 12056 parts)",
        url="https://en.tienda.aenor.com/Paginas/normas-y-libros/Normas/Normas-DIN.aspx?TermId=68d250f4-8cb8-4ce5-bb21-70336ee39a53&TermSetId=c0c24438-f227-4594-9eb7-30942b744d4d&TermStoreId=30422a6b-6877-4e28-82d6-96d5dac7e3b1&c=norma-din-1986-100-2008-05-106712878",
        accessed=ACCESS_DATE,
        kind="Context",
    ),
    "EN12056_INTERTEK": Source(
        id="EN12056_INTERTEK",
        title="Intertek inform listing: EN 12056-2 (scope: sanitary pipework, layout and calculation)",
        url="https://www.intertekinform.com/en-gb/standards/en-12056-2-2000-331036_saig_cen_cen_761384/",
        accessed=ACCESS_DATE,
        kind="Context",
    ),

    # Fire (PCI)
    "VDS_DIN14675": Source(
        id="VDS_DIN14675",
        title="VdS page: Specialist companies DIN 14675 (planning, installation, commissioning, acceptance, maintenance)",
        url="https://vds.de/en/expertise/fire-safety/certification/installation-and-specialist-companies/specialist-companies-din-14675",
        accessed=ACCESS_DATE,
        kind="Context",
    ),
    "VDS_SPRINKLER_GUIDELINE": Source(
        id="VDS_SPRINKLER_GUIDELINE",
        title="VdS page: Sprinkler guideline (mentions DIN EN 12845 and CEA 4001 used as guide)",
        url="https://vds.de/en/certification/inspection-service/information-innovation/information-innovation/sprinkler-guideline",
        accessed=ACCESS_DATE,
        kind="Guideline/Recommendation",
    ),
    "VDS_CEA4001_PDF": Source(
        id="VDS_CEA4001_PDF",
        title="VdS CEA 4001en: 2021-01 (07) — Guidelines for sprinkler systems (PDF download)",
        url="https://shop.vds.de/download/V4001EN/4f4e0ad0-2efd-4221-af3e-41f57a44524f",
        accessed=ACCESS_DATE,
        kind="Guideline/Recommendation",
    ),
}

def sources_as_rows(module: str, criteria: List[dict]) -> List[dict]:
    rows = []
    for c in criteria:
        for sid in c.get("sources", []):
            s = SOURCES.get(sid)
            if not s:
                continue
            rows.append({
                "Module": module,
                "Criterion": c.get("criterion",""),
                "Type": s.kind,
                "Source": s.title,
                "Link": s.url,
                "Access date": s.accessed,
                "ID": s.id,
            })
    return rows
