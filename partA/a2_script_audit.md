# A2: fertility.py Script & Metric Audit

## Bug 1: `.lower()` distorts the comparison (real, asymmetric)
`analyze()` lowercases text before tokenizing. GPT-2 is case-sensitive,
so lowercasing changes English's token count. Hindi (Devanagari) has no
case system, so it's completely unaffected.
- Evidence: English fertility 1.2293 (no lowercase) vs 1.2652 (lowercase) 
  - a 2.9% increase. Hindi: 7.44845 in both cases - zero change.
- Effect: slightly overstates the eng/hin gap (~3%), but doesn't 
  explain the bulk of it.

## Bug 2: `split(" ")` word-counting (real, but symmetric)
Splitting on a literal single space (not general whitespace) means
double-spaced lines produce a phantom extra "word" (an empty string).
- Evidence: on the sample corpus, English word count 79 (naive) vs 78 
  (whitespace-aware); Hindi 62 vs 61 - one double-spaced line each.
- Effect: negligible impact on the eng/hin ratio, since it occurs 
  symmetrically in both languages.

## Bug 3 (conceptual): Report misattributes the fertility gap to "script property"
REPORT_v0 claims Hindi's high fertility is "a property of the script,
not the tokenizer." This is testable and false.
- Evidence: re-running fertility.py with the same corpus but swapping
  GPT-2 for a multilingual tokenizer (xlm-roberta-base) collapsed the
  gap from 5.89x down to 1.10x on the sample corpus, and from 7.44x/
  13.59x/15.43x down to 1.26x/1.37x/1.35x (hin/kan/tam) on the full
  FLORES+ corpus.
- Conclusion: the gap is overwhelmingly a tokenizer-vocabulary artifact
  (GPT-2 trained mostly on English), not an inherent property of these
  languages' scripts. This is the core conceptual bug in the report.

## Non-bug: `random.seed(1337)` (flagged as fine, with evidence)
`random` is imported and seeded but never called anywhere else in the
script (confirmed via `Select-String-Pattern "random\."`, only one
match - the seed line itself). This is dead code with zero effect on
any reported number. Flagged as harmless, not a bug.