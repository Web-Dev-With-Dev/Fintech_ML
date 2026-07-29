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
        "ta": {
            "name": "தேசிய இணையக் குற்றப் பிரிவு",
            "description": "நிதி இணைய மோசடிகளை உடனடியாகப் புகாரளிக்கவும்."
        }
    },
    "14448": {
        "hi": {
            "name": "आरबीआई लोकपाल (Ombudsman)",
            "description": "बैंकों और एनबीएफसी के खिलाफ शिकायतों का निवारण करें।"
        }
    },
    "1800-120-1740": {
        "hi": {
            "name": "एनपीसीआई हेल्पलाइन",
            "description": "यूपीआई और डिजिटल भुगतान संबंधी समस्याओं के लिए।"
        }
    }
}

def get_target_lang(lang: Optional[str] = None, language: Optional[str] = None) -> str:
    return lang or language or "en"

def translate_helpline(h: HelplineInfo, target_lang: str) -> HelplineInfo:
    if target_lang in ["hi", "ta"] and h.number in HELPLINE_TRANSLATIONS:
        t_data = HELPLINE_TRANSLATIONS[h.number].get(target_lang, {})
        return HelplineInfo(
            number=h.number,
            name=t_data.get("name", h.name),
            description=t_data.get("description", h.description),
            available_24x7=h.available_24x7
        )
    return h

@router.get("", response_model=List[HelplineInfo])
async def get_helplines(
    lang: Optional[str] = Query(None),
    language: Optional[str] = Query(None)
) -> List[HelplineInfo]:
    target_lang = get_target_lang(lang, language)
    return [translate_helpline(h, target_lang) for h in NATIONAL_HELPLINES]

@router.get("/{state}", response_model=List[HelplineInfo])
async def get_state_helplines(
    state: str,
    lang: Optional[str] = Query(None),
    language: Optional[str] = Query(None)
) -> List[HelplineInfo]:
    target_lang = get_target_lang(lang, language)
    base_helplines = NATIONAL_HELPLINES.copy()
    state_lower = state.lower()
    if state_lower in STATE_CYBER_CELLS:
        base_helplines.append(STATE_CYBER_CELLS[state_lower])

    return [translate_helpline(h, target_lang) for h in base_helplines]

