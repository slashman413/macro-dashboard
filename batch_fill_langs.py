#!/usr/bin/env python3
"""batch_fill_langs.py — Fill missing language translations in industries.json."""
import json, os, sys, time
from googletrans import Translator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "industries.json")

# Languages we need to add (missing from check)
NEEDED = ["es", "ar", "ru", "ko", "vi", "it", "en"]

def translate(text, dest, src="zh-TW"):
    for attempt in range(3):
        try:
            r = Translator().translate(text, src=src, dest=dest)
            if r and r.text:
                return r.text
        except:
            if attempt < 2: time.sleep(1)
    return text

def main():
    lang = sys.argv[1]
    if lang not in NEEDED:
        print(f"Skipping {lang}, not in needed list.")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        industries = json.load(f)

    nk = f"name_{lang}"
    dk = f"desc_{lang}"
    cn, cd = 0, 0

    for ind in industries:
        if nk not in ind or not ind.get(nk):
            src = ind.get("name_en") or ind["name"]
            sl = "en" if ind.get("name_en") else "zh-TW"
            ind[nk] = translate(src, lang, src=sl)
            time.sleep(0.2)
            cn += 1
        if dk not in ind or not ind.get(dk):
            src = ind.get("desc_en") or ind["desc"]
            sl = "en" if ind.get("desc_en") else "zh-TW"
            ind[dk] = translate(src, lang, src=sl)
            time.sleep(0.3)
            cd += 1

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(industries, f, ensure_ascii=False, indent=2)

    print(f"✅ {lang}: {cn} names + {cd} descriptions")


if __name__ == "__main__":
    main()
