#!/usr/bin/env python3
"""
generate_translations.py v2 — Batch-generate translations.json using googletrans.
Smaller batches per run to avoid timeout.
"""

import json, os, sys, time
from googletrans import Translator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(SCRIPT_DIR, "translations-base.json")
OUT_PATH = os.path.join(SCRIPT_DIR, "translations.json")

# Languages to fill (all except zh-TW)
TARGET_LANGS = ["en", "es", "hi", "ar", "pt", "bn", "ru", "ja", "fr", "de", "ko", "vi", "it", "tr"]

def load_base():
    with open(BASE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_existing():
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def translate_batch(texts, dest, src="zh-TW"):
    """Translate a batch of texts using googletrans."""
    try:
        t = Translator()
        # Translate one by one to avoid issues
        results = []
        for text in texts:
            r = t.translate(text, src=src, dest=dest)
            results.append(r.text if r and r.text else text)
            time.sleep(0.25)
        return results
    except Exception as e:
        print(f"    ⚠️  Batch error for {dest}: {e}")
        return texts  # fallback

def main():
    want_lang = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    base = load_base()
    existing = load_existing()
    data = existing if existing else base
    
    # Collect all string paths and zh-TW values
    def walk(d, prefix=""):
        items = []
        for k, v in d.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                # Check if this is a leaf dict with language keys
                if "zh-TW" in v:
                    items.append((path, v["zh-TW"]))
                else:
                    items.extend(walk(v, path))
        return items
    
    all_strings = walk(data)
    
    langs = TARGET_LANGS if want_lang == "all" else [want_lang]
    
    for lang in langs:
        if lang == "zh-TW":
            continue
        print(f"\n🌐 {lang}...")
        
        # Check which strings need translation
        to_translate = []
        paths = []
        for path, source in all_strings:
            # Navigate to the leaf dict
            parts = path.split(".")
            d = data
            for p in parts:
                d = d[p]
            if d.get(lang) and d[lang].strip():
                continue  # already translated
            to_translate.append(source)
            paths.append(path)
        
        if not to_translate:
            print(f"   ✅ Already complete")
            continue
        
        print(f"   {len(to_translate)} strings to translate...")
        
        # Translate in batches
        batch_size = 5
        for i in range(0, len(to_translate), batch_size):
            batch_texts = to_translate[i:i+batch_size]
            batch_paths = paths[i:i+batch_size]
            batch_results = translate_batch(batch_texts, lang)
            
            for path, result in zip(batch_paths, batch_results):
                parts = path.split(".")
                d = data
                for p in parts:
                    d = d[p]
                d[lang] = result
            
            print(f"   -> {min(i+batch_size, len(to_translate))}/{len(to_translate)}")
        
        # Save after each language
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ {lang} saved ({len(to_translate)} translations)")
    
    print(f"\n✅ Done! translations.json updated")


if __name__ == "__main__":
    main()
