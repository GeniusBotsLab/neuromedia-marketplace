#!/usr/bin/env python3
"""Create a safe, complete public catalog snapshot from the live public API."""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://neuromedia.cloud"
PRODUCTS = f"{BASE}/api/v1/products?sort=newest&page=1&per_page=100"
CATEGORIES = f"{BASE}/api/v1/categories"


def fetch(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "Neuromedia-Public-Catalog-Exporter/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def localized(item: dict, key: str, locale: str) -> str:
    value = item.get(f"{key}_i18n", {}).get(locale) or item.get(key) or ""
    return " ".join(str(value).split())


def category_record(category: dict, locale: str) -> dict:
    return {
        "slug": category["slug"],
        "name": localized(category, "name", locale),
        "description": localized(category, "short_description", locale),
    }


def product_record(product: dict, locale: str) -> dict:
    category = product["category"]
    category_slug = category["slug"]
    return {
        "slug": product["slug"],
        "name": localized(product, "name", locale),
        "category": category_slug,
        "price_usd": float(product["sale_price"] or product["price"]),
        "price_display": f"{float(product['sale_price'] or product['price']):g} USD",
        "availability": "in_stock" if product.get("stock") is None or product["stock"] > 0 else "out_of_stock",
        "delivery": "subscription" if product["delivery_type"] == "subscription" else "manual",
        "url": f"{BASE}/catalog/{category_slug}/{product['slug']}",
        "summary": localized(product, "short_description", locale),
    }


def main() -> None:
    products_payload = fetch(PRODUCTS)
    products = products_payload["items"]
    if products_payload["total"] != len(products):
        raise RuntimeError("Public API did not return the full product list")
    roots = fetch(CATEGORIES)
    category_by_slug = {}
    for root in roots:
        category_by_slug[root["slug"]] = root
        for child in root.get("children", []):
            category_by_slug[child["slug"]] = child
    # The product response carries the public category data even when that
    # category is not nested in the navigation endpoint.
    for product in products:
        category_by_slug.setdefault(product["category"]["slug"], product["category"])
    used_categories = {product["category"]["slug"] for product in products}
    if not used_categories <= set(category_by_slug):
        raise RuntimeError("A public product refers to an unknown category")
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    out_dir = Path("content/catalog")
    for locale in ("ru", "en"):
        catalog = {
            "$schema": "../meta/catalog.schema.json",
            "catalog_version": "1.1",
            "locale": locale,
            "source": BASE,
            "generated_at": generated_at,
            "disclaimer": "Публичный справочный срез. Актуальные цена, доступность и условия — на странице товара в магазине." if locale == "ru" else "A public informational snapshot. Confirm current price, availability, and terms on the live marketplace product page.",
            "categories": [category_record(category_by_slug[slug], locale) for slug in sorted(used_categories)],
            "featured_products": [product_record(product, locale) for product in products],
        }
        (out_dir / f"catalog.{locale}.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {locale}: {len(catalog['categories'])} categories, {len(catalog['featured_products'])} products")


if __name__ == "__main__":
    main()
