import re

text = "Hello!!!  This   is   an Example...   "
print("Original:", text)

# Convert to lowercase
text = text.lower()

# Replace multiple punctuation like !!! or ... with a single .
text = re.sub(r'[!?.]+', '.', text)

# Remove extra spaces
text = re.sub(r'\s+', ' ', text).strip()

print("Cleaned:", text)
C