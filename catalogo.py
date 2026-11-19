"""Scraping and preparation helpers for the books.toscrape.com lab."""

from __future__ import annotations

import time
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "UCJC-Lab1-BookCatalog/1.0 (educational project)"}
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
RAW_COLUMNS = [
    "title",
    "price_text",
    "rating_text",
    "availability_text",
    "category",
    "product_url",
]


def _get_soup(
    session: requests.Session, url: str, delay: float
) -> BeautifulSoup:
    """Fetch one page with an identifying User-Agent and a polite delay."""
    time.sleep(delay)
    response = session.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def scrape_catalogue(
    output_path: str | Path = "data/raw/libros_raw.csv",
    delay: float = 0.25,
) -> pd.DataFrame:
    """Scrape every category and its paginated listings into a raw CSV."""
    if delay < 0:
        raise ValueError("delay debe ser mayor o igual que cero")

    session = requests.Session()
    home = _get_soup(session, BASE_URL, delay)
    categories = home.select(".side_categories ul ul a")
    if not categories:
        raise RuntimeError("No se encontraron categorías en la página principal.")

    books: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    for category_link in categories:
        category = category_link.get_text(strip=True)
        next_url = urljoin(BASE_URL, category_link["href"])
        visited_pages: set[str] = set()

        while next_url:
            if next_url in visited_pages:
                raise RuntimeError(f"Paginación repetida detectada: {next_url}")
            visited_pages.add(next_url)
            page = _get_soup(session, next_url, delay)

            for product in page.select("article.product_pod"):
                title_link = product.select_one("h3 a")
                price = product.select_one(".price_color")
                rating = product.select_one(".star-rating")
                availability = product.select_one(".availability")
                if not all((title_link, price, rating, availability)):
                    continue

                product_url = urljoin(next_url, title_link["href"])
                if product_url in seen_urls:
                    continue
                seen_urls.add(product_url)
                books.append(
                    {
                        "title": title_link.get("title", title_link.get_text(strip=True)),
                        "price_text": price.get_text(strip=True),
                        "rating_text": next(
                            (name for name in rating.get("class", []) if name in RATINGS),
                            "",
                        ),
                        "availability_text": " ".join(
                            availability.stripped_strings
                        ),
                        "category": category,
                        "product_url": product_url,
                    }
                )

            next_link = page.select_one("li.next a")
            next_url = urljoin(next_url, next_link["href"]) if next_link else ""

    if not books:
        raise RuntimeError("El scraping no obtuvo libros.")

    raw = pd.DataFrame(books, columns=RAW_COLUMNS)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(destination, index=False, encoding="utf-8")
    return raw


def clean_catalogue(raw: pd.DataFrame) -> pd.DataFrame:
    """Convert scraped strings to analysis-ready numeric columns."""
    required = set(RAW_COLUMNS)
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"Faltan columnas en los datos: {', '.join(sorted(missing))}")

    clean = raw.drop_duplicates(subset="product_url").copy()
    clean["price_gbp"] = pd.to_numeric(
        clean["price_text"].str.replace(r"[^\d.]", "", regex=True),
        errors="coerce",
    )
    clean["rating"] = clean["rating_text"].map(RATINGS)
    clean["available"] = clean["availability_text"].str.contains(
        "In stock", case=False, na=False
    )
    clean = clean.dropna(subset=["title", "price_gbp", "rating", "category"])
    clean["rating"] = clean["rating"].astype("int64")
    return clean[
        [
            "title",
            "price_gbp",
            "rating",
            "category",
            "available",
            "product_url",
        ]
    ].reset_index(drop=True)
