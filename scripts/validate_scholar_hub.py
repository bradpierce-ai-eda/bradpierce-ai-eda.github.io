#!/usr/bin/env python3
"""Fail-closed Google Scholar readiness checks for the public paper hub."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from lxml import html
from pypdf import PdfReader


PAPERS = (
    {'key': 'basalt-calcium', 'title': 'Basalt-Derived Calcium for Lower Carbon Portland Cement', 'subtitle': 'A Carbon Budget for Process Development', 'date': '2026/10/21', 'slug': 'basalt-derived-calcium-for-lower-carbon-portland-cement', 'pdf': 'basalt-derived-calcium-for-lower-carbon-portland-cement.pdf', 'pdf_sha256': 'e0107c1ae5c10fd03bc54908df28cffb7032f491767cf0b68ea389a97e5f8c6a', 'validator': ['python3', '-B', 'scripts/validate_derivative.py', '--repo', '.']},
    {'key': 'who-else', 'title': 'Who Else Wants to Know?', 'subtitle': 'How AI could help strangers discover unexpected questions and fund the answers together.', 'date': '2026/10/21', 'slug': 'who-else-wants-to-know', 'pdf': 'who-else-wants-to-know.pdf', 'pdf_sha256': 'fc7583e903f1059c74e5474e5f4bca9ae479a41b3b3189af23ff27abbc866979', 'validator': ['python3', '-B', 'scripts/validate_derivative.py', '--repo', '.']},
    {'key': 'silicate', 'title': 'Silicate Rocks and Mineral Residues as Sources of Cementitious Precursors: A Literature Survey', 'display_title': 'Silicate Rocks and Mineral Residues as Sources of Cementitious Precursors', 'subtitle': 'A Literature Survey', 'date': '2026/10/21', 'slug': 'silicate-cementitious-precursors', 'pdf': 'silicate-cementitious-precursors.pdf', 'pdf_sha256': '43a1b73ebb707c94e1f6a09dc3e356707d288beb27d8e5c8582ef60445fdfdca', 'validator': [sys.executable, '-B', 'scripts/validate_derivative.py', '--repo', '.']},
    {'key': 'basalt', 'title': 'Basalt and Basalt-Derived Materials in Cement Manufacture and Cementitious Composites: A Global Literature Survey', 'display_title': 'Basalt and Basalt-Derived Materials in Cement Manufacture and Cementitious Composites', 'subtitle': 'A Global Literature Survey', 'date': '2026/10/20', 'slug': 'basalt-cement-survey', 'pdf': 'basalt-cement-survey.pdf', 'pdf_sha256': 'd48f566893a941cd4ca474d33b5160eb43fe275b11527db024ee45f3db0a3294', 'validator': [sys.executable, '-B', 'scripts/validate_derivative.py', '--repo', '.']},
    {'key': 'external-analysis', 'title': 'External Analysis of Protected Data', 'subtitle': 'Data Clean Rooms, Confidential Computing, Approved Queries, and the Emerging Agent Interface', 'date': '2026/10/14', 'slug': 'external-analysis-of-protected-data', 'pdf': 'external-analysis-of-protected-data.pdf', 'pdf_sha256': '6d6ecdf9d44e18f296844af01b0dd55facbc8a3f09c358638f0c4cf7b1f97892', 'validator': ['python3', 'scripts/validate_derivative.py', '--repo', '.']},
    {
        "key": "staying-capable",
        "title": "Staying Capable in a World That Pushes Back",
        "date": "2026/10/11",
        "slug": "staying-capable-in-a-world-that-pushes-back",
        "pdf": "staying-capable-in-a-world-that-pushes-back.pdf",
        "pdf_sha256": "2ddc5af6b5251382d025e4dadfeb02c56198035e9b988919a5350613e62fcb0e",
        "validator": ["python3", "scripts/validate_derivative.py", "--repo", "."],
    },
    {
        "key": "design-exploration",
        "title": "When Design Exploration Gets Cheap",
        "date": "2026/10/09",
        "slug": "when-design-exploration-gets-cheap",
        "pdf": "paper.pdf",
        "pdf_sha256": "8bf249abfb22647ec9a71340e0fc7b26931c6a392de45685c1e7a5e8dad41194",
        "validator": ["python3", "scripts/validate_derivative.py", "."],
    },
    {
        "key": "transitions",
        "title": "Controlling Consequential Transitions: An Execution Contract and Architecture-Review Method for Agent Workflows",
        "display_title": "Controlling Consequential Transitions",
        "subtitle": "An Execution Contract and Architecture-Review Method for Agent Workflows",
        "date": "2026/09/22",
        "slug": "controlling-consequential-transitions",
        "pdf": "controlling-consequential-transitions.pdf",
        "pdf_sha256": "fd0182d44e827ab8d1ed2cc78e06be8b225cf97d690a8e2db20be0c52190a934",
        "validator": ["python3", "scripts/validate_derivative.py", "--repo", "."],
    },
    {
        "key": "intelligence",
        "title": "Intelligence by Appointment",
        "date": "2026/09/21",
        "slug": "intelligence-by-appointment",
        "pdf": "intelligence-by-appointment.pdf",
        "pdf_sha256": "fb340eba69d493b9539c506903b1b3a7a8ccc81080647a53aa5543112400b9f4",
        "validator": ["python3", "scripts/validate_derivative.py", "."],
    },
    {'key': 'architecture', 'title': 'The Architecture Is Old. The Computational Actor Is New.', 'subtitle': 'C++HDL, AI agents, and moving the RTL development loop while keeping SystemVerilog at the boundary', 'date': '2026/09/13', 'slug': 'the-architecture-is-old-the-computational-actor-is-new', 'pdf': 'the-architecture-is-old-the-computational-actor-is-new.pdf', 'pdf_sha256': '6f31c26c9859a616437d6014697db2fc838166bcf639d4e93384678a4263d67f', 'validator': ['python3', 'scripts/validate_derivative.py', '--repo', '.']},
    {'key': 'agents-act', 'title': 'Agents Act. Systems Remember. Rules Authorize. People Govern.', 'subtitle': 'A Practical Architecture for Governed AI Agents', 'date': '2026/09/19', 'slug': 'agents-act-systems-remember-rules-authorize-people-govern', 'pdf': 'agents-act-systems-remember-rules-authorize-people-govern.pdf', 'pdf_sha256': '51987f1c4f6ce3cfe5511af0b367ef56086d1de0b68e13995231176ba700c214', 'validator': ['python3', 'scripts/validate_derivative.py', '--repo', '.']},
{'key': 'reasoning', 'title': 'When Reasoning Leaves the Transcript', 'subtitle': 'A Research Program for Hybrid Computation, Semantic Boundaries, and Consequential Agency', 'date': '2026/10/15', 'slug': 'when-reasoning-leaves-the-transcript', 'pdf': 'when-reasoning-leaves-the-transcript.pdf', 'pdf_sha256': '8dc68083df17ae51a7b6b8a2ab877bc7fd0814416bf33b5f15eb8142a9353fc8', 'validator': ['python3', 'scripts/validate_derivative.py', '--repo', '.']},
    {'key': 'questions', 'title': 'When Questions Become Markets', 'subtitle': 'AI, Evidence Discovery, and the Financing of New Observations', 'date': '2026/10/19', 'slug': 'when-questions-become-markets', 'pdf': 'when-questions-become-markets.pdf', 'pdf_sha256': 'd5667e31ab98eed51a4781fe745ff241ef319b3751e2cdb34edb23ca85ed3780', 'validator': ['python3', 'scripts/validate_derivative.py', '--repo', '.']},
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_paper(root: Path, spec: dict) -> dict:
    source = (root / "index.html").read_text(encoding="utf-8")
    page = html.fromstring(source.encode("utf-8"))
    article_url = f"https://bradpierce.ai/{spec['slug']}/"
    pdf_url = article_url + spec["pdf"]

    require(page.xpath('//meta[@name="citation_title"]/@content') == [spec["title"]], f"{spec['key']}: citation_title mismatch")
    require(page.xpath('//meta[@name="citation_author"]/@content') == ["Brad Pierce"], f"{spec['key']}: citation_author mismatch")
    require(page.xpath('//meta[@name="citation_publication_date"]/@content') == [spec["date"]], f"{spec['key']}: citation date mismatch")
    require(page.xpath('//meta[@name="citation_pdf_url"]/@content') == [pdf_url], f"{spec['key']}: citation_pdf_url mismatch")
    require(page.xpath('//meta[@name="citation_fulltext_html_url"]/@content') == [article_url], f"{spec['key']}: full-text URL mismatch")
    require(page.xpath('//link[@rel="canonical"]/@href') == [article_url], f"{spec['key']}: canonical URL mismatch")
    require(source.index('id="scholarly-front-matter"') < source.index('id="relevance-and-citation-scope"') < source.index('id="canonical-paper"'), f"{spec['key']}: page order mismatch")
    require("bradpierce-ai-eda.github.io" not in source, f"{spec['key']}: legacy host remains in index.html")

    front = page.xpath('//*[@id="scholarly-front-matter"]')
    require(len(front) == 1, f"{spec['key']}: scholarly front matter missing")
    front_text = " ".join(front[0].text_content().split())
    visible_title = spec.get("display_title", spec["title"])
    require(visible_title in front_text and spec.get("subtitle", "") in front_text and "Brad Pierce" in front_text and "Abstract" in front_text, f"{spec['key']}: incomplete visible front matter")

    pdf = root / spec["pdf"]
    require(pdf.stat().st_size < 5_000_000, f"{spec['key']}: PDF is not below 5 MB")
    require(sha256(pdf) == spec["pdf_sha256"], f"{spec['key']}: published PDF changed")
    reader = PdfReader(pdf)
    pdf_text = " ".join("\n".join((page.extract_text() or "") for page in reader.pages).split())
    require(visible_title in pdf_text and spec.get("subtitle", "") in pdf_text and "Brad Pierce" in pdf_text and ("references" in pdf_text.casefold() or "bibliography" in pdf_text.casefold()), f"{spec['key']}: PDF searchability check failed")

    proc = subprocess.run(spec["validator"], cwd=root, text=True, capture_output=True)
    require(proc.returncode == 0, f"{spec['key']}: repository validator failed\n{proc.stdout}\n{proc.stderr}")
    return {"title": spec["title"], "article_url": article_url, "pdf_url": pdf_url, "pdf_sha256": spec["pdf_sha256"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", type=Path, required=True)
    parser.add_argument("--staying-capable", type=Path, required=True)
    parser.add_argument("--design-exploration", type=Path, required=True)
    parser.add_argument("--intelligence", type=Path, required=True)
    parser.add_argument("--transitions", type=Path, required=True)
    parser.add_argument("--architecture", type=Path, required=True)
    parser.add_argument("--agents-act", type=Path, required=True)
    parser.add_argument("--external-analysis", type=Path, required=True)
    parser.add_argument("--reasoning", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--basalt", type=Path, required=True)
    parser.add_argument("--silicate", type=Path, required=True)
    parser.add_argument("--who-else", type=Path, required=True)
    parser.add_argument("--basalt-calcium", type=Path, required=True)
    args = parser.parse_args()

    home = args.home.resolve()
    home_source = (home / "index.html").read_text(encoding="utf-8")
    home_page = html.fromstring(home_source.encode("utf-8"))
    require(home_page.xpath('//link[@rel="canonical"]/@href') == ["https://bradpierce.ai/"], "Home canonical URL mismatch")
    require(not home_page.xpath('//meta[starts-with(@name, "citation_")]'), "Home page must not represent multiple papers as one scholarly record")
    require("bradpierce-ai-eda.github.io" not in home_source, "Legacy host remains in home page")

    roots = {
        "staying-capable": args.staying_capable.resolve(),
        "design-exploration": args.design_exploration.resolve(),
        "intelligence": args.intelligence.resolve(),
        "transitions": args.transitions.resolve(),
    }
    roots["architecture"] = args.architecture.resolve()
    roots["agents-act"] = args.agents_act.resolve()
    roots["external-analysis"] = args.external_analysis.resolve()
    roots["reasoning"] = args.reasoning.resolve()
    roots["questions"] = args.questions.resolve()
    roots["basalt"] = args.basalt.resolve()
    roots["silicate"] = args.silicate.resolve()
    roots["who-else"] = args.who_else.resolve()
    roots["basalt-calcium"] = args.basalt_calcium.resolve()
    results = [validate_paper(roots[spec["key"]], spec) for spec in PAPERS]

    sitemap = (home / "sitemap.xml").read_text(encoding="utf-8")
    robots = (home / "robots.txt").read_text(encoding="utf-8")
    require("Sitemap: https://bradpierce.ai/sitemap.xml" in robots, "Root robots.txt does not name the root sitemap")
    for result in results:
        require(result["article_url"] in home_source, f"Home page does not link to {result['article_url']}")
        require(result["pdf_url"] in home_source, f"Home page does not link to {result['pdf_url']}")
        require(result["article_url"] in sitemap and result["pdf_url"] in sitemap, f"Root sitemap is incomplete for {result['title']}")

    expected_order = ["When Design Exploration Gets Cheap", "Staying Capable in a World That Pushes Back", "Controlling Consequential Transitions", "Intelligence by Appointment", "The Architecture Is Old. The Computational Actor Is New.", "Agents Act. Systems Remember. Rules Authorize. People Govern.", "External Analysis of Protected Data", "When Reasoning Leaves the Transcript", "When Questions Become Markets", 'Basalt and Basalt-Derived Materials in Cement Manufacture and Cementitious Composites', 'Silicate Rocks and Mineral Residues as Sources of Cementitious Precursors', 'Who Else Wants to Know?', 'Basalt-Derived Calcium for Lower Carbon Portland Cement']
    require(home_page.xpath('//article/h3/text()') == expected_order, "Selected-paper ordering changed")
    from lxml import etree
    locs = etree.fromstring(sitemap.encode()).xpath('//*[local-name()="loc"]/text()')
    expected_urls = {"https://bradpierce.ai/"} | {r[k] for r in results for k in ("article_url", "pdf_url")}
    require(len(locs) == len(set(locs)) == 27 and set(locs) == expected_urls, "Sitemap does not exactly cover thirteen papers")
    require((home / "CNAME").read_text().strip() == "bradpierce.ai", "Custom domain changed")
    require(sha256(home / "googled0bbaedd4ac79dfb.html") == "8718036a2e6efadaa108f68526a22772d506c9b45b86fe9bd6a125e66eb41c85", "Permanent Google verification file changed")
    print(json.dumps({"status": "PASS", "home": "https://bradpierce.ai/", "papers": results}, indent=2))


if __name__ == "__main__":
    main()
