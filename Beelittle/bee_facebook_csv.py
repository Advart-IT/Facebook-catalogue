# generate_facebook_feed.py
import csv
import os
import math
import urllib.parse
import pandas as pd
from items.aalam_fetcher import fetch_items
from items.config import BUSINESS_CONFIG

FACEBOOK_COLS = [
    'id', 'title', 'description', 'availability', 'condition',
    'link', 'image_link', 'brand', 'google_product_category',
    'fb_product_category', 'sale price', 'price'
]

def coalesce(*vals):
    for v in vals:
        if v is not None and v != "" and not (isinstance(v, float) and math.isnan(v)):
            return v
    return None

def to_float(x, default=0.0):
    try:
        if x is None or x == "" or (isinstance(x, float) and math.isnan(x)):
            return default
        return float(x)
    except Exception:
        return default

def build_title(name, subtitle):
    parts = [p for p in [name, subtitle] if p]
    return "-".join(parts)

def ensure_scheme(url_or_domain):
    if url_or_domain.startswith("http://") or url_or_domain.startswith("https://"):
        return url_or_domain
    return f"https://{url_or_domain}"

def main(business_name):
    if business_name not in BUSINESS_CONFIG:
        raise KeyError(f"Business '{business_name}' not found in BUSINESS_CONFIG keys: {list(BUSINESS_CONFIG.keys())}")

    bcfg = BUSINESS_CONFIG[business_name]
    host = bcfg.get("url")
    token = bcfg.get("auth_token")
    if not host or not token:
        raise ValueError(f"'url' and 'auth_token' are required for {business_name}")

    domain = bcfg.get("domain")
    brand  = bcfg.get("brand") or business_name.title()

    if domain:
        domain = ensure_scheme(domain)
    else:
        domain = ensure_scheme(host)

    df = fetch_items(host, token)

    def _normalize(s):
        return "".join(ch.lower() for ch in str(s) if ch.isalnum())

    col_map = { _normalize(c): c for c in df.columns }

    def col(df, name, idx=None):
        n = _normalize(name)
        if n in col_map:
            return df[col_map[n]]
        for k, orig in col_map.items():
            if n in k or k in n:
                return df[orig]
        if idx is not None and idx < df.shape[1]:
            return df.iloc[:, idx]
        return pd.Series([None]*len(df))

    c_id       = col(df, "ID", 0)
    c_name     = col(df, "Name", 1)
    c_type     = col(df, "Type", 2)
    c_sku      = col(df, "SKU", 3)
    c_price    = col(df, "Price", 4)
    c_discount = col(df, "Discount", 5)
    c_stock    = col(df, "Stock", 11)
    c_subtitle = col(df, "Subtitle", 12)

    rows_out = []
    for i in range(len(df)):
        _id       = coalesce(c_id.iloc[i])
        name      = coalesce(c_name.iloc[i], "")
        subtitle  = coalesce(c_subtitle.iloc[i], "")
        _type     = coalesce(c_type.iloc[i], "")
        sku       = coalesce(c_sku.iloc[i], "")
        price     = to_float(c_price.iloc[i], 0.0)
        discount  = to_float(c_discount.iloc[i], None)  # keep None if no discount
        stock     = to_float(c_stock.iloc[i], 0.0)

        title = build_title(name, subtitle)
        description = title
        availability = "in stock" if stock > 0 else "out of stock"
        condition = "new"

        # Price (original)
        price_str = f"{round(price, 2)} INR" if price else ""

        # Sale price (only if discount is present)
        if discount is not None:
            sale_price_val = round(price * (1 - (discount or 0)/100.0), 2)
            sale_price_str = f"{sale_price_val} INR"
        else:
            sale_price_str = ""

        link = f"{domain}/store/item/{urllib.parse.quote_plus(str(name))}?id={_id}"
        image_link = f"{domain}/aalam/stock/item/{_id}/image/_/face-img"

        rows_out.append([
            sku,  # id
            title,
            description,
            availability,
            condition,
            link,
            image_link,
            brand,
            "Apparel & Accessories > Clothing",
            "Clothing & Accessories > Clothing",
            sale_price_str,
            price_str
        ])

    out_path = f"{business_name}_facebook_catalog.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FACEBOOK_COLS)
        writer.writerows(rows_out)

    print(f"Done. Wrote {len(rows_out)} rows to {out_path}")

if __name__ == "__main__":
    main("beelittle")
