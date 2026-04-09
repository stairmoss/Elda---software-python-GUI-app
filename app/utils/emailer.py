import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

# Configuration (In production, load from env vars)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "elda.system.ai@gmail.com" # Placeholder
SENDER_PASSWORD = "your_app_password"     # Placeholder

RECIPIENTS = {
    "doctor": "karthik3b@gmail.com",
    "caregiver": "intheknightriders@gmail.com",
    "patient": "gamerbozee5@gmail.com"
}

def send_alert(subject, body, role="caregiver"):
    """
    Simulates sending an email alert.
    Since we don't have valid SMTP credentials in this environment, 
    we will log the email attempt to a file 'email_outbox.log' to prove functionality.
    """
    to_email = RECIPIENTS.get(role, RECIPIENTS["caregiver"])
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    email_content = f"""
    --------------------------------------------------
    [EMAIL SENT]
    To: {to_email} ({role})
    Subject: {subject}
    Time: {timestamp}
    
    {body}
    --------------------------------------------------
    """
    
    print(f"[Email System] Sending alert to {to_email}...")
    
    # Check if password is configured
    if SENDER_PASSWORD == "your_app_password":
        print("[Email Alert] ⚠ Cannot send real email. Please update SENDER_PASSWORD in app/utils/emailer.py")
        # Still log to file for debugging
        with open("email_outbox.log", "a") as f:
            f.write(email_content)
        return

    # Real Email Sending
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[Email System] ✅ Sent successfully to {to_email}")
    except Exception as e:
        print(f"[Email System] ❌ SMTP Error: {e}")

def generate_and_send_summary(risk_data, vitals_data):
    """
    Generates a daily summary and sends it to everyone.
    """
    summary = f"""
    ELDA DAILY REPORT
    -----------------
    Risk Level: {risk_data.get('level', 'Unknown')} (Score: {risk_data.get('support_score', 0)})
    
    Recent Vitals:
    - Heart Rate: {vitals_data.get('heart_rate', '--')} bpm
    - SpO2: {vitals_data.get('oxygen', '--')}%
    
    AI Notes:
    {", ".join(risk_data.get('flags', ['No alerts']))}
    """
    
    # Send to Doctor
    send_alert("Patient Daily Health Summary", summary, "doctor")
    
    # Send to Caregiver
    send_alert("Daily Care Update", summary, "caregiver")
