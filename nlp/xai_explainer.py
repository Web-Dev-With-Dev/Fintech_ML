import numpy as np

try:
    import shap
except ImportError:
    shap = None

EXPLANATION_TEMPLATES = {
    'otp_keyword': {
        'hi': 'OTP मांगा गया है (यह बैंक कभी नहीं मांगता)',
        'en': 'OTP was requested (banks never ask for this)',
        'hinglish': 'OTP maanga gaya hai (bank kabhi nahi maangta)',
        'ta': 'OTP கேட்கப்பட்டது (வங்கி இதை ஒருபோதும் கேட்காது)',
        'te': 'OTP అడిగారు (బ్యాంకు ఎప్పుడూ అడగదు)',
        'bn': 'OTP চাওয়া হয়েছে (ব্যাঙ্ক কখনও এটি চায় না)',
        'mr': 'OTP विचारला आहे (बँक कधीही विचारत नाही)',
        'gu': 'OTP માંગવામાં આવ્યો છે (બેંક ક્યારેય માંગતી નથી)'
    },
    'urgent_tone': {
        'hi': 'संदेश में जल्दबाजी दिखाई गई है (धोखेबाज अक्सर ऐसा करते हैं)',
        'en': 'The message shows urgency (scammers often do this)',
        'hinglish': 'Message me jaldbaazi dikhai gayi hai (scammers aesa karte hai)',
        'ta': 'செய்தி அவசரத்தைக் காட்டுகிறது',
        'te': 'సందేశం అత్యవసరాన్ని చూపుతుంది',
        'bn': 'বার্তায় তাড়া দেখানো হয়েছে',
        'mr': 'संदेशात घाई दाखवली आहे',
        'gu': 'સંદેશમાં ઉતાવળ બતાવવામાં આવી છે'
    },
    'contains_url': {
        'hi': 'संदेश में एक संदिग्ध लिंक है',
        'en': 'The message contains a suspicious link',
        'hinglish': 'Message me ek suspicious link hai',
        'ta': 'செய்தியில் சந்தேகத்திற்குரிய இணைப்பு உள்ளது',
        'te': 'సందేశంలో అనుமாనాస్పద లింక్ ఉంది',
        'bn': 'বার্তায় একটি সন্দেহজনক লিঙ্ক রয়েছে',
        'mr': 'संदेशात संशयास्पद लिंक आहे',
        'gu': 'સંદેશમાં શંકાસ્પદ લિંક છે'
    },
    'kyc_expiry': {
        'hi': 'KYC खत्म होने की झूठी चेतावनी',
        'en': 'False warning about KYC expiry',
        'hinglish': 'KYC expire hone ki jhoothi warning',
        'ta': 'KYC காலாவதியாகும் என்ற தவறான எச்சரிக்கை',
        'te': 'KYC గడువు ముగిసిందనే తప్పుడు హెచ్చరిక',
        'bn': 'KYC মেয়াদ শেষ হওয়ার মিথ্যা সতর্কতা',
        'mr': 'KYC संपण्याची खोटी चेतावणी',
        'gu': 'KYC સમાપ્ત થવાની ખોટી ચેતવણી'
    },
    'account_blocked': {
        'hi': 'खाता ब्लॉक होने का डर दिखाया गया है',
        'en': 'Threat of account being blocked',
        'hinglish': 'Account block hone ka darr dikhaya gaya hai',
        'ta': 'கணக்கு முடக்கப்படும் என்ற அச்சுறுத்தல்',
        'te': 'ఖాతా బ్లాక్ చేయబడుతుందనే భయం',
        'bn': 'অ্যাকাউন্ট ব্লক হওয়ার ভয় দেখানো হয়েছে',
        'mr': 'खाते ब्लॉक होण्याची भीती दाखवली आहे',
        'gu': 'એકાઉન્ટ બ્લોક થવાનો ડર બતાવવામાં આવ્યો છે'
    },
    'lottery_won': {
        'hi': 'लॉटरी जीतने का झूठा दावा',
        'en': 'False claim of winning a lottery',
        'hinglish': 'Lottery jeetne ka jhootha dawa',
        'ta': 'லாட்டரி வென்றதாக தவறான கூற்று',
        'te': 'లాటరీ గెలిచినట్లు తప్పుడు దావా',
        'bn': 'লটারি জেতার মিথ্যা দাবি',
        'mr': 'लॉटरी जिंकण्याचा खोटा दावा',
        'gu': 'લોટરી જીતવાનો ખોટો દાવો'
    },
    'unknown_sender': {
        'hi': 'अज्ञात नंबर से संदेश आया है',
        'en': 'Message from an unknown number',
        'hinglish': 'Unknown number se message aaya hai',
        'ta': 'தெரியாத எண்ணிலிருந்து செய்தி',
        'te': 'తెలియని నంబర్ నుండి సందేశం',
        'bn': 'অজানা নম্বর থেকে বার্তা',
        'mr': 'अज्ञात क्रमांकावरून संदेश',
        'gu': 'અજાણ્યા નંબરથી સંદેશ'
    },
    'high_amount': {
        'hi': 'बड़ी रकम का लालच दिया गया है',
        'en': 'Temptation of a large amount of money',
        'hinglish': 'Badi rakam ka lalach diya gaya hai',
        'ta': 'அதிக பணத்தின் தூண்டுதல்',
        'te': 'పెద్ద మొత్తంలో డబ్బు ప్రలోభం',
        'bn': 'বিপুল পরিমাণ অর্থের প্রলোভন',
        'mr': 'मोठ्या रकमेचे आमिष दाखवले आहे',
        'gu': 'મોટી રકમની લાલચ આપવામાં આવી છે'
    },
    'pan_update': {
        'hi': 'PAN कार्ड अपडेट करने को कहा गया है',
        'en': 'Asked to update PAN card',
        'hinglish': 'PAN card update karne ko kaha gaya hai',
        'ta': 'பான் கார்டை புதுப்பிக்கச் சொன்னார்கள்',
        'te': 'పాన్ కార్డ్ అప్‌డేట్ చేయమన్నారు',
        'bn': 'প্যান কার্ড আপডেট করতে বলা হয়েছে',
        'mr': 'पॅन कार्ड अपडेट करण्यास सांगितले आहे',
        'gu': 'પાન કાર્ડ અપડેટ કરવાનું કહ્યું છે'
    },
    'aadhaar_link': {
        'hi': 'आधार लिंक करने का बहाना',
        'en': 'Pretext of linking Aadhaar',
        'hinglish': 'Aadhaar link karne ka bahana',
        'ta': 'ஆதாரை இணைக்கும் சாக்கு',
        'te': 'ఆధార్ లింక్ చేయాలనే సాకు',
        'bn': 'আধার লিঙ্ক করার অজুহাত',
        'mr': 'आधार लिंक करण्याचे निमित्त',
        'gu': 'આધાર લિંક કરવાનું બહાનું'
    },
    'app_download': {
        'hi': 'अज्ञात ऐप डाउनलोड करने को कहा गया है',
        'en': 'Asked to download an unknown app',
        'hinglish': 'Unknown app download karne ko kaha gaya hai',
        'ta': 'தெரியாத செயலியை பதிவிறக்கச் சொன்னார்கள்',
        'te': 'తెలియని యాప్‌ను డౌన్‌లోడ్ చేయమన్నారు',
        'bn': 'অজানা অ্যাপ ডাউনলোড করতে বলা হয়েছে',
        'mr': 'अज्ञात अॅप डाउनलोड करण्यास सांगितले आहे',
        'gu': 'અજાણી એપ ડાઉનલોડ કરવાનું કહ્યું છે'
    },
    'job_offer': {
        'hi': 'फर्जी नौकरी का प्रस्ताव',
        'en': 'Fake job offer',
        'hinglish': 'Fake job offer',
        'ta': 'போலியான வேலை வாய்ப்பு',
        'te': 'నకిలీ ఉద్యోগ ఆఫర్',
        'bn': 'ভুয়া চাকরির অফার',
        'mr': 'बनावट नोकरीची ऑफर',
        'gu': 'નકલી નોકરીની ઓફર'
    },
    'crypto_mention': {
        'hi': 'क्रिप्टोकरेंसी या निवेश का जिक्र',
        'en': 'Mention of cryptocurrency or investment',
        'hinglish': 'Cryptocurrency ya investment ka zikr',
        'ta': 'கிரிப்டோகரன்சி அல்லது முதலீடு பற்றிய குறிப்பு',
        'te': 'క్రిప్టోకరెన్సీ లేదా పెట్టుబడి ప్రస్తావన',
        'bn': 'ক্রিপ্টোকারেন্সি বা বিনিয়োগের উল্লেখ',
        'mr': 'क्रिप्टोकरन्सी किंवा गुंतवणुकीचा उल्लेख',
        'gu': 'ક્રિપ્ટોકરન્સી અથવા રોકાણનો ઉલ્લેખ'
    },
    'asks_for_pin': {
        'hi': 'PIN या पासवर्ड मांगा गया है',
        'en': 'PIN or password requested',
        'hinglish': 'PIN ya password maanga gaya hai',
        'ta': 'PIN அல்லது கடவுச்சொல் கேட்கப்பட்டது',
        'te': 'PIN లేదా పాస్‌వర్డ్ అడిగారు',
        'bn': 'PIN বা পাসওয়ার্ড চাওয়া হয়েছে',
        'mr': 'PIN किंवा पासवर्ड विचारला आहे',
        'gu': 'PIN અથવા પાસવર્ડ માંગવામાં આવ્યો છે'
    },
    'suspicious_phone': {
        'hi': 'संदेश में एक संदिग्ध फोन नंबर है',
        'en': 'Message contains a suspicious phone number',
        'hinglish': 'Message me ek suspicious phone number hai',
        'ta': 'செய்தியில் சந்தேகத்திற்குரிய தொலைபேசி எண் உள்ளது',
        'te': 'సందేశంలో అనుమానాస్పద ఫోన్ నంబర్ ఉంది',
        'bn': 'বার্তায় একটি সন্দেহজনক ফোন নম্বর রয়েছে',
        'mr': 'संदेशात संशयास्पद फोन नंबर आहे',
        'gu': 'સંદેશમાં શંકાસ્પદ ફોન નંબર છે'
    }
}

