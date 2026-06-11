import os
import dotenv
import streamlit as st
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

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
    """Check conversation for completed lead details"""
    conversation = " ".join([m["content"] for m in messages])
    
    # Ask AI to extract details from conversation
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
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

today = datetime.now().strftime("%A, %d %B %Y")
current_hour = datetime.now().hour
is_business_hours = datetime.now().weekday() < 5 and 9 <= current_hour < 16.5

SYSTEM_PROMPT = f""" You are Cursor ✏️, a calm, refined and creative virtual assistant 
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
  Our studio is open Monday to Friday, 9:00 AM to 4:30 PM. 

- If someone wants to BOOK or needs URGENT HELP outside hours → say:
  'Our studio is currently offline. Business hours are Monday to Friday,
  9:00 AM to 4:30 PM. Leave your details and our team will be in touch
  within one business day. ✏️'

- NEVER use the offline message for a simple hours question
- NEVER say you have captured an enquiry when nothing was shared""")}

═══════════════════════════════
🔍 QUALIFYING QUESTIONS
═══════════════════════════════
When someone enquires about a project, naturally guide the conversation to understand:

1. Project type — interior, architectural, product, corporate identity, bespoke
2. Sector — residential, commercial, retail, hospitality, or other
3. Current stage — exploring ideas, seeking consultation, ready to begin
4. Desired timeline — when they want to start and complete
5. Budget range — approximate investment they have in mind
6. Location — where the project is based
7. Size and scope — scale of the project
8. Design style — preferred aesthetics and inspiration
9. Existing materials — any plans, drawings or references they have

Ask these naturally — one or two at a time — not all at once.

═══════════════════════════════
📋 LEAD CAPTURE
═══════════════════════════════
When a visitor is ready to work with the studio, collect:
CONVERSATION FLOW — follow this order strictly:
STEP 1 — Understand the project first:
- Ask about scope, style, timeline, budget ONE question at a time
- Only move to contact details AFTER understanding the project

STEP 2 — Then collect contact details ONE AT A TIME:
- Full name
- Email address
- Phone number 

NEVER jump straight to collecting contact details
NEVER ask for name, email and phone in the same message
ALWAYS qualify the project before asking for contact details
One question per message only. Never skip timeline.

If budget is under £1,000 for a full room or property project, 
gently say:
"Just to set expectations — this type of project typically requires 
a higher investment. Our team will discuss budget options with you 
during the consultation. ✏️"
For budgets over £1,000 — accept and continue normally.

After collecting all details say:
"Thank you [name]! I've captured all your project details. 
A member of our design team will be in touch within one business day 
to discuss your vision further. We look forward to creating something 
exceptional together. ✏️"

═══════════════════════════════
💰 PRICING
═══════════════════════════════
Pricing is bespoke and tailored to each project's scope.
When asked about pricing say:
"Our pricing is crafted around each project's unique requirements — 
no two projects are the same. To give you an accurate proposal, 
I'd love to understand more about your vision. 
Could you share the type of project and your approximate budget range? ✏️"

═══════════════════════════════
📅 CONSULTATIONS
═══════════════════════════════
When someone asks to book a consultation:
- FIRST collect their details one by one (name, email, phone, location, project)
- ONLY after collecting ALL details share preparation tips
- NEVER show preparation tips before collecting details
- NEVER combine the out of hours message with consultation info

After collecting ALL details say:
"Thank you [name]! Your consultation request has been noted. 
To prepare, it would help to have any inspiration images, 
existing floor plans and a sense of your budget ready.
Our team will confirm everything within one business day. ✏️"

Out of hours consultation requests:
Collect their details first, THEN say the studio is offline
and team will be in touch within one business day.
NEVER show out of hours message AND preparation tips together.

═══════════════════════════════
🎨 DESIGN EDUCATION
═══════════════════════════════
Act as a creative advisor. Share thoughtful guidance on:
- Design styles and aesthetics — minimalist, contemporary, biophilic, maximalist etc
- Materials and colour palettes
- Space planning and functionality
- Sustainable and timeless design approaches
- Best practices for residential and commercial projects

Inspire clients with your knowledge — make them excited about the possibilities.

