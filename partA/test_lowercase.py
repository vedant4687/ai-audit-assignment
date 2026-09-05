import tiktoken

enc = tiktoken.get_encoding("gpt2")

def read_lines(path):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if line:
                lines.append(line)
    return lines

def fertility(lines, lowercase):
    per_line = []
    for line in lines:
        if lowercase:
            line = line.lower()
        tokens = enc.encode(line)
        words = line.split(" ")
        per_line.append(len(tokens) / len(words))
    return sum(per_line) / len(per_line)

eng_lines = read_lines("starter_kit/corpus_sample/eng_sample.txt")
hin_lines = read_lines("starter_kit/corpus_sample/hin_sample.txt")

print("English:")
print("  with lowercase:   ", fertility(eng_lines, True))
print("  without lowercase:", fertility(eng_lines, False))

print("Hindi:")
print("  with lowercase:   ", fertility(hin_lines, True))
print("  without lowercase:", fertility(hin_lines, False))
