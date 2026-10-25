#!/usr/bin/env python3
"""For the teaching team, not used by the routines: make tools/sample_data/ from a set of saved SEC answers.

    python3 tools/earnings.py watch --save-raw /tmp/sec_raw
    python3 tools/earnings.py assess --save-raw /tmp/sec_raw
    python3 _dev/make_sample_data.py /tmp/sec_raw

It trims each answer so the folder stays small, and keeps every word the tool reads:
- the filings lists keep only 8-K, 10-Q and 10-K filings;
- the company facts keep only the five tags the assessor reads, from 2025 onwards;
- the full-text search answer (the earnings radar) keeps its hits and drops the search's own counts by category;
- the press releases lose their layout (style, class, width and similar attributes, images, span and font tags),
  and the script checks that the plain text the tool makes from each one is exactly the same as before;
- the filing indexes are copied as they are.
Python 3.9+ standard library only.
"""

import importlib.util
import json
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "tools", "sample_data")
TAGS = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "OperatingIncomeLoss", "NetIncomeLoss",
        "EarningsPerShareDiluted"]
FORMS = {"8-K", "10-Q", "10-K"}
KEEP_FILINGS = 20
FACTS_FROM = "2025-01-01"
LAYOUT = re.compile(r"""\s(?:style|class|id|width|height|align|valign|bgcolor|border|cellpadding|cellspacing|"""
                    r"""colspan|rowspan)\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""", re.I)


def load_tool():
    spec = importlib.util.spec_from_file_location("earnings", os.path.join(HERE, "tools", "earnings.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def note(path):
    saved = datetime.fromtimestamp(os.path.getmtime(path), timezone(timedelta(hours=8))).strftime("%d %B %Y, %H:%M")
    return f"Trimmed copy of an SEC EDGAR answer saved on {saved} Singapore time, for --offline tests."


def trim_submissions(data, path):
    recent = data["filings"]["recent"]
    keep = [i for i, f in enumerate(recent["form"]) if f in FORMS][:KEEP_FILINGS]
    return {"_note": note(path), "cik": data.get("cik"), "entityType": data.get("entityType"),
            "name": data.get("name"), "tickers": data.get("tickers"), "exchanges": data.get("exchanges"),
            "fiscalYearEnd": data.get("fiscalYearEnd"),
            "filings": {"recent": {k: [v[i] for i in keep] for k, v in recent.items() if isinstance(v, list)},
                        "files": []}}


def trim_facts(data, path):
    gaap = data.get("facts", {}).get("us-gaap", {})
    out = {}
    for tag in TAGS:
        if tag in gaap:
            units = {u: [r for r in rows if str(r.get("end", "")) >= FACTS_FROM]
                     for u, rows in gaap[tag].get("units", {}).items()}
            out[tag] = {"label": gaap[tag].get("label"), "units": units}
    return {"_note": note(path), "cik": data.get("cik"), "entityName": data.get("entityName"),
            "facts": {"us-gaap": out}}


def trim_search(data, path):
    return {"_note": note(path) + " The tool keeps the hits whose filing dates fall in the morning's window.",
            "hits": data.get("hits")}


def trim_html(tool, raw, name):
    html = tool.decode_text(raw)
    trimmed = LAYOUT.sub("", html)
    trimmed = re.sub(r"<img\b[^>]*>|</?(?:span|font)\b[^>]*>", "", trimmed, flags=re.I)
    trimmed = re.sub(r"[ \t]*\n\s*", "\n", trimmed)
    if tool.html_to_text(trimmed, name) != tool.html_to_text(html, name):
        print("  the trimmed text differs, so", name, "is copied as it is")
        return raw
    return trimmed.encode("utf-8")


def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        sys.exit("Usage: python3 _dev/make_sample_data.py <folder of saved SEC answers>")
    tool = load_tool()
    os.makedirs(OUT, exist_ok=True)
    for name in sorted(os.listdir(sys.argv[1])):
        src = os.path.join(sys.argv[1], name)
        dst = os.path.join(OUT, name)
        if name.startswith("data.sec.gov_submissions_"):
            data = trim_submissions(json.load(open(src, encoding="utf-8")), src)
        elif name.startswith("data.sec.gov_api_xbrl_companyfacts_"):
            data = trim_facts(json.load(open(src, encoding="utf-8")), src)
        elif name.startswith("efts.sec.gov_"):
            data = trim_search(json.load(open(src, encoding="utf-8")), src)
        elif re.search(r"\.html?$", name, re.I):
            with open(src, "rb") as fh:
                body = trim_html(tool, fh.read(), name)
            with open(dst, "wb") as fh:
                fh.write(body)
            print("trimmed", name, os.path.getsize(src), "->", os.path.getsize(dst), "bytes")
            continue
        else:
            shutil.copyfile(src, dst)
            print("copied ", name, os.path.getsize(dst), "bytes")
            continue
        with open(dst, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print("trimmed", name, os.path.getsize(src), "->", os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    main()
