"""Validation and testing utilities"""
import re
from fd_data import FD_OPTIONS


def validate_fd_option(option: dict) -> bool:
    required = ["bank", "tenure", "rate", "min_amount", "example"]
    return all(k in option for k in required)


def get_all_banks():
    return [opt["bank"] for opt in FD_OPTIONS]


def find_fd_by_bank(bank_name: str):
    for opt in FD_OPTIONS:
        if bank_name.lower() in opt["bank"].lower():
            return opt
    return None


def validate_advice_output(advice: str) -> dict:
    result = {"valid": True, "issues": []}
    
    if len(advice) > 300:
        result["issues"].append("Output too long (>300 chars)")
        result["valid"] = False
    
    banks_mentioned = []
    for bank in get_all_banks():
        if bank.lower() in advice.lower():
            banks_mentioned.append(bank)
    
    if not banks_mentioned:
        result["issues"].append("No bank names found")
        result["valid"] = False
    
    result["banks_mentioned"] = banks_mentioned
    return result


def has_hindi_text(text: str) -> bool:
    hindi_pattern = re.compile(r"[\u0900-\u097F]")
    return bool(hindi_pattern.search(text))


def count_words(text: str) -> int:
    return len(text.split())


def mock_transcribe(audio_bytes=None) -> str:
    return "मुझे 50,000 रुपये FD में रखने हैं, कहाँ रखूँ?"


def mock_fd_advice(query: str) -> str:
    return (
        "Ab aapke paas 50,000 rupees hai, toh 1 saal ke liye yeh best options hain:\n\n"
        "Bajaj Finance se aapko 8.05% se ₹4,025 milenge ek saal mein. "
        "HDFC Bank se 7.1% se ₹3,550 milenge. "
        "SBI se 6.8% se ₹3,400 milenge.\n\n"
        "Mera suggestion: Agar aapko fully safe bank chahiye toh SBI best hai - yeh government backed hai. "
        "Lekin agar aapka sabse zyada fayda chahiye, toh Bajaj Finance best rahega."
    )


def run_mock_test():
    test_query = "मुझे 50,000 FD में रखने हैं"
    
    advice = mock_fd_advice(test_query)
    validation = validate_advice_output(advice)
    
    print(f"Query: {test_query}")
    print(f"Advice: {advice}")
    print(f"Valid: {validation}")
    print(f"Has Hindi: {has_hindi_text(advice)}")
    print(f"Word count: {count_words(advice)}")
    
    return validation["valid"]


if __name__ == "__main__":
    run_mock_test()