from __future__ import annotations
from lxml import etree
from pathlib import Path

def join_text_parts(parts: list[str]) -> str:
    """Join a list of text parts into a single string."""
    text = " ".join([part.strip() for part in parts if part.strip()])
    return " ".join(text.split())

def parse_xml(file_path: Path) -> dict:
    """Parse an XML file and return a dictionary of the data."""
    file_path = Path(str(file_path))
    tree = etree.parse(file_path)
    root = tree.getroot()
    abstract_parts = root.xpath("//abstract//text()")
    print("Abstract found:", len(abstract_parts))
    pmcid = root.find(".//article-id[@pub-id-type='pmcid']").text
    pmcid_ver = root.find(".//article-id[@pub-id-type='pmcid-ver']").text
    pmid = root.find(".//article-id[@pub-id-type='pmid']").text
    title = root.find(".//article-title").text
    journal_title = root.find(".//journal-title").text
    year = root.find(".//pub-date[@pub-type='ppub']/year").text
    month = root.find(".//pub-date[@pub-type='ppub']/month").text
    article_type = root.attrib.get("article-type")
    scanned_value = root.xpath(
        "//custom-meta[@meta-name='pmc-prop-is-scanned-article']/@meta-value/text()"
    )
    if scanned_value:
        is_scanned = scanned_value[0].lower() == "yes"
    else:
        is_scanned = False
    license_value = root.xpath(
        "//custom-meta[@meta-name='pmc-license-ref']/@meta-value/text()"
    )
    if license_value:
        license = license_value[0]
    else:
        license = None
    ocr_parts = root.xpath("//custom-meta[@meta-name='pmc-prop-is-ocr-article']/@meta-value/text()")
    if ocr_parts:
        is_ocr = ocr_parts[0].lower() == "yes"
    else:
        is_ocr = False
    body_parts = root.xpath("//body//text()")
    body = join_text_parts(body_parts)
    # print(body_parts)
        
    
    return {
        "pmcid": pmcid,
        "pmcid_ver": pmcid_ver,
        "pmid": pmid,
        "title": title,
        "journal_title": journal_title,
        "year": year,
        "month": month,
        "article_type": article_type,
        "is_scanned": is_scanned,
        "license": license,
        "source": {
            "provider": "PMC",
            "s3_prefix": pmcid_ver,
            "xml_filename": file_path.name,
        },
        "body": body,
    }

print(parse_xml(Path("data/pmc_sample/PMC10000003.1.xml")))