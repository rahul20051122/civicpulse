"""
CivicPulse AI — Smart Civic Hazard Triage Platform
Tagline: Every Report Matters. Every Hazard Counts.
Challenge: AI for Better Living & Smarter Communities.

An editorial multimodal civic intelligence platform inspired by modern high-end editorial design,
powered by Google Gemini Multimodal AI, Streamlit, Plotly, and Pandas.
"""

import os
import io
import json
import uuid
import base64
import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Google GenAI SDK import with graceful fallback
try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    APIError = Exception


# -----------------------------------------------------------------------------
# Asset Helpers & Base64 Encoders
# -----------------------------------------------------------------------------
def get_base64_image(image_path: str) -> str:
    """Reads a local image file and returns base64 encoded string."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


def get_image_bytes(image_path: str) -> Optional[bytes]:
    """Reads a local image file and returns raw bytes."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return f.read()
    return None


# -----------------------------------------------------------------------------
# Data Models & Schemas
# -----------------------------------------------------------------------------
VALID_CATEGORIES = [
    "Roads",
    "Electricity",
    "Sanitation",
    "Water",
    "Drainage",
    "Public Safety",
    "Other"
]

VALID_SEVERITIES = ["Critical", "High", "Moderate", "Low"]
VALID_STATUSES = ["Submitted", "Under Review", "Resolved"]

@dataclass
class CivicReport:
    id: str
    timestamp: str
    locality: str
    user_description: str
    category: str
    title: str
    description: str
    severity: str
    severity_reason: str
    department: str
    recommended_action: str
    suggested_sla: str
    visual_evidence: List[str]
    uncertainties: List[str]
    needs_human_review: bool
    status: str
    image_bytes: Optional[bytes] = None
    is_demo_mode: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("image_bytes", None)
        return d


# -----------------------------------------------------------------------------
# Initial Sample Records (Preloaded with Authentic Project Imagery)
# -----------------------------------------------------------------------------
sample_road_bytes = get_image_bytes("assets/sample_pothole.jpg")

DEFAULT_SEED_REPORTS: List[CivicReport] = [
    CivicReport(
        id="CP-2026-874",
        timestamp=(datetime.datetime.now() - datetime.timedelta(hours=3, minutes=20)).strftime("%Y-%m-%d %H:%M"),
        locality="Green Valley North, Main Arterial Rd",
        user_description="Deep crater pothole with fractured aggregate causing vehicles to swerve into opposing lanes.",
        category="Roads",
        title="Deep Asphalt Cavity & Pavement Structural Deterioration",
        description="Severe asphalt disintegration measuring approx 3x2 feet with exposed aggregate foundation and loose gravel scatter in active lane.",
        severity="High",
        severity_reason="High vehicular impact hazard with imminent risk of wheel damage and sudden evasive steering collisions.",
        department="Public Works & Highway Maintenance",
        recommended_action="Deploy cold asphalt patch crew and warning road cones prior to evening rush hour.",
        suggested_sla="Same-Day / < 8 Hours (Illustrative Target)",
        visual_evidence=["Deep cavity with fractured asphalt perimeter", "Orange emergency safety cones on perimeter", "Skid marks indicating sudden driver braking"],
        uncertainties=["Sub-base moisture saturation depth cannot be verified by surface optical photo"],
        needs_human_review=True,
        status="Under Review",
        image_bytes=sample_road_bytes,
        is_demo_mode=True
    ),
    CivicReport(
        id="CP-2026-901",
        timestamp=(datetime.datetime.now() - datetime.timedelta(hours=1, minutes=10)).strftime("%Y-%m-%d %H:%M"),
        locality="Downtown Metro Corridor (Sector 4)",
        user_description="Exposed frayed power cable hanging from broken pole bracket after thunderstorm.",
        category="Electricity",
        title="Severed High-Voltage Conductor Near Pedestrian Crosswalk",
        description="Suspended utility conduit hanging within 4.5 feet of commercial pedestrian sidewalk with damaged insulation sheath.",
        severity="Critical",
        severity_reason="Severe potential electrocution hazard along a high-density urban footway.",
        department="Municipal Electricity & Power Distribution",
        recommended_action="Emergency perimeter cordoning and lineman isolation within 1 hour.",
        suggested_sla="Immediate / < 2 Hours (Illustrative Target)",
        visual_evidence=["Heavy gauge wiring drooping into footway clearance", "Fractured mounting arm on utility pillar"],
        uncertainties=["Active voltage state cannot be verified without physical probe meter", "Ownership cross-connect requires field diagnostic"],
        needs_human_review=True,
        status="Submitted",
        image_bytes=None,
        is_demo_mode=True
    ),
    CivicReport(
        id="CP-2026-842",
        timestamp=(datetime.datetime.now() - datetime.timedelta(hours=12, minutes=30)).strftime("%Y-%m-%d %H:%M"),
        locality="Maplewood Central Market Square",
        user_description="Commercial dumpster overflow spilling across storm drain inlet.",
        category="Sanitation",
        title="Commercial Solid Waste Overflow Blocking Storm Grate",
        description="Multiple uncontained bags of municipal solid waste obstructing curb stormwater inlet and creating foul street drainage.",
        severity="Moderate",
        severity_reason="Sanitary nuisance, odor propagation, and imminent drainage blockage in case of rainfall.",
        department="Solid Waste Management & Sanitation",
        recommended_action="Schedule heavy compactor clearance and sanitize surrounding pavement.",
        suggested_sla="Within 24 Hours (Illustrative Target)",
        visual_evidence=["Overfilled municipal refuse container", "Debris scattered across 15 feet of gutter channel"],
        uncertainties=["Hazardous chemical or organic decomposition stage cannot be confirmed optically"],
        needs_human_review=False,
        status="Resolved",
        image_bytes=None,
        is_demo_mode=True
    ),
    CivicReport(
        id="CP-2026-799",
        timestamp=(datetime.datetime.now() - datetime.timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M"),
        locality="Riverfront Promenade - Pier 3",
        user_description="Pressurized potable water main leaking beneath promenade tiles.",
        category="Water",
        title="Underground Municipal Supply Pipe Leakage",
        description="Continuous clean freshwater weeping through pedestrian paving joints, causing localized sub-surface subsidence.",
        severity="Moderate",
        severity_reason="Treated water wastage and structural undermining of promenade pedestrian foundation.",
        department="Water Supply & Sewerage Board",
        recommended_action="Acoustic leak pinpointing and pipeline sleeve replacement.",
        suggested_sla="Within 12-24 Hours (Illustrative Target)",
        visual_evidence=["Continuous bubbling clear water ponding", "Sub-base sediment displacement along tile margins"],
        uncertainties=["Underground supply line pressure and pipe caliber cannot be assessed from surface"],
        needs_human_review=True,
        status="Under Review",
        image_bytes=None,
        is_demo_mode=True
    ),
    CivicReport(
        id="CP-2026-751",
        timestamp=(datetime.datetime.now() - datetime.timedelta(days=1, hours=9)).strftime("%Y-%m-%d %H:%M"),
        locality="Eastwood Community Park, Path B",
        user_description="Missing solar pathway lamp lens, minor cosmetic housing damage.",
        category="Public Safety",
        title="Damaged Solar Park Luminaire Fixture",
        description="Polycarbonate diffuser missing from pathway bollard light; internal LED circuitry intact and non-hazardous.",
        severity="Low",
        severity_reason="Low-voltage fixture, no exposed conductors, ambient illumination remains safe.",
        department="Parks & Recreation Department",
        recommended_action="Include replacement diffuser casing on weekly routine maintenance route.",
        suggested_sla="Routine / 3-5 Business Days (Illustrative Target)",
        visual_evidence=["Intact LED module without loose wiring", "Minor hairline fracture on decorative collar"],
        uncertainties=["Internal moisture ingress damage will require physical disassembly"],
        needs_human_review=False,
        status="Submitted",
        image_bytes=None,
        is_demo_mode=True
    )
]


# -----------------------------------------------------------------------------
# Helper Functions: Image Resizing & Processing
# -----------------------------------------------------------------------------
def process_and_resize_image(uploaded_file, max_dimension: int = 1024) -> tuple[Optional[Image.Image], Optional[bytes], Optional[str]]:
    """
    Validates uploaded file, ensures it is a readable image,
    resizes to max_dimension preserving aspect ratio, and returns JPEG bytes.
    """
    try:
        image = Image.open(uploaded_file)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        w, h = image.size
        if max(w, h) > max_dimension:
            scale = max_dimension / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85, optimize=True)
        img_bytes = buffer.getvalue()
        return image, img_bytes, None
    except Exception as e:
        return None, None, f"Image processing error: {str(e)}"


