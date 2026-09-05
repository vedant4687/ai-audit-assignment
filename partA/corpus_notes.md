# A1: Eval Corpus Construction

## Source
FLORES+ (`openlanguagedata/flores_plus`), `dev` split — a parallel
multilingual benchmark where the same set of sentences is professionally
translated into 200+ languages. This is the modern, actively maintained
successor to FLORES-200 (the original `facebook/flores` and
`Muennighoff/flores200` mirrors are either gated or use a deprecated
loading-script format, so this repo was used instead).

## Languages selected
- **English** (`eng_Latn`) — baseline, matches the original report
- **Hindi** (`hin_Deva`) — required by the assignment
- **Kannada** (`kan_Knda`) — Dravidian language #1
- **Tamil** (`tam_Taml`) — Dravidian language #2

## Corpus size and domain
997 parallel sentences per language (`dev` split), identical content
across all 4 languages. Content is **news/journalistic text** — short
factual reports on real-world events (science, politics, accidents,
etc.), written in a formal, editorial register. Example (English):
"On Monday, scientists from the Stanford University School of Medicine
announced the invention of a new diagnostic tool..."

## Preprocessing
- Stripped trailing/leading whitespace per line
- Saved as UTF-8 plain text, one sentence per line
- No lowercasing, punctuation stripping, or other normalization applied
  at corpus-build time — normalization choices are handled explicitly
  in the tokenizer analysis script (A3), not baked into the raw corpus,
  so we can test different preprocessing choices without re-downloading

## What this corpus cannot tell you
- **Register mismatch**: FLORES is formal/editorial news text. It will
  not reflect how a production chat assistant's traffic actually looks —
  conversational text, code-mixed text (e.g. Hindi-English "Hinglish"),
  or domain-specific vocabulary (technical support, legal, medical) may
  tokenize very differently than clean news prose.
- **Sample size**: 997 sentences per language is enough for stable
  aggregate averages, but too small to catch rare or long-tail
  tokenization edge cases (e.g. rare compound words, code snippets,
  emoji, numbers formatted differently).
- **Language coverage**: only 4 languages were tested. Conclusions about
  "Indic tokenization" should not be assumed to generalize evenly to all
  Indic or Dravidian languages — each has different scripts, morphology,
  and Unicode representations (e.g. Tamil has a smaller character
  inventory than Kannada or Hindi, which may affect tokenization
  differently).
- **Sentence-level, not real-user-utterance-level**: FLORES sentences
  are complete, well-formed, grammatically correct sentences — real user
  queries are often shorter, informal, and less grammatically clean.