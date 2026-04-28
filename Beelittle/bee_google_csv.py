# generate_facebook_feed.py
import csv
import os
import math
import urllib.parse
import pandas as pd
from items.aalam_fetcher import fetch_items
from items.config import BUSINESS_CONFIG

ITEM_TYPE_TO_CATEGORY = {
    "A-Line Frock": "Apparel & Accessories > Clothing > Dresses",
    "Alia Cut": "Apparel & Accessories > Clothing > Dresses",
    "Applique Jabla": "Apparel & Accessories > Clothing > Baby Clothing",
    "Baby Briefs": "Apparel & Accessories > Clothing > Baby Clothing",
    "Bandana Bib": "Apparel & Accessories > Clothing > Baby Clothing",
    "Bed Protector": "Apparel & Accessories > Bedding",
    "Bed with Net": "Apparel & Accessories > Bedding",
    "Bio-safe Diapers": "Apparel & Accessories > Baby Clothing > Diapers",
    "Brush And Comb Set": "Health & Beauty > Personal Care > Hair Care",
    "Burp Cloth": "Apparel & Accessories > Baby Clothing",
    "Butterfly Frock": "Apparel & Accessories > Clothing > Dresses",
    "Carry Nest": "Apparel & Accessories > Baby Clothing",
    "Changing Mat": "Apparel & Accessories > Baby Clothing",
    "Cloth Diapers": "Apparel & Accessories > Baby Clothing > Diapers",
    "Co-ord Sets": "Apparel & Accessories > Clothing",
    "Collar Frock": "Apparel & Accessories > Clothing > Dresses",
    "Combo Pant": "Apparel & Accessories > Clothing > Pants",
    "Cotton Cap Mittens and Booties": "Apparel & Accessories > Baby Clothing",
    "Cotton Joggers": "Apparel & Accessories > Clothing > Pants",
    "Cotton Kimono Sweater and Pant": "Apparel & Accessories > Clothing",
    "Cotton Mittens": "Apparel & Accessories > Baby Clothing",
    "Cotton Socks": "Apparel & Accessories > Clothing > Socks",
    "Cotton Stuffed Toys": "Toys & Games > Stuffed Toys",
    "Cotton Wrap Bed": "Apparel & Accessories > Bedding",
    "Crinkle Frock": "Apparel & Accessories > Clothing > Dresses",
    "Crinkled Set": "Apparel & Accessories > Clothing",
    "Cut and Sew Frock": "Apparel & Accessories > Clothing > Dresses",
    "Dhoti": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Diaper Caddy": "Apparel & Accessories > Baby Clothing > Diapers",
    "Dohar": "Apparel & Accessories > Bedding",
    "Dungaree Frock": "Apparel & Accessories > Clothing > Dresses",
    "Dungarees": "Apparel & Accessories > Clothing",
    "Feeding Apron": "Apparel & Accessories > Baby Clothing",
    "Feeding Pillow": "Apparel & Accessories > Baby Clothing",
    "Frock Triple Cloth Collection": "Apparel & Accessories > Clothing > Dresses",
    "FrockFS Triple Cloth Collection": "Apparel & Accessories > Clothing > Dresses",
    "Full Rompers": "Apparel & Accessories > Clothing > Baby Clothing",
    "Full sleeve T-Shirt": "Apparel & Accessories > Clothing > Shirts",
    "Gift Hamper": "Gifts > Gift Baskets",
    "Gift Wrap": "Gifts > Gift Wrapping Supplies",
    "Girls Top": "Apparel & Accessories > Clothing > Tops",
    "Girls Top and Pant": "Apparel & Accessories > Clothing",
    "Girls Top and Shorts": "Apparel & Accessories > Clothing",
    "Hair Accessories": "Apparel & Accessories > Accessories > Hair Accessories",
    "Hakoba Frock": "Apparel & Accessories > Clothing > Dresses",
    "Half Sleeve Jabla and Shorts": "Apparel & Accessories > Baby Clothing",
    "Hello Baby Kit": "Apparel & Accessories > Baby Clothing",
    "Henley Shirt and Pant": "Apparel & Accessories > Clothing",
    "Henley Shirts": "Apparel & Accessories > Clothing > Shirts",
    "Herbal Dyed Jabla": "Apparel & Accessories > Baby Clothing",
    "Herbal Dyed Jabla and Shorts": "Apparel & Accessories > Baby Clothing",
    "Holding Sheet": "Apparel & Accessories > Baby Clothing",
    "Hoodie": "Apparel & Accessories > Clothing > Outerwear",
    "Hospital Kit": "Health & Beauty > Health Care",
    "Ikkat Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - A-Line Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Cap Sleeve Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Choli": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Ind - Cotton Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Crop Top With Skirt": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Ind - Dhoti Set": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Ind - Embroidered Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Frock With Coat": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Fusion Jabla And Pant": "Apparel & Accessories > Baby Clothing",
    "Ind - Indo Western Suit Set": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Ind - Jabla With Panjakajam": "Apparel & Accessories > Baby Clothing",
    "Ind - Jump Suit": "Apparel & Accessories > Clothing",
    "Ind - Kimono Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Knot Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Kota Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Kurta Set": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Ind - Kurta Set With Dhoti": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Ind - Kurta Set With Waist Coat": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Ind - Organza Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Premium Cotton Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Scalloped Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind - Shirt": "Apparel & Accessories > Clothing > Shirts",
    "Ind - Shirt And Shorts": "Apparel & Accessories > Clothing",
    "Ind - Short Kurta Set With Dhot": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Ind - Side Placket Set": "Apparel & Accessories > Clothing",
    "Ind - Skirt And Top": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Ind - Suit Set": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Ind - Tissue Frock": "Apparel & Accessories > Clothing > Dresses",
    "Ind -Scalloped Top And Skirt": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Infant Pillow": "Apparel & Accessories > Baby Clothing",
    "Jabla and Pant Set": "Apparel & Accessories > Baby Clothing",
    "Jaipur Knot Frock": "Apparel & Accessories > Clothing > Dresses",
    "Jaipur Tie-up Style Frock": "Apparel & Accessories > Clothing > Dresses",
    "Jumbo Newborn essential kit": "Apparel & Accessories > Baby Clothing",
    "Jump Suits": "Apparel & Accessories > Clothing",
    "Kapok Silk Bed Set": "Apparel & Accessories > Bedding",
    "Kimono Frock": "Apparel & Accessories > Clothing > Dresses",
    "Knitted Cap Sleeve Frock": "Apparel & Accessories > Clothing > Dresses",
    "Knitted Frill Frock": "Apparel & Accessories > Clothing > Dresses",
    "Knitted Full Sleeve Frock": "Apparel & Accessories > Clothing > Dresses",
    "Knitted Full Sleeve Jabla": "Apparel & Accessories > Baby Clothing",
    "Knitted Half Sleeve Frock": "Apparel & Accessories > Clothing > Dresses",
    "Knitted Half Sleeve Jabla": "Apparel & Accessories > Baby Clothing",
    "Knitted Mittens": "Apparel & Accessories > Baby Clothing",
    "Knitted Nappy": "Apparel & Accessories > Baby Clothing",
    "Knitted Pyjamas": "Apparel & Accessories > Clothing > Pants",
    "Knitted Shorts": "Apparel & Accessories > Clothing > Shorts",
    "Knitted Sleeveless Frock": "Apparel & Accessories > Clothing > Dresses",
    "Knitted Sleeveless Jabla": "Apparel & Accessories > Baby Clothing",
    "Knitted Yoke Button Frock": "Apparel & Accessories > Clothing > Dresses",
    "Knot Frock": "Apparel & Accessories > Clothing > Dresses",
    "Knot Jabla": "Apparel & Accessories > Baby Clothing",
    "Kurta Set": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Kurta Set With Waist Coat": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Laro Frock": "Apparel & Accessories > Clothing > Dresses",
    "Linen Collection": "Apparel & Accessories > Clothing",
    "Masks": "Health & Beauty > Personal Care > Face Masks",
    "Mat Bed": "Apparel & Accessories > Bedding",
    "Maternity Pads": "Health & Beauty > Health Care",
    "Maternity Pant": "Apparel & Accessories > Clothing > Pants",
    "Maternity Parallel Pant": "Apparel & Accessories > Clothing > Pants",
    "Maternity Wear": "Apparel & Accessories > Clothing",
    "Medium Newborn essential kit": "Apparel & Accessories > Baby Clothing",
    "Milestone Cards": "Toys & Games > Educational Toys",
    "Mini Newborn essential kit": "Apparel & Accessories > Baby Clothing",
    "Mulmul Cotton Jabla": "Apparel & Accessories > Baby Clothing",
    "Mulmul Jabla and Shorts": "Apparel & Accessories > Baby Clothing",
    "Mulmul Top and Bottom Set": "Apparel & Accessories > Baby Clothing",
    "MulMul Welcome Kit": "Apparel & Accessories > Baby Clothing",
    "Muslin Blanket": "Apparel & Accessories > Bedding",
    "Muslin Carry Nest": "Apparel & Accessories > Baby Clothing",
    "Muslin Frock": "Apparel & Accessories > Clothing > Dresses",
    "Muslin Hood Towel": "Apparel & Accessories > Baby Clothing",
    "Muslin Jabla": "Apparel & Accessories > Baby Clothing",
    "Muslin Jabla and Nappy": "Apparel & Accessories > Baby Clothing",
    "Muslin Jabla and Shorts": "Apparel & Accessories > Baby Clothing",
    "Muslin Jabla Nappy and Shorts": "Apparel & Accessories > Baby Clothing",
    "Muslin Nappy": "Apparel & Accessories > Baby Clothing",
    "Muslin Shorts": "Apparel & Accessories > Baby Clothing",
    "Muslin Sleeveless Frock": "Apparel & Accessories > Clothing > Dresses",
    "Muslin Top and Bottom Set": "Apparel & Accessories > Baby Clothing",
    "Muslin Towel": "Apparel & Accessories > Baby Clothing",
    "Muslin Wipes": "Apparel & Accessories > Baby Clothing",
    "Neem Detergent Soap": "Health & Beauty > Household Supplies",
    "Nursery Decor Frames": "Home & Garden > Decor",
    "Onesie": "Apparel & Accessories > Baby Clothing",
    "Org Cotton Snap Button Jabla": "Apparel & Accessories > Baby Clothing",
    "Org Muslin Mittens and Booties": "Apparel & Accessories > Baby Clothing",
    "Organic Cotton Bck Button Frock": "Apparel & Accessories > Clothing > Dresses",
    "Organic Cotton Cap and Booties": "Apparel & Accessories > Baby Clothing",
    "Organic Cotton Cap With Fold": "Apparel & Accessories > Baby Clothing",
    "Organic Cotton Jabla": "Apparel & Accessories > Baby Clothing",
    "Organic Cotton Jabla and Shorts": "Apparel & Accessories > Baby Clothing",
    "Organic Cotton Knot Frock": "Apparel & Accessories > Clothing > Dresses",
    "Organic Cotton Sweaters": "Apparel & Accessories > Clothing > Outerwear",
    "Pant": "Apparel & Accessories > Clothing > Pants",
    "Pillow and Bolsters Set": "Apparel & Accessories > Bedding",
    "Pleat Frock": "Apparel & Accessories > Clothing > Dresses",
    "Pocket Frock": "Apparel & Accessories > Clothing > Dresses",
    "Polo Tees": "Apparel & Accessories > Clothing > Shirts",
    "Pyjama Sets": "Apparel & Accessories > Clothing > Sleepwear",
    "Rattles": "Toys & Games > Baby Toys",
    "Rayon Frock": "Apparel & Accessories > Clothing > Dresses",
    "Reversible Shirts": "Apparel & Accessories > Clothing > Shirts",
    "Reversible V-Neck Jabla": "Apparel & Accessories > Baby Clothing",
    "Romper Triple Cloth Collection": "Apparel & Accessories > Baby Clothing",
    "Rompers": "Apparel & Accessories > Baby Clothing",
    "Set Triple Cloth Collection": "Apparel & Accessories > Baby Clothing",
    "Shirt And Shorts": "Apparel & Accessories > Clothing",
    "Shirts": "Apparel & Accessories > Clothing > Shirts",
    "Shoulder Button Jabla": "Apparel & Accessories > Baby Clothing",
    "Side Placket Shirt And Shorts": "Apparel & Accessories > Baby Clothing",
    "Skirt and Top Ethnic Wear": "Apparel & Accessories > Clothing > Ethnic Wear",
    "Sleeping Bag": "Apparel & Accessories > Baby Clothing",
    "Sleepsuits": "Apparel & Accessories > Baby Clothing",
    "Sleeveless shirt and shorts": "Apparel & Accessories > Baby Clothing",
    "Sleeveless Top and  Skirt": "Apparel & Accessories > Clothing",
    "Smocking Top and Bottom": "Apparel & Accessories > Clothing",
    "Strap Frock": "Apparel & Accessories > Clothing > Dresses",
    "Swaddle": "Apparel & Accessories > Baby Clothing",
    "Sweat Shirt": "Apparel & Accessories > Clothing > Outerwear",
    "T-Shirt": "Apparel & Accessories > Clothing > Shirts",
    "T-Shirt and Pant Set": "Apparel & Accessories > Clothing",
    "T-Shirt and Shorts Set": "Apparel & Accessories > Clothing",
    "T-Shirt Boys": "Apparel & Accessories > Clothing > Shirts",
    "T-Shirt Girls": "Apparel & Accessories > Clothing > Shirts",
    "Teether": "Toys & Games > Baby Toys",
    "Terry Top and Shorts Set": "Apparel & Accessories > Clothing",
    "Test": "Miscellaneous",
    "Thermos Flask": "Home & Garden > Kitchen & Dining",
    "Thottil": "Apparel & Accessories > Baby Clothing",
    "Toddler - Quilt and Blanket": "Apparel & Accessories > Bedding",
    "Top and Pant KTP": "Apparel & Accessories > Clothing",
    "Top and Pant PTP": "Apparel & Accessories > Clothing",
    "Top and Pant Set": "Apparel & Accessories > Clothing",
    "Top and Pant WFJP": "Apparel & Accessories > Clothing",
    "Triple Cloth Jabla and Shorts": "Apparel & Accessories > Baby Clothing",
    "Triple Layer Frock": "Apparel & Accessories > Clothing > Dresses",
    "Turtle Neck T-Shirt": "Apparel & Accessories > Clothing > Shirts",
    "Ultra Slim Snap Button Shirt": "Apparel & Accessories > Baby Clothing",
    "V-Neck Frocks": "Apparel & Accessories > Clothing > Dresses",
    "V-Neck Jabla": "Apparel & Accessories > Baby Clothing",
    "Velvet Frock": "Apparel & Accessories > Clothing > Dresses",
    "Vericated Rib Sleeveless Frock": "Apparel & Accessories > Clothing > Dresses",
    "Vest and Shorts": "Apparel & Accessories > Baby Clothing",
    "Vests": "Apparel & Accessories > Baby Clothing",
    "Waffled Sets": "Apparel & Accessories > Clothing",
    "Wide Fit T-Shirt": "Apparel & Accessories > Clothing > Shirts",
    "Winter Throw": "Apparel & Accessories > Bedding",
    "Wooden Toys": "Toys & Games > Wooden Toys",
    "Woven Cap Sleeve Frock": "Apparel & Accessories > Clothing > Dresses",
    "Woven Frill Frock": "Apparel & Accessories > Clothing > Dresses",
    "Woven Full Sleeve Frock": "Apparel & Accessories > Clothing > Dresses",
    "Woven Net Frock": "Apparel & Accessories > Clothing > Dresses",
    "Woven Pant": "Apparel & Accessories > Clothing > Pants",
    "Woven Rompers": "Apparel & Accessories > Baby Clothing",
    "Woven Shorts": "Apparel & Accessories > Clothing > Shorts",
    "Woven Sleeveless Frock": "Apparel & Accessories > Clothing > Dresses",
    "Woven Yoke Frock": "Apparel & Accessories > Clothing > Dresses",
}

