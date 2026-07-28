import re

class Transliterator:

    def __init__(self):
        self.mapping = {
            'otp': 'ओटीपी', 'khata': 'खाता', 'band': 'बंद', 'paisa': 'पैसा',
            'bank': 'बैंक', 'account': 'अकाउंट', 'block': 'ब्लॉक', 'kyc': 'केवाईसी',
            'update': 'अपडेट', 'link': 'लिंक', 'click': 'क्लिक', 'urgent': 'अर्जेंट',
            'password': 'पासवर्ड', 'pin': 'पिन', 'cvv': 'सीवीवी', 'debit': 'डेबिट',
            'credit': 'क्रेडिट', 'card': 'कार्ड', 'atm': 'एटीएम', 'cash': 'कैश',
            'lottery': 'लॉटरी', 'prize': 'इनाम', 'won': 'जीता', 'claim': 'क्लेम',
            'winner': 'विजेता', 'free': 'मुफ्त', 'gift': 'गिफ्ट', 'offer': 'ऑफर',
            'alert': 'अलर्ट', 'warning': 'चेतावनी', 'suspend': 'सस्पेंड', 'expire': 'एक्सपायर',
            'validity': 'वैधता', 'recharge': 'रिचार्ज', 'bill': 'बिल', 'pay': 'पे',
            'payment': 'पेमेंट', 'send': 'भेजें', 'receive': 'प्राप्त', 'money': 'पैसे',
            'transfer': 'ट्रांसफर', 'fund': 'फंड', 'rupee': 'रुपये', 'rs': 'रुपये',
            'loan': 'लोन', 'approve': 'अप्रूव', 'emi': 'ईएमआई', 'interest': 'ब्याज',
            'tax': 'टैक्स', 'refund': 'रिफंड', 'return': 'रिटर्न', 'income': 'इनकम',
            'salary': 'सैलरी', 'job': 'जॉब', 'work': 'काम', 'home': 'घर',
            'call': 'कॉल', 'number': 'नंबर', 'message': 'मैसेज', 'sms': 'एसएमएस',
            'whatsapp': 'व्हाट्सएप', 'app': 'ऐप', 'download': 'डाउनलोड', 'install': 'इंस्टॉल',
            'login': 'लॉगिन', 'register': 'रजिस्टर', 'verify': 'वेरिफाई', 'verification': 'वेरिफिकेशन',
            'aadhaar': 'आधार', 'pan': 'पैन', 'document': 'डॉक्यूमेंट', 'detail': 'डिटेल',
            'share': 'शेयर', 'forward': 'फॉरवर्ड', 'scan': 'स्कैन', 'qr': 'क्यूआर',
            'code': 'कोड', 'online': 'ऑनलाइन', 'internet': 'इंटरनेट', 'digital': 'डिजिटल',
            'wallet': 'वॉलेट', 'upi': 'यूपीआई', 'paytm': 'पेटीएम', 'phonepe': 'फोनपे',
            'gpay': 'जीपे', 'google': 'गूगल', 'customer': 'कस्टमर', 'care': 'केयर',
            'support': 'सपोर्ट', 'help': 'हेल्प', 'helpline': 'हेल्पलाइन', 'officer': 'ऑफिसर',
            'manager': 'मैनेजर', 'police': 'पुलिस', 'crime': 'क्राइम', 'cyber': 'साइबर',
            'fraud': 'फ्रॉड', 'scam': 'स्कैम', 'fake': 'फेक', 'real': 'रियल',
            'safe': 'सेफ', 'secure': 'सिक्योर', 'security': 'सिक्योरिटी', 'risk': 'रिस्क',
            'danger': 'खतरा', 'stop': 'स्टॉप', 'cancel': 'कैंसिल', 'confirm': 'कंफर्म',
            'success': 'सक्सेस', 'fail': 'फेल', 'error': 'एरर', 'problem': 'प्रॉब्लम',
            'issue': 'इशू', 'resolve': 'रिसॉल्व', 'fix': 'फिक्स', 'time': 'टाइम',
            'today': 'आज', 'tomorrow': 'कल', 'now': 'अभी', 'immediately': 'तुरंत',
            'fast': 'फास्ट', 'quick': 'क्विक', 'hurry': 'जल्दी', 'late': 'लेट',
            'dear': 'डियर', 'sir': 'सर', 'madam': 'मैडम', 'user': 'यूजर',
            'client': 'क्लाइंट', 'member': 'मेंबर', 'friend': 'दोस्त', 'family': 'परिवार',
            'aap': 'आप', 'aapka': 'आपका', 'aapki': 'आपकी', 'mera': 'मेरा',
            'meri': 'मेरी', 'hum': 'हम', 'hamara': 'हमारा', 'yeh': 'यह',
            'woh': 'वह', 'kya': 'क्या', 'kyon': 'क्यों', 'kaise': 'कैसे',
            'kahan': 'कहां', 'kab': 'कब', 'kaun': 'कौन', 'kuch': 'कुछ',
            'koi': 'कोई', 'sab': 'सब', 'bohot': 'बहुत', 'kam': 'कम',
            'zyada': 'ज्यादा', 'accha': 'अच्छा', 'bura': 'बुरा', 'sahi': 'सही',
            'galat': 'गलत', 'haan': 'हां', 'nahi': 'नहीं', 'mat': 'मत',
            'karo': 'करो', 'karna': 'करना', 'kiya': 'किया', 'hoga': 'होगा',
            'hai': 'है', 'tha': 'था', 'hume': 'हमें', 'unhe': 'उन्हें',
            'mujhe': 'मुझे', 'tujhe': 'तुझे', 'apna': 'अपना', 'apni': 'अपनी',
            'liye': 'लिए', 'diya': 'दिया', 'liya': 'लिया', 'aaya': 'आया',
            'gaya': 'गया', 'bola': 'बोला', 'kaha': 'कहा', 'suna': 'सुना',
            'dekha': 'देखा', 'socha': 'सोचा', 'samjha': 'समझा', 'jaana': 'जाना',
            'aana': 'आ आना', 'khana': 'खाना', 'peena': 'पीना', 'sona': 'सोना',
            'uthna': 'उठना', 'baithna': 'बैठना', 'chalna': 'चलना', 'rukna': 'रुकना',
            'bhaagna': 'भागना', 'girna': 'गिरना', 'khelna': 'खेलना', 'padhna': 'पढ़ना',
            'likhna': 'लिखना', 'bolna': 'बोलना', 'sunna': 'सुनना', 'dekhna': 'देखना',
            'hona': 'होना', 'dena': 'देना', 'lena': 'लेना',
            'chahiye': 'चाहिए', 'sakta': 'सकता', 'payega': 'पाएगा', 'raha': 'रहा',
            'rahi': 'रही', 'rahe': 'रहे', 'chuka': 'चुका', 'chuki': 'चुकी'
        }

    def romanized_hindi_to_devanagari(self, text: str) -> str:
        if not text:
            return ""

        words = text.split()
        converted_words = []
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word.lower())

            if clean_word in self.mapping:
                devanagari_word = self.mapping[clean_word]
                lower_word = word.lower()
                idx = lower_word.find(clean_word)
                if idx != -1:
                    prefix = word[:idx]
                    suffix = word[idx + len(clean_word):]
                    converted_words.append(f"{prefix}{devanagari_word}{suffix}")
                else:
                    converted_words.append(devanagari_word)
            else:
                converted_words.append(word)

        return ' '.join(converted_words)

    def detect_hinglish(self, text: str) -> float:
        if not text:
            return 0.0

        words = set([re.sub(r'[^\w\s]', '', w.lower()) for w in text.split()])
        if not words:
            return 0.0

        mapped_words = set(self.mapping.keys())
        overlap = words.intersection(mapped_words)

        score = len(overlap) / len(words)

        confidence = min(1.0, score * 1.5)
        return confidence

    def normalize_for_classification(self, text: str, target_lang: str) -> str:
        if target_lang == 'hi' and self.detect_hinglish(text) > 0.3:
            return self.romanized_hindi_to_devanagari(text)
        return text
