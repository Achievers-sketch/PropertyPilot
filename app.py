import os
import re
import json
import pandas as pd
import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None

st.set_page_config(page_title="PropertyPilot AI", page_icon="🏠", layout="wide")

# Groq currently supports GPT-OSS 120B with JSON mode and agentic/tool-use capabilities.
MODEL = "openai/gpt-oss-120b"

@st.cache_data
def load_properties():
    return pd.read_csv("data/properties.csv")

properties = load_properties()


def parse_requirement_demo(text):
    t = text.lower()
    result = {
        "city": None, "area": None, "property_type": None, "size_marla": None,
        "max_budget_pkr": None, "min_bedrooms": None, "purpose": "Buy"
    }

    cities = ["lahore", "islamabad", "karachi", "rawalpindi", "peshawar", "multan"]
    for city in cities:
        if city in t:
            result["city"] = city.title()
            break

    areas = sorted(properties["area"].dropna().unique(), key=len, reverse=True)
    for area in areas:
        if area.lower() in t:
            result["area"] = area
            break

    if re.search(r"\b(apartment|flat)\b", t):
        result["property_type"] = "Apartment"
    elif re.search(r"\b(house|home|villa)\b", t):
        result["property_type"] = "House"
    elif "plot" in t:
        result["property_type"] = "Plot"

    size = re.search(r"(\d+(?:\.\d+)?)\s*(?:marla|marlas)", t)
    if size:
        result["size_marla"] = float(size.group(1))

    beds = re.search(r"(?:at least\s+|minimum\s+|min\s+)?(\d+)\s*(?:bedroom|bedrooms|bed)", t)
    if beds:
        result["min_bedrooms"] = int(beds.group(1))

    crore = re.search(r"(?:under|below|less than|max(?:imum)?|budget(?: of)?)\s*(?:pkr\s*)?(\d+(?:\.\d+)?)\s*crore", t)
    million = re.search(r"(?:under|below|less than|max(?:imum)?|budget(?: of)?)\s*(?:pkr\s*)?(\d+(?:\.\d+)?)\s*(?:million|m)", t)
    lakh = re.search(r"(?:under|below|less than|max(?:imum)?|budget(?: of)?)\s*(?:pkr\s*)?(\d+(?:\.\d+)?)\s*(?:lakh|lac)", t)
    if crore:
        result["max_budget_pkr"] = int(float(crore.group(1)) * 10_000_000)
    elif million:
        result["max_budget_pkr"] = int(float(million.group(1)) * 1_000_000)
    elif lakh:
        result["max_budget_pkr"] = int(float(lakh.group(1)) * 100_000)

    if re.search(r"\b(rent|rental|lease)\b", t):
        result["purpose"] = "Rent"

    return result


def extract_with_groq(text):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or Groq is None:
        return parse_requirement_demo(text), False

    client = Groq(api_key=api_key)
    prompt = f'''Extract property search requirements from the user's message.
Return ONLY valid JSON with these keys:
city, area, property_type, size_marla, max_budget_pkr, min_bedrooms, purpose.
Use null for unknown values. property_type must be House, Apartment, Plot, or null.
purpose must be Buy or Rent.
Convert crore to PKR (1 crore = 10,000,000) and million to PKR (1 million = 1,000,000).
Never invent missing values.
User message: {text}'''
    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            reasoning_effort="medium",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You extract structured real-estate requirements. Never invent missing values."},
                {"role": "user", "content": prompt},
            ],
        )
        data = json.loads(response.choices[0].message.content)
        return data, True
    except Exception:
        return parse_requirement_demo(text), False


def score_property(row, req):
    score = 0.0
    reasons = []

    if req.get("city"):
        if str(row.city).lower() == str(req["city"]).lower():
            score += 20
            reasons.append("city matches")
    else:
        score += 20

    if req.get("area"):
        if str(row.area).lower() == str(req["area"]).lower():
            score += 10
            reasons.append("preferred area matches")
    else:
        score += 10

    if req.get("max_budget_pkr"):
        if row.price_pkr <= req["max_budget_pkr"]:
            score += 30
            reasons.append("within budget")
        else:
            gap = (row.price_pkr - req["max_budget_pkr"]) / req["max_budget_pkr"]
            score += max(0, 30 - min(30, gap * 60))
    else:
        score += 30

    if req.get("property_type"):
        if str(row.property_type).lower() == str(req["property_type"]).lower():
            score += 15
            reasons.append("property type matches")
    else:
        score += 15

    if req.get("size_marla"):
        if float(row.size_marla) == float(req["size_marla"]):
            score += 15
            reasons.append("size matches")
        elif float(row.size_marla) >= float(req["size_marla"]):
            score += 10
            reasons.append("size is larger than requested")
    else:
        score += 15

    if req.get("min_bedrooms"):
        if int(row.bedrooms) >= int(req["min_bedrooms"]):
            score += 10
            reasons.append("bedroom requirement met")
        else:
            score += max(0, 10 - (req["min_bedrooms"] - row.bedrooms) * 3)
    else:
        score += 10

    return round(score, 1), reasons


