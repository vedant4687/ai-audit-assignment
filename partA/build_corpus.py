from datasets import load_dataset
import sys

# openlanguagedata/flores_plus - modern Parquet-based FLORES successor
langs = {
    "eng": "eng_Latn",
    "hin": "hin_Deva",
    "kan": "kan_Knda",
    "tam": "tam_Taml",
}

for short, code in langs.items():
    print(f"Loading {short} ({code})...", flush=True)
    try:
        ds = load_dataset("openlanguagedata/flores_plus", code, split="dev")
        sentences = ds["text"]  # note: column may be named "text" not "sentence"
        out_path = f"corpus/{short}.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            for s in sentences:
                f.write(s.strip() + "\n")
        print(f"{short}: {len(sentences)} sentences saved to {out_path}", flush=True)
    except Exception as e:
        print(f"FAILED for {short}: {e}", flush=True)
        sys.exit(1)