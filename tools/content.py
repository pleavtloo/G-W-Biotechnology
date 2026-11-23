# -*- coding: utf-8 -*-
"""Content model for the G&W Biotechnologie GmbH site.

All editable content lives in content/*.yaml (see CONTENT-SCHEMA.md). This module
is the single loading point for build_site.py / build_docs.py / build_dist.py and
normalises three shapes the renderers expect:

  * product specs are stored as an ordered list of {k, v} (so a CMS can reorder
    rows) and exposed here as an ordered mapping
  * application steps are stored as {label, text} and exposed as (label, text)
  * application counts are computed from PRODUCTS[].apps, never hand-written

The narrative blocks at the bottom (SERVICES, NAV, POSITIONING, STACK, LOOP,
PORTFOLIO_*, AUTOMATION, NETWORK, EXPERT) stay inline: they change rarely and
are out of scope for the CMS (CONTENT-SCHEMA.md section 8).
"""
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONTENT_DIR = os.path.join(ROOT, "content")


def _load(name, key=None):
    """Read content/<name>. Pass key for files whose root is {key: [...]} (Decap needs
    an object at the root of every file it edits)."""
    with open(os.path.join(CONTENT_DIR, name), encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data[key] if key else data


def _load_dir(sub):
    """One YAML per entry (content/<sub>/*.yaml), ordered by the `order` field.

    Directories rather than one big list so the CMS can show every entry as its own
    record. `order` is authoritative: file names must never decide catalogue order.
    """
    folder = os.path.join(CONTENT_DIR, sub)
    rows = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".yaml"):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                rows.append(yaml.safe_load(f) or {})
    rows.sort(key=lambda r: r.get("order", 10 ** 6))
    return rows


COMPANY = _load("site.yaml")
CATEGORIES = _load("categories.yaml", "categories")
ARTICLES = _load_dir("articles")
FAQ = [(row["question"], row["answer"]) for row in _load_dir("faq")]

PRODUCTS = []
for _row in _load_dir("products"):
    _item = dict(_row)
    _item["specs"] = {cell["k"]: cell["v"] for cell in (_row.get("specs") or [])}
    _item["price"] = _row.get("price")          # CMS may drop an empty price field
    PRODUCTS.append(_item)

APPLICATIONS = _load_dir("applications")
_APP_COUNTS = {}
for _product in PRODUCTS:
    for _app_id in _product["apps"]:
        _APP_COUNTS[_app_id] = _APP_COUNTS.get(_app_id, 0) + 1
for _app in APPLICATIONS:
    _app["steps"] = [(step["label"], step["text"]) for step in _app["steps"]]
    _app["count"] = _APP_COUNTS.get(_app["id"], 0)


SERVICES = [
    dict(icon="magnet", title="Magnetic Bead Customisation",
         desc="Conjugate your antibody or ligand to 50 nm – 4.5 µm magnetic particles, with coupling density, blocking and release chemistry developed against your target cell.",
         tags=["Custom coupling", "Bead size screening", "Pilot → GMP lot"]),
    dict(icon="protein", title="GMP Protein Expression & Purification",
         desc="Constructs designed by the model, expressed in E. coli, HEK293 or CHO, then scaled through process development into GMP manufacturing.",
         tags=["E. coli / HEK293 / CHO", "Process development", "GMP manufacturing"]),
    dict(icon="dna", title="Gene Editing Services",
         desc="CRISPR and knock-in/knock-out engineering for cell lines and primary cells, with off-target assessment and clonal characterisation.",
         tags=["CRISPR Cas9", "Knock-in / KO", "Off-target analysis"]),
    dict(icon="beaker", title="Formulation Development",
         desc="Buffer, excipient and lyophilisation development for unstable proteins and reagents, including stability-indicating assay design.",
         tags=["Lyophilisation", "Buffer screening", "Stability studies"]),
    dict(icon="chart", title="Protein Characterisation",
         desc="Identity, purity and activity packages — SEC-HPLC, SDS-PAGE, MS, endotoxin, residual host-cell protein and cell-based potency.",
         tags=["SEC-HPLC", "Mass spec", "Potency assays"]),
    dict(icon="car", title="CAR-NK Process Support",
         desc="End-to-end process consulting for CAR-NK development, from vector and electroporation strategy to expansion and release testing.",
         tags=["CAR-NK", "Process design", "Release testing"]),
]


NAV = [
    dict(label="Platform", href="platform.html", mega="platform"),
    dict(label="Products", href="products.html", mega="products"),
    dict(label="Applications", href="applications.html", mega="applications"),
    dict(label="Services", href="services.html", mega="services"),
    dict(label="Quality", href="quality.html", mega=None),
    dict(label="Company", href="about.html", mega="company"),
]

