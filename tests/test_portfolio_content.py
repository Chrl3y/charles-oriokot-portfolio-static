import re
import subprocess
import unittest
import zipfile
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.nodes = []

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "text": ""}
        self.nodes.append(node)
        self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.nodes.append({"tag": tag, "attrs": dict(attrs), "text": ""})

    def handle_data(self, data):
        for node in self.stack:
            node["text"] += data

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                return


def parse_html(path):
    parser = DocumentParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def node_by_id(parser, node_id):
    return next(
        node for node in parser.nodes if node["attrs"].get("id") == node_id
    )


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


class PortfolioContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = parse_html(ROOT / "index.html")

    def test_completed_networking_and_ai_skills_are_visible(self):
        skills = normalized(node_by_id(self.index, "skills-section")["text"])
        for expected in (
            "Cisco Certified Network Associate (CCNA)",
            "AI-assisted engineering",
            "Data science & machine learning",
        ):
            self.assertIn(expected, skills)

        progress_bars = [
            node
            for node in self.index.nodes
            if "progress-bar" in node["attrs"].get("class", "").split()
        ]
        self.assertEqual(15, len(progress_bars))

    def test_credentials_distinguish_ccna_from_course_certificates(self):
        credentials = normalized(node_by_id(self.index, "credentials-section")["text"])
        self.assertIn("Cisco Certified Network Associate (CCNA)", credentials)
        self.assertIn("Introduction to Data Science", credentials)
        self.assertIn("U.S. Mission Uganda", credentials)
        self.assertIn("Soft Skills", credentials)

        image_sources = {
            node["attrs"].get("src")
            for node in self.index.nodes
            if node["tag"] == "img"
        }
        self.assertIn(
            "assets/certificates/cisco-netacad-introduction-to-data-science.png",
            image_sources,
        )
        self.assertIn(
            "assets/certificates/us-mission-uganda-soft-skills.png",
            image_sources,
        )

    def test_vici_reality_is_presented_as_a_current_initiative(self):
        section = normalized(node_by_id(self.index, "initiatives-section")["text"])
        self.assertIn("VICI Reality", section)
        self.assertIn("In formation · pre-pilot", section)
        self.assertIn("Evidence-Gated Venture Foundry", section)
        self.assertIn("Spatial evidence research", section)

        hrefs = {
            node["attrs"].get("href")
            for node in self.index.nodes
            if node["tag"] == "a"
        }
        self.assertIn("vici-reality.html", hrefs)

        venture = parse_html(ROOT / "vici-reality.html")
        page_text = normalized(" ".join(node["text"] for node in venture.nodes))
        self.assertIn("Venture in formation · pre-pilot", page_text)
        self.assertIn("phone", page_text.lower())
        self.assertIn("browser", page_text.lower())
        self.assertIn("Charles Oriokot", page_text)
        for unsupported in ("registered company", "patent pending", "customer revenue"):
            self.assertNotIn(unsupported, page_text.lower())

    def test_organizations_and_project_atlas_are_evidence_tiered(self):
        section = normalized(node_by_id(self.index, "ecosystem-section")["text"])
        for expected in (
            "Nova Microfinance",
            "eTranzact",
            "Simba Automotives",
            "Arc Ride Uganda",
        ):
            self.assertIn(expected, section)

        atlas = parse_html(ROOT / "ecosystem.html")
        atlas_text = normalized(" ".join(node["text"] for node in atlas.nodes))
        for expected in (
            "Current role · employer systems",
            "Exploratory · integration design",
            "Live trial · permission-dependent case study",
            "Concept and proposal stage",
            "VICI Reality",
            "SmartRide",
            "Regulated Operations Workbench",
            "SACCO Hub",
            "Value OS / EvidenceOS",
            "Migration Assurance Studio",
            "GitHub Intelli-Agent",
            "NFC verified identity and lead handoff",
        ):
            self.assertIn(expected, atlas_text)

        for unsupported in (
            "signed eTranzact partnership",
            "deployed Arc Ride operations centre",
            "UGX 3.0M",
        ):
            self.assertNotIn(unsupported.lower(), atlas_text.lower())

    def test_census_pictorial_and_clean_event_photos_are_published(self):
        pictorial = normalized(node_by_id(self.index, "pictorial-section")["text"])
        self.assertIn("Digital Census device readiness", pictorial)
        self.assertIn("National ICT Innovation Hub", pictorial)

        image_sources = [
            node["attrs"].get("src")
            for node in self.index.nodes
            if node["tag"] == "img"
        ]
        self.assertIn("images/community/ursb-ip-session-01.jpg", image_sources)
        self.assertIn("images/community/ursb-ip-session-02.jpg", image_sources)
        self.assertGreaterEqual(
            len([src for src in image_sources if src and "census-device-readiness" in src]),
            4,
        )

        for filename in ("ursb-ip-session-01.jpg", "ursb-ip-session-02.jpg"):
            path = ROOT / "images" / "community" / filename
            result = subprocess.run(
                ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("pixelWidth: 720", result.stdout)
            self.assertIn("pixelHeight: 720", result.stdout)

    def test_downloadable_cv_records_completed_ccna(self):
        cv_path = ROOT / "assets" / "Oriokot_Charles_Ediu_CV_2026.docx"
        with zipfile.ZipFile(cv_path) as archive:
            document_xml = archive.read("word/document.xml").decode("utf-8")
        text = normalized(re.sub(r"<[^>]+>", " ", document_xml))
        self.assertIn("Cisco Certified Network Associate (CCNA)", text)
        self.assertNotIn("Cisco Certified Network Associate (CCNA) - Ongoing", text)

    def test_local_page_links_and_media_resolve(self):
        pages = [ROOT / "index.html", ROOT / "vici-reality.html", ROOT / "ecosystem.html"]
        missing = []
        for page in pages:
            parser = parse_html(page)
            for node in parser.nodes:
                target = node["attrs"].get("href") or node["attrs"].get("src")
                if not target or target.startswith(("#", "http:", "https:", "mailto:", "tel:")):
                    continue
                clean_target = target.split("#", 1)[0].split("?", 1)[0]
                if clean_target and not (ROOT / clean_target).exists():
                    missing.append(f"{page.name}: {clean_target}")
        self.assertEqual([], missing)

    def test_small_mobile_hero_wraps_without_clipping(self):
        css = (ROOT / "css" / "custom.css").read_text(encoding="utf-8")
        self.assertIn("@media (max-width:575.98px)", css)
        self.assertIn(".owl-carousel.home-slider .slider-item .slider-text h1", css)
        self.assertIn(".owl-carousel.home-slider .slider-item .slider-text p", css)
        self.assertIn("grid-template-columns:1fr", css)


if __name__ == "__main__":
    unittest.main()
