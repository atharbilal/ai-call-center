"""
System prompts and language-specific messages for the AI call center agent.
"""

from typing import Dict

# Supported languages and their display names
SUPPORTED_LANGUAGES = {
    "english": "English",
    "hindi": "हिन्दी (Hindi)",
    "tamil": "தமிழ் (Tamil)",
    "telugu": "తెలుగు (Telugu)",
    "bengali": "বাংলা (Bengali)",
    "marathi": "मराठी (Marathi)",
    "kannada": "ಕನ್ನಡ (Kannada)",
    "malayalam": "മലയാളം (Malayalam)",
    "gujarati": "ગુજરાતી (Gujarati)",
    "punjabi": "ਪੰਜਾਬੀ (Punjabi)",
}

# Greeting messages in each language (first thing agent says)
GREETING_MESSAGES: Dict[str, str] = {
    "english": "Hello! Thank you for calling. I'm your AI assistant. I can help you with your account, billing, orders, and more. Could you please share your registered phone number or account ID so I can pull up your details?",
    "hindi": "नमस्ते! कॉल करने के लिए धन्यवाद। मैं आपका AI असिस्टेंट हूँ। मैं आपके अकाउंट, बिलिंग, ऑर्डर और अन्य मामलों में मदद कर सकता हूँ। कृपया अपना रजिस्टर्ड फोन नंबर या अकाउंट ID बताएं।",
    "tamil": "வணக்கம்! அழைத்ததற்கு நன்றி. நான் உங்கள் AI உதவியாளர். உங்கள் கணக்கு, பில்லிங், ஆர்டர் தொடர்பான உதவி செய்ய தயாராக இருக்கிறேன். உங்கள் பதிவு செய்யப்பட்ட தொலைபேசி எண் அல்லது கணக்கு ID கொடுக்க முடியுமா?",
    "telugu": "నమస్కారం! కాల్ చేసినందుకు ధన్యవాదాలు. నేను మీ AI అసిస్టెంట్. మీ అకౌంట్, బిల్లింగ్, ఆర్డర్లకు సంబంధించిన సహాయం చేయగలను. మీ రిజిస్టర్డ్ ఫోన్ నంబర్ లేదా అకౌంట్ ID చెప్పగలరా?",
    "bengali": "নমস্কার! ফোন করার জন্য ধন্যবাদ। আমি আপনার AI সহায়ক। আপনার অ্যাকাউন্ট, বিলিং, অর্ডার সম্পর্কিত সাহায্য করতে পারব। আপনার নিবন্ধিত ফোন নম্বর বা অ্যাকাউন্ট ID জানাবেন কি?",
    "marathi": "नमस्कार! फोन केल्याबद्दल धन्यवाद. मी तुमचा AI सहाय्यक आहे. तुमच्या अकाऊंट, बिलिंग, ऑर्डर संबंधी मदत करू शकतो. तुमचा नोंदणीकृत फोन नंबर किंवा अकाऊंट ID सांगाल का?",
    "kannada": "ನಮಸ್ಕಾರ! ಕರೆ ಮಾಡಿದ್ದಕ್ಕೆ ಧನ್ಯವಾದ. ನಾನು ನಿಮ್ಮ AI ಸಹಾಯಕ. ನಿಮ್ಮ ಖಾತೆ, ಬಿಲ್ಲಿಂಗ್, ಆರ್ಡರ್ ಗಳಿಗೆ ಸಂಬಂಧಿಸಿದ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. ನಿಮ್ಮ ನೋಂದಾಯಿತ ಫೋನ್ ನಂಬರ್ ಅಥವಾ ಖಾತೆ ID ಹೇಳಬಹುದೇ?",
    "malayalam": "നമസ്കാരം! വിളിച്ചതിന് നന്ദി. ഞാൻ നിങ്ങളുടെ AI അസിസ്റ്റന്റ് ആണ്. നിങ്ങളുടെ അക്കൗണ്ട്, ബില്ലിംഗ്, ഓർഡർ എന്നിവ സംബന്ധിച്ച് സഹായിക്കാൻ തയ്യാറാണ്. നിങ്ങളുടെ ഫോൺ നമ്പർ അല്ലെങ്കിൽ അക്കൗണ്ട് ID പറയാമോ?",
    "gujarati": "નમસ્તે! ફોન કર્યા બદલ આભાર. હું તમારો AI સહાયક છું. તમારા અકાઉન્ટ, બિલિંગ, ઓર્ડર સંબંધિત મદદ કરી શકું છું. તમારો નોંધાયેલ ફોન નંબર અથવા અકાઉન્ટ ID જણાવશો?",
    "punjabi": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਫ਼ੋਨ ਕਰਨ ਲਈ ਧੰਨਵਾਦ। ਮੈਂ ਤੁਹਾਡਾ AI ਸਹਾਇਕ ਹਾਂ। ਤੁਹਾਡੇ ਅਕਾਊਂਟ, ਬਿਲਿੰਗ, ਆਰਡਰ ਨਾਲ ਸਬੰਧਤ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਰਜਿਸਟਰਡ ਫ਼ੋਨ ਨੰਬਰ ਜਾਂ ਅਕਾਊਂਟ ID ਦੱਸੋ।",
}

