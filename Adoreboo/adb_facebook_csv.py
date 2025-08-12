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
    'fb_product_category', 'price', 'color', 'pattern', 'size', 'material'
]

def coalesce(*vals):
    for v in vals:
        if v is not None and v != "" and not (isinstance(v, float) and math.isnan(v)):
            return v
    return ""

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
    if url_or_domain.startswith(("http://", "https://")):
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

    domain = ensure_scheme(bcfg.get("domain") or host)

    df = fetch_items(host, token)
    # print(df.columns)  # uncomment if you want to inspect headers

    def col(df, name, idx=None):
        if name in df.columns:
            return df[name]
        elif idx is not None and idx < df.shape[1]:
            return df.iloc[:, idx]
        else:
            return pd.Series([None]*len(df))

    # Base fields (keep same mapping you had)
    c_id       = col(df, "ID", 0)
    c_name     = col(df, "Name", 1)
    c_type     = col(df, "Type", 2)
    c_sku      = col(df, "SKU", 3)
    c_price    = col(df, "Price", 4)
    c_discount = col(df, "Discount", 5)     # not used for sale price now, but kept in case needed
    c_stock    = col(df, "Stock", 11)
    c_subtitle = col(df, "Subtitle", 12)

    # New mapped attributes
    c_color    = col(df, "PROPERTY:Colour")
    c_pattern  = col(df, "PROPERTY:Print Collections")
    c_size     = col(df, "PROPERTY:Age")

    rows_out = []
    for i in range(len(df)):
        _id       = coalesce(c_id.iloc[i])
        name      = coalesce(c_name.iloc[i])
        subtitle  = coalesce(c_subtitle.iloc[i])
        sku       = coalesce(c_sku.iloc[i])
        price     = to_float(c_price.iloc[i], 0.0)
        stock     = to_float(c_stock.iloc[i], 0.0)

        title = build_title(name, subtitle)
        description = title  # keep same as before
        availability = "in stock" if stock > 0 else "out of stock"
        condition = "new"

        price_str = f"{round(price, 2)} INR" if price else ""

        link = f"{domain}/store/item/{urllib.parse.quote_plus(str(name))}?id={_id}"
        image_link = f"{domain}/aalam/stock/item/{_id}/image/_/face-img"

        color   = coalesce(c_color.iloc[i])
        pattern = coalesce(c_pattern.iloc[i])
        size    = coalesce(c_size.iloc[i]) or "Free Size"
        material = "Cotton"

        rows_out.append([
            sku,                                  # id (kept as SKU; swap to _id if you prefer)
            title,                                # title
            description,                          # description
            availability,                         # availability
            condition,                            # condition
            link,                                 # link
            image_link,                           # image_link
            "adoreboo",                           # brand (fixed)
            "Apparel & Accessories > Clothing",   # google_product_category
            "Clothing & Accessories > Clothing",  # fb_product_category
            price_str,                            # price
            color,                                # color (PROPERTY:Colour)
            pattern,                              # pattern (PROPERTY:Print Collections)
            size,                                 # size (PROPERTY:Age, default Free Size)
            material                              # material (always Cotton)
        ])

    out_path = f"{business_name}_facebook_catalog.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FACEBOOK_COLS)
        writer.writerows(rows_out)

    print(f"Done. Wrote {len(rows_out)} rows to {out_path}")

if __name__ == "__main__":
    main("adoreaboo")  # change if needed