ACTION_ADVICE = {
    'hi': 'OTP या अपनी निजी जानकारी किसी को न दें। किसी भी लिंक पर क्लिक न करें। अगर आपके साथ धोखाधड़ी हुई है, तो तुरंत 1930 पर कॉल करें।',
    'en': 'Do not share OTP or personal details. Do not click on any links. If you suspect fraud, call 1930 immediately.',
    'hinglish': 'OTP ya personal details share na karein. Kisi link par click na karein. Fraud hone par turant 1930 par call karein.',
    'ta': 'OTP அல்லது தனிப்பட்ட விவரங்களை பகிர வேண்டாம். எந்த இணைப்பிலும் கிளிக் செய்ய வேண்டாம். மோசடி என சந்தேகித்தால், உடனடியாக 1930 ஐ அழைக்கவும்.',
    'te': 'OTP లేదా వ్యక్తిగత వివరాలను పంచుకోవద్దు. ఏ లింక్‌లపై క్లిక్ చేయవద్దు. మోసం అని అనుమానిస్తే, వెంటనే 1930 కు కాల్ చేయండి.',
    'bn': 'OTP বা ব্যক্তিগত বিবরণ শেয়ার করবেন পণ্ডিত হবেন না। কোনো লিঙ্কে ক্লিক করবেন না। প্রতারণার সন্দেহ হলে অবিলম্বে 1930 নম্বরে কল করুন।',
    'mr': 'OTP किंवा वैयक्तिक माहिती शेअर करू नका. कोणत्याही लिंकवर क्लिक करू नका. फसवणूक झाल्याचा संशय आल्यास, त्वरित 1930 वर कॉल करा.',
    'gu': 'OTP અથવા વ્યક્તિગત વિગતો શેર કરશો નહીં. કોઈપણ લિંક પર ક્લિક કરશો નહીં. જો તમને છેતરપિંડીની શંકા હોય, તો તરત જ 1930 પર કૉલ કરો.'
}

