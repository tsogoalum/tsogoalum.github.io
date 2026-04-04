#!/usr/bin/env python3
"""
Convert Tsogo Alumni Society static HTML archive to Jekyll Markdown posts and pages.
Usage: python3 convert.py
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

from bs4 import BeautifulSoup
from markdownify import markdownify as md

DOCS_DIR = Path("../tsogo-static/docs")
POSTS_DIR = Path("_posts")
PAGES_DIR = Path("_pages")
ASSETS_DIR = Path("assets/images")

POSTS_DIR.mkdir(exist_ok=True)
PAGES_DIR.mkdir(exist_ok=True)


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text


def extract_post_meta(soup, url_path):
    """Extract title, date, categories, tags from a post HTML file."""
    meta = {
        "title": "",
        "date": "",
        "categories": [],
        "tags": [],
        "author": "Tsogo Alumni Society",
    }

    # Title
    title_el = soup.find("h1", class_="post-title") or soup.find("h2", class_="post-title")
    if title_el:
        a = title_el.find("a")
        meta["title"] = (a or title_el).get_text(strip=True)
    else:
        title_el = soup.find("title")
        if title_el:
            meta["title"] = title_el.get_text().split("–")[0].split("|")[0].strip()

    # Date — prefer <time> element, fall back to URL path /YYYY/MM/
    time_el = soup.find("time", class_="entry-date") or soup.find("time")
    if time_el and time_el.get("datetime"):
        raw = time_el["datetime"]
        try:
            meta["date"] = datetime.fromisoformat(raw[:10]).strftime("%Y-%m-%d")
        except ValueError:
            pass

    if not meta["date"]:
        # Fall back to year/month from URL path
        parts = str(url_path).split("/")
        year_parts = [p for p in parts if re.match(r"^20\d\d$", p)]
        month_parts = [p for p in parts if re.match(r"^\d{2}$", p)]
        if year_parts and month_parts:
            meta["date"] = f"{year_parts[0]}-{month_parts[0]}-01"
        elif year_parts:
            meta["date"] = f"{year_parts[0]}-01-01"

    # Categories
    cat_div = soup.find("p", class_="post-categories")
    if cat_div:
        meta["categories"] = [a.get_text(strip=True) for a in cat_div.find_all("a")]

    # Tags
    tag_div = soup.find("p", class_="post-tags") or soup.find(class_="tags-links")
    if tag_div:
        meta["tags"] = [a.get_text(strip=True) for a in tag_div.find_all("a")]

    return meta


def html_to_markdown(content_el):
    """Convert post content HTML element to clean Markdown."""
    if not content_el:
        return ""
    # Remove archive notice divs
    for el in content_el.find_all("div", class_="archive-notice"):
        el.decompose()
    # Remove WordPress sidebar widgets that leaked into entry-content
    for el in content_el.find_all("div", class_="widget"):
        el.decompose()
    # Remove script/style tags
    for el in content_el.find_all(["script", "style"]):
        el.decompose()
    # Fix image src paths — keep wp-content relative paths
    for img in content_el.find_all("img"):
        src = img.get("src", "")
        if src.startswith("http://tsogoalumni.org.za") or src.startswith("https://tsogoalumni.org.za"):
            img["src"] = "/" + src.split("tsogoalumni.org.za/", 1)[-1]
    html = str(content_el)
    text = md(html, heading_style="ATX", bullets="-", strip=["a"] if False else None)
    # Clean up excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def yaml_escape(s):
    """Escape a string for YAML front matter."""
    s = str(s).replace('"', '\\"')
    return f'"{s}"'


def write_post(meta, body, slug, output_path):
    date = meta["date"]
    title = yaml_escape(meta["title"])
    categories = meta["categories"]
    tags = meta["tags"]

    cats_str = ""
    if categories:
        cats_str = "\ncategories:\n" + "\n".join(f"  - {c}" for c in categories)

    tags_str = ""
    if tags:
        tags_str = "\ntags:\n" + "\n".join(f"  - {t}" for t in tags)

    front_matter = f"""---
title: {title}
date: {date}
author: "Tsogo Alumni Society"{cats_str}{tags_str}
layout: single
---

