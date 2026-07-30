import os
import json

dirs = [
    "graph/nodes",
    "agents",
    "rag/docs",
    "tools",
    "data",
    "logs",
    "config",
    "tests"
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

# 1. .env.example
env_example = """GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
"""
with open(".env.example", "w") as f:
    f.write(env_example)

with open(".env", "w") as f:
    f.write(env_example)

# 2. requirements.txt
reqs = """streamlit
langchain-google-genai
langchain-groq
sentence-transformers
chromadb
langgraph
pydantic
python-dotenv
"""
with open("requirements.txt", "w") as f:
    f.write(reqs)

# 3. data/mock_records.json
mock_records = [
    {"id": "TKT-1001", "status": "Open", "subject": "VPN Access Issue"},
    {"id": "TKT-1002", "status": "Resolved", "subject": "Laptop Replacement"},
    {"id": "TKT-1003", "status": "In Progress", "subject": "Software License Request"}
]
with open("data/mock_records.json", "w") as f:
    json.dump(mock_records, f, indent=2)

# 4. rag/docs/ (8 synthetic files)
docs = {
    "refund_policy.md": "# Refund Policy\nAll software purchases made through the company portal are eligible for a full refund within 30 days of purchase. Hardware purchases are non-refundable unless defective. To initiate a refund, please log a ticket with your purchase ID.",
    "wfh_stipend_policy.md": "# Work From Home Stipend Policy\nFull-time employees are eligible for a $500 WFH stipend every calendar year. This can be used for desks, chairs, monitors, and peripherals. Submit your receipts through the expense portal. Approvals take up to 3 business days.",
    "it_troubleshooting.md": "# IT Troubleshooting Guide\n## VPN Issues\nIf you cannot connect to the VPN, first ensure your Cisco AnyConnect client is updated to version 5.x. If the issue persists, reset your password via the self-service portal.\n## Monitor not working\nEnsure the HDMI/DisplayPort cable is firmly connected and the monitor is set to the correct input source.",
    "leave_policy.md": "# Leave Policy\nEmployees accrue 1.5 days of PTO per month. Sick leave is unlimited but requires a doctor's note for absences longer than 3 consecutive days. Parental leave is up to 12 weeks fully paid for primary caregivers.",
    "expense_policy.md": "# Expense Policy\nMeals during business travel are covered up to $75 per day. Alcohol is not covered unless entertaining clients. All expenses over $25 require an itemized receipt.",
    "travel_policy.md": "# Travel Policy\nAll business travel must be booked through the Navan portal. Flights over 6 hours are eligible for Business Class if approved by a VP. Otherwise, Economy is standard.",
    "hardware_request.md": "# Hardware Request Guidelines\nStandard issue laptops are 14-inch MacBook Pros or equivalent Windows machines (Dell XPS). Upgrades to 16-inch or higher RAM configurations require manager approval and a valid business justification.",
    "security_guidelines.md": "# Security Guidelines\nNever share your passwords or MFA tokens. The IT department will never ask for your password. Lock your computer when leaving it unattended in public spaces or at the office."
}
for name, content in docs.items():
    with open(f"rag/docs/{name}", "w") as f:
        f.write(content)

# 5. tests/test_queries.json
# Covering: knowledge-only, action-only, multi-intent, deliberately ambiguous
test_queries = [
    {"query": "How much is the WFH stipend?", "expected_type": "knowledge_query"},
    {"query": "Can I expense alcohol on a business trip?", "expected_type": "knowledge_query"},
    {"query": "I need to open a ticket because my VPN is broken.", "expected_type": "action_request"},
    {"query": "Check the status of ticket TKT-1002.", "expected_type": "action_request"},
    {"query": "Send a notification to user@example.com about the new leave policy.", "expected_type": "action_request"},
    {"query": "What is the refund policy for hardware, and also open a ticket for my defective monitor.", "expected_type": "multi_intent"},
    {"query": "I have an issue.", "expected_type": "ambiguous"},
    {"query": "Tell me about the universe.", "expected_type": "ambiguous"},
    {"query": "Send an email to my manager.", "expected_type": "ambiguous_action"}, # missing email param
    {"query": "How many days of PTO do I get?", "expected_type": "knowledge_query"},
    {"query": "Look up TKT-9999", "expected_type": "action_request"}, # intentional not-found
    {"query": "I bought a chair, how do I get reimbursed? Also email hr@example.com that I submitted it.", "expected_type": "multi_intent"},
    {"query": "What laptops are standard issue?", "expected_type": "knowledge_query"},
    {"query": "My monitor isn't working, what should I do?", "expected_type": "knowledge_query"},
    {"query": "Hello there!", "expected_type": "zero_intent"}
]
with open("tests/test_queries.json", "w") as f:
    json.dump(test_queries, f, indent=2)

# 6. test scripts
test_gemini = """import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "your_gemini_api_key_here":
    print("Please set GEMINI_API_KEY in .env")
    exit(1)

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Respond with exactly one word: Success'
)
print("Gemini API Test:", response.text)
"""
with open("test_gemini.py", "w") as f:
    f.write(test_gemini)

test_email = """import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
gmail_address = os.getenv("GMAIL_ADDRESS")
gmail_password = os.getenv("GMAIL_APP_PASSWORD")

if not gmail_address or gmail_address == "your_email@gmail.com":
    print("Please set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env")
    exit(1)

msg = EmailMessage()
msg.set_content("This is a test email from AgentOps Phase 0.")
msg["Subject"] = "AgentOps SMTP Test"
msg["From"] = gmail_address
msg["To"] = gmail_address

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(gmail_address, gmail_password)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully to", gmail_address)
except Exception as e:
    print("Failed to send email:", e)
"""
with open("test_email.py", "w") as f:
    f.write(test_email)

print("Phase 0 setup complete. Folders and files created.")
