"""Tehnomix Google-style feed (google-new.csv) -> OpenAI Ads product feed (file-upload spec, CSV).
Spec: developers.openai.com/commerce/specs/file-upload/products + /ads/product-feeds.
Usage: python3 build_openai_feed.py <google-new.csv> <out.csv>
The source sits behind Cloudflare (403 for scripts) - download it from a browser first."""
import csv, collections, re, sys

SRC, OUT = sys.argv[1], sys.argv[2]
SELLER, SELLER_URL = "Tehnomix", "https://www.tehnomix.bg"
HEADER = ["item_id", "title", "description", "url", "brand", "seller_name", "image_url", "availability",
          "price", "sale_price", "product_category", "condition", "seller_url",
          "is_eligible_search", "is_ads_eligible", "is_eligible_checkout"]

# Cyrillic look-alikes that appear inside Latin words in the source titles (e.g. "Ѕhаrk")
LOOK = str.maketrans({"А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P", "С": "C",
                      "Т": "T", "Х": "X", "І": "I", "Ѕ": "S", "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
                      "х": "x", "і": "i", "ѕ": "s", "у": "y"})
NOT_BRANDS = {"Design", "Bang", "Bio", "Wok", "TV", "Pad", "WiFi", "OneBlade", "Bitty", "NanoProtect", "Roomba",
              "WPRO", "Therabody"}  # product words / sub-lines, not manufacturers (Therabody handled below)
KEEP_CAPS = {"AEG", "LG", "TCL", "WMF", "AENO", "JOVS", "JVC", "HP", "TP-Link"}


def fix(tok):
    return tok.translate(LOOK) if re.search(r"[A-Za-z]", tok) and re.search(r"[АВЕКМНОРСТХІЅаеорсхіѕу]", tok) else tok


def money(s):
    n, cur = s.split()
    return float(n), cur


def fmt(n, cur):
    return "%.2f %s" % (n, cur)


def clean_desc(d, title):
    d = re.sub(r"^\s*Технически спецификации:\s*", "", d or "")
    d = re.sub(r"[\xa0\s]*\n[\xa0\s]*", ". ", d.strip())
    d = re.sub(r"\.\s*\.", ".", re.sub(r"\s+", " ", d)).strip(" .")
    return (d + ".") if d else title


with open(SRC, encoding="utf-8", newline="") as f:
    src = list(csv.DictReader(f))

# pass 1: brand vocabulary = Latin tokens right after the Cyrillic product-type words, frequent enough to trust
cand = collections.Counter()
for r in src:
    for t in r["Item title"].replace(",", " ").split()[1:]:
        t = fix(t)
        if re.fullmatch(r"[A-Za-z][A-Za-z&'.\-]+", t):
            cand[t.lower()] += 1
            break
fav = {}
for r in src:
    for t in r["Item title"].replace(",", " ").split()[1:]:
        t = fix(t)
        if re.fullmatch(r"[A-Za-z][A-Za-z&'.\-]+", t):
            fav.setdefault(t.lower(), collections.Counter())[t] += 1
            break
vocab = {}
for low, n in cand.items():
    form = fav[low].most_common(1)[0][0]
    if n >= 3 and form not in NOT_BRANDS and form.lower() not in {b.lower() for b in NOT_BRANDS}:
        vocab[low] = form if (form in KEEP_CAPS or not form.isupper() or len(form) <= 3 and form in KEEP_CAPS) else form.title()
vocab["irobot"] = "iRobot"
vocab["therabody"] = "Therabody"
vocab["delonghi"] = "DeLonghi"
vocab.pop("controler", None)
# brands too rare for the frequency rule, plus typos / sub-lines seen in the source titles
ALIAS = {"wpro": "Wpro", "senseo": "Senseo", "climastar": "Climastar", "royal": "Royal", "revlon": "Revlon",
         "indesit": "Indesit", "illy": "Illy", "blanco": "Blanco", "edesa": "Edesa", "flyme": "Flyme", "beha": "Beha",
         "gree": "Gree", "treo": "Treo", "beko": "Beko", "gaggenau": "Gaggenau", "apple": "Apple",
         "bitty": "Bitty Boomers", "simplehuman": "Simplehuman", "kimbo": "Kimbo", "bialetti": "Bialetti",
         "witt": "Witt", "collezione": "Collezione", "carrier": "Carrier", "muhler": "Muhler", "maclean": "Maclean",
         "innoliving": "Innoliving", "berner": "Berner", "hutt": "Hutt", "roomba": "iRobot", "samsnung": "Samsung",
         "philps": "Philips", "theraface": "Therabody", "ellen": "Ellen", "pizzaexpert": "PizzaExpert"}
vocab.update(ALIAS)
MULTI = [("bang & olufsen", "Bang & Olufsen"), ("bio ionic", "Bio Ionic"), ("amazon basics", "Amazon Basics")]


def brand_of(title):
    low = title.lower()
    for k, v in MULTI:
        if k in low:
            return v
    toks = [fix(t.strip("®™")) for t in title.replace(",", " ").split()]
    for t in toks:
        if t.lower() in vocab:
            return vocab[t.lower()]
    return ""


rows, drop = [], collections.Counter()
for r in src:
    title = re.sub(r"\s+", " ", r["Item title"].translate({0xa0: " "})).strip()
    if "no_selection" in r["Image URL"]:
        drop["no image"] += 1
        continue
    brand = brand_of(title)
    if not brand:
        drop["no brand"] += 1
        continue
    p, cur = money(r["Price"])
    if p <= 0:
        drop["no price"] += 1
        continue
    s, _ = money(r["Sale price"]) if r["Sale price"] else (0, cur)
    sale = fmt(s, cur) if 0 < s < p else ""
    rows.append([r["ID"], title[:150], clean_desc(r["item description"], title)[:5000], r["Final URL"], brand, SELLER,
                 r["Image URL"], "in_stock", fmt(p, cur), sale, r["Item category"], "new", SELLER_URL,
                 "true", "true", "false"])

if len(rows) < 3000:
    raise SystemExit("Only %d rows - output NOT written" % len(rows))
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(HEADER)
    w.writerows(rows)
print("%d in, %d out, dropped %s, %d with sale price, %d brands" % (
    len(src), len(rows), dict(drop), sum(1 for x in rows if x[9]), len({x[4] for x in rows})))