# -----------------------------------------------------------------------------
# AI Analysis Engine: Gemini Multimodal SDK with Fallback
# -----------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """
You are CivicPulse AI, an expert multimodal civic intelligence and municipal hazard assessment system.
Analyze the citizen-provided photo and description of a municipal or public infrastructure hazard.

Provide structured decision-support analysis. Follow these critical guidelines:
1. Objectivity: Base observations strictly on visual evidence visible in the photo.
2. Safety Disclaimers: Do NOT infer or claim to verify live electrical current, explosive gas risk, or subterranean engineering faults solely from appearance.
3. Address Transparency: Do NOT claim to identify an exact street address or GPS coordinate from the photo alone.
4. SLA Clarity: Label suggested review targets as configurable illustrative targets, never official municipal response commitments.
5. Non-Civic Images: If the image does not depict a municipal/public civic hazard (e.g. personal selfies, indoor furniture, animals), classify as 'Other' and state this clearly in uncertainties.

You must return a valid JSON object matching the requested schema strictly.
"""

ANALYSIS_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "category": {
            "type": "STRING",
            "enum": ["Roads", "Electricity", "Sanitation", "Water", "Drainage", "Public Safety", "Other"],
            "description": "Civic hazard category"
        },
        "title": {
            "type": "STRING",
            "description": "Concise, professional headline for the issue (max 10 words)"
        },
        "description": {
            "type": "STRING",
            "description": "Evidence-based factual description of the visible condition"
        },
        "severity": {
            "type": "STRING",
            "enum": ["Critical", "High", "Moderate", "Low"],
            "description": "Recommended severity tier"
        },
        "severity_reason": {
            "type": "STRING",
            "description": "Justification explaining why this severity level was recommended"
        },
        "department": {
            "type": "STRING",
            "description": "Specific municipal or utility department recommended to handle this"
        },
        "recommended_action": {
            "type": "STRING",
            "description": "Immediate practical next step for triage operators"
        },
        "suggested_sla": {
            "type": "STRING",
            "description": "Configurable illustrative review target (e.g., 'Within 2 Hours (Target)')"
        },
        "visual_evidence": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "List of 2 to 4 specific visible details in the image"
        },
        "uncertainties": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "List of conditions that cannot be determined solely from optical inspection"
        },
        "needs_human_review": {
            "type": "BOOLEAN",
            "description": "True if severity is Critical/High or visual evidence contains ambiguity"
        }
    },
    "required": [
        "category", "title", "description", "severity", "severity_reason",
        "department", "recommended_action", "suggested_sla", "visual_evidence",
        "uncertainties", "needs_human_review"
    ]
}


def get_gemini_api_key(manual_key: Optional[str] = None) -> Optional[str]:
    """Retrieves API key from manual input, Streamlit secrets, or environment."""
    if manual_key and manual_key.strip():
        return manual_key.strip()
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if os.getenv("GEMINI_API_KEY"):
        return os.getenv("GEMINI_API_KEY")
    return None


def run_gemini_multimodal_analysis(
    image_bytes: bytes,
    locality: str,
    user_description: str,
    api_key: Optional[str]
) -> tuple[Optional[Dict[str, Any]], bool, Optional[str]]:
    """
    Executes multimodal hazard analysis via google-genai SDK.
    Returns: (parsed_json, is_demo_mode, error_message)
    """
    if not api_key or not GENAI_AVAILABLE:
        mock_data = generate_intelligent_demo_analysis(locality, user_description)
        return mock_data, True, None

    try:
        client = genai.Client(api_key=api_key)
        prompt_text = f"""
Analyze this citizen civic report.
Locality provided by citizen: "{locality if locality else 'Not specified'}"
Additional citizen description: "{user_description if user_description else 'None provided'}"

Examine the image carefully. Return structured JSON matching the defined schema.
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg",
                ),
                prompt_text
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=ANALYSIS_SCHEMA,
                temperature=0.2,
            )
        )

        raw_text = response.text
        parsed = json.loads(raw_text)

        for field in ["category", "title", "description", "severity", "department"]:
            if field not in parsed:
                raise ValueError(f"Missing mandatory field in response: {field}")

        return parsed, False, None

    except Exception as e:
        err_msg = str(e)
        fallback = generate_intelligent_demo_analysis(locality, user_description)
        return fallback, True, f"Gemini API note: {err_msg} (Fallback to Demo Engine)"


