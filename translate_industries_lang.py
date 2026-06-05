#!/usr/bin/env python3
"""translate_industries_lang.py — Translate industries into ONE language.
Usage: python translate_industries_lang.py <lang_code>
Example: python translate_industries_lang.py ja
"""

import json, os, sys, time
from googletrans import Translator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "industries.json")

def translate(text, dest, src="zh-TW"):
    for attempt in range(3):
        try:
            r = Translator().translate(text, src=src, dest=dest)
            if r and r.text:
                return r.text
        except Exception as e:
            if attempt < 2:
                time.sleep(0.5)
    return text

def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    if lang == "zh-TW":
        print("Source language, nothing to do.")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        industries = json.load(f)

    name_key = f"name_{lang.replace('-', '_')}"
    desc_key = f"desc_{lang.replace('-', '_')}"
    count_name = 0
    count_desc = 0

    for i, ind in enumerate(industries):
        # Translate name
        if name_key not in ind or not ind.get(name_key):
            src = ind.get("name_en") or ind["name"]
            src_lang = "en" if "name_en" in ind and ind["name_en"] else "zh-TW"
            ind[name_key] = translate(src, lang, src=src_lang)
            count_name += 1
            print(f"  [{i+1}/14] name_{lang}: {ind[name_key][:30]}…")
            time.sleep(0.2)

        # Translate description
        if desc_key not in ind or not ind.get(desc_key):
            src = ind.get("desc_en") or ind["desc"]
            src_lang = "en" if "desc_en" in ind and ind["desc_en"] else "zh-TW"
            ind[desc_key] = translate(src, lang, src=src_lang)
            count_desc += 1
            print(f"  [{i+1}/14] desc_{lang}: {ind[desc_key][:30]}…")
            time.sleep(0.3)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(industries, f, ensure_ascii=False, indent=2)

    print(f"  ✅ {lang}: {count_name} names + {count_desc} descriptions")


if __name__ == "__main__":
    main()
