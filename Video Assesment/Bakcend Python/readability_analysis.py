import textstat

def evaluate_readability(text):
    score = textstat.flesch_reading_ease(text)
    return "Best" if score > 70 else "Good" if score > 60 else "Average"
