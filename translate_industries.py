#!/usr/bin/env python3
"""
translate_industries.py — Translate industry names & descriptions into 15 languages.
Reads industries.json (latest version with holdings data), adds 'name_*' and 'desc_*' fields.
"""

import json, os, time, shutil
from googletrans import Translator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "industries.json")

LANGUAGES = [
    ("zh-TW", "zh-TW"),  # already present
    ("en", "en"),
    ("es", "es"),
    ("hi", "hi"),
    ("ar", "ar"),
    ("pt", "pt"),
    ("bn", "bn"),
    ("ru", "ru"),
    ("ja", "ja"),
    ("fr", "fr"),
    ("de", "de"),
    ("ko", "ko"),
    ("vi", "vi"),
    ("it", "it"),
    ("tr", "tr"),
]

def translate_text(text, dest, src="zh-TW"):
    for attempt in range(3):
        try:
            t = Translator()
            r = t.translate(text, src=src, dest=dest)
            if r and r.text:
                return r.text
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                print(f"    ⚠️  '{text[:20]}'→{dest}: {e}")
    return text


def main():
    print("=" * 50)
    print("🌐 產業中英文翻譯器")
    print("=" * 50)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        industries = json.load(f)

    print(f"\n📂 載入 {len(industries)} 個產業")

    # Backup
    shutil.copy2(JSON_PATH, JSON_PATH.replace(".json", "-pre-translate.json"))

    total = 0
    for i, ind in enumerate(industries):
        name_zh = ind["name"]
        desc_zh = ind["desc"]
        name_en = ind.get("name_en", "")

        print(f"\n[{i+1}/{len(industries)}] {name_zh} → {name_en}")

        for lang_code, goog_src in LANGUAGES:
            if lang_code == "zh-TW":
                # Skip source
                continue

            # Translate name
            name_key = f"name_{lang_code.replace('-', '_')}"
            if name_key not in ind or not ind[name_key]:
                if lang_code == "en":
                    ind[name_key] = name_en or translate_text(name_zh, "en")
                    print(f"  name_{lang_code}: {ind[name_key]}")
                else:
                    # Translate from English (cleaner results)
                    source_text = name_en or name_zh
                    ind[name_key] = translate_text(source_text, goog_src, src="en" if name_en else "zh-TW")
                    print(f"  name_{lang_code}: {ind[name_key][:25]}…")
                total += 1
                time.sleep(0.3)

            # Translate description
            desc_key = f"desc_{lang_code.replace('-', '_')}"
            if desc_key not in ind or not ind[desc_key]:
                if lang_code == "en":
                    ind[desc_key] = translate_text(desc_zh, "en")
                else:
                    source_desc = ind.get(desc_key.replace(f"_{lang_code}", "_en")) or desc_zh
                    ind[desc_key] = translate_text(source_desc, goog_src,
                                                   src="en" if desc_key in ind or name_en else "zh-TW")
                total += 1
                time.sleep(0.3)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(industries, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 50}")
    print(f"✅ industries.json 已更新！")
    print(f"   新增 {total} 筆翻譯")
    print(f"   每個產業支援 {len(LANGUAGES)} 種語言")

    # Summary
    for ind in industries:
        langs = [k for k in ind.keys() if k.startswith("name_")]
        print(f"  {ind['name']}: {len(langs)} languages")


if __name__ == "__main__":
    main()