# Retry message when customer doesn't provide a valid ID
ID_RETRY_MESSAGES: Dict[str, str] = {
    "english": "I'm sorry, I couldn't find an account with that information. Could you please try again? Please say your 10-digit mobile number or your account ID starting with ACC.",
    "hindi": "माफ करें, उस जानकारी से कोई अकाउंट नहीं मिला। क्या आप फिर से कोशिश कर सकते हैं? कृपया अपना 10 अंकों का मोबाइल नंबर या ACC से शुरू होने वाला अकाउंट ID बोलें।",
    "tamil": "மன்னிக்கவும், அந்த தகவல்களில் கணக்கு கிடைக்கவில்லை. மீண்டும் முயற்சிக்க முடியுமா? உங்கள் 10 இலக்க மொபைல் எண் அல்லது ACC என்று தொடங்கும் கணக்கு ID சொல்லுங்கள்.",
}

# Escalation message
ESCALATION_MESSAGES: Dict[str, str] = {
    "english": "I understand this requires special attention. Let me connect you with one of our senior agents right away. Please hold for just a moment. Your reference number for this call is {call_sid}.",
    "hindi": "मैं समझता हूँ, इस मामले पर विशेष ध्यान देने की जरूरत है। मैं आपको अभी हमारे वरिष्ठ एजेंट से जोड़ता हूँ। एक पल रुकिए। इस कॉल का रेफरेंस नंबर है {call_sid}।",
    "tamil": "இது சிறப்பு கவனம் தேவைப்படும் என புரிகிறது. உடனே மூத்த அதிகாரியிடம் இணைக்கிறேன். ஒரு நிமிடம் பொறுங்கள். இந்த கால் மேற்கோள் எண் {call_sid}.",
}

# Closing message
CLOSING_MESSAGES: Dict[str, str] = {
    "english": "I'm glad I could help! Is there anything else you need assistance with today? If not, have a wonderful day!",
    "hindi": "खुशी हुई कि मैं मदद कर सका! क्या आज आपको और किसी चीज़ में मदद चाहिए? अगर नहीं, तो आपका दिन शुभ हो!",
    "tamil": "உதவி செய்ய முடிந்ததில் மகிழ்ச்சி! இன்று வேறு ஏதாவது உதவி வேண்டுமா? இல்லையென்றால், நல்ல நாளாக இருக்கட்டும்!",
}

def get_main_system_prompt(customer_data: dict, language: str) -> str:
    """
    Returns the main system prompt for the resolution stage.
    Injects customer data dynamically.
    """
    customer_name = customer_data.get("name", "the customer") if customer_data else "the customer"
    account_status = customer_data.get("status", "unknown") if customer_data else "unknown"
    balance = customer_data.get("balance_due", 0) if customer_data else 0
    plan = customer_data.get("plan", "unknown") if customer_data else "unknown"
    last_order = customer_data.get("last_order_status", "N/A") if customer_data else "N/A"
    open_tickets = customer_data.get("open_tickets", []) if customer_data else []
    
    return f"""You are a professional, empathetic, and efficient AI customer support agent on a live phone call.

CUSTOMER INFORMATION:
- Name: {customer_name}
- Account Status: {account_status}
- Plan: {plan}
- Balance Due: ₹{balance}
- Last Order Status: {last_order}
- Open Tickets: {', '.join(open_tickets) if open_tickets else 'None'}

LANGUAGE: Respond ONLY in {language}. This is critical — customer speaks {language}.

CALL BEHAVIOR RULES:
1. You are on a PHONE CALL — keep responses SHORT (2-3 sentences maximum per turn). No bullet points, no lists. Natural conversational speech only.
2. Address to customer by their first name.
3. Be warm, empathetic, and professional.
4. If account is suspended, first explain why clearly, then explain how to resolve it.
5. If balance is due, mention the amount and offer payment instructions.
6. Use the tools provided to look up information — never make up details.
7. If you cannot resolve an issue, say you are escalating to a human agent.
8. Never share any customer's data with anyone other than verified account holder.

AVAILABLE TOOLS:
- customer_lookup_tool: to fetch customer details
- order_status_tool: to check order status  
- knowledge_base_search: to find company policies and FAQs
- web_search (if available): for general information lookup

Always be human-like. Never say "As an AI..." or "I am a language model...". Just act like a helpful customer care executive."""