def generate_intelligent_demo_analysis(locality: str, user_description: str) -> Dict[str, Any]:
    """
    Generates structured, context-aware simulation data for hackathon presentation
    when an API key is not configured or offline.
    """
    desc_lower = (user_description or "").lower()

    if any(k in desc_lower for k in ["wire", "electric", "spark", "cable", "pole", "shock", "current"]):
        return {
            "category": "Electricity",
            "title": "[DEMO MODE] Compromised Overhead Electrical Cabling",
            "description": "Simulated analysis: Visible sagging high-voltage conduit with compromised weather insulation near pedestrian space.",
            "severity": "Critical",
            "severity_reason": "Severe electrocution hazard in vicinity of public footway.",
            "department": "Municipal Electricity Distribution Board",
            "recommended_action": "Emergency cordoning and physical isolation by rapid-response linemen.",
            "suggested_sla": "Immediate / < 2 Hours (Illustrative Target)",
            "visual_evidence": ["Dangling cable within 6 feet of ground", "Weathering along insulation sheath", "Close proximity to metal guardrail"],
            "uncertainties": ["Active voltage state cannot be verified without physical probe meter", "Network branch connection ID unverified"],
            "needs_human_review": True
        }
    elif any(k in desc_lower for k in ["water", "leak", "pipe", "flood", "burst", "drain"]):
        return {
            "category": "Water",
            "title": "[DEMO MODE] Pressurized Sub-Pavement Water Conduit Fracture",
            "description": "Simulated analysis: Upwelling freshwater pooling along roadway curb with noticeable sub-base sediment transport.",
            "severity": "High",
            "severity_reason": "Substantial water resource loss and risk of roadway structural undermining.",
            "department": "Department of Water Resources & Pipeline Maintenance",
            "recommended_action": "Shut off local sectional isolation valve and inspect pipe sleeve.",
            "suggested_sla": "Within 6 Hours (Illustrative Target)",
            "visual_evidence": ["Continuous bubbling of clear pressurized water", "Sediment accumulation at roadway edge"],
            "uncertainties": ["Exact pipe depth and pipe gauge cannot be determined from optical photo"],
            "needs_human_review": True
        }
    elif any(k in desc_lower for k in ["garbage", "trash", "waste", "dump", "smell", "sanitation"]):
        return {
            "category": "Sanitation",
            "title": "[DEMO MODE] Uncontained Waste Accumulation at Municipal Collection Point",
            "description": "Simulated analysis: Overflow of residential and commercial solid waste spilling past container borders onto public lane.",
            "severity": "Moderate",
            "severity_reason": "Sanitary nuisance, odor propagation, and obstruction of street drainage channels.",
            "department": "Municipal Sanitation & Waste Logistics",
            "recommended_action": "Deploy auxiliary compactor truck and apply enzymatic disinfectant spray.",
            "suggested_sla": "Within 24 Hours (Illustrative Target)",
            "visual_evidence": ["Overfilled 4-yard collection bin", "Debris scatter covering ~20 sq ft of roadway"],
            "uncertainties": ["Biochemical or medical waste presence cannot be confirmed optically"],
            "needs_human_review": False
        }
    else:
        return {
            "category": "Roads",
            "title": "[DEMO MODE] Pavement Surface Cavity & Roadway Deterioration",
            "description": "Simulated analysis: Pothole depression with fractured asphalt perimeter and exposed aggregate base course.",
            "severity": "High",
            "severity_reason": "Traffic disruption hazard with potential for vehicular wheel damage or emergency swerving.",
            "department": "Public Works & Roadway Engineering",
            "recommended_action": "Deploy cold asphalt patching unit and establish temporary traffic cones.",
            "suggested_sla": "Within 12 Hours (Illustrative Target)",
            "visual_evidence": ["Irregular cavity measuring ~2.5 ft diameter", "Loose asphalt gravel scattered in travel lane"],
            "uncertainties": ["Sub-surface moisture saturation depth cannot be verified by visual analysis"],
            "needs_human_review": True
        }


def init_session_state():
    """Initializes Streamlit session state stores."""
    if "reports" not in st.session_state:
        st.session_state.reports = list(DEFAULT_SEED_REPORTS)
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "last_analyzed_hash" not in st.session_state:
        st.session_state.last_analyzed_hash = None
    if "submitted_report_id" not in st.session_state:
        st.session_state.submitted_report_id = None


