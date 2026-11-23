"""
Generate downloadable technical documents for every catalogue SKU.

Output: website/docs/*.pdf
  datasheet-<slug>.pdf   technical datasheet, 2 pages
  coa-<slug>.pdf         representative certificate of analysis, 1 page
  sds-<cat>.pdf          safety data sheet per product family
  dmf-summary.pdf        DMF filing summary
  quality-overview.pdf   quality system overview

Run:  ./.venv/Scripts/python.exe tools/build_docs.py
"""
import hashlib
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fpdf import FPDF

from content import APPLICATIONS, CATEGORIES, COMPANY, PRODUCTS

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "website", "docs")

NAVY = (10, 27, 51)
BRAND = (42, 66, 153)
SKY = (47, 143, 208)
INK = (27, 44, 68)
MUTED = (94, 112, 134)
LINE = (214, 222, 232)
MIST = (244, 248, 254)
GREEN = (16, 122, 87)

FONT_DIR = "C:/Windows/Fonts"
FONT = "calibri"
FONT_B = "calibrib"

CAT_CODE = {"beads": "BD", "antibodies": "AB", "proteins": "PR", "media": "MD"}

# characters Arial/Calibri may lack
# Calibri covers the full set we use (checked with fontTools); only HTML entities
# leaking in from content.py need unwrapping.
SUBS = {"&amp;": "&", "&nbsp;": " ", "&deg;": "\u00b0"}


def clean(t):
    for k, v in SUBS.items():
        t = t.replace(k, v)
    return t


def cat_of(p):
    return next(c for c in CATEGORIES if c["id"] == p["cat"])


def code_of(p):
    i = [x["slug"] for x in PRODUCTS].index(p["slug"]) + 1
    return "TL-%s-%03d" % (CAT_CODE.get(p["cat"], "XX"), 100 + i)


def lot_of(p):
    h = hashlib.md5(p["slug"].encode()).hexdigest()
    n = int(h[:6], 16) % 9000 + 1000
    return "L%s-%03d" % (h[:4].upper(), n % 1000)


def money(v):
    return "${:,}".format(v)


