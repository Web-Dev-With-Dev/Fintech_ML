from fastapi import APIRouter, Depends
from ..schemas import LoanCheckRequest, LoanCheckResponse, ScamVerdict
from ..dependencies import ModelRegistry, get_model_registry

router = APIRouter(prefix="/analyze", tags=["Loan Analysis"])

LOAN_TRANSLATIONS = {
    'regulatory_note_scam': {
        'hi': 'चेतावनी: भारतीय रिज़र्व बैंक (RBI) के दिशानिर्देशों के अनुसार कोई भी डिजिटल लोन ऐप पहले से एडवांस प्रोसेसिंग फीस नहीं मांग सकता और न ही आपके फोन कांटेक्ट लिस्ट चुरा सकता है।',
        'en': 'WARNING: RBI guidelines mandate that no digital lending platform can collect upfront processing fees or scrape phone contact lists.',
        'hinglish': 'WARNING: RBI rules ke according koi bhi digital loan app pehle se advance processing fee nahi maang sakta aur aapke phone contacts scrape nahi kar sakta.',
        'ta': 'எச்சரிக்கை: ஆர்பிஐ விதிகளின்படி எந்த டிஜிட்டல் கடன் செயலியும் முன்பணம் கேட்க முடியாது.',
        'te': 'హెచ్చరిక: RBI మార్గదర్శకాల ప్రకారం డిజిటల్ లోన్ యాప్‌లు ముందస్తు ప్రాసెసింగ్ ఫీజును వసూలు చేయకూడదు.',
        'bn': 'সতর্কতা: আরবিআই নিয়ম নির্দেশিকা অনুসারে কোনো ডিজিটাল লোন অ্যাপ অগ্রিম প্রসেসিং ফি দাবি করতে পারে না।',
        'mr': 'चेतावणी: आरबीआय नियमांनुसार कोणतेही डिजिटल कर्ज ॲप आगाऊ प्रक्रिया शुल्क मागू शकत नाही.',
        'gu': 'ચેતવણી: RBI નિયમો મુજબ કોઈપણ ડિજિટલ લોન એપ પહેલાથી એડવાન્સ પ્રોસેસિંગ ફી માંગી શકતી નથી.'
    },
    'regulatory_note_safe': {
        'hi': 'ऋण लेने से पहले हमेशा सत्यापित करें कि ऋणदाता RBI में पंजीकृत NBFC है या नहीं।',
        'en': 'Always verify if the lender is an RBI-registered NBFC before taking a loan.',
        'hinglish': 'Loan lene se pehle hamesha verify karein ki lender RBI-registered NBFC hai ya nahi.'
    },
    'flags': {
        'advance_fee': {
            'hi': 'ऋण वितरण से पहले ही एडवांस प्रोसेसिंग फीस की मांग की गई',
            'en': 'Advance processing fee demanded before loan disbursement',
            'hinglish': 'Loan dene se pehle advance processing fee maangi gayi'
        },
        'no_cibil': {
            'hi': 'बिना किसी KYC या क्रेडिट जांच के तुरंत लोन का झूठा दावा',
            'en': 'Unrealistic instant loan offer skipping mandatory KYC/credit check',
            'hinglish': 'Bina KYC ya credit check ke instant loan ka jhootha offer'
        },
        'device_access': {
            'hi': 'अनुचित डिवाइस अनुमतियों (संपर्क/फोटो) का अनुरोध किया गया',
            'en': 'Requests excessive device permissions (contacts/photos)',
            'hinglish': 'Excessive device permissions (contacts/photos) maangi gayi'
        },
        'unregistered_app': {
            'hi': 'अनधिकृत गैर-बैंकिंग वित्तीय कंपनी (NBFC) ऐप नाम पैटर्न',
            'en': 'Unregistered NBFC app name pattern detected',
            'hinglish': 'Unregistered NBFC app name pattern detected'
        }
    }
}

@router.post("/loan", response_model=LoanCheckResponse)
async def analyze_loan(
    payload: LoanCheckRequest,
    registry: ModelRegistry = Depends(get_model_registry)
) -> LoanCheckResponse:
    text = (payload.offer_text or "").lower()
    app_name = (payload.app_name or "").lower()
    lang = payload.get_language()

    flag_keys = []
    if any(w in text for w in ["advance", "processing fee", "upfront", "fee"]):
        flag_keys.append("advance_fee")
    if any(w in text for w in ["cibil", "no cibil", "no verification", "instant 5 mins"]):
        flag_keys.append("no_cibil")
    if any(w in text for w in ["contact", "contacts", "gallery", "access"]):
        flag_keys.append("device_access")
    if any(w in app_name for w in ["quick", "fast", "pocket", "cash", "rupee"]):
        flag_keys.append("unregistered_app")

    warning_flags = []
    for fk in flag_keys:
        f_dict = LOAN_TRANSLATIONS['flags'].get(fk, {})
        loc_f = f_dict.get(lang, f_dict.get('en', fk))
        warning_flags.append(loc_f)

    if len(warning_flags) >= 2:
        risk_score = 0.92
        verdict = ScamVerdict.SCAM
    elif len(warning_flags) == 1:
        risk_score = 0.65
        verdict = ScamVerdict.SUSPICIOUS
    else:
        risk_score = 0.10
        verdict = ScamVerdict.SAFE

    if verdict in [ScamVerdict.SCAM, ScamVerdict.SUSPICIOUS]:
        notes = LOAN_TRANSLATIONS['regulatory_note_scam']
        reg_note = notes.get(lang, notes['en'])
    else:
        notes = LOAN_TRANSLATIONS['regulatory_note_safe']
        reg_note = notes.get(lang, notes['en'])

    return LoanCheckResponse(
        verdict=verdict,
        confidence=0.90 if verdict != ScamVerdict.SAFE else 0.95,
        risk_score=risk_score,
        warning_flags=warning_flags,
        regulatory_note=reg_note
    )


