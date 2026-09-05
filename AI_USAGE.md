# AI Usage Summary

I used Claude throughout this assignment as a guide and pair-programmer,
not as a black box to generate final answers without understanding them.

## Where AI helped
- Drafted the initial experiment scripts (lowercase toggle test, word-split
  test, corrected_analysis.py) quickly, which saved time on boilerplate
  Python/argument-parsing code
- Helped debug the FLORES+ dataset download, which hit several real
  blockers (facebook/flores gated, Muennighoff/flores200 using a
  deprecated loading-script format) before landing on
  openlanguagedata/flores_plus with proper HuggingFace authentication
- Explained the KV-cache formula (B1) and the goodput-vs-throughput
  distinction (B3) step by step until I could actually explain them
  back in my own words, rather than just accepting the final numbers
- Helped structure the repo (NOTEBOOK.md, AI_USAGE.md, partA/partB/partC)
  to match the required deliverable format

## Where AI required correction or extra scrutiny
- I had to explicitly push back and ask for re-verification on the B3
  goodput formula — it had only been checked against one data row
  (batch=16) initially; asking to re-check against a second row
  (batch=24) confirmed the formula wasn't a coincidence, which
  strengthened the evidence rather than just trusting the first match
- The B1 KV-cache calculation used a GB vs GiB assumption (binary vs
  decimal memory units) that wasn't explicitly stated as a caveat until
  I asked for a second review pass — this is a subtlety I now
  understand needs to be flagged, since GPU spec sheets are often
  ambiguous about this
- For B4 (confirmation metric), no live experiment was possible since
  I don't have access to a real serving stack — that answer is
  reasoned/predicted, not measured, and I made sure this distinction
  was written into NOTEBOOK.md explicitly rather than presenting it as
  if it were tested like A2/A3/B1

## What I made sure I understood myself
Initially I did not understand why the goodput/throughput distinction
mattered, or why KV heads (8) rather than attention heads (24) are used
in the cache formula. I asked for these to be re-explained with simpler
analogies until I could restate them correctly in my own words before
moving forward — this is reflected in the conversation and in
NOTEBOOK.md's entries.