class Doc(FPDF):
    def __init__(self, kind, title):
        super().__init__(format="A4")
        self.kind = kind
        self.doc_title = title
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(18, 18, 18)
        self.add_font(FONT, "", os.path.join(FONT_DIR, "calibri.ttf"))
        self.add_font(FONT, "B", os.path.join(FONT_DIR, "calibrib.ttf"))
        self.add_font(FONT, "I", os.path.join(FONT_DIR, "calibrii.ttf"))
        self.set_font(FONT, "", 10)

    # ---------- chrome ----------
    def header(self):
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 22, "F")
        self.set_text_color(255, 255, 255)
        self.set_font(FONT, "B", 10.5)
        self.set_xy(18, 7)
        self.cell(90, 6, "T&L BIOTECHNOLOGY", align="L")
        self.set_font(FONT, "", 8.5)
        self.set_text_color(160, 190, 225)
        self.set_xy(18, 12.6)
        self.cell(120, 5, "Life science tools - designed in silico, validated at the bench")
        self.set_text_color(255, 255, 255)
        self.set_font(FONT, "B", 8.5)
        self.set_xy(110, 9)
        self.cell(82, 6, self.kind.upper(), align="R")
        self.set_y(30)
        self.set_text_color(*INK)

    def footer(self):
        self.set_y(-16)
        self.set_draw_color(*LINE)
        self.set_line_width(0.3)
        self.line(18, self.get_y() - 2, 192, self.get_y() - 2)
        self.set_font(FONT, "", 7.4)
        self.set_text_color(*MUTED)
        self.set_y(-13)
        self.cell(0, 4, clean("%s  |  %s  |  %s" % (COMPANY["name"], COMPANY["email"], COMPANY["phone"])), align="L")
        self.set_y(-9)
        self.cell(0, 4, "Page %d" % self.page_no(), align="R")

    # ---------- blocks ----------
    def h1(self, title, sub=""):
        self.set_font(FONT, "B", 19)
        self.set_text_color(*NAVY)
        self.multi_cell(174, 8.4, clean(title), new_x="LMARGIN", new_y="NEXT")
        if sub:
            self.ln(1)
            self.set_font(FONT, "", 10)
            self.set_text_color(*MUTED)
            self.multi_cell(174, 5.2, clean(sub), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def h2(self, title):
        self.ln(3.4)
        self.set_font(FONT, "B", 8.6)
        self.set_text_color(*SKY)
        self.cell(0, 4.6, clean(title.upper()), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*LINE)
        self.set_line_width(0.3)
        self.line(18, self.get_y() + 1.2, 192, self.get_y() + 1.2)
        self.ln(4.4)

    def body(self, text, size=9.6, color=INK, lh=5.0):
        self.set_font(FONT, "", size)
        self.set_text_color(*color)
        self.multi_cell(174, lh, clean(text))
        self.ln(1.2)

    def kv_table(self, rows, widths=(58, 116)):
        fill = False
        for k, v in rows:
            self.set_font(FONT, "", 8.8)
            lines = self.multi_cell(widths[1], 5.4, clean(str(v)), dry_run=True,
                                    output="LINES")
            h = max(7.2, 5.4 * len(lines) + 2.0)
            self.set_fill_color(*(MIST if fill else (255, 255, 255)))
            self.set_draw_color(*LINE)
            self.set_line_width(0.2)
            x, y = 18, self.get_y()
            self.set_xy(x, y)
            self.set_font(FONT, "B", 8.6)
            self.set_text_color(*MUTED)
            self.multi_cell(widths[0], h, clean(k), border="B", fill=True, align="L",
                            new_x="RIGHT", new_y="TOP")
            self.set_font(FONT, "", 9)
            self.set_text_color(*INK)
            self.set_xy(x + widths[0], y)
            self.multi_cell(widths[1], h, clean(str(v)), border="B", fill=True, align="L",
                            new_x="LMARGIN", new_y="TOP")
            self.set_y(y + h)
            fill = not fill
        self.ln(2.4)

    def grid_table(self, head, rows, widths):
        self.set_font(FONT, "B", 8)
        self.set_fill_color(*NAVY)
        self.set_text_color(255, 255, 255)
        for h, w in zip(head, widths):
            self.cell(w, 7, clean(h), border=0, fill=True, align="L")
        self.ln()
        self.set_text_color(*INK)
        fill = False
        for r in rows:
            self.set_fill_color(*(MIST if fill else (255, 255, 255)))
            hmax = 7
            for c, w in zip(r, widths):
                self.set_font(FONT, "", 8.8)
                lines = self.multi_cell(w, 5.4, clean(str(c)), align="L",
                                        dry_run=True, output="LINES")
                hmax = max(hmax, 5.4 * len(lines) + 1.8)
            y0 = self.get_y()
            for c, w in zip(r, widths):
                self.set_xy(self.get_x(), y0)
                self.multi_cell(w, 5.4, clean(str(c)), border=0, align="L", fill=True,
                                new_x="RIGHT", new_y="TOP")
            self.set_y(y0 + hmax)
            self.set_draw_color(*LINE)
            self.set_line_width(0.2)
            self.line(18, self.get_y(), 192, self.get_y())
            fill = not fill
        self.ln(3)

    def bullets(self, items):
        self.set_font(FONT, "", 9.4)
        self.set_text_color(*INK)
        for it in items:
            y = self.get_y()
            self.set_fill_color(*BRAND)
            self.rect(19.6, y + 2.0, 1.5, 1.5, "F")
            self.set_x(24)
            self.multi_cell(168, 5.0, clean(it))
            self.ln(0.6)
        self.ln(1.6)

    def note(self, text):
        self.set_fill_color(*MIST)
        self.set_draw_color(*LINE)
        self.set_line_width(0.2)
        x, y = 18, self.get_y()
        self.set_font(FONT, "I", 8.4)
        self.set_text_color(*MUTED)
        self.set_xy(22, y + 3)
        self.multi_cell(164, 4.6, clean(text))
        h = self.get_y() - y + 1
        self.rect(x, y, 174, h, "D")
        self.set_y(y + h + 3)


def meta_strip(doc, cells):
    """Four small meta cells across the page."""
    doc.set_font(FONT, "", 7.6)
    w = 174 / len(cells)
    y = doc.get_y()
    for i, (k, v) in enumerate(cells):
        x = 18 + i * w
        doc.set_xy(x, y)
        doc.set_text_color(*MUTED)
        doc.set_font(FONT, "", 7.2)
        doc.cell(w - 2, 4, clean(k.upper()))
        doc.set_xy(x, y + 4)
        doc.set_font(FONT, "B", 9)
        doc.set_text_color(*INK)
        doc.cell(w - 2, 5, clean(v))
    doc.set_y(y + 11)
    doc.set_draw_color(*LINE)
    doc.set_line_width(0.3)
    doc.line(18, doc.get_y(), 192, doc.get_y())
    doc.ln(4)


# --------------------------------------------------------------------------
def datasheet(p):
    cat = cat_of(p)
    d = Doc("Technical datasheet", p["name"])
    d.add_page()
    d.h1(p["name"], "%s  -  %s" % (cat["name"], p["blurb"]))
    meta_strip(d, [
        ("Catalogue no.", code_of(p)),
        ("Family", cat["name"]),
        ("Revision", "2.1"),
        ("Effective", date(2026, 10, 1).strftime("%d %b %Y")),
    ])

    d.h2("Description")
    d.body(p["desc"])

    d.h2("Ordering information")
    rows = []
    for i, s in enumerate(p["sizes"]):
        if p["price"]:
            unit = p["price"] * (1 + i * 1.9)
            rows.append([s, code_of(p) + "-%02d" % (i + 1), money(int(round(unit, -1))),
                         "In stock" if i < 2 else "3-5 days"])
        else:
            rows.append([s, code_of(p) + "-%02d" % (i + 1), "On request", "On request"])
    d.grid_table(["Pack size", "Order code", "List price (USD)", "Lead time"], rows,
                 [40, 44, 48, 42])
    d.body("List prices are for research pack sizes, excluding shipping and local duties. "
           "Process-scale quantities and GMP lots are quoted individually.", 8.6, MUTED, 4.6)

    d.h2("Specifications")
    d.kv_table([(k, v) for k, v in p["specs"].items()])

    d.h2("Key features")
    d.bullets(p["highlights"])

    # ---- page two ----
    d.add_page()
    d.set_font(FONT, "B", 11)
    d.set_text_color(*NAVY)
    d.multi_cell(174, 6, clean("%s - %s" % (p["name"], code_of(p))),
                 new_x="LMARGIN", new_y="NEXT")
    d.set_font(FONT, "", 8.4)
    d.set_text_color(*MUTED)
    d.multi_cell(174, 4.6, "continued", new_x="LMARGIN", new_y="NEXT")

    d.h2("Handling and storage")
    d.body("Store as stated in the specification table. Do not aliquot into glass unless the "
           "surface is passivated; proteins at low concentration adsorb to glass and to some "
           "low-bind plastics. Equilibrate to room temperature before use and avoid repeated "
           "freeze-thaw cycles.")
    d.body("Where a lot-specific value differs from the catalogue range, the value on the "
           "Certificate of Analysis takes precedence.")

    d.h2("Where it is used")
    app_names = [a["name"] for a in APPLICATIONS if a["id"] in p.get("apps", [])]
    if app_names:
        d.body("Catalogue applications: " + ", ".join(app_names) + ".")
    d.bullets([
        "Bench-scale process development and assay qualification",
        "Analytical method transfer, where the reagent is part of the readout",
        "Pilot and clinical manufacturing, in the GMP grade of the same design",
    ])
    d.body("The GMP and RUO grades share the same design and the same release panel; the grade "
           "determines the documentation package and the release criteria, not the reagent "
           "chemistry. Qualify once, then scale on the same specification.", 9.4, MUTED, 4.8)

    d.h2("Compatibility")
    d.kv_table([
        ("Automated platforms", "Validated on closed, functionally closed and open bench formats"),
        ("Bead removal", "Where applicable, removal is optional; residual beads do not interfere "
                         "with downstream flow cytometry at the recommended ratio"),
        ("Downstream assays", "Flow cytometry, viability, expansion and cytotoxicity readouts"),
        ("Container", "Supplied in low-bind plastic; do not transfer to glass for storage"),
    ])

    d.h2("Revision history")
    d.grid_table(["Rev", "Date", "Change"],
                 [["2.1", "01 Oct 2026", "Ordering table aligned to 2026 list prices; handling notes expanded"],
                  ["2.0", "12 Mar 2025", "Specification panel harmonised across GMP and RUO grades"],
                  ["1.0", "05 Jun 2023", "First release"]],
                 [16, 34, 124])

    d.h2("Related documents")
    d.kv_table([
        ("Certificate of Analysis", "Supplied with every lot; representative copy available on request"),
        ("Safety data sheet", "Available for this product family"),
        ("DMF", "Referenceable filing where applicable - see the DMF summary"),
        ("Quality overview", "ISO 13485:2016 and ISO 9001 certification scope"),
    ])
    d.note("This datasheet describes the catalogue specification. Final acceptance criteria are "
           "fixed in the lot-specific Certificate of Analysis and, for GMP material, in the "
           "quality agreement.")
    d.output(os.path.join(OUT, "datasheet-%s.pdf" % p["slug"]))
    return "datasheet-%s.pdf" % p["slug"]


def coa(p):
    cat = cat_of(p)
    lot = lot_of(p)
    d = Doc("Certificate of analysis", p["name"])
    d.add_page()
    d.h1("Certificate of Analysis", p["name"])
    meta_strip(d, [
        ("Catalogue no.", code_of(p)),
        ("Lot no.", lot),
        ("Manufacture", "2026-08-14"),
        ("Retest", "2028-08-13"),
    ])

    fmt = p["specs"].get("Format", "")
    powder = "lyoph" in fmt.lower()
    appearance = ("White to off-white lyophilised powder" if powder
                  else "Clear to slightly opalescent liquid" if p["cat"] != "media"
                  else "Clear liquid, free of visible particulates")
    d.h2("Product identification")
    d.kv_table([
        ("Product", p["name"]),
        ("Family", cat["name"]),
        ("Appearance", appearance),
        ("Pack size", p["sizes"][0]),
        ("Storage", p["specs"].get("Storage", "2-8 \u00b0C")),
        ("Shelf life", p["specs"].get("Shelf life", "24 months")),
    ])

    endotoxin = p["specs"].get("Endotoxin", "\u2264 0.5 EU/mL")
    eu_unit = "EU/\u00b5g" if "/\u00b5g" in endotoxin else "EU/mL"
    eu_result = "0.06 " + eu_unit if eu_unit == "EU/\u00b5g" else "0.18 " + eu_unit
    rows = [
        ["Identity", "Peptide mapping / Western blot", "Conforms", "Conforms", "Pass"],
        ["Purity", "SDS-PAGE, densitometry", ">= 95.0 %", "97.4 %", "Pass"],
        ["Concentration", "A280, extinction coefficient", "As labelled", "Conforms", "Pass"],
        ["Endotoxin", "LAL, kinetic turbidimetric", clean(endotoxin), eu_result, "Pass"],
        ["Sterility", "Membrane filtration, 14 days", "No growth", "No growth", "Pass"],
        ["pH", "Potentiometric", "7.0 - 7.6", "7.2", "Pass"],
        ["Appearance", "Visual, against reference", "Conforms", "Conforms", "Pass"],
        ["Batch record review", "Documented release", "Complete", "Complete", "Pass"],
    ]
    d.h2("Test results")
    d.grid_table(["Test", "Method", "Specification", "Result", "Status"], rows,
                 [34, 52, 38, 34, 16])

    d.h2("Release statement")
    d.body("This lot has been manufactured and tested in accordance with the registered "
           "specification and released by Quality Control. Retain samples are held for the "
           "shelf-life period plus twelve months. The product is intended for research use or "
           "further manufacturing; it is not intended for direct diagnostic use.")

    d.ln(6)
    y = d.get_y()
    d.set_draw_color(*LINE)
    d.line(18, y, 88, y)
    d.line(110, y, 192, y)
    d.set_font(FONT, "", 8)
    d.set_text_color(*MUTED)
    d.set_xy(18, y + 2)
    d.cell(70, 4, "Released by - Quality Control")
    d.set_xy(110, y + 2)
    d.cell(82, 4, "Authorised signatory - Quality Assurance")

    d.ln(10)
    d.note("Representative certificate. The lot-specific COA is issued with your shipment and "
           "carries the release signatures; values shown here illustrate the test panel and are "
           "not a release record for any specific lot.")
    d.output(os.path.join(OUT, "coa-%s.pdf" % p["slug"]))
    return "coa-%s.pdf" % p["slug"]


SDS_SECTIONS = [
    ("1. Identification",
     "Product identifier: {name}. Relevant identified uses: laboratory reagent for research and "
     "further manufacturing. Not for direct diagnostic, therapeutic or household use. "
     "Supplier: T&L Biotechnology Ltd., Carlsbad, CA, United States. Emergency telephone: see "
     "the number on the shipping documentation."),
    ("2. Hazards identification",
     "Not classified as hazardous under CLP or OSHA HazCom 2012 in the supplied form. The "
     "product contains a preserved aqueous buffer; repeated skin contact may cause dryness. "
     "No signal word, no hazard pictogram."),
    ("3. Composition",
     "Aqueous buffered solution containing the active {active} component, a carrier protein "
     "where applicable, and 0.02 % (w/v) sodium azide as preservative unless stated otherwise "
     "on the label. Sodium azide is toxic to aquatic life."),
    ("4. First aid measures",
     "Inhalation: move to fresh air. Skin contact: wash with water and soap. Eye contact: rinse "
     "with water for at least 15 minutes, holding the eyelids open. Ingestion: rinse the mouth, "
     "do not induce vomiting, seek medical advice if symptoms persist. Show this document to the "
     "attending physician."),
    ("5. Firefighting measures",
     "Not flammable. Use extinguishing media appropriate to the surrounding fire. Thermal "
     "decomposition may release nitrogen oxides and carbon oxides. Wear self-contained breathing "
     "apparatus in an enclosed space."),
    ("6. Accidental release measures",
     "Small spills: absorb with inert material, wipe the surface, dispose of as laboratory waste. "
     "Large spills: contain with absorbent booms, prevent entry into drains and surface water. "
     "Do not allow sodium azide-containing waste to contact copper or lead plumbing, where "
     "explosive azide salts can form."),
    ("7. Handling and storage",
     "Handle under normal laboratory conditions with gloves and eye protection. Store at 2-8 deg C, "
     "do not freeze. Keep the container tightly closed when not in use. Avoid repeated "
     "temperature cycling."),
    ("8. Exposure controls",
     "No occupational exposure limit is assigned to the preparation. General laboratory "
     "ventilation is adequate. Where aerosols may be generated, use local exhaust ventilation. "
     "Gloves: nitrile. Eye protection: safety glasses."),
    ("9. Physical and chemical properties",
     "Appearance: clear liquid. Odour: odourless. pH: 7.0-7.6. Boiling point: approximately "
     "100 deg C. Water solubility: fully miscible. Flash point: not applicable."),
    ("10. Stability and reactivity",
     "Stable under the recommended storage conditions. No hazardous reactions known. Avoid "
     "strong oxidising agents and prolonged exposure to light."),
    ("11. Toxicological information",
     "No acute toxicity data are available for the preparation as a whole. The active component "
     "is a protein or antibody; sensitisation by inhalation of aerosols cannot be excluded for "
     "sensitised individuals. Sodium azide is harmful if swallowed."),
    ("12. Ecological information",
     "Sodium azide is very toxic to aquatic life. Do not release the product or its waste into "
     "the environment. Dilute small quantities with copious water before disposal through the "
     "sanitary sewer where local regulations permit."),
    ("13. Disposal",
     "Dispose of as laboratory chemical waste in accordance with local, regional and national "
     "regulations. Do not reuse empty containers."),
    ("14. Transport information",
     "Not classified as dangerous goods for road, rail, sea or air transport. No UN number, "
     "no packing group. Ship with cold packs where the product requires 2-8 deg C."),
    ("15. Regulatory information",
     "Not a controlled substance. The product is not registered as a medicinal product. Where "
     "the product is supplied as GMP-grade material, the applicable quality agreement applies "
     "in addition to this sheet."),
    ("16. Other information",
     "Revision 3.0, effective 01 October 2026. This sheet describes the product family and is "
     "superseded by any product-specific sheet issued with a GMP lot."),
]


def sds(cat):
    name = "%s family reagents" % cat["name"]
    d = Doc("Safety data sheet", name)
    d.add_page()
    d.h1("Safety Data Sheet", "%s - all catalogue items in this family" % cat["name"])
    meta_strip(d, [
        ("Document", "SDS-%s" % CAT_CODE.get(cat["id"], "XX")),
        ("Revision", "3.0"),
        ("Effective", "01 Oct 2026"),
        ("Format", "16 sections, CLP / HazCom aligned"),
    ])
    for title, text in SDS_SECTIONS:
        d.h2(title)
        d.body(text.format(name=name, active=cat["short"].lower()))
    d.note("This sheet covers the product family. Where an item carries a product-specific "
           "hazard statement, the sheet issued with the shipment takes precedence.")
    d.output(os.path.join(OUT, "sds-%s.pdf" % cat["id"]))
    return "sds-%s.pdf" % cat["id"]


def dmf_summary():
    d = Doc("Regulatory summary", "Type II Drug Master Files")
    d.add_page()
    d.h1("DMF filing summary", "Two Type II Drug Master Files on record with the US FDA")
    meta_strip(d, [
        ("DMF 038124", "ActSep CD3/CD28 beads"),
        ("DMF 038820", "Anti-human CD28 mAb"),
        ("Type", "II - drug substance / excipient"),
        ("Status", "Active"),
    ])
    d.h2("What a DMF allows")
    d.body("A Type II DMF is a submission to the FDA containing confidential manufacturing "
           "information for a material used in a drug product. It is not approved or rejected - "
           "it is reviewed only when a sponsor references it in their own filing. The value to a "
           "sponsor is that the chemistry, manufacturing and controls detail is already on file, "
           "so the material can be referenced in an IND without duplicating that work.")
    d.h2("Files on record")
    d.grid_table(
        ["Reference", "Material", "Coverage", "Status"],
        [["038124", "ActSep CD3/CD28 separation and activation beads",
          "Manufacture, release testing, stability", "Active"],
         ["038820", "Anti-human CD28 monoclonal antibody",
          "Manufacture, release testing, stability", "Active"]],
        [26, 62, 62, 24])
    d.h2("How to reference a file")
    d.bullets([
        "Request a letter of authorisation naming your company and the file number.",
        "We issue the letter to the file holder of record within five business days.",
        "Your regulatory team submits the letter with the reference in your IND or BLA.",
        "We answer FDA information requests directly; the file content stays confidential.",
    ])
    d.h2("Scope and limits")
    d.body("The files cover the materials as manufactured at our Carlsbad facility under the "
           "current process. A change of manufacturing site, scale or process triggers an annual "
           "report or an amendment, and sponsors referencing the file are notified where the "
           "change is relevant to their application.")
    d.note("This summary is a communication aid, not the filing itself. The file content is "
           "confidential and is released to the agency, not to sponsors.")
    d.output(os.path.join(OUT, "dmf-summary.pdf"))
    return "dmf-summary.pdf"


def quality_overview():
    d = Doc("Quality overview", "Quality management system")
    d.add_page()
    d.h1("Quality overview", "ISO 13485:2016 and ISO 9001 certified - one system, two scopes")
    meta_strip(d, [
        ("Certification", "ISO 13485:2016 / ISO 9001"),
        ("Facility", "3,200 m2, Carlsbad CA"),
        ("Last audit", "Customer audits supported"),
        ("Revision", "4.0"),
    ])
    d.h2("Scope")
    d.body("The system covers design control, supplier management, manufacturing, release "
           "testing, storage and distribution of reagents for cell and gene therapy. GMP-grade "
           "and RUO-grade material are produced under the same system; the grade determines the "
           "release criteria and the documentation package, not the controls behind them.")
    d.h2("What the system controls")
    d.bullets([
        "Design control with documented inputs, outputs, verification and review",
        "Supplier qualification and incoming material testing",
        "Batch record issuance, review and release by a named QA signatory",
        "Equipment qualification, calibration and maintenance schedules",
        "Deviation, CAPA and change control with effectiveness checks",
        "Stability programme with defined retest intervals",
        "Annual product quality review and management review",
    ])
    d.h2("Documentation available to customers")
    d.grid_table(
        ["Document", "Timing", "Notes"],
        [["Certificate of Analysis", "With every lot", "Lot-specific, signed release"],
         ["Technical datasheet", "On request", "Catalogue specification"],
         ["Safety data sheet", "On request", "Per product family"],
         ["Quality agreement", "Before first GMP order", "Bilateral, signed"],
         ["Audit report / site visit", "On request", "Under confidentiality"],
         ["DMF letter of authorisation", "On request", "Where a file exists"]],
        [58, 52, 64])
    d.h2("Audit history")
    d.body("Customer and prospective-customer audits are supported under a confidentiality "
           "agreement. Audit reports, deviation logs and the CAPA register are made available "
           "in a secure data room rather than sent by email.")
    d.note("Certificates, scope statements and the current quality manual index are released "
           "after a mutual NDA. Nothing in this document constitutes a quality agreement.")
    d.output(os.path.join(OUT, "quality-overview.pdf"))
    return "quality-overview.pdf"


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for p in PRODUCTS:
        made.append(datasheet(p))
        made.append(coa(p))
    for c in CATEGORIES:
        made.append(sds(c))
    made.append(dmf_summary())
    made.append(quality_overview())
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in made)
    print("generated %d documents, %.1f KB total" % (len(made), total / 1024))


if __name__ == "__main__":
    main()
