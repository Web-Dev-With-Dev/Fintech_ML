from fastapi import APIRouter, Query
from typing import List, Optional
from ..schemas import HelplineInfo

router = APIRouter(prefix="/helplines", tags=["Helplines"])

NATIONAL_HELPLINES = [
    HelplineInfo(
        number="1930",
        name="National Cyber Crime Reporting Portal",
        description="Report financial cyber fraud immediately.",
        available_24x7=True
    ),
    HelplineInfo(
        number="14448",
        name="RBI Ombudsman",
        description="Resolve grievances against banks and NBFCs.",
        available_24x7=False
    ),
    HelplineInfo(
        number="1800-120-1740",
        name="NPCI Helpline",
        description="For UPI and digital payment related issues.",
        available_24x7=True
    )
]

STATE_CYBER_CELLS = {
    "maharashtra": HelplineInfo(
        number="022-22822273",
        name="Maharashtra Cyber Cell",
        description="State specific cyber crime reporting.",
        available_24x7=True
    ),
    "karnataka": HelplineInfo(
        number="112",
        name="Karnataka Police Cyber Division",
        description="State specific emergency and cyber division.",
        available_24x7=True
    )
}

HELPLINE_TRANSLATIONS = {
    "1930": {
        "hi": {
            "name": "राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल",
            "description": "वित्तीय साइबर धोखाधड़ी की तुरंत 24x7 रिपोर्ट करें।"
        },
        "bn": {
            "name": "জাতীয় সাইবার অপরাধ রিপোর্টিং পোর্টাল",
            "description": "অবিলম্বে আর্থিক সাইবার জালিয়াতির রিপোর্ট করুন (২৪x৭)।"
        },
        "mr": {
            "name": "राष्ट्रीय सायबर गुन्हा नोंदणी पोर्टल",
            "description": "आर्थिक सायबर फसवणुकीची त्वरित २४x७ तक्रार करा."
        },
        "gu": {
            "name": "રાષ્ટ્રીય સાયબર ક્રાઇમ રિપોર્ટિંગ પોર્ટલ",
            "description": "નાણાકીય સાયબર છેતરપિંડીની તરત જ ૨૪x૭ રિપોર્ટ કરો."
        },
        "hinglish": {
            "name": "National Cyber Crime Reporting Portal",
            "description": "Financial cyber fraud ki turant 24x7 report maarein."
        },
        "ta": {
            "name": "தேசிய இணையக் குற்றப் பிரிவு",
            "description": "நிதி இணைய மோசடிகளை உடனடியாகப் புகாரளிக்கவும்."
        },
        "te": {
            "name": "జాతీయ సైబర్ నేరాల నివేదిక పోర్టల్",
            "description": "ఆర్థిక సైబర్ మోసాన్ని వెంటనే 24x7 నివేదించండి."
        }
    },
    "14448": {
        "hi": {
            "name": "आरबीआई लोकपाल (Ombudsman)",
            "description": "बैंकों और एनबीएफसी के खिलाफ शिकायतों का निवारण करें।"
        },
        "bn": {
            "name": "আরবিআই ওম্বুডসম্যান (RBI Ombudsman)",
            "description": "ব্যাঙ্ক এবং এনবিএফসি-র বিরুদ্ধে অভিযোগ প্রতিকার করুন।"
        },
        "mr": {
            "name": "आरबीआय लोकपाल (Ombudsman)",
            "description": "बँका आणि NBFCs विरुद्ध तक्रारींचे निवारण करा."
        },
        "gu": {
            "name": "આરબીઆઈ લોકપાલ (Ombudsman)",
            "description": "બેંકો અને એનબીએફસી સામેની ફરિયાદોનું નિવારણ કરો."
        },
        "hinglish": {
            "name": "RBI Ombudsman",
            "description": "Banks aur NBFCs ke khilaaf complaint resolve karein."
        },
        "ta": {
            "name": "ஆர்பிஐ குறைதீர்ப்பாளர்",
            "description": "வங்கிகள் மற்றும் என்பிஎஃப்சிகளுக்கு எதிரான புகார்களைத் தீர்க்கவும்."
        },
        "te": {
            "name": "ఆర్బీఐ ఓంబుడ్స్‌మన్",
            "description": "బ్యాంకులు మరియు ఎన్‌బిఎఫ్‌సిలపై ఫిర్యాదులను పరిష్కరించండి."
        }
    },
    "1800-120-1740": {
        "hi": {
            "name": "एनपीसीआई हेल्पलाइन",
            "description": "यूपीआई और डिजिटल भुगतान संबंधी समस्याओं के लिए।"
        },
        "bn": {
            "name": "এনপিসিআই হেল্পলাইন (NPCI)",
            "description": "ইউপিআই এবং ডিজিটাল পেমেন্ট সংক্রান্ত সমস্যার জন্য।"
        },
        "mr": {
            "name": "என்சிபிഐ हेल्पलाइन",
            "description": "यूपीआय आणि डिजिटल पेमेंट संबंधित समस्यांसाठी."
        },
        "gu": {
            "name": "એનપીસીઆઈ હેલ્પલાઈન",
            "description": "યુપીઆઈ અને ડિજિટલ ચૂકવણી સંબંધિત સમસ્યાઓ માટે."
        },
        "hinglish": {
            "name": "NPCI Helpline",
            "description": "UPI aur digital payment issues ke liye 24x7 helpline."
        },
        "ta": {
            "name": "என்.பி.சி.ஐ உதவி எண்",
            "description": "யுபிஐ மற்றும் டிஜிட்டல் கட்டணச் சிக்கல்களுக்கு."
        },
        "te": {
            "name": "ఎన్‌పిసిఐ హెల్ప్‌లైన్",
            "description": "యుపిఐ మరియు డిజిటల్ చెల్లింపు సమస్యల కోసం."
        }
    }
}

def get_target_lang(lang: Optional[str] = None, language: Optional[str] = None) -> str:
    return lang or language or "en"

def translate_helpline(h: HelplineInfo, target_lang: str) -> HelplineInfo:
    if h.number in HELPLINE_TRANSLATIONS and target_lang in HELPLINE_TRANSLATIONS[h.number]:
        t_data = HELPLINE_TRANSLATIONS[h.number][target_lang]
        return HelplineInfo(
            number=h.number,
            name=t_data.get("name", h.name),
            description=t_data.get("description", h.description),
            available_24x7=h.available_24x7
        )
    return h


@router.get("", response_model=List[HelplineInfo])
async def get_helplines(
    lang: Optional[str] = None,
    language: Optional[str] = None
) -> List[HelplineInfo]:
    target_lang = get_target_lang(lang, language)
    return [translate_helpline(h, target_lang) for h in NATIONAL_HELPLINES]

@router.get("/{state}", response_model=List[HelplineInfo])
async def get_state_helplines(
    state: str,
    lang: Optional[str] = None,
    language: Optional[str] = None
) -> List[HelplineInfo]:
    target_lang = get_target_lang(lang, language)
    base_helplines = NATIONAL_HELPLINES.copy()
    state_lower = state.lower()
    if state_lower in STATE_CYBER_CELLS:
        base_helplines.append(STATE_CYBER_CELLS[state_lower])

    return [translate_helpline(h, target_lang) for h in base_helplines]


