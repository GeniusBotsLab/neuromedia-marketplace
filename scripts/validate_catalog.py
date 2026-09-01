#!/usr/bin/env python3
"""Validate a public Neuromedia catalog snapshot without external dependencies."""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, cast

Catalog = dict[str, Any]
from urllib.parse import urlparse

SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|secret|token|password|authorization|bearer|private[_-]?key)")
ALLOWED_AVAILABILITY = {"in_stock", "out_of_stock", "on_request"}
ALLOWED_DELIVERY = {"subscription", "manual", "digital", "service"}


def fail(message: str) -> None:
    raise ValueError(message)


def allowed_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.netloc == "neuromedia.cloud"


def validate_catalog(data: object) -> None:
    if not isinstance(data, dict):
        fail("Catalog root must be an object")
    catalog = cast(Catalog, data)
    for field in ("catalog_version", "locale", "source", "generated_at", "categories", "featured_products"):
        if field not in catalog:
            fail(f"Missing required field: {field}")
    if catalog["locale"] not in {"ru", "en"}:
        fail("locale must be ru or en")
    if not allowed_url(catalog["source"]):
        fail("source must be an HTTPS neuromedia.cloud URL")
    datetime.fromisoformat(catalog["generated_at"].replace("Z", "+00:00"))
    if not isinstance(catalog["categories"], list) or not isinstance(catalog["featured_products"], list):
        fail("categories and featured_products must be arrays")

    category_slugs = set()
    for category in catalog["categories"]:
        if set(category) - {"slug", "name", "description"}:
            fail("Category contains a non-public field")
        if not all(isinstance(category.get(k), str) and category[k] for k in ("slug", "name", "description")):
            fail("Every category needs non-empty slug, name, and description")
        if not re.fullmatch(r"[a-z0-9-]+", category["slug"]):
            fail("Invalid category slug")
        category_slugs.add(category["slug"])

    for product in catalog["featured_products"]:
        allowed = {"slug", "name", "category", "price_usd", "price_display", "availability", "delivery", "url", "summary"}
        if set(product) - allowed:
            fail("Product contains a non-public field")
        required = {"slug", "name", "category", "price_usd", "availability", "delivery", "url", "summary"}
        if not required <= set(product):
            fail("Product is missing a required public field")
        if not isinstance(product["price_usd"], (int, float)) or isinstance(product["price_usd"], bool) or product["price_usd"] < 0:
            fail("price_usd must be a non-negative number")
        if product["category"] not in category_slugs:
            fail("Product category is absent from categories")
        if product["availability"] not in ALLOWED_AVAILABILITY or product["delivery"] not in ALLOWED_DELIVERY:
            fail("Invalid availability or delivery")
        if not allowed_url(product["url"]):
            fail("Product URL must be an HTTPS neuromedia.cloud URL")
        if not all(isinstance(product.get(k), str) and product[k] for k in ("slug", "name", "summary")):
            fail("Product slug, name, and summary must be non-empty strings")

    rendered = json.dumps(catalog, ensure_ascii=False)
    if SECRET_PATTERN.search(rendered):
        fail("Secret-like field/value detected")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_catalog.py PATH", file=sys.stderr)
        sys.exit(2)
    try:
        payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        validate_catalog(payload)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        sys.exit(1)
    print(f"Valid public catalog: {sys.argv[1]}")
