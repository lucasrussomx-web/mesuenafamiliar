#!/usr/bin/env python3
"""
Agrega un artículo de LinkedIn a web/articulos.json.
Uso:  python scripts/update_articles.py <url_del_articulo>
"""

import json
import sys
import os
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Instalá las dependencias: pip install requests beautifulsoup4")
    sys.exit(1)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

MAX_ARTICLES = 3
JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "web", "articulos.json")


def fetch_metadata(url: str) -> dict:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    def og(prop: str) -> str:
        tag = soup.find("meta", property=f"og:{prop}")
        return (tag.get("content") or "").strip() if tag else ""

    def meta(name: str) -> str:
        tag = soup.find("meta", attrs={"name": name})
        return (tag.get("content") or "").strip() if tag else ""

    title = og("title") or (soup.title.get_text(strip=True) if soup.title else "")
    description = og("description") or meta("description") or ""
    image = og("image") or ""

    # Fecha de publicación
    pub_tag = soup.find("meta", property="article:published_time")
    if pub_tag and pub_tag.get("content"):
        pub_date = pub_tag["content"][:10]
    else:
        pub_date = datetime.now().strftime("%Y-%m-%d")

    return {
        "titulo": title,
        "descripcion": description,
        "fecha": pub_date,
        "url": url,
        "imagen": image,
    }


def update_articles(url: str) -> None:
    json_path = os.path.normpath(JSON_PATH)

    with open(json_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    if any(a.get("url") == url for a in articles):
        print(f"El artículo ya existe en articulos.json: {url}")
        return

    print(f"Obteniendo metadatos de: {url}")
    article = fetch_metadata(url)

    articles.insert(0, article)
    articles = articles[:MAX_ARTICLES]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"✓ Artículo agregado: {article['titulo']}")
    print(f"  Fecha:  {article['fecha']}")
    print(f"  Imagen: {article['imagen'][:80]}{'...' if len(article['imagen']) > 80 else ''}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/update_articles.py <url_del_articulo_linkedin>")
        sys.exit(1)

    update_articles(sys.argv[1].strip())