def find_matches(req):
    df = properties.copy()
    if req.get("purpose"):
        df = df[df.purpose.str.lower() == str(req["purpose"]).lower()]

    scored = []
    for _, row in df.iterrows():
        score, reasons = score_property(row, req)
        scored.append((row, score, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:5]


def format_pkr(value):
    return f"PKR {value:,.0f}"


def generate_message(req, matches):
    if not matches:
        return "I could not identify a suitable property from the current demo inventory. Please share your preferred location, budget and property type so I can refine the search."
    top = matches[0][0]
    return (f"Hi! Based on your requirement, I found a promising option in {top.area}, {top.city}: "
            f"a {int(top.size_marla)} Marla {top.property_type} with {int(top.bedrooms)} bedrooms at {format_pkr(top.price_pkr)}. "
            "Would you like me to prepare a comparison with the other available options?")


st.title("🏠 PropertyPilot AI")
st.caption("AI workflow copilot for Pakistan's real-estate professionals")

with st.sidebar:
    st.header("Agent Workflow")
    st.markdown("1. 🧠 Requirement Agent")
    st.markdown("2. 🔎 Matching Engine")
    st.markdown("3. 📊 Analysis Agent")
    st.markdown("4. 📋 Lead Agent")
    st.markdown("5. 💬 Communication Agent")
    st.divider()
    st.caption("Demo inventory only — listings are synthetic and not live market listings.")

example = "I'm looking for a 5 marla house in Lahore under 2 crore, preferably Bahria Town, with at least 4 bedrooms."
query = st.text_area("Describe your client's property requirement", value=example, height=120)

if st.button("🚀 Find Properties", type="primary", use_container_width=True):
    if not query.strip():
        st.warning("Please enter a property requirement.")
        st.stop()

    with st.spinner("PropertyPilot agents are working..."):
        req, ai_used = extract_with_groq(query)
        matches = find_matches(req)

    st.success("Workflow completed")

    st.subheader("🧠 AI Understanding")
    cols = st.columns(7)
    labels = ["City", "Area", "Type", "Size", "Budget", "Bedrooms", "Purpose"]
    values = [
        req.get("city") or "Not specified",
        req.get("area") or "Not specified",
        req.get("property_type") or "Not specified",
        f"{req['size_marla']} Marla" if req.get("size_marla") else "Not specified",
        format_pkr(req["max_budget_pkr"]) if req.get("max_budget_pkr") else "Not specified",
        str(req["min_bedrooms"]) if req.get("min_bedrooms") else "Not specified",
        req.get("purpose") or "Buy",
    ]
    for col, label, value in zip(cols, labels, values):
        col.metric(label, value)

    st.caption("Requirement extraction: Groq GPT-OSS 120B" if ai_used else "Requirement extraction: demo fallback parser")

    st.subheader("🤖 Agent Activity")
    activity = st.columns(5)
    for col, name, status in zip(activity,
        ["Requirement", "Matching", "Analysis", "Lead", "Communication"],
        ["Complete", "Complete", "Complete", "Complete", "Ready"]):
        col.success(f"**{name}**\n\n{status}")

    st.subheader("🏆 Top Property Matches")
    if matches:
        display = []
        for row, score, _ in matches[:3]:
            display.append({
                "ID": row.property_id,
                "Location": f"{row.area}, {row.city}",
                "Type": row.property_type,
                "Size": f"{int(row.size_marla)} Marla",
                "Beds": int(row.bedrooms),
                "Price": format_pkr(row.price_pkr),
                "Match": f"{score}%",
            })
        st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)

        top_row, top_score, reasons = matches[0]
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💡 Why this property?")
            st.write(f"**{top_row.property_id} — {top_row.area}, {top_row.city}**")
            for reason in reasons:
                st.write(f"✓ {reason.capitalize()}")
            st.write(f"**Match score:** {top_score}%")
        with c2:
            st.subheader("📋 Lead Agent")
            missing = []
            if not req.get("area"): missing.append("preferred area")
            if not req.get("max_budget_pkr"): missing.append("maximum budget")
            if not req.get("min_bedrooms"): missing.append("minimum bedrooms")
            if missing:
                st.warning("Missing information: " + ", ".join(missing))
            else:
                st.success("Core search requirements captured.")
            st.info("Next action: confirm availability, listing details and viewing preference with the client.")

        st.subheader("💬 Client Follow-up Message")
        st.text_area("Ready-to-send draft", value=generate_message(req, matches), height=130)
    else:
        st.warning("No properties matched the selected purpose in the demo inventory.")

st.divider()
st.caption("PropertyPilot AI is a prototype. Match scores are design assumptions, not professional valuation or legal verification. All demo listings are synthetic and must not be represented as live listings.")
