import os
import json

docs = {
    # Engineering
    "eng_deployment_guidelines.md": "# Engineering Deployment Guidelines\nAll code must be deployed via Jenkins pipelines. Deployments to production (us-east-1) are only allowed between 9AM and 3PM EST on Tuesdays and Thursdays. Any out-of-band deployments require VP of Engineering approval. Staging deployments can happen at any time.",
    "eng_code_review.md": "# Code Review Standards\nEvery PR must have at least 2 approving reviews from senior engineers before merging. All PRs must include unit tests with at least 80% coverage. Do not commit secrets or AWS keys; use AWS Secrets Manager.",
    "eng_incident_response.md": "# Incident Response Protocol\nWhen PagerDuty alerts, the on-call engineer must acknowledge within 5 minutes. If unresolved within 15 minutes, escalate to the secondary on-call. Create a Slack channel prefixed with `#inc-` for coordination. A post-mortem document is required within 48 hours.",

    # HR
    "hr_onboarding_day1.md": "# Day 1 Onboarding Guide\nWelcome! On Day 1, you must: 1) Pick up your laptop from IT (2nd floor). 2) Complete the I-9 verification in Workday. 3) Attend the 10AM orientation in conference room Alpha. Lunch will be catered.",
    "hr_benefits.md": "# Medical Benefits\nWe offer a choice between a high-deductible health plan (HDHP) with an HSA, or a standard PPO plan. The company matches up to $1,000 annually to your HSA. Dental and Vision are fully covered. Open enrollment is in November.",
    "hr_401k.md": "# 401(k) Match Policy\nThe company matches 100% of the first 4% of your salary contributed to the 401(k) plan, and 50% of the next 2%. Vesting is immediate. You can change your contribution rate in Fidelity at any time.",

    # Finance
    "fin_corporate_card.md": "# Corporate Credit Card Policy\nCorporate cards are issued to Directors and above, or employees who travel more than once a quarter. Personal expenses are strictly prohibited. Late expense reports (past 30 days) will result in card suspension.",
    "fin_vendor_procurement.md": "# Vendor Procurement\nAll new software vendors exceeding $5,000/year must go through a security review (InfoSec) and a legal review (Redlining). Submit requests via the Coupa platform. Typical turnaround is 3-4 weeks.",
    
    # IT & Support
    "it_password_reset.md": "# Password Reset Policy\nPasswords expire every 90 days. You will receive an email warning 7 days prior. If you lock yourself out, call the IT helpdesk at x4455. IT will verify your identity using your manager's approval.",
    "it_guest_wifi.md": "# Guest WiFi Access\nThe 'Corp-Guest' WiFi requires a daily rotating password. You can generate a 24-hour pass for your guests in the Envoy app. Guests are restricted from accessing internal IP subnets.",
    "it_lost_device.md": "# Lost or Stolen Device\nIf your laptop or phone is lost or stolen, report it to IT IMMEDIATELY via emergency email or phone call. We will issue a remote wipe command within 15 minutes to protect company data.",
    
    # Facilities
    "fac_office_hours.md": "# Office Hours and Access\nThe main office is open 24/7 for employees with badge access. HVAC is only active Monday through Friday, 7AM to 7PM. To request weekend HVAC, file a facilities ticket.",
    "fac_parking.md": "# Office Parking\nParking is free for all employees in the East Garage. EV charging spots are limited to 4 hours maximum per vehicle. If you leave your car overnight, you must register it with security.",
    "fac_dogs_in_office.md": "# Dog Policy\nWe are a dog-friendly office! Dogs must be up-to-date on vaccinations, potty-trained, and kept on a leash in common areas. If a dog barks excessively, you may be asked to take them home."
}

for name, content in docs.items():
    with open(f"rag/docs/{name}", "w") as f:
        f.write(content)

print(f"Created {len(docs)} new synthetic documents.")

# Append to mock_records.json
mock_records_path = "data/mock_records.json"
try:
    with open(mock_records_path, "r") as f:
        records = json.load(f)
except Exception:
    records = []

new_records = [
    {"id": "TKT-1004", "status": "Closed", "subject": "Need access to AWS Staging"},
    {"id": "TKT-1005", "status": "In Progress", "subject": "Monitor flickering"},
    {"id": "TKT-1006", "status": "Open", "subject": "Order new ergonomic chair"},
    {"id": "TKT-1007", "status": "Resolved", "subject": "Update GitHub permissions"},
    {"id": "TKT-1008", "status": "Open", "subject": "Guest WiFi pass for client meeting"}
]

# Merge without duplicates
existing_ids = {r["id"] for r in records}
for nr in new_records:
    if nr["id"] not in existing_ids:
        records.append(nr)

with open(mock_records_path, "w") as f:
    json.dump(records, f, indent=2)

print(f"Added {len(new_records)} new mock records.")

# Rebuild the RAG index
os.system("python rag/build_index.py")
print("RAG Index rebuilt successfully!")