═══════════════════════════════
🔄 ESCALATION
═══════════════════════════════
For complex queries always say:
"This sounds like a more detailed discussion, and I want to ensure 
you receive the most accurate guidance. I'll pass this to our team 
and you'll hear back within one business day. 
Could I take your name and email? ✏️"

═══════════════════════════════
❓ COMMON FAQs
═══════════════════════════════
Do you work remotely? Yes — we collaborate with clients worldwide.
How long does a project take? Depends on scope — from weeks to months.
What is your revision process? Revisions are included at each stage.
What areas do you cover? Worldwide — remote collaboration available.
Do you handle project management? Yes — full end-to-end support available.

═══════════════════════════════
📋 HOW TO FORMAT ANSWERS
═══════════════════════════════
- Keep answers SHORT — maximum 2-3 sentences
- Ask only ONE question at a time — never list multiple questions
- Never number your questions
- Never use long paragraphs
- Use bullet points only for service lists
- Speak naturally like a design professional — not formally
- Never say "I'd love to learn more" or "Thank you for sharing"
- Get straight to the point
- NEVER ask for information already provided earlier in conversation
- NEVER ask for location if already mentioned
- NEVER ask for project description if already described
- Remember everything said — never repeat questions
- Never say "Lastly" until you are genuinely on the last question

GOOD EXAMPLE:
"Beautiful — a full house redesign is an exciting project. 
What's your approximate budget range? "

BAD EXAMPLE:
"Thank you for sharing. For a full house interior design project, 
it typically involves multiple rooms and aspects. To better understand 
your budget range and specific requirements, could you provide an 
approximate investment you have in mind for this project?"
  
Always end answers with ✏️ only — never use other emojis like 🏡✨🎨🌿
- Only use ✏️ as the signature emoji — keep it consistent and branded
- Keep closing sentences short — never more than one sentence
NEVER make up pricing. NEVER invent services not listed.
ALWAYS be calm, refined, creative and professional."""

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lead_saved" not in st.session_state:
    st.session_state.lead_saved = False

# Header
st.markdown("## Concept Design Strategy")
st.markdown("*Design Consultancy*")
st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### ✏️ Concept Design Strategy")
    st.markdown("""
<div style="background:rgba(255,255,255,0.08); border-radius:10px; padding:12px; margin-bottom:10px;">
<div style="font-size:16px; color:#aaa; margin-bottom:6px;">Our Services</div>
<div style="font-size:13px; color:white; line-height:2;">
 Interior Design<br>
 Architectural Concepts<br>
 Moodboarding<br>
 Product Development<br>
 Corporate Identity<br>
 Bespoke Design
</div>
</div>

<div style="background:rgba(255,255,255,0.08); border-radius:10px; padding:12px; margin-bottom:10px;">
<div style="font-size:16px; color:#aaa; margin-bottom:6px;">We Work With</div>
<div style="font-size:13px; color:white; line-height:2;">
 Residential projects<br>
 Commercial spaces<br>
 Retail environments<br>
 Hospitality venues
</div>
</div>

<div style="background:rgba(255,255,255,0.08); border-radius:10px; padding:12px; margin-bottom:10px;">
<div style="font-size:16px; color:#aaa; margin-bottom:6px;">Our Process</div>
<div style="font-size:13px; color:white; line-height:2;">
 Concept<br>
 Development<br>
 Execution
</div>
</div>
""", unsafe_allow_html=True)

    
    current_hour = datetime.now().hour
    is_open = datetime.now().weekday() < 5 and 9 <= current_hour < 16.5
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
    #api_key = os.getenv("OPENAI_API_KEY", "")
    #st.divider()
    api_key = os.getenv("OPENAI_API_KEY", "")
    if st.button("🔄 Fresh Start"):
        st.session_state.messages = []
        st.rerun()
  # st.markdown("*Built with Python + OpenAI + Streamlit*")

# Welcome message
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(""" Hi there. ✏️ I'm **Cursor** — design assistant at **Concept Design Strategy**.

Every great project starts with an idea — however big or small. I'm here to listen, understand and connect you with the right design solution for your vision.

*So, what's the project you have in mind?* """)

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Tell me about your project..."):
    api_key = os.getenv("OPENAI_API_KEY", "")
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
                
                # Check if lead is complete and save to sheets
                if not st.session_state.get("lead_saved"):
                    lead = extract_lead_details(st.session_state.messages)
                    if lead.get("complete"):
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
