import re

HINDI_NUM_WORDS = {
    # Romanized
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5, "chah": 6, "saath": 7, "aath": 8, "nau": 9, "das": 10,
    "gyaarah": 11, "baarah": 12, "teerah": 13, "choudah": 14, "pandrah": 15, "solah": 16, "satrah": 17, "atharah": 18, "unnees": 19, "bees": 20,
    "tees": 30, "chaalis": 40, "pachaas": 50, "saath": 60, "sattar": 70, "assi": 80, "nabbe": 90, "sau": 100,
    # Devanagari
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "छह": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10,
    "ग्यारह": 11, "बारह": 12, "तेरह": 13, "चौदह": 14, "पंद्रह": 15, "सोलह": 16, "सत्रह": 17, "अठारह": 18, "उन्नीस": 19, "बीस": 20,
    "तीस": 30, "चालीस": 40, "पचास": 50, "साठ": 60, "सत्तर": 70, "अस्सी": 80, "नब्बे": 90, "सौ": 100,
}

SCALE_WORDS = {
    "hazaar": 1000, "hazara": 1000, "hazr": 1000, "hazar": 1000,
    "lakh": 100000, "laak": 100000, "laz": 100000,
    "karod": 10000000, "crore": 10000000,
    "हज़ार": 1000, "हजार": 1000,
    "लाख": 100000, "लाक": 100000,
    "करोड़": 10000000, "करोड": 10000000,
}

def parse_hindi_number(text: str) -> int | None:
    if not text:
        return None
    
    text = text.lower().strip()
    
    # Handle "5 lakh", "5laz", "5 लाख", "एक लाख"
    match = re.search(r'(\d+|ek|do|teen|char|paanch|chah|saath|aath|nau|das|एक|दो|तीन|चार|पांच|छह|सात|आठ|नौ|दस)\s*(lakh|laak|laz|karod|crore|haazar|hazaar|hazr|hazar|लाख|लाक|हज़ार|हजार|करोड़|करोड)', text, re.IGNORECASE)
    if match:
        num_str = match.group(1)
        scale_str = match.group(2)
        
        if num_str.isdigit():
            num = int(num_str)
        else:
            num = HINDI_NUM_WORDS.get(num_str.lower(), 1)
            
        scale = SCALE_WORDS.get(scale_str.lower(), 1)
        return num * scale
        
    # Check for pure digits
    digit_match = re.search(r'(\d[0-9,]*)', text)
    if digit_match:
        digits_only = digit_match.group(1).replace(',', '')
        try:
            return int(digits_only)
        except ValueError:
            pass

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
    if not text:
        return None
    return parse_hindi_number(text)

def extract_tenure(text: str) -> int | None:
    if not text:
        return None
    text = text.lower()
    
    # Look for "X saal", "X sal", "X साल", "X वर्ष"
    match = re.search(r'(\d+|ek|do|teen|char|paanch|chah|saath|aath|nau|das|एक|दो|तीन|चार|पांच|छह|सात|आठ|नौ|दस)\s*(saal|sal|saalo|salo|साल|सालों|वर्ष)', text)
    if match:
        num_str = match.group(1)
        if num_str.isdigit():
            return int(num_str)
        else:
            return HINDI_NUM_WORDS.get(num_str.lower())
            
    return None