"""
    output_path.write_text(front_matter + body, encoding="utf-8")


def convert_posts():
    """Convert all year/month/slug/index.html blog posts."""
    year_dirs = sorted([d for d in DOCS_DIR.iterdir() if d.is_dir() and re.match(r"^20\d\d$", d.name)])
    converted = 0
    skipped = 0

    for year_dir in year_dirs:
        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir():
                continue
            for post_dir in sorted(month_dir.iterdir()):
                index_file = post_dir / "index.html"
                if not index_file.exists():
                    continue

                with open(index_file, encoding="utf-8", errors="replace") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")

                # Only process if it looks like a post (has post-content)
                content_el = soup.find("div", class_="entry-content") or soup.find("div", class_="post-content")
                if not content_el:
                    skipped += 1
                    continue

                meta = extract_post_meta(soup, index_file)
                if not meta["title"]:
                    meta["title"] = post_dir.name.replace("-", " ").title()

                body = html_to_markdown(content_el)
                if not body.strip():
                    skipped += 1
                    continue

                slug = post_dir.name
                date = meta["date"] or f"{year_dir.name}-01-01"
                filename = f"{date}-{slug}.md"
                output_path = POSTS_DIR / filename

                write_post(meta, body, slug, output_path)
                converted += 1
                print(f"  ✓ {filename}")

    print(f"\nPosts: {converted} converted, {skipped} skipped")
    return converted


def convert_static_page(html_path, output_filename, title_override=None, content_override=None, extra_front=None):
    """Convert a static HTML page to a Jekyll _pages Markdown file."""
    if content_override:
        body = content_override
        title = title_override or "Page"
    else:
        with open(html_path, encoding="utf-8", errors="replace") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        content_el = soup.find("div", class_="entry-content") or soup.find("div", class_="post-content")
        title = title_override
        if not title:
            t = soup.find("h1", class_="post-title") or soup.find("h2", class_="post-title") or soup.find("title")
            title = t.get_text().split("–")[0].split("|")[0].strip() if t else output_filename.replace(".md", "")
        body = html_to_markdown(content_el) if content_el else ""

    # Build front matter — extra_front can override default permalink
    permalink = f"/{output_filename.replace('.md', '/')}/"
    extra_items = {}
    if extra_front:
        extra_items.update(extra_front)
    if "permalink" in extra_items:
        permalink = extra_items.pop("permalink")
    extra = ""
    if extra_items:
        extra = "\n" + "\n".join(f"{k}: {v}" for k, v in extra_items.items())

    front_matter = f"""---
title: {yaml_escape(title)}
layout: single
permalink: {permalink}{extra}
---

"""
    out = PAGES_DIR / output_filename
    out.write_text(front_matter + body, encoding="utf-8")
    print(f"  ✓ _pages/{output_filename}")


def convert_pages():
    """Convert static pages to Jekyll _pages."""

    # About / Contact
    convert_static_page(
        DOCS_DIR / "about" / "index.html",
        "about.md",
        title_override="About",
    )

    # Current Learners
    convert_static_page(
        DOCS_DIR / "current-learners" / "index.html",
        "current-learners.md",
    )

    # Alumni Starter Pack
    convert_static_page(
        DOCS_DIR / "the-alumni-starter-pack" / "index.html",
        "alumni-starter-pack.md",
    )

    # Executive — replaced with generic hiatus version
    executive_content = """The Tsogo Alumni Society was governed by a volunteer Executive Committee (ExCo) elected by its members.

## Last Active Executive (2018/2019)

| Role | Name |
|------|------|
| President | Vukosi Marivate |
| Vice President | Moshabi Pitsoane |
| Treasurer | Thabiso Setshedi |
| School Liaison | Ntefeng Moloisane |
| Member | Omphile Sehoole |
| Member | Karabo Motswatswe |

## Previous Executives

**2016/2017**

Thato Mmaditla, Thabo Ncalo, Thabiso Setshedi, Karabo Motswatswe, Omphile Sehoole, Motlalepula Phakedi, Moshabi Pitsoane (Vice President), Vukosi Marivate (President)

**2015/2016**

Thabo Ncalo (President), Vukosi Marivate (Vice President), Motlalepula Phakedi, Omphile Sehoole, Karabo Motswatswe, Thabiso Setshedi, Thato Mmaditla

**2009/2010**

Ms. Motlalepula Phakedi — Chairperson, Mr. Pono Mogoera — Deputy Chairperson, Mr. Malebo Chadi CA (SA) — Treasurer, Mr. Thabo Ncalo — Secretary, Mr. Botshelo Letswalo & Mr. Kabelo Modikwe — Events, Mr. Moses Mokgoko & Mr. Prince Kotu — Projects, Ms. Thabiso Mokwena — Additional Member

---

*The Society has been on hiatus since 2020. We are grateful to all members who served on the Executive over the years.*
"""
    convert_static_page(
        None,
        "executive.md",
        title_override="Executive Committee",
        content_override=executive_content,
        extra_front={"permalink": "/society/executive/"},
    )

    # Society / About
    society_content = """The Tsogo Alumni Society was established to connect alumni of Tsogo High School (later Tsogo Secondary School) in Atteridgeville, Pretoria, South Africa.

## Our Mission

- Support current learners at Tsogo Secondary School
- Connect alumni with each other and with the school
- Run bursary and career development programmes
- Preserve the history and community of Tsogo

## NPO Registration

The Society is registered as a Non-Profit Organisation: **053-952-NPO**

## Status

The Tsogo Alumni Society has been **on hiatus since 2020**. This site is preserved as an archive of our activities from 2009 to 2020.

If you are a Tsogo alumnus and would like to help revive the Society, please use the contact details on the [About](/about/) page.
"""
    convert_static_page(
        None,
        "society.md",
        title_override="The Society",
        content_override=society_content,
        extra_front={"permalink": "/society/"},
    )

    print(f"\nPages converted.")


def main():
    print("=== Converting blog posts ===")
    convert_posts()
    print("\n=== Converting static pages ===")
    convert_pages()
    print("\nDone. Run `bundle exec jekyll serve` to preview.")


if __name__ == "__main__":
    main()
