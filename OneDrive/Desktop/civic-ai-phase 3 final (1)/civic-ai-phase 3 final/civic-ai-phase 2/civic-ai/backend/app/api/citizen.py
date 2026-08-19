from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/citizen", tags=["Citizen Experience (Phase 10A)"])

HELPLINES = [
    {
        "department": "Police",
        "category": "Emergency / Safety",
        "number": "100",
        "purpose": "Immediate police emergency assistance",
    },
    {
        "department": "Ambulance",
        "category": "Emergency / Medical",
        "number": "108",
        "purpose": "Medical emergency & ambulance dispatch",
    },
    {
        "department": "Fire & Rescue",
        "category": "Emergency / Fire",
        "number": "101",
        "purpose": "Fire, hazard, and rescue emergency",
    },
    {
        "department": "Municipal Support",
        "category": "Civic / Public Works",
        "number": "1912",
        "purpose": "Municipal civic problem & grievance reporting",
    },
]

CIVIC_DEPARTMENTS = [
    {
        "id": 1,
        "name": "Roads / Public Works Department",
        "name_ta": "நெடுஞ்சாலை / பொதுப்பணித் துறை",
        "purpose": "Handles potholes, road damage, asphalt repairs, and footpath maintenance.",
        "service_area": "City-wide road network and municipal arterial roads",
    },
    {
        "id": 2,
        "name": "Sanitation / Waste Management Department",
        "name_ta": "துப்புரவு / கழிவு மேலாண்மை துறை",
        "purpose": "Handles open garbage dumps, overflowing bins, and street cleaning.",
        "service_area": "Residential and commercial municipal sectors",
    },
    {
        "id": 3,
        "name": "Water Supply / Water Department",
        "name_ta": "குடிநீர் வழங்கல் / நீர் மேலாண்மை துறை",
        "purpose": "Handles pipe leakages, water contamination, and supply disruptions.",
        "service_area": "Urban water supply network & pipelines",
    },
    {
        "id": 4,
        "name": "Electrical / Streetlight Municipal Department",
        "name_ta": "மின்சாரம் / தெருவிளக்கு நகராட்சி துறை",
        "purpose": "Handles broken streetlights, exposed wiring, and power poles.",
        "service_area": "Public street lighting and municipal electrical grid",
    },
    {
        "id": 5,
        "name": "Storm Water / Disaster Management Department",
        "name_ta": "மழைநீர் வடிநிலம் / பேரிடர் மேலாண்மை துறை",
        "purpose": "Handles urban flooding, clogged drains, open manholes, and storm water runoff.",
        "service_area": "Low-lying zones, storm drains, and flood risk areas",
    },
]

FAQS = [
    {
        "id": 1,
        "question": "What types of civic issues can I report?",
        "question_ta": "நான் எந்த வகையான சமூகப் பிரச்சனைகளைப் புகாரளிக்கலாம்?",
        "answer": "You can report problems such as potholes, open manholes, garbage, flooding, broken streetlights, and water leakage.",
        "answer_ta": "சாலைக் குழி, திறந்த சாக்கடை, குப்பை மேடு, வெள்ளம், பழுதடைந்த தெருவிளக்கு மற்றும் குடிநீர் கசிவு போன்ற பிரச்சனைகளை நீங்கள் புகாரளிக்கலாம்.",
    },
    {
        "id": 2,
        "question": "How does Civic AI verify my report?",
        "question_ta": "சிவிக் AI எனது புகாரை எவ்வாறு சரிபார்க்கிறது?",
        "answer": "AI analyzes the submitted image, and nearby citizens may verify the issue. The system uses these inputs to assess the incident.",
        "answer_ta": "செயற்கை நுண்ணறிவு சமர்ப்பிக்கப்பட்ட புகைப்படத்தை ஆய்வு செய்கிறது, மேலும் அருகிலுள்ள குடிமக்கள் பிரச்சனையை சரிபார்க்கலாம்.",
    },
    {
        "id": 3,
        "question": "What happens after I report an issue?",
        "question_ta": "நான் புகாரளித்த பிறகு என்ன நடக்கும்?",
        "answer": "The issue is analyzed and assessed. Normal civic issues can be routed to the appropriate department, and you can track the status until resolution.",
        "answer_ta": "பிரச்சனை ஆய்வு செய்யப்பட்டு மதிப்பிடப்படுகிறது. சாதாரண சமூகப் பிரச்சனைகள் பொருத்தமான துறைக்கு அனுப்பப்பட்டு, தீர்வு வரை நிலையைக் கண்காணிக்கலாம்.",
    },
]

@router.get("/help", summary="Get configurable helpline & department information for citizens")
def get_citizen_help(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Returns helplines and department information."""
    return {
        "helplines": HELPLINES,
        "departments": CIVIC_DEPARTMENTS,
    }

@router.get("/faqs", summary="Get citizen FAQs with multi-language support")
def get_citizen_faqs() -> List[Dict[str, Any]]:
    """Returns list of frequently asked questions with English and Tamil answers."""
    return FAQS
