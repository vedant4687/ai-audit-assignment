# Tokenizer Audit — Corrected Findings & Recommendation

## Corrected headline numbers
Using a real ~1000-sentence parallel corpus (FLORES+, news domain) and
two tokenizers:

| Language | GPT-2 (tok/sentence ratio vs Eng) | XLM-RoBERTa (multilingual) |
|---|---|---|
| Hindi    | 7.44x  | 1.26x |
| Kannada  | 13.59x | 1.37x |
| Tamil    | 15.43x | 1.35x |

REPORT_v0's "5.89x" figure was reproduced, but its explanation was
wrong. The gap is not a property of Hindi/Kannada/Tamil as languages —
it is almost entirely an artifact of using GPT-2, a tokenizer trained
overwhelmingly on English text. Swapping to a multilingual tokenizer
collapses the gap from 7–15x down to a tight 1.26–1.37x band across
all three Indic/Dravidian languages tested.

## Routing recommendation
**Do not budget 6–15x serving cost for Indic languages.** Instead:
1. Serve Indic-language traffic through a multilingual/Indic-aware
   tokenizer and model (e.g. an XLM-R-family or Indic-specific model),
   not the English-centric GPT-2-family pipeline.
2. Once on an appropriate tokenizer, expect Indic languages to cost
   roughly **1.3x** English per equivalent request — not the 6x+
   figure in REPORT_v0. Capacity and cost planning should use this
   revised figure.
3. The original recommendation to route Indic traffic to a
   specialized model is directionally reasonable — but for the
   opposite reason stated. It's needed because GPT-2 is poorly suited
   to these scripts, not because the languages are inherently
   expensive.

## Biggest caveat
This analysis uses FLORES+, a formal, news-register parallel corpus.
Real production traffic (conversational, code-mixed "Hinglish"-style
text, short informal queries) may tokenize differently than clean
news prose. The 1.3x figure should be treated as a domain-formal-text
estimate, not a guarantee for all traffic types — it should be
validated against a sample of real user queries before being locked
into capacity planning.

## Metric to monitor in production
**Tokens-per-request, segmented by detected input language**, tracked
over time after switching tokenizers. If the Indic/English ratio drifts
meaningfully above ~1.3–1.5x in real traffic, that's a signal this
analysis's domain assumptions (formal, sentence-level FLORES text) no
longer hold for actual usage patterns, and the estimate needs
revisiting.