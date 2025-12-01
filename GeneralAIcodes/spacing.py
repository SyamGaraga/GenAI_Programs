import re

text = "Hello,world!Let's test:spacing."
print("Before:", text)

# Add spacing around punctuation
text = re.sub(r'([,.!?;:])', r' \1 ', text)
text = re.sub(r'\s+', ' ', text).strip()

print("After:", text)
