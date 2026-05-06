import re

HINDI_NUM_WORDS = {
    "ek": 1,
    "do": 2,
    "teen": 3,
    "char": 4,
    "paanch": 5,
    "chah": 6,
    "saath": 7,
    "aath": 8,
    "nau": 9,
    "das": 10,
    "gyaarah": 11,
    "baarah": 12,
    "teerah": 13,
    "choudah": 14,
    "pandrah": 15,
    "solah": 16,
    "satrah": 17,
    "atharah": 18,
    "unnees": 19,
    "bees": 20,
    "tees": 30,
    "chaalis": 40,
    "pachaas": 50,
    "saath": 60,
    "sattar": 70,
    "assi": 80,
    "nabbe": 90,
    "sau": 100,
    "hazaar": 1000,
    "hazara": 1000,
    "hazr": 1000,
    "lakh": 100000,
    "lakh": 100000,
    "laz": 100000,
}

SCALE_WORDS = {
    "hazaar": 1000,
    "hazara": 1000,
    "hazr": 1000,
    "lakh": 100000,
    "laz": 100000,
    "karod": 10000000,
    "crore": 10000000,
}


def parse_hindi_number(text: str) -> int | None:
    """Convert Hindi number words to integer. Returns None if no number found."""
    if not text:
        return None
    
    text = text.lower().strip()
    
    # First check for pure digit strings (handles typed/spoken numbers like 500000)
    digit_match = re.search(r'(\d[0-9,]*)', text)
    if digit_match:
        digits_only = digit_match.group(1).replace(',', '')
        try:
            return int(digits_only)
        except ValueError:
            pass
    
    # Handle common patterns like "500000" or "5,00,000"
    if re.match(r'^[\d,]+$', text):
        return int(text.replace(',', ''))
    
    # Handle "5 lakh" or "5laz" or "5 लाख" style
    match = re.match(r'^(\d+)\s*(lakh|laz|karod|crore|haazar|hazaar|hazr)?$', text, re.IGNORECASE)
    if match:
        num = int(match.group(1))
        scale = match.group(2)
        if scale:
            scale = scale.lower()
            if scale in ['lakh', 'laz']:
                return num * 100000
            elif scale in ['karod', 'crore']:
                return num * 10000000
            elif scale in ['haazar', 'hazaar', 'hazr']:
                return num * 1000
        return num
    
    words = text.replace(',', ' ').replace('-', ' ').split()
    total = 0
    current = 0
    
    for word in words:
        word = word.lower().strip()
        if not word:
            continue
        
        if word in SCALE_WORDS:
            if current > 0:
                total += current * SCALE_WORDS[word]
                current = 0
            else:
                total += SCALE_WORDS[word]
        elif word in HINDI_NUM_WORDS:
            current += HINDI_NUM_WORDS[word]
        elif word.isdigit():
            current += int(word)
    
    total += current
    
    if total > 0:
        return total
    
    return None


def extract_amount(text: str) -> int | None:
    """Extract money amount from text. Looks for amount patterns."""
    if not text:
        return None
    
    # Try to find: "500000", "5,00,000", "5 lakh", "panch lakh", etc.
    # First normalize text
    normalized = text.lower()
    
    # Look for lakh/haazar patterns with numbers
    match = re.search(r'(\d+)\s*(lakh|laz|haazar|hazaar)', normalized)
    if match:
        num = int(match.group(1))
        scale = match.group(2).lower()
        if scale in ['lakh', 'laz']:
            return num * 100000
        else:
            return num * 1000
    
    # Look for pura digit amount
    match = re.search(r'(\d{4,})', normalized.replace(',', ''))
    if match:
        return int(match.group(1))
    
    # Try Hindi word parsing
    return parse_hindi_number(text)


def extract_tenure(text: str) -> int | None:
    """Extract tenure in years from text. Looks for "1 saal", "2 saal", etc."""
    if not text:
        return None
    
    text = text.lower()
    
    # Look for "X saal" or "X sal"
    match = re.search(r'(\d+)\s*(saal|sal|saalo|salo)', text)
    if match:
        return int(match.group(1))
    
    # Handle Hindi words for years
    tenure_words = {
        "ek": 1,
        "do": 2,
        "teen": 3,
        "char": 4,
        "paanch": 5,
        "chah": 6,
        "saath": 7,
        "aath": 8,
        "nau": 9,
        "das": 10,
    }
    
    for word, value in tenure_words.items():
        pattern = rf'\b{word}\s*(saal|sal)\b'
        if re.search(pattern, text):
            return value
    
    return None