# -----------------------------------------------------------------------------
# Main Application Flow
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="CivicPulse AI — Smart Civic Triage",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    # Load editorial background and hero assets
    bg_b64 = get_base64_image("assets/bg_backdrop.jpg")
    hero_b64 = get_base64_image("assets/hero_banner.jpg")

    # Dynamic CSS with Editorial Serif Typography & Nature-Blended Background
    bg_css = f'url("data:image/jpeg;base64,{bg_b64}")' if bg_b64 else 'none'
    hero_css = f'url("data:image/jpeg;base64,{hero_b64}")' if hero_b64 else 'none'

    EDITORIAL_CSS = f"""
    <style>
        /* Editorial Typography from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600;1,700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        }}

        /* Full page background with nature depth-of-field overlay */
        .stApp {{
            background: linear-gradient(180deg, rgba(12, 17, 13, 0.88) 0%, rgba(9, 13, 10, 0.95) 100%),
                        {bg_css} center top / cover fixed no-repeat;
            color: #F5F3EB;
        }}

        /* Editorial Serif Headings */
        h1, h2, h3, h4, .editorial-heading {{
            font-family: 'Playfair Display', Georgia, serif;
            font-weight: 700;
            letter-spacing: -0.015em;
            color: #FDFBF7;
        }}

        h1 em, h2 em, h3 em, h4 em, .editorial-heading em {{
            font-family: 'Playfair Display', Georgia, serif;
            font-style: italic;
            font-weight: 400;
            color: #EBF0D8;
        }}

        /* Editorial Hero Banner */
        .editorial-hero-banner {{
            position: relative;
            border-radius: 20px;
            padding: 50px 32px;
            margin-bottom: 28px;
            background: linear-gradient(180deg, rgba(13, 19, 14, 0.72) 0%, rgba(8, 12, 9, 0.90) 100%),
                        {hero_css} center center / cover no-repeat;
            border: 1px solid rgba(235, 240, 216, 0.22);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
            text-align: center;
        }}

        .editorial-hero-tag {{
            display: inline-block;
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: #D8E2B2;
            background: rgba(216, 226, 178, 0.12);
            border: 1px solid rgba(216, 226, 178, 0.25);
            padding: 4px 14px;
            border-radius: 9999px;
            margin-bottom: 14px;
        }}

        .editorial-hero-heading {{
            font-size: 2.85rem;
            line-height: 1.15;
            margin: 0 auto 12px auto;
            max-width: 900px;
            color: #FFFFFF;
        }}

        .editorial-hero-sub {{
            font-size: 1.08rem;
            color: #D6DFD0;
            max-width: 680px;
            margin: 0 auto 18px auto;
            line-height: 1.5;
        }}

        /* Pill badges matching reference image */
        .editorial-pill-badge {{
            display: inline-block;
            background-color: #EBF0D8;
            color: #121813;
            padding: 6px 18px;
            border-radius: 9999px;
            font-size: 0.84rem;
            font-weight: 600;
            margin: 3px 6px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.25);
        }}

        /* Streamlit Buttons styled as elegant rounded pills */
        .stButton > button {{
            border-radius: 9999px !important;
            background-color: #EBF0D8 !important;
            color: #121813 !important;
            font-weight: 600 !important;
            border: 1px solid rgba(0,0,0,0.08) !important;
            padding: 0.5rem 1.6rem !important;
            transition: all 0.25s ease !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
        }}
        .stButton > button:hover {{
            background-color: #FFFFFF !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(235, 240, 216, 0.35) !important;
        }}

        /* Editorial Dark Cards */
        .editorial-dark-card {{
            background: rgba(18, 26, 20, 0.82);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(235, 240, 216, 0.12);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        }}

        /* Warm Cream Accent Card (like featured cards in reference image) */
        .editorial-cream-card {{
            background: #EBF0D8;
            color: #121813;
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.4);
        }}
        .editorial-cream-card h3, .editorial-cream-card h4, .editorial-cream-card h5 {{
            color: #111813 !important;
            font-family: 'Playfair Display', serif;
        }}
        .editorial-cream-card p, .editorial-cream-card span {{
            color: #2D382F;
        }}

        /* Metric Cards */
        .metric-card {{
            background: rgba(18, 26, 20, 0.8);
            border: 1px solid rgba(235, 240, 216, 0.12);
            border-radius: 16px;
            padding: 18px 20px;
            transition: transform 0.2s ease, border-color 0.2s ease;
            box-shadow: 0 6px 16px rgba(0,0,0,0.25);
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(216, 226, 178, 0.4);
        }}
        .metric-label {{
            font-size: 0.78rem;
            color: #A3B19B;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 600;
        }}
        .metric-value {{
            font-family: 'Playfair Display', serif;
            font-size: 2.1rem;
            font-weight: 700;
            margin: 6px 0;
            color: #FFFFFF;
        }}
        .metric-sub {{
            font-size: 0.76rem;
            color: #798A74;
        }}

        /* Editorial Severity Badges */
        .badge-critical {{
            background: rgba(220, 38, 38, 0.2);
            color: #FCA5A5;
            border: 1px solid rgba(239, 68, 68, 0.4);
            border-radius: 9999px;
            padding: 3px 12px;
            font-weight: 700;
            font-size: 0.8rem;
            display: inline-block;
        }}
        .badge-high {{
            background: rgba(224, 159, 62, 0.2);
            color: #FCD34D;
            border: 1px solid rgba(224, 159, 62, 0.4);
            border-radius: 9999px;
            padding: 3px 12px;
            font-weight: 700;
            font-size: 0.8rem;
            display: inline-block;
        }}
        .badge-moderate {{
            background: rgba(216, 226, 178, 0.2);
            color: #EBF0D8;
            border: 1px solid rgba(216, 226, 178, 0.4);
            border-radius: 9999px;
            padding: 3px 12px;
            font-weight: 700;
            font-size: 0.8rem;
            display: inline-block;
        }}
        .badge-low {{
            background: rgba(52, 211, 153, 0.2);
            color: #6EE7B7;
            border: 1px solid rgba(52, 211, 153, 0.4);
            border-radius: 9999px;
            padding: 3px 12px;
            font-weight: 700;
            font-size: 0.8rem;
            display: inline-block;
        }}

        /* Status indicators */
        .status-pill {{
            border-radius: 9999px;
            padding: 2px 10px;
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-block;
        }}
        .status-submitted {{
            background: rgba(168, 85, 247, 0.2);
            color: #D8B4FE;
            border: 1px solid rgba(168, 85, 247, 0.35);
        }}
        .status-review {{
            background: rgba(245, 158, 11, 0.2);
            color: #FDE68A;
            border: 1px solid rgba(245, 158, 11, 0.35);
        }}
        .status-resolved {{
            background: rgba(16, 185, 129, 0.2);
            color: #A7F3D0;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }}

        /* Danger Banner */
        .danger-alert {{
            background: rgba(220, 38, 38, 0.16);
            border-left: 4px solid #EF4444;
            border-radius: 10px;
            padding: 14px 18px;
            margin: 14px 0;
            color: #FCA5A5;
            font-size: 0.92rem;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: #0A0F0B !important;
            border-right: 1px solid rgba(235, 240, 216, 0.08);
        }}
    </style>
    """
    st.markdown(EDITORIAL_CSS, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Sidebar Navigation & Settings
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 14px 0 20px 0;">
            <div style="font-size: 2.2rem; margin-bottom: 4px;">🛡️</div>
            <div style="font-family: 'Playfair Display', serif; font-size: 1.45rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.01em;">
                CivicPulse <em>AI</em>
            </div>
            <div style="font-size: 0.74rem; color: #D8E2B2; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 4px;">
                Autonomous Civic Triage
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        
        st.markdown("### 🎛️ Navigation")
        app_mode = st.radio(
            "Workspace View",
            [
                "🚨 Report Hazard & AI Triage",
                "📊 Operations Command Center",
                "📋 Priority Triage Queue",
                "🗺️ Locality & Geographic Pulse",
                "ℹ️ Responsible AI & Architecture"
            ],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### 🔑 AI Engine Configuration")
        
        api_key_env = get_gemini_api_key()
        has_api_key = bool(api_key_env)
        
        if has_api_key:
            st.success("✅ Gemini Multimodal Active")
            st.caption("Connected via environment / secrets.")
        else:
            st.warning("⚠️ Demo Mode Enabled")
            st.caption("No API key detected. Running realistic simulated civic analysis.")
            
        manual_api_key = st.text_input(
            "Override Gemini API Key (optional)",
            type="password",
            placeholder="AIzaSy...",
            help="Paste a Google Gemini API Key for live multimodal inference. Never hardcoded or logged."
        )

        st.markdown("---")
        st.markdown("### 🔄 Demo Data Management")
        col_reset1, col_reset2 = st.columns(2)
        with col_reset1:
            if st.button("Reset Seed", use_container_width=True):
                st.session_state.reports = list(DEFAULT_SEED_REPORTS)
                st.session_state.analysis_result = None
                st.success("Reset!")
                st.rerun()
        with col_reset2:
            if st.button("Clear All", use_container_width=True):
                st.session_state.reports = []
                st.session_state.analysis_result = None
                st.info("Cleared!")
                st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.74rem; color: #798A74; line-height: 1.45;">
            <strong>CivicPulse AI</strong> v1.2.0<br>
            Editorial Design & Multimodal Intelligence.<br>
            <em>Every Report Matters. Every Hazard Counts.</em>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Editorial Hero Banner (Matching Reference Aesthetic with Civic Imagery)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="editorial-hero-banner">
        <div class="editorial-hero-tag">MUNICIPAL MULTIMODAL INTELLIGENCE</div>
        <h1 class="editorial-hero-heading">CivicPulse from a <em>City in Progress</em></h1>
        <p class="editorial-hero-sub">
            Every Report Matters. Every Hazard Counts. Transforming citizen evidence into structured municipal triage in seconds.
        </p>
        <div>
            <span class="editorial-pill-badge">⚡ Real-time Multimodal Vision</span>
            <span class="editorial-pill-badge">🏛️ Automated Ward Routing</span>
            <span class="editorial-pill-badge">🛡️ Responsible AI Disclaimers</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # VIEW 1: REPORT HAZARD & AI TRIAGE WORKSPACE
    # -------------------------------------------------------------------------
    if app_mode == "🚨 Report Hazard & AI Triage":
        st.markdown("## Citizen Hazard Intake & <em>Multimodal Triage</em>", unsafe_allow_html=True)
        st.write(
            "Upload a photograph of a civic hazard (damaged pavement, exposed electrical wire, overflow garbage, water leakage). "
            "Our Gemini multimodal engine analyzes visual evidence, recommends department ownership, and determines severity."
        )

        col_input, col_preview = st.columns([1.1, 0.9])

        with col_input:
            st.markdown("<div class='editorial-dark-card'>", unsafe_allow_html=True)
            st.markdown("### 1. Citizen Evidence Intake", unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Upload Hazard Photo (JPG, JPEG, PNG)",
                type=["jpg", "jpeg", "png"],
                help="High-detail photos help the model identify physical hazards accurately."
            )

            locality_input = st.text_input(
                "Locality / Street / Landmark *",
                placeholder="e.g. 5th Avenue & Elm St, West Sector",
                help="Approximate location helps route reports to regional municipal wards."
            )

            user_desc_input = st.text_area(
                "Citizen Description (Optional observations)",
                placeholder="e.g. Sparks noticed during rain; cars swerving suddenly; water bubbling from under curb...",
                height=90
            )

            if user_desc_input and any(k in user_desc_input.lower() for k in ["wire", "electric", "spark", "gas", "fire", "collapse"]):
                st.markdown("""
                <div class="danger-alert">
                    <strong>⚠️ IMMEDIATE SAFETY NOTICE:</strong><br>
                    If this situation involves active electrical arcing, gas smells, or imminent structural collapse,
                    <strong>do not approach or touch</strong>. Immediately call your local emergency dispatch service.
                </div>
                """, unsafe_allow_html=True)

            analyze_btn = st.button("⚡ Analyze Civic Hazard with Gemini", type="primary", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        processed_image = None
        processed_bytes = None
        
        with col_preview:
            st.markdown("<div class='editorial-dark-card'>", unsafe_allow_html=True)
            st.markdown("### 2. Photographic Verification", unsafe_allow_html=True)
            
            if uploaded_file is not None:
                processed_image, processed_bytes, err = process_and_resize_image(uploaded_file)
                if err:
                    st.error(f"❌ {err}")
                else:
                    st.image(processed_image, caption=f"Verified Evidence: {uploaded_file.name} ({processed_image.width}x{processed_image.height}px)", use_container_width=True)
            else:
                st.info("📷 No image uploaded yet. Upload a photo on the left to preview evidence.")
                st.markdown("---")
                st.markdown("💡 **Testing without a local photo?** You can select a preloaded scenario:")
                sample_choice = st.selectbox(
                    "Or load a sample test scenario:",
                    [
                        "— Select a sample scenario —",
                        "🕳️ Road Hazard: Deep arterial pavement crater (With Real Photo)",
                        "⚡ Live Electrical Hazard: Severed street wire after rainstorm",
                        "💧 Water Hazard: Main supply conduit rupture on sidewalk",
                        "🗑️ Sanitation Hazard: Commercial dumpster spill blocking storm drain"
                    ]
                )
                if sample_choice != "— Select a sample scenario —":
                    if "Road Hazard" in sample_choice:
                        locality_input = "Green Valley North, Main Arterial Rd"
                        user_desc_input = "Deep road cavity with sharp broken edges causing severe vehicle swerving."
                        if os.path.exists("assets/sample_pothole.jpg"):
                            sample_img = Image.open("assets/sample_pothole.jpg")
                            st.image(sample_img, caption="Preloaded Evidence: Urban Road Cavity with Cones", use_container_width=True)
                            processed_bytes = get_image_bytes("assets/sample_pothole.jpg")
                            processed_image = sample_img
                    elif "Electrical" in sample_choice:
                        locality_input = "Metro Transit Hub, Pillar 42"
                        user_desc_input = "High voltage dangling wire sparking near pedestrian zebra crossing."
                    elif "Water" in sample_choice:
                        locality_input = "Civic Centre Plaza"
                        user_desc_input = "Potable water pipeline weeping heavily through pedestrian paving blocks."
                    elif "Sanitation" in sample_choice:
                        locality_input = "North Market Lane"
                        user_desc_input = "Overflowing waste container with refuse spilling into open gutter."
                    st.caption(f"Loaded scenario: *{sample_choice}*")
            st.markdown("</div>", unsafe_allow_html=True)

        # Trigger Analysis
        if analyze_btn:
            if not uploaded_file and not user_desc_input and not processed_bytes:
                st.error("⚠️ Please upload a photograph or provide details about the hazard before initiating analysis.")
            else:
                with st.spinner("🤖 Gemini Multimodal analyzing physical hazards, estimating severity & department ownership..."):
                    active_api_key = get_gemini_api_key(manual_api_key)
                    
                    if not processed_bytes:
                        dummy_img = Image.new("RGB", (600, 400), color=(18, 26, 20))
                        buf = io.BytesIO()
                        dummy_img.save(buf, format="JPEG")
                        processed_bytes = buf.getvalue()
                        processed_image = dummy_img

                    analysis_json, is_demo, api_msg = run_gemini_multimodal_analysis(
                        image_bytes=processed_bytes,
                        locality=locality_input,
                        user_description=user_desc_input,
                        api_key=active_api_key
                    )

                    st.session_state.analysis_result = {
                        "data": analysis_json,
                        "is_demo": is_demo,
                        "locality": locality_input or "Citywide Ward (Unspecified)",
                        "user_description": user_desc_input,
                        "image_bytes": processed_bytes,
                        "api_msg": api_msg
                    }

        # Display Analysis Result
        if st.session_state.analysis_result:
            res = st.session_state.analysis_result
            data = res["data"]
            is_demo = res["is_demo"]
            api_msg = res.get("api_msg")

            st.markdown("---")
            st.markdown("## AI Hazard Assessment <em>Report</em>", unsafe_allow_html=True)

            if is_demo:
                st.warning(
                    "🟡 **DEMO MODE SIMULATION**: Analysis generated by CivicPulse local decision-support simulator. "
                    "(Provide a Gemini API key in the sidebar for live multimodal reasoning)."
                )
            if api_msg:
                st.info(f"ℹ️ {api_msg}")

            if data.get("severity") == "Critical":
                st.markdown("""
                <div class="danger-alert">
                    <strong>🚨 CRITICAL HAZARD CLASSIFICATION:</strong><br>
                    This incident exhibits indicators of immediate physical risk. Standard emergency protocols suggest priority escalation.
                </div>
                """, unsafe_allow_html=True)

            col_a1, col_a2 = st.columns([1.2, 0.8])

            with col_a1:
                st.markdown(f"### **{data.get('title', 'Civic Hazard')}**")
                st.write(data.get("description", "No description generated."))

                st.markdown("**🔍 Observed Visual Evidence:**")
                for ev in data.get("visual_evidence", []):
                    st.markdown(f"- 👁️ {ev}")

                st.markdown("**❓ Technical Uncertainties (Inspection Limitations):**")
                for uncert in data.get("uncertainties", []):
                    st.markdown(f"- ⚠️ {uncert}")

            with col_a2:
                st.markdown("<div class='editorial-cream-card'>", unsafe_allow_html=True)
                st.markdown("#### **Triage Classification**")
                
                sev = data.get("severity", "Moderate")
                sev_style = f"badge-{sev.lower()}"
                st.markdown(f"**Recommended Severity:** <span class='{sev_style}'>{sev.upper()}</span>", unsafe_allow_html=True)
                st.caption(f"**Rationale:** {data.get('severity_reason', 'Not provided')}")

                st.markdown(f"**Department:** `{data.get('department', 'Public Works')}`")
                st.markdown(f"**Category:** `{data.get('category', 'Roads')}`")
                st.markdown(f"**Suggested Action:** {data.get('recommended_action', 'Inspect on-site')}")
                st.markdown(f"**Review Target (SLA):** `{data.get('suggested_sla', 'Within 24 Hours')}`")
                st.caption("*(Note: Suggested review target is an illustrative benchmark, not an official municipal SLA commitment)*")

                needs_review = data.get("needs_human_review", True)
                if needs_review:
                    st.markdown("🛡️ **Human Verification Recommended:** Yes (Field inspector review required)")
                else:
                    st.markdown("✅ **Human Verification Recommended:** Routine queue")
                st.markdown("</div>", unsafe_allow_html=True)

            # Submission Form
            st.markdown("### 3. Review & Submit to Municipal <em>Priority Queue</em>", unsafe_allow_html=True)
            sub_col1, _ = st.columns([1, 1])

            with sub_col1:
                confirm_submit = st.button("🚀 Confirm & Submit to Priority Queue", type="primary", use_container_width=True)

            if confirm_submit:
                new_id = f"CP-2026-{uuid.uuid4().hex[:4].upper()}"
                new_report = CivicReport(
                    id=new_id,
                    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    locality=res["locality"],
                    user_description=res["user_description"],
                    category=data.get("category", "Other"),
                    title=data.get("title", "Untitled Hazard"),
                    description=data.get("description", ""),
                    severity=data.get("severity", "Moderate"),
                    severity_reason=data.get("severity_reason", ""),
                    department=data.get("department", "Municipal Services"),
                    recommended_action=data.get("recommended_action", ""),
                    suggested_sla=data.get("suggested_sla", "24h"),
                    visual_evidence=data.get("visual_evidence", []),
                    uncertainties=data.get("uncertainties", []),
                    needs_human_review=data.get("needs_human_review", True),
                    status="Submitted",
                    image_bytes=res["image_bytes"],
                    is_demo_mode=res["is_demo"]
                )
                st.session_state.reports.insert(0, new_report)
                st.session_state.submitted_report_id = new_id
                st.session_state.analysis_result = None
                st.success(f"🎉 Report **{new_id}** successfully queued for municipal dispatch!")
                st.balloons()
                st.rerun()

    # -------------------------------------------------------------------------
    # VIEW 2: OPERATIONS COMMAND CENTER
    # -------------------------------------------------------------------------
    elif app_mode == "📊 Operations Command Center":
        st.markdown("## Civic Operations <em>Command Center</em>", unsafe_allow_html=True)
        st.write("Real-time municipal telemetry, hazard distributions, and resolution velocity metrics.")

        reports = st.session_state.reports

        if not reports:
            st.info("No active reports currently stored. Use the Intake view or click 'Reset Seed' in the sidebar.")
        else:
            total_reports = len(reports)
            critical_count = sum(1 for r in reports if r.severity == "Critical")
            under_review_count = sum(1 for r in reports if r.status == "Under Review")
            resolved_count = sum(1 for r in reports if r.status == "Resolved")
            submitted_count = sum(1 for r in reports if r.status == "Submitted")

            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Reports</div>
                    <div class="metric-value">{total_reports}</div>
                    <div class="metric-sub">Active session records</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="metric-card" style="border-color: rgba(239, 68, 68, 0.4);">
                    <div class="metric-label" style="color: #F87171;">Critical Hazards</div>
                    <div class="metric-value" style="color: #F87171;">{critical_count}</div>
                    <div class="metric-sub">Immediate escalation tier</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label" style="color: #D8B4FE;">Awaiting Triage</div>
                    <div class="metric-value">{submitted_count}</div>
                    <div class="metric-sub">Fresh citizen intakes</div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label" style="color: #FDE68A;">Under Review</div>
                    <div class="metric-value">{under_review_count}</div>
                    <div class="metric-sub">Field crews assigned</div>
                </div>
                """, unsafe_allow_html=True)
            with m5:
                st.markdown(f"""
                <div class="metric-card" style="border-color: rgba(16, 185, 129, 0.4);">
                    <div class="metric-label" style="color: #6EE7B7;">Resolved</div>
                    <div class="metric-value" style="color: #6EE7B7;">{resolved_count}</div>
                    <div class="metric-sub">Mitigated & closed</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Recurring Hotspot Detection
            locality_counts = {}
            for r in reports:
                loc = r.locality.strip()
                locality_counts[loc] = locality_counts.get(loc, 0) + 1

            recurring_localities = [loc for loc, count in locality_counts.items() if count >= 2]
            if recurring_localities:
                st.markdown(f"""
                <div class="danger-alert" style="background: rgba(224, 159, 62, 0.14); border-color: #E09F3E; color: #FDE68A;">
                    <strong>⚠️ RECURRING HAZARD HOTSPOT ALERT:</strong><br>
                    Clustered hazard reports detected in: <strong>{", ".join(recurring_localities)}</strong>.<br>
                    Area supervisors should coordinate cross-department inspection to evaluate infrastructure degradation.
                </div>
                """, unsafe_allow_html=True)

            chart_col1, chart_col2 = st.columns(2)
            df = pd.DataFrame([r.to_dict() for r in reports])

            sev_colors = {
                "Critical": "#EF4444",
                "High": "#E09F3E",
                "Moderate": "#D8E2B2",
                "Low": "#52B788"
            }

            with chart_col1:
                st.markdown("### Hazard Severity <em>Breakdown</em>", unsafe_allow_html=True)
                sev_counts = df["severity"].value_counts().reset_index()
                sev_counts.columns = ["Severity", "Count"]

                fig_sev = px.pie(
                    sev_counts,
                    names="Severity",
                    values="Count",
                    hole=0.60,
                    color="Severity",
                    color_discrete_map=sev_colors
                )
                fig_sev.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#F5F3EB",
                    font_family="Playfair Display",
                    margin=dict(t=10, b=10, l=10, r=10),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_sev, use_container_width=True)

            with chart_col2:
                st.markdown("### Reports by <em>Category</em>", unsafe_allow_html=True)
                cat_counts = df["category"].value_counts().reset_index()
                cat_counts.columns = ["Category", "Count"]

                fig_cat = px.bar(
                    cat_counts,
                    x="Category",
                    y="Count",
                    color="Category",
                    color_discrete_sequence=["#D8E2B2", "#A3B18A", "#588157", "#3A5A40", "#E09F3E", "#EF4444", "#748CAB"]
                )
                fig_cat.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#F5F3EB",
                    font_family="Playfair Display",
                    margin=dict(t=10, b=10, l=10, r=10),
                    xaxis=dict(gridcolor="rgba(235,240,216,0.06)"),
                    yaxis=dict(gridcolor="rgba(235,240,216,0.06)"),
                    showlegend=False
                )
                st.plotly_chart(fig_cat, use_container_width=True)

            st.markdown("### Departmental Workload <em>Allocation</em>", unsafe_allow_html=True)
            dept_counts = df["department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Incident Count"]
            
            fig_dept = px.bar(
                dept_counts,
                y="Department",
                x="Incident Count",
                orientation="h",
                color="Incident Count",
                color_continuous_scale=["#131C15", "#588157", "#D8E2B2"]
            )
            fig_dept.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#F5F3EB",
                font_family="Playfair Display",
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis=dict(gridcolor="rgba(235,240,216,0.06)"),
                yaxis=dict(gridcolor="rgba(235,240,216,0.06)")
            )
            st.plotly_chart(fig_dept, use_container_width=True)

    # -------------------------------------------------------------------------
    # VIEW 3: PRIORITY TRIAGE QUEUE
    # -------------------------------------------------------------------------
    elif app_mode == "📋 Priority Triage Queue":
        st.markdown("## Municipal Priority <em>Triage Queue</em>", unsafe_allow_html=True)
        st.write(
            "Hazards auto-ranked by AI severity. Municipal officers can update operational status, "
            "inspect photographic evidence, and review suggested target resolutions."
        )

        reports = st.session_state.reports

        if not reports:
            st.info("No reports in queue. Submit new reports or restore sample seed data.")
        else:
            st.markdown("<div class='editorial-dark-card'>", unsafe_allow_html=True)
            f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1, 1, 1])

            with f_col1:
                search_query = st.text_input("🔍 Search Keyword / Locality / Title", placeholder="e.g. wire, Downtown, pothole...")
            with f_col2:
                filter_sev = st.selectbox("Severity Filter", ["All Severities"] + VALID_SEVERITIES)
            with f_col3:
                filter_cat = st.selectbox("Category Filter", ["All Categories"] + VALID_CATEGORIES)
            with f_col4:
                filter_status = st.selectbox("Status Filter", ["All Statuses"] + VALID_STATUSES)
            st.markdown("</div>", unsafe_allow_html=True)

            filtered = reports
            if search_query:
                q = search_query.lower()
                filtered = [
                    r for r in filtered
                    if q in r.title.lower() or q in r.locality.lower() or q in r.description.lower() or q in r.department.lower() or q in r.id.lower()
                ]
            if filter_sev != "All Severities":
                filtered = [r for r in filtered if r.severity == filter_sev]
            if filter_cat != "All Categories":
                filtered = [r for r in filtered if r.category == filter_cat]
            if filter_status != "All Statuses":
                filtered = [r for r in filtered if r.status == filter_status]

            severity_rank = {"Critical": 0, "High": 1, "Moderate": 2, "Low": 3}
            filtered.sort(key=lambda r: severity_rank.get(r.severity, 4))

            st.caption(f"Showing **{len(filtered)}** matching reports (Sorted by Criticality first)")

            for i, rep in enumerate(filtered):
                status_class = {
                    "Submitted": "status-submitted",
                    "Under Review": "status-review",
                    "Resolved": "status-resolved"
                }.get(rep.status, "status-submitted")

                sev_style = f"badge-{rep.severity.lower()}"

                with st.expander(f"[{rep.severity.upper()}] {rep.id} — {rep.title} ({rep.locality})", expanded=(i == 0)):
                    card_c1, card_c2 = st.columns([1.3, 0.9])

                    with card_c1:
                        st.markdown(f"""
                        <div>
                            <span class="{sev_style}">{rep.severity}</span>
                            <span class="status-pill {status_class}">{rep.status}</span>
                            <span style="font-size: 0.8rem; color: #A3B19B; margin-left: 8px;">Logged: {rep.timestamp}</span>
                            {f'<span style="background: rgba(235,240,216,0.1); color: #EBF0D8; padding: 2px 8px; border-radius: 9999px; font-size: 0.72rem; margin-left: 6px;">SAMPLE DATA</span>' if rep.is_demo_mode else ''}
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"**Locality:** {rep.locality}")
                        st.markdown(f"**Description:** {rep.description}")
                        if rep.user_description:
                            st.caption(f"Citizen note: *\"{rep.user_description}\"*")

                        st.markdown("**Evidence Observed:**")
                        for ev in rep.visual_evidence:
                            st.markdown(f"- 🔎 {ev}")

                        st.markdown("**Assessment Uncertainties:**")
                        for uncert in rep.uncertainties:
                            st.markdown(f"- ⚠️ {uncert}")

                    with card_c2:
                        st.markdown("<div class='editorial-cream-card'>", unsafe_allow_html=True)
                        st.markdown(f"**Department:** `{rep.department}`")
                        st.markdown(f"**Category:** `{rep.category}`")
                        st.markdown(f"**Recommended Action:** {rep.recommended_action}")
                        st.markdown(f"**Target SLA:** `{rep.suggested_sla}`")

                        if rep.image_bytes:
                            try:
                                card_img = Image.open(io.BytesIO(rep.image_bytes))
                                st.image(card_img, caption="Filed Photographic Evidence", use_container_width=True)
                            except Exception:
                                st.caption("(Image stored in binary buffer)")

                        st.markdown("---")
                        st.markdown("⚙️ **Update Status (Demo Control):**")
                        stat_col1, stat_col2, stat_col3 = st.columns(3)
                        
                        with stat_col1:
                            if st.button("📥 Received", key=f"btn_sub_{rep.id}", disabled=(rep.status == "Submitted")):
                                rep.status = "Submitted"
                                st.rerun()
                        with stat_col2:
                            if st.button("🔍 In Review", key=f"btn_rev_{rep.id}", disabled=(rep.status == "Under Review")):
                                rep.status = "Under Review"
                                st.rerun()
                        with stat_col3:
                            if st.button("✅ Resolve", key=f"btn_res_{rep.id}", disabled=(rep.status == "Resolved")):
                                rep.status = "Resolved"
                                st.rerun()

                        st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # VIEW 4: LOCALITY & GEOGRAPHIC PULSE
    # -------------------------------------------------------------------------
    elif app_mode == "🗺️ Locality & Geographic Pulse":
        st.markdown("## Locality Hazard <em>Distribution</em>", unsafe_allow_html=True)
        st.write(
            "Geographic concentration of reported civic concerns. Helps municipal teams dispatch "
            "ward-specific maintenance vehicles to areas experiencing multiple infrastructure faults."
        )

        reports = st.session_state.reports

        if not reports:
            st.info("No locality data available. Submit reports to generate geographic insights.")
        else:
            df_geo = pd.DataFrame([r.to_dict() for r in reports])

            loc_summary = df_geo.groupby("locality").agg(
                total_incidents=("id", "count"),
                critical_incidents=("severity", lambda s: sum(s == "Critical")),
                departments=("department", lambda d: ", ".join(set(d)))
            ).reset_index().sort_values(by="total_incidents", ascending=False)

            col_g1, col_g2 = st.columns([1.1, 0.9])

            with col_g1:
                st.markdown("### Active Wards & <em>Hazard Densities</em>", unsafe_allow_html=True)
                st.dataframe(
                    loc_summary,
                    column_config={
                        "locality": st.column_config.TextColumn("Locality / Ward"),
                        "total_incidents": st.column_config.NumberColumn("Total Reports"),
                        "critical_incidents": st.column_config.NumberColumn("Critical Alerts"),
                        "departments": st.column_config.TextColumn("Involved Departments")
                    },
                    hide_index=True,
                    use_container_width=True
                )

            with col_g2:
                st.markdown("### Incident Distribution by <em>Locality</em>", unsafe_allow_html=True)
                fig_loc = px.bar(
                    loc_summary,
                    x="total_incidents",
                    y="locality",
                    orientation="h",
                    color="critical_incidents",
                    color_continuous_scale=["#131C15", "#E09F3E", "#EF4444"],
                    labels={"total_incidents": "Reports", "locality": "Locality"}
                )
                fig_loc.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#F5F3EB",
                    font_family="Playfair Display",
                    margin=dict(t=10, b=10, l=10, r=10),
                    xaxis=dict(gridcolor="rgba(235,240,216,0.06)"),
                    yaxis=dict(gridcolor="rgba(235,240,216,0.06)")
                )
                st.plotly_chart(fig_loc, use_container_width=True)

            st.markdown("""
            <div class="editorial-dark-card" style="margin-top: 15px;">
                <strong>ℹ️ Geographic Metadata Notice:</strong><br>
                CivicPulse AI adheres to responsible privacy standards. We intentionally do not extrapolate or invent precise
                GPS coordinates when citizens provide neighborhood/ward names. All geographic clustering is grouped based on citizen-provided locality inputs.
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # VIEW 5: RESPONSIBLE AI & ARCHITECTURE
    # -------------------------------------------------------------------------
    elif app_mode == "ℹ️ Responsible AI & Architecture":
        st.markdown("## Responsible AI, <em>Transparency</em> & Architecture", unsafe_allow_html=True)
        
        col_r1, col_r2 = st.columns(2)

        with col_r1:
            st.markdown("<div class='editorial-dark-card'>", unsafe_allow_html=True)
            st.markdown("### 🛡️ Responsible AI Principles", unsafe_allow_html=True)
            st.markdown("""
            - **Decision-Support Only:** AI recommendations provide prioritization assistance for human triage coordinators. They are **not** official engineering determinations.
            - **No Fictitious Dispatches:** The system does not claim to dispatch official municipal emergency crews unless connected to an authenticated municipal ERP or 311 API.
            - **No Inferred Precision GPS:** We never fabricate GPS coordinates or claim optical photos prove exact property boundaries.
            - **Transparent Uncertainties:** Every analysis provides an explicit list of **what cannot be determined from the image** (e.g., live electrical voltage, pipe pressure, internal sub-base soil erosion).
            - **Safety-First Routing:** When high-voltage or structural threats are described, clear warnings are surfaced advising the user not to touch and to contact emergency services immediately.
            """)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_r2:
            st.markdown("<div class='editorial-cream-card'>", unsafe_allow_html=True)
            st.markdown("### ⚙️ Technical Architecture", unsafe_allow_html=True)
            st.markdown("""
            - **Editorial UI System:** Streamlit styled with Google's Playfair Display serif fonts, nature-blended depth-of-field imagery, and ivory pill buttons.
            - **AI Multimodal Core:** Google Gen AI SDK (`google-genai`), leveraging Gemini multimodal models with constrained JSON schemas.
            - **Image Pre-processing:** Pillow LANCZOS resampling to optimize payload bandwidth while retaining fine optical crack/wire details.
            - **Data Model:** Structured dataclasses with type validation and session persistence.
            - **Data Storage:** Streamlit session state memory (demonstration records are ephemeral across server restarts).
            """)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Municipal Severity <em>Definitions</em>", unsafe_allow_html=True)
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.15); border-top: 3px solid #EF4444; padding: 14px; border-radius: 12px;">
                <strong style="color: #F87171; font-family: 'Playfair Display', serif; font-size: 1.1rem;">Critical</strong><br>
                <span style="font-size: 0.85rem; color: #E2E8F0;">Potentially imminent danger requiring prompt human review and emergency escalation.</span>
            </div>
            """, unsafe_allow_html=True)
        with sc2:
            st.markdown("""
            <div style="background: rgba(224, 159, 62, 0.15); border-top: 3px solid #E09F3E; padding: 14px; border-radius: 12px;">
                <strong style="color: #FCD34D; font-family: 'Playfair Display', serif; font-size: 1.1rem;">High</strong><br>
                <span style="font-size: 0.85rem; color: #E2E8F0;">Potentially significant hazard requiring timely field verification and same-day scheduling.</span>
            </div>
            """, unsafe_allow_html=True)
        with sc3:
            st.markdown("""
            <div style="background: rgba(216, 226, 178, 0.15); border-top: 3px solid #D8E2B2; padding: 14px; border-radius: 12px;">
                <strong style="color: #EBF0D8; font-family: 'Playfair Display', serif; font-size: 1.1rem;">Moderate</strong><br>
                <span style="font-size: 0.85rem; color: #E2E8F0;">Civic problem requiring standard review and planned maintenance within 24-48 hours.</span>
            </div>
            """, unsafe_allow_html=True)
        with sc4:
            st.markdown("""
            <div style="background: rgba(82, 183, 136, 0.15); border-top: 3px solid #52B788; padding: 14px; border-radius: 12px;">
                <strong style="color: #74C69D; font-family: 'Playfair Display', serif; font-size: 1.1rem;">Low</strong><br>
                <span style="font-size: 0.85rem; color: #E2E8F0;">Minor cosmetic or non-critical issue suitable for routine weekly municipal rounds.</span>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Footer
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #798A74; font-size: 0.84rem; padding-bottom: 24px;">
        <strong>CivicPulse AI</strong> — Hackathon Prototype for <em>AI for Better Living & Smarter Communities</em>.<br>
        Decision-support assistance only. In an emergency, dial local official municipal emergency dispatch services.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
