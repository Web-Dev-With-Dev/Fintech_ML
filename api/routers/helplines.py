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

def translate_description(desc: str, lang: str) -> str:
    if lang == 'hi':
        return desc + " (हिंदी अनुवाद)"
    return desc

@router.get("", response_model=List[HelplineInfo])
async def get_helplines(lang: Optional[str] = Query("en")) -> List[HelplineInfo]:
    translated = []
    for h in NATIONAL_HELPLINES:
        translated.append(HelplineInfo(
            number=h.number,
            name=h.name,
            description=translate_description(h.description, lang),
            available_24x7=h.available_24x7
        ))
    return translated

@router.get("/{state}", response_model=List[HelplineInfo])
async def get_state_helplines(state: str, lang: Optional[str] = Query("en")) -> List[HelplineInfo]:
    translated = []
    base_helplines = NATIONAL_HELPLINES.copy()
    state_lower = state.lower()
    if state_lower in STATE_CYBER_CELLS:
        base_helplines.append(STATE_CYBER_CELLS[state_lower])

    for h in base_helplines:
        translated.append(HelplineInfo(
            number=h.number,
            name=h.name,
            description=translate_description(h.description, lang),
            available_24x7=h.available_24x7
        ))
    return translated
