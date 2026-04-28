# generate_facebook_feed.py
import csv
import os
import math
import urllib.parse
import pandas as pd
from items.aalam_fetcher import fetch_items
from items.config import BUSINESS_CONFIG
CUSTOM_TYPE_MAP = {
    "Exp-Dress": "Apparel & Accessories > Clothing > Dresses",
    "Exp-Aline-Dress": "Apparel & Accessories > Clothing > Dresses",
    "New-Exp-Dress": "Apparel & Accessories > Clothing > Dresses",
    "Exp-Co-ord Set": "Apparel & Accessories > Clothing > Outfit Sets",
    "Exp-Aline-Co-ord Set": "Apparel & Accessories > Clothing > Outfit Sets",
    "MTO-Co-ord Set": "Apparel & Accessories > Clothing > Outfit Sets",
    "MTO-Aline-Co-ord Set": "Apparel & Accessories > Clothing > Outfit Sets",
    "New-Exp-Co-ord Set": "Apparel & Accessories > Clothing > Outfit Sets",
    "New-Exp-Aline-Co-ord Set": "Apparel & Accessories > Clothing > Outfit Sets",
    "New-MTO-Aline-Co-ord Set": "Apparel & Accessories > Clothing > Outfit Sets",
    "New-MTO-Co-ord Set": "Apparel & Accessories > Clothing > Outfit Sets",
    "Exp-Kurta": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "Exp-Aline-Kurta": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "MTO-Kurta": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "MTO-Aline-Kurta": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "New-MTO-Aline-Kurta": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "New-Exp-Kurta": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "New-Exp-Aline-Kurta": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "Exp-Kurta Set": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "Exp-Aline-Kurta Set": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "MTO-Aline-Kurta Set": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "New-Exp-Kurta Set": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "New-Exp-Aline-Kurta Set": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "New-MTO-Aline-Kurta Set": "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing",
    "Exp-Pant": "Apparel & Accessories > Clothing > Pants",
    "Dupatta": "Apparel & Accessories > Clothing Accessories > Scarves & Shawls",
    "Duppata": "Apparel & Accessories > Clothing Accessories > Scarves & Shawls",
    "New-Top": "Apparel & Accessories > Clothing > Shirts & Tops",
    "Pyjamas": "Apparel & Accessories > Clothing > Sleepwear & Loungewear > Pajamas",
    "Shorts Set": "Apparel & Accessories > Clothing > Outfit Sets",
}
FACEBOOK_COLS = [
    'id', 'title', 'description', 'availability', 'condition',
    'link', 'image_link', 'brand', 'color', 'material', 'pattern', 'size',
    'google_product_category', 'fb_product_category', 'gender', 'age_group',
    'sale price', 'price'
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
    brand  = bcfg.get("brand") or business_name.title()

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

    # base fields (same as your earlier script)
    c_id       = col(df, "ID", 0)
    c_name     = col(df, "Name", 1)
    c_type     = col(df, "Type", 2)
    c_sku      = col(df, "SKU", 3)              # used as 'id' in output (unchanged)
    c_price    = col(df, "Price", 4)            # original price
    c_discount = col(df, "Discount", 5)         # for sale price
    c_stock    = col(df, "Stock", 11)
    c_subtitle = col(df, "Subtitle", 12)

    # new mappings
    c_color    = col(df, "PROPERTY:Colour")
    c_material = col(df, "PROPERTY:Fabric")
    c_pattern  = col(df, "PROPERTY:Print")
    c_size     = col(df, "PROPERTY:Size")

    rows_out = []
    for i in range(len(df)):
        _id       = coalesce(c_id.iloc[i])
        name      = coalesce(c_name.iloc[i])
        _type     = str(coalesce(c_type.iloc[i], "")).strip()
        subtitle  = coalesce(c_subtitle.iloc[i])
        sku       = coalesce(c_sku.iloc[i])

        price     = to_float(c_price.iloc[i], 0.0)
        discount  = to_float(c_discount.iloc[i], None)
        stock     = to_float(c_stock.iloc[i], 0.0)

        title = build_title(name, subtitle)
        description = title
        availability = "in stock" if stock > 0 else "out of stock"
        condition = "new"
        google_product_category = CUSTOM_TYPE_MAP.get(_type, "Apparel & Accessories > Clothing")

        price_str = f"{round(price, 2)} INR" if price else "0.00 INR"
        sale_price_str = f"{round(price * (1 - (discount or 0)/100.0), 2)} INR" if discount is not None else ""

        link = f"{domain}/store/item/{urllib.parse.quote_plus(str(name))}?id={_id}"
        image_link = f"{domain}/aalam/stock/item/{_id}/image/_/face-img"

        color    = coalesce(c_color.iloc[i])
        material = coalesce(c_material.iloc[i])
        pattern  = coalesce(c_pattern.iloc[i])
        size     = coalesce(c_size.iloc[i])

        rows_out.append([
            sku,                                 
            title,                               
            description,                         
            availability,                        
            condition,                           
            link,                                
            image_link,                          # image_link
            brand,                               # brand (same behavior as before)
            color,                               # color -> PROPERTY:Colour
            material,                            # material -> PROPERTY:Fabric
            pattern,                             # pattern -> PROPERTY:Print
            size,                                # size -> PROPERTY:Size
            google_product_category,             # google_product_category
            "Clothing & Accessories > Clothing", # fb_product_category
            "Female",                            # gender
            "adult",                             # age_group
            sale_price_str,                      # sale price
            price_str                            # price
        ])

    out_path = f"{business_name}_facebook_catalog.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FACEBOOK_COLS)
        writer.writerows(rows_out)

    print(f"Done. Wrote {len(rows_out)} rows to {out_path}")

if __name__ == "__main__":
    main("prathiksham")
