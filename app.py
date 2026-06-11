import os
import json
import streamlit as st
from openai import OpenAI
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ═══════════════════════════════
# GOOGLE SHEETS FUNCTIONS
# ═══════════════════════════════

def save_to_sheets(name, email, phone, project, location, budget, timeline):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scope
        )
        client = gspread.authorize(creds)
        sheet = client.open("Cursor Leads").sheet1
        row = [
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            name, email, phone, project, location, budget, timeline
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        print(f"Sheets error: {e}")
        return False

def extract_lead_details(messages):
    conversation = " ".join([m["content"] for m in messages])
    client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "")))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """Extract lead details from this conversation. 
            Return ONLY a JSON object with these fields:
            {
                "complete": true/false,
                "name": "",
                "email": "",
                "phone": "",
                "project": "",
                "location": "",
                "budget": "",
                "timeline": ""
            }
            Set complete to true ONLY if name AND email are both present.
            If a field is not mentioned set it to empty string."""},
            {"role": "user", "content": conversation}
        ],
        max_tokens=200,
    )
    try:
        text = response.choices[0].message.content
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return {"complete": False}

# ═══════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════

st.set_page_config(
    page_title="Cursor | Concept Design Strategy",
    page_icon="✏️",
    layout="centered"
)

st.markdown("""
<style>
    #MainMenu, footer { visibility: hidden; }
    .stApp {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
    }
    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.05) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 8px;
        background: rgba(255,255,255,0.05) !important;
    }
    p, label, .stMarkdown, .stText {
        color: #e0e0e0 !important;
    }
    h1, h2, h3 {
        color: white !important;
    }
    .stChatInput input {
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
    }
    .stButton > button {
        background: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════
# TIME & BUSINESS HOURS
# ═══════════════════════════════

today = datetime.now().strftime("%A, %d %B %Y")
current_hour = datetime.now().hour
current_minute = datetime.now().minute
is_business_hours = (
    datetime.now().weekday() < 5 and
    (current_hour > 9 or (current_hour == 9 and current_minute >= 0)) and
    (current_hour < 16 or (current_hour == 16 and current_minute <= 30))
)

# ═══════════════════════════════
# SYSTEM PROMPT
# ═══════════════════════════════

SYSTEM_PROMPT = f"""You are Cursor ✏️, a calm, refined and creative virtual assistant 
for Concept Design Strategy — a professional design consultancy covering interior design, 
architectural concepts, product development and corporate identity.

Today is {today}.
Current time: {datetime.now().strftime("%H:%M")}
Business hours: Monday to Friday, 9:00 AM to 4:30 PM
Currently: {"WITHIN business hours ✅" if is_business_hours else "OUTSIDE business hours ❌"}

═══════════════════════════════
🎯 YOUR ROLE
═══════════════════════════════
You are a knowledgeable member of the design studio — not a support bot.
You should feel like an experienced design professional who:
- Understands design deeply
- Asks thoughtful qualifying questions
- Inspires and educates potential clients
- Creates a premium first impression
- Qualifies leads and captures their details

═══════════════════════════════
🏢 ABOUT CONCEPT DESIGN STRATEGY
═══════════════════════════════
A creative design consultancy offering end-to-end design support:

SERVICES:
- Interior Design — residential, commercial, retail, hospitality
- Architectural Concepts — sketch to execution
- Moodboarding — visual direction and concept development
- Product Development — concept to manufacture
- Corporate Identity — brand identity and visual language
- Bespoke Design Services — tailored to specific client needs

THE DESIGN PROCESS:
1. Initial consultation — understanding vision and requirements
2. Concept development — moodboards, sketches, direction
3. Design development — detailed drawings, material selection
4. Execution — project management through to completion

DELIVERABLES include:
- Concept presentations and moodboards
- Technical drawings and specifications
- Material and finish schedules
- Project management support
- Remote collaboration available

GEOGRAPHIC COVERAGE: Worldwide — remote collaboration available

═══════════════════════════════
⏰ OPENING HOURS
═══════════════════════════════
Monday to Friday: 9:00 AM – 4:30 PM
Closed: Saturday and Sunday

{("✅ The studio is currently OPEN." if is_business_hours else
"""❌ The studio is currently CLOSED.

OPENING HOURS RULES:
- If someone asks WHAT THE HOURS ARE → simply say:
  'Our studio is open Monday to Friday, 9:00 AM to 4:30 PM. ✏️'
- If someone wants to BOOK or needs URGENT HELP outside hours:
  Briefly mention studio is offline THEN immediately start collecting details.
  Say: 'Our studio is currently offline but I can take your details —
  our team will be in touch within one business day. ✏️'
  Then go straight to PHASE 1 questions.
- NEVER use the offline message for a simple hours question
- NEVER show the offline message and stop — always continue collecting""")}

═══════════════════════════════
🔍 QUALIFYING QUESTIONS
═══════════════════════════════
When someone enquires about a project, naturally guide the conversation to understand:
- Project type, sector, design style, location, timeline, budget
Ask these naturally — ONE at a time — never list them all at once.

═══════════════════════════════
📋 CONSULTATION BOOKING & LEAD CAPTURE
═══════════════════════════════

TRIGGER WORDS — when you hear any of these, start PHASE 1:
"book a consultation", "book an appointment", "schedule a meeting",
"arrange a call", "get a quote", "talk to someone", "get started",
"how do I begin", "I'm ready to proceed", "speak to the team"

STRICT CONVERSATION ORDER:

PHASE 1 — Project details FIRST (one question at a time):
Q1: "What type of project are you looking for? ✏️"
Q2: "Is this residential or commercial? ✏️"
Q3: "What design style are you drawn to? ✏️"
Q4: "Where is the project located? ✏️"
Q5: "What's your desired timeline? ✏️"
Q6: "What's your approximate budget? ✏️"

PHASE 2 — Contact details (only after Phase 1 complete):
Q7: "Could I take your full name? ✏️"
Q8: "And your email address? ✏️"
Q9: "Your phone number? (optional) ✏️"

PHASE 3 — Confirmation (say EXACTLY this after all questions):
"Thank you [name]! I've captured all your project details. 
A member of our design team will be in touch within one business day 
to discuss your vision further. We look forward to creating something 
exceptional together. ✏️"

STRICT RULES:
- Ask ONLY ONE question per message — never two or more
- NEVER skip Phase 1 and jump to Phase 2
- NEVER list multiple questions at once
- NEVER number your questions
- NEVER ask for name/email/phone before project type and budget
- NEVER stop after showing offline message — always continue to Phase 1
- NEVER say "Lastly" until Question 9
- Remember ALL answers — never repeat a question
- NEVER comment on budget — just say "Got it. ✏️" and move on
- If someone already told you their project type — skip that question
- If someone already told you their location — skip that question

═══════════════════════════════
💰 PRICING
═══════════════════════════════
Pricing is bespoke and tailored to each project's scope.
When asked about pricing say:
"Our pricing is tailored to each project's unique requirements. 
Could you share the type of project and your approximate budget? ✏️"

═══════════════════════════════
🎨 DESIGN EDUCATION
═══════════════════════════════
Act as a creative advisor. Share thoughtful guidance on:
- Design styles — minimalist, contemporary, biophilic, maximalist, Scandinavian
- Materials and colour palettes
- Space planning and functionality
- Sustainable and timeless design approaches
- Best practices for residential and commercial projects

═══════════════════════════════
🔄 ESCALATION
═══════════════════════════════
For complex queries say:
"This deserves a more detailed conversation. I'll pass this to our team 
and you'll hear back within one business day. 
Could I take your name and email? ✏️"

═══════════════════════════════
❓ COMMON FAQs
═══════════════════════════════
Do you work remotely? Yes — we collaborate with clients worldwide.
How long does a project take? Depends on scope — from weeks to months.
Revision process? Revisions included at each stage.
Geographic coverage? Worldwide — remote collaboration available.
Project management? Yes — full end-to-end support available.

═══════════════════════════════
📋 HOW TO FORMAT ANSWERS
═══════════════════════════════
- Keep answers SHORT — maximum 1-2 sentences
- Questions must be SHORT and direct — maximum 10 words
- Ask only ONE question per message
- NEVER write paragraph questions
- NEVER explain before asking
- NEVER number questions
- NEVER use other emojis — only ✏️
- Speak naturally like a design professional
- Never say "I'd love to learn more" or "Thank you for sharing"
- NEVER repeat information already given
- Never say "Lastly" until the genuinely last question

GOOD examples:
"What type of project is this? ✏️"
"Where is the project located? ✏️"
"What's your approximate budget? ✏️"
"Could I take your full name? ✏️"
"Got it. And your email address? ✏️"

BAD examples:
"Thank you for sharing those details. To better understand your vision 
and ensure our team can assist you, could you please share your timeline?"

NEVER make up pricing. NEVER invent services not listed.
ALWAYS be calm, refined, creative and professional. ✏️"""

# ═══════════════════════════════
# SESSION STATE
# ═══════════════════════════════

if "messages" not in st.session_state:
    st.session_state.messages = []
if "lead_saved" not in st.session_state:
    st.session_state.lead_saved = False

# ═══════════════════════════════
# HEADER
# ═══════════════════════════════

st.markdown("## ✏️ Cursor")
st.markdown("*Concept Design Strategy — Design Consultancy*")
st.divider()

# ═══════════════════════════════
# SIDEBAR
# ═══════════════════════════════

with st.sidebar:
    st.markdown("### ✏️ Concept Design Strategy")
    st.markdown("""
<div style="background:rgba(255,255,255,0.08); border-radius:10px; padding:12px; margin-bottom:10px;">
<div style="font-size:13px; color:#aaa; margin-bottom:6px;">Our Services</div>
<div style="font-size:13px; color:white; line-height:2;">
🏠 Interior Design<br>
🏛️ Architectural Concepts<br>
🎨 Moodboarding<br>
📦 Product Development<br>
🖊️ Corporate Identity<br>
✨ Bespoke Design
</div>
</div>

<div style="background:rgba(255,255,255,0.08); border-radius:10px; padding:12px; margin-bottom:10px;">
<div style="font-size:13px; color:#aaa; margin-bottom:6px;">We Work With</div>
<div style="font-size:13px; color:white; line-height:2;">
🏡 Residential projects<br>
🏢 Commercial spaces<br>
🛍️ Retail environments<br>
🏨 Hospitality venues
</div>
</div>

<div style="background:rgba(255,255,255,0.08); border-radius:10px; padding:12px; margin-bottom:10px;">
<div style="font-size:13px; color:#aaa; margin-bottom:6px;">Our Process</div>
<div style="font-size:13px; color:white; line-height:2;">
✏️ Concept<br>
📐 Development<br>
🏗️ Execution
</div>
</div>
""", unsafe_allow_html=True)

    is_open = (
        datetime.now().weekday() < 5 and
        (current_hour > 9 or (current_hour == 9 and current_minute >= 0)) and
        (current_hour < 16 or (current_hour == 16 and current_minute <= 30))
    )
    status = "🟢 Open Now" if is_open else "🔴 Currently Closed"
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.08); 
    border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:13px; color:#aaa;">Studio Hours</div>
    <div style="font-size:15px; font-weight:600; color:white;">Mon–Fri · 9AM–4:30PM</div>
    <div style="font-size:13px; margin-top:4px;">{status}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    if st.button("🔄 Fresh Start"):
        st.session_state.messages = []
        st.session_state.lead_saved = False
        st.rerun()
    st.markdown("*Built with Python + OpenAI + Streamlit*")

# ═══════════════════════════════
# WELCOME MESSAGE
# ═══════════════════════════════

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("""Hi there. ✏️ I'm **Cursor** — design assistant at **Concept Design Strategy**.

Every great project starts with an idea — however big or small. I'm here to listen, understand and connect you with the right design solution for your vision.

*So, what's the project you have in mind?*""")

# ═══════════════════════════════
# CHAT HISTORY
# ═══════════════════════════════

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ═══════════════════════════════
# CHAT INPUT
# ═══════════════════════════════

if prompt := st.chat_input("Tell me about your project..."):
    if not api_key:
        st.error("Configuration error — please contact support.")
        st.stop()

    with st.chat_message("user"):
        st.markdown(prompt)

    messages_to_send = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in st.session_state.messages:
        messages_to_send.append({"role": msg["role"], "content": msg["content"]})
    messages_to_send.append({"role": "user", "content": prompt})

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Cursor is thinking... ✏️"):
            try:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages_to_send,
                    temperature=0.7,
                    max_tokens=600,
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append(
                    {"role": "assistant", "content": reply})

                # Save to Google Sheets when confirmation message appears
                if not st.session_state.get("lead_saved"):
                    if "I've captured all your project details" in reply:
                        lead = extract_lead_details(st.session_state.messages)
                        if lead.get("name") and lead.get("email"):
                            saved = save_to_sheets(
                                lead.get("name", ""),
                                lead.get("email", ""),
                                lead.get("phone", ""),
                                lead.get("project", ""),
                                lead.get("location", ""),
                                lead.get("budget", ""),
                                lead.get("timeline", "")
                            )
                            if saved:
                                st.session_state.lead_saved = True
                                st.toast("✅ Lead captured!", icon="✏️")
            except Exception as e:
                st.error(f"Error: {e}")
