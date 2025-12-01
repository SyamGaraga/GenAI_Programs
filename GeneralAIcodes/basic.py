from nltk.tokenize import word_tokenize
import nltk

# Download tokenizer package (only first time)
nltk.download('punkt')

sentence = "Let's learn tokenization in AI!"
tokens = word_tokenize(sentence)

print("Tokens:", tokens)
