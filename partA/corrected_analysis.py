import tiktoken
from transformers import AutoTokenizer

def read_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_tokenizers():
    gpt2_enc = tiktoken.get_encoding("gpt2")
    xlmr_tok = AutoTokenizer.from_pretrained("xlm-roberta-base")

    return {
        "gpt2": lambda s: gpt2_enc.encode(s),
        "xlm-roberta": lambda s: xlmr_tok.encode(s, add_special_tokens=False),
    }

def analyze(lines, encode):
    total_tokens = 0
    total_words = 0
    total_chars = 0
    total_bytes = 0
    total_sentences = len(lines)

    for line in lines:
        tokens = encode(line)
        words = line.split()  # whitespace-aware, fixes earlier bug
        total_tokens += len(tokens)
        total_words += len(words)
        total_chars += len(line)
        total_bytes += len(line.encode("utf-8"))

    return {
        "tok_per_word": total_tokens / total_words,
        "tok_per_char": total_tokens / total_chars,
        "tok_per_byte": total_tokens / total_bytes,
        "tok_per_sentence": total_tokens / total_sentences,
    }

langs = ["eng", "hin", "kan", "tam"]
tokenizers = get_tokenizers()

results = {}
for tok_name, encode in tokenizers.items():
    print(f"\n=== Tokenizer: {tok_name} ===")
    print(f"{'lang':<6}{'tok/word':>10}{'tok/char':>10}{'tok/byte':>10}{'tok/sent':>10}")
    for lang in langs:
        lines = read_lines(f"corpus/{lang}.txt")
        metrics = analyze(lines, encode)
        results[(tok_name, lang)] = metrics
        print(f"{lang:<6}{metrics['tok_per_word']:>10.3f}{metrics['tok_per_char']:>10.3f}"
              f"{metrics['tok_per_byte']:>10.3f}{metrics['tok_per_sentence']:>10.2f}")

# Ratios relative to English, per tokenizer
print("\n\n=== Ratios vs English (tok/sentence — the fair comparison) ===")
for tok_name in tokenizers:
    eng_val = results[(tok_name, "eng")]["tok_per_sentence"]
    print(f"\nTokenizer: {tok_name}")
    for lang in langs[1:]:
        val = results[(tok_name, lang)]["tok_per_sentence"]
        ratio = val / eng_val
        print(f"  {lang}: {ratio:.2f}x English")