# --------------------------------------------------------------------------
# AI-for-science positioning
# --------------------------------------------------------------------------
POSITIONING = {
    "eyebrow": "AI for science · life science tools",
    "h1_a": "Life science tools,",
    "h1_b": "designed in silico",
    "h1_c": "and proven at the bench.",
    "lede": "G&amp;W is building an AI-native tool stack for discovery teams: recombinant proteins, "
            "antibodies, separation reagents and culture systems, designed against your target, "
            "validated in our own lab, and delivered through a network of qualified facilities.",
}

# The four-layer stack that replaces the old "four platforms" story.
STACK = [
    dict(n="01", k="Data", title="Assay and process data",
         desc="Every lot, every protocol, every failed condition is recorded in a structured form. "
              "This is the layer most tool vendors never build.",
         meta="Lot-level records · protocol outcomes · QC release data",
         tone="a"),
    dict(n="02", k="Models", title="Expression design models",
         desc="Give a sequence and a constraint — titre, solubility, timeline — and the models propose "
              "the construct: codon usage matched to the host, signal peptide and tag choice, induction "
              "window. Candidates are ranked before anything is synthesised.",
         meta="Codon optimisation · host selection · solubility prediction",
         tone="b"),
    dict(n="03", k="Products", title="Physical reagents",
         desc="Proteins, antibodies, magnetic beads and defined media — the part your experiment "
              "actually touches. Designed for the assay, not for a catalogue slot.",
         meta=f"{len(PRODUCTS)} catalogue SKUs · GMP &amp; RUO grades · custom builds",
         tone="c"),
    dict(n="04", k="Lab network", title="Capacity to run the work",
         desc="Our own 3,200 m² laboratory, plus qualified partner facilities that absorb overflow. "
              "One order, routed to whichever bench can run it best.",
         meta="In-house lab · partner facilities · automation roadmap",
         tone="d"),
]

LOOP = [
    ("Design", "Model-proposed constructs, ranked by predicted yield and soluble fraction."),
    ("Build", "Gene synthesis, cloning and transformation — in house or through qualified partners."),
    ("Test", "Expression matrix at bench scale: titre, soluble fraction, purity by SDS-PAGE."),
    ("Learn", "Every result — including the failures — updates the model for the next round."),
]

# Today vs next: honest portfolio roadmap.
PORTFOLIO_NOW = [
    ("Cell separation & activation", "Magnetic beads, release chemistry, activation reagents", "products.html?cat=beads"),
    ("Recombinant proteins", "Cytokines, growth factors, matrix proteins", "products.html?cat=proteins"),
    ("Monoclonal antibodies", "Functional-grade anti-human mAbs", "products.html?cat=antibodies"),
    ("Media & culture systems", "Serum-free, chemically defined, animal-origin-free", "products.html?cat=media"),
]

PORTFOLIO_NEXT = [
    ("Nucleic acid extraction", "Silica and magnetic workflows, automation-friendly formats", "In development"),
    ("Cell culture systems", "Stem, immune and organoid formats beyond CGT", "In development"),
    ("Protein purification", "Resins, buffers and pre-packed columns", "In development"),
    ("Antibody discovery", "AI-proposed binders, wet-lab validated", "Research stage"),
]

# Automation maturity — deliberately honest.
AUTOMATION = [
    dict(phase="Available now", state="Bench-scale, expert-led",
         desc="A named scientist runs your design at the bench — small batches, tight iteration, "
              "judgement on every decision that the model cannot make.",
         points=["Named application scientist per project", "1–5 L bench scale",
                 "7–10 day typical turnaround"],
         tone="now"),
    dict(phase="Rolling out 2026–27", state="Automated screening",
         desc="Liquid handling and digital work instructions take over the repetitive transfer steps, "
              "so the same team carries more concurrent projects without losing oversight.",
         points=["Automated liquid handling on core assays", "Digital work instructions",
                 "Concurrency up ~3×"],
         tone="next"),
    dict(phase="From 2027", state="Network throughput",
         desc="A scheduling layer routes batches across qualified sites. Throughput becomes a "
              "function of the network, not of one building.",
         points=["Multi-site capacity routing", "Standardised data return",
                 "Order-to-result SLA"],
         tone="later"),
]

NETWORK = [
    ("Order intake", "One specification, one contract, one point of contact — regardless of where the work runs."),
    ("Qualification", "Each partner facility is audited on method fit, data format and turnaround before it receives work."),
    ("Routing", "The scheduler assigns each batch to the bench with the right capability and free capacity."),
    ("Return", "Results come back in one format, under our quality system, with our name on the report."),
]

EXPERT = {
    "title": "Your first call is a scientist, not a sales rep.",
    "desc": "Application support sits between your protocol and our roadmap. The team has run these "
            "workflows inside instrument and reagent companies before — which is why the questions "
            "they ask on the first call are the ones that decide whether a project is feasible.",
    "background": "Backgrounds at Miltenyi Biotec and STEMCELL Technologies",
    "bullets": [
        "Protocol review before you commit to a reagent",
        "Failure-mode triage on existing workflows",
        "Direct line into product development for custom builds",
    ],
}
