text="i love india"
tokens=text.split()
print(tokens)

vocab={
    "i":1,
    "love":2,
    "india":3
}
ids=[vocab[token] for token in tokens]
print(ids)