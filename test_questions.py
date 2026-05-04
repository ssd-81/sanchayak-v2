SAMPLE_QUESTIONS = [
    "Mujhe 50,000 rupaye FD mein rakhne hain, kahan rakhun?",
    "1 lakh ke liye konsa FD behtarin hai?",
    "Kitne din ke FD par sabse zyada return milta hai?",
    "Mujhe 6 mahine ke liye paisa rakhna hai",
    "Post office FD kaisa hai?",
    "Minimum kitna amount chahiye SBI FD ke liye?",
    "HDFC Bank ki FD scheme kya hai?",
    "Bajaj Finance ka FD rate kitna hai?",
]

SAMPLE_QUESTIONS_HINDI = [
    "मुझे 50,000 रुपये FD में रखने हैं, कहाँ रखूँ?",
    "1 lakh के लिए कौनसा FD बेहतर है?",
    "कितने दिन के FD पर सबसे ज्यादा return मिलता है?",
    "मुझे 6 महीने के लिए पैसा रखना है",
    "Post office FD कैसा है?",
    "Minimum कितना amount चाहिए SBI FD के लिए?",
    "HDFC Bank की FD scheme क्या है?",
    "Bajaj Finance का FD rate कितना है?",
]


def get_random_question():
    import random
    return random.choice(SAMPLE_QUESTIONS)


def get_sample_for_demo():
    return {
        "question": SAMPLE_QUESTIONS[0],
        "question_hindi": SAMPLE_QUESTIONS_HINDI[0],
        "expected_banks": ["SBI", "HDFC Bank", "Bajaj Finance"],
    }