FACEBOOK_COLS = [
    'id', 'title', 'description', 'availability', 'condition',
    'link', 'image_link', 'brand', 'google_product_category', 'size', 'price'
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
    c_age      = col(df, "PROPERTY:Age")

    rows_out = []
    for i in range(len(df)):
        _id       = coalesce(c_id.iloc[i])
        name      = coalesce(c_name.iloc[i], "")
        subtitle  = coalesce(c_subtitle.iloc[i], "")
        _type     = str(coalesce(c_type.iloc[i], "")).strip()
        sku       = coalesce(c_sku.iloc[i], "")
        price     = to_float(c_price.iloc[i], 0.0)
        discount  = to_float(c_discount.iloc[i], None)  # keep None if no discount
        stock     = to_float(c_stock.iloc[i], 0.0)
        age       = coalesce(c_age.iloc[i], "")

        title = build_title(name, subtitle)
        description = title
        availability = "in stock" if stock > 0 else "out of stock"
        condition = "new"
        google_product_category = ITEM_TYPE_TO_CATEGORY.get(
            _type,
            "Apparel & Accessories > Clothing"  # fallback
        )
        # Price (original)
        price_str = f"{price:.2f} INR" if price else "0.00 INR"

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
            google_product_category,
            age,
            price_str
        ])

    out_path = f"{business_name}_google_catalog.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FACEBOOK_COLS)
        writer.writerows(rows_out)

    print(f"Done. Wrote {len(rows_out)} rows to {out_path}")

if __name__ == "__main__":
    main("beelittle")
