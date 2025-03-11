import re

KEYWORDS = {"algorithm", "data structure", "complexity"}

def keyword_coverage(extracted_text):
    words = set(re.findall(r'\b\w+\b', extracted_text.lower()))
    return "Best" if len(words & KEYWORDS) > 2 else "Good"
