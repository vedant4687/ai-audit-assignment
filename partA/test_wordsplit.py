def read_lines(path):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if line:
                lines.append(line)
    return lines

def word_counts(lines, method):
    counts = []
    for line in lines:
        if method == "naive":
            words = line.split(" ")
        else:  # whitespace-aware
            words = line.split()
        counts.append(len(words))
    return counts

eng_lines = read_lines("starter_kit/corpus_sample/eng_sample.txt")
hin_lines = read_lines("starter_kit/corpus_sample/hin_sample.txt")

eng_naive = word_counts(eng_lines, "naive")
eng_ws = word_counts(eng_lines, "whitespace")
hin_naive = word_counts(hin_lines, "naive")
hin_ws = word_counts(hin_lines, "whitespace")

print("English total words - naive split(' '):", sum(eng_naive))
print("English total words - whitespace split():", sum(eng_ws))
print("Hindi total words - naive split(' '):", sum(hin_naive))
print("Hindi total words - whitespace split():", sum(hin_ws))

# Show if any line produces a different count between methods
print("\nLines where counts differ (eng):")
for i, (a, b) in enumerate(zip(eng_naive, eng_ws)):
    if a != b:
        print(f"  line {i}: naive={a}, whitespace={b} -> {eng_lines[i]!r}")

print("\nLines where counts differ (hin):")
for i, (a, b) in enumerate(zip(hin_naive, hin_ws)):
    if a != b:
        print(f"  line {i}: naive={a}, whitespace={b} -> {hin_lines[i]!r}")