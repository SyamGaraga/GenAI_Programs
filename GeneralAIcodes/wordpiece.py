from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

text = "Artificial Intelligence revolutionizes industries!"
tokens = tokenizer.tokenize(text)

print("Subword Tokens:", tokens)