class VernacularExplainer:

    def __init__(self, model, feature_names: list):
        self.model = model
        self.feature_names = feature_names

        if shap and model:
            try:
                self.explainer = shap.TreeExplainer(model)
            except Exception:
                self.explainer = None
        else:
            self.explainer = None

    def explain(self, text_features: np.ndarray, raw_text: str, lang: str) -> dict:
        shap_values_dict = {}

        if self.explainer is not None:
            try:
                shap_vals = self.explainer.shap_values(text_features)
                if isinstance(shap_vals, list):
                    shap_vals = shap_vals[1]

                if len(shap_vals.shape) > 1:
                    shap_vals = shap_vals[0]

                for idx, fname in enumerate(self.feature_names):
                    shap_values_dict[fname] = float(shap_vals[idx])
            except Exception:
                shap_values_dict = self._fallback_explanation(text_features)
        else:
            shap_values_dict = self._fallback_explanation(text_features)

        vernacular_exp = self.shap_to_vernacular(shap_values_dict, lang)

        return {
            'shap_values': shap_values_dict,
            'explanation_text': vernacular_exp,
            'raw_text': raw_text
        }

    def _fallback_explanation(self, text_features: np.ndarray) -> dict:
        shap_values_dict = {}
        features = text_features[0] if len(text_features.shape) > 1 else text_features

        for idx, fname in enumerate(self.feature_names):
            val = features[idx]
            if fname in EXPLANATION_TEMPLATES and val > 0:
                shap_values_dict[fname] = 0.5
            else:
                shap_values_dict[fname] = 0.0

        return shap_values_dict

    def shap_to_vernacular(self, shap_values: dict, lang: str) -> str:
        sorted_features = sorted(shap_values.items(), key=lambda x: x[1], reverse=True)

        top_reasons = []
        for feature, importance in sorted_features:
            if importance > 0.05:
                if feature in EXPLANATION_TEMPLATES:
                    local_text = EXPLANATION_TEMPLATES[feature].get(lang, EXPLANATION_TEMPLATES[feature]['en'])
                    top_reasons.append(local_text)

            if len(top_reasons) >= 2:
                break

        if not top_reasons:
            fallback = {
                'hi': 'संदेश का पैटर्न संदिग्ध है।',
                'en': 'The message pattern is suspicious.',
                'hinglish': 'Message ka pattern suspicious hai.',
                'ta': 'செய்தி முறை சந்தேகத்திற்குரியது.',
                'te': 'సందేశం నమూనా అనుమానాస్పదంగా ఉంది.',
                'bn': 'বার্তার প্যাটার্ন সন্দেহজনক।',
                'mr': 'संदेशाचा नमुना संशयास्पद आहे.',
                'gu': 'સંદેશની પેટર્ન શંકાસ્પદ છે.'
            }
            return fallback.get(lang, fallback['en'])

        return " | ".join(top_reasons)

    def get_action_advice(self, verdict: str, lang: str) -> str:
        if verdict.lower() in ['scam', 'fraud', 'phishing']:
            return ACTION_ADVICE.get(lang, ACTION_ADVICE['en'])

        safe_advice = {
            'hi': 'यह संदेश सुरक्षित लग रहा है, फिर भी सतर्क रहें।',
            'en': 'This message appears safe, but stay alert.',
            'hinglish': 'Yeh message safe lag raha hai, par satark rahein.',
            'ta': 'இந்த செய்தி பாதுகாப்பானதாகத் தெரிகிறது, ஆனால் எச்சரிக்கையாக இருங்கள்.',
            'te': 'ఈ సందేశం సురక్షితంగా కనిపిస్తుంది, కానీ అప్రமత్తంగా ఉండండి.',
            'bn': 'এই বার্তাটি নিরাপদ বলে মনে হচ্ছে, তবে সতর্ক থাকুন।',
            'mr': 'हा संदेश सुरक्षित वाटत आहे, तरीही सतर्क राहा.',
            'gu': 'આ સંદેશ સુરક્ષિત લાગે છે, પણ સાવચેત રહો.'
        }
        return safe_advice.get(lang, safe_advice['en'])
