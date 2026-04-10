"""
Run this script DIRECTLY on your machine (same server as Flask app):
    python test_email.py

It will tell you EXACTLY what is wrong with the email setup.
"""
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

EMAIL_SENDER    = "food@abhyuday.in"
EMAIL_PASSWORD  = "J@#nv!$200"
EMAIL_RECIPIENT = "food@abhyuday.in"
SMTP_SERVER     = "smtp.office365.com"
SMTP_PORT       = 587

print("=" * 55)
print("  Abhyuday Foods — SMTP Email Diagnostic Tool")
print("=" * 55)
print(f"  Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  From   : {EMAIL_SENDER}")
print(f"  To     : {EMAIL_RECIPIENT}")
print(f"  Server : {SMTP_SERVER}:{SMTP_PORT}")
print("=" * 55)

# ── Step 1: Network reachability ──────────────────────
print("\n[1/5] Testing network connection to smtp.office365.com:587 ...")
try:
    s = socket.create_connection((SMTP_SERVER, SMTP_PORT), timeout=10)
    s.close()
    print("  ✅ Network OK — server is reachable")
except socket.timeout:
    print("  ❌ TIMEOUT — firewall is blocking port 587")
    print("     FIX: Ask your hosting provider to open outbound port 587")
    raise SystemExit(1)
except OSError as e:
    print(f"  ❌ NETWORK ERROR: {e}")
    print("     FIX: Check your internet connection or DNS settings")
    raise SystemExit(1)

# ── Step 2: SMTP connection + EHLO ───────────────────
print("\n[2/5] Connecting to SMTP server ...")
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
    server.set_debuglevel(0)   # set to 1 for raw SMTP logs
    resp = server.ehlo("abhyuday.in")
    print(f"  ✅ Connected — EHLO response: {resp[0]}")
    caps = server.esmtp_features
    print(f"  ℹ️  Server capabilities: {list(caps.keys())}")
except Exception as e:
    print(f"  ❌ Connection failed: {e}")
    raise SystemExit(1)

# ── Step 3: STARTTLS ─────────────────────────────────
print("\n[3/5] Starting TLS encryption ...")
try:
    server.starttls()
    server.ehlo("abhyuday.in")
    print("  ✅ TLS started successfully")
except smtplib.SMTPException as e:
    print(f"  ❌ TLS failed: {e}")
    server.quit()
    raise SystemExit(1)

# ── Step 4: LOGIN ────────────────────────────────────
print(f"\n[4/5] Logging in as {EMAIL_SENDER} ...")
try:
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    print("  ✅ Login successful")
except smtplib.SMTPAuthenticationError as e:
    print(f"  ❌ AUTH FAILED: {e}")
    print()
    print("  Most likely causes:")
    print("  A) SMTP AUTH is disabled in Microsoft 365 Admin Center")
    print("     → Go to: admin.microsoft.com")
    print("       Settings → Org settings → Modern authentication")
    print("       OR: Active users → food@abhyuday.in → Mail tab")
    print("       → Enable 'Authenticated SMTP'")
    print()
    print("  B) Multi-Factor Authentication (MFA) is enabled")
    print("     → Create an App Password:")
    print("       Microsoft Account → Security → App passwords")
    print("       Use that app password instead of your normal password")
    print()
    print("  C) Wrong password")
    print(f"     → Verify you can log in to outlook.com with {EMAIL_SENDER}")
    server.quit()
    raise SystemExit(1)
except Exception as e:
    print(f"  ❌ Login error: {type(e).__name__}: {e}")
    server.quit()
    raise SystemExit(1)

# ── Step 5: Send test email ───────────────────────────
print(f"\n[5/5] Sending test email to {EMAIL_RECIPIENT} ...")
try:
    msg = MIMEMultipart('alternative')
    msg['From']    = f"Abhyuday Foods <{EMAIL_SENDER}>"
    msg['To']      = EMAIL_RECIPIENT
    msg['Subject'] = f"✅ Test Email — {datetime.now().strftime('%d %b %Y %H:%M')}"

    html = f"""<html><body>
    <h2 style="color:#C0541A;">✅ Email is Working!</h2>
    <p>This is a test email from your Abhyuday Foods backend.</p>
    <p><strong>Sent at:</strong> {datetime.now().strftime('%d %B %Y at %I:%M %p')}</p>
    <p>Your enquiry notification emails will now be delivered correctly.</p>
    <hr>
    <small style="color:#999;">Abhyuday Bharat Food Cluster LLP</small>
    </body></html>"""

    msg.attach(MIMEText("Email is working! Test sent at " + datetime.now().strftime('%d %B %Y %H:%M'), 'plain'))
    msg.attach(MIMEText(html, 'html'))

    server.send_message(msg)
    server.quit()

    print("  ✅ TEST EMAIL SENT SUCCESSFULLY!")
    print(f"     Check your inbox at {EMAIL_RECIPIENT}")
    print()
    print("=" * 55)
    print("  🎉  Everything is working correctly.")
    print("      Enquiry emails will now be delivered.")
    print("=" * 55)

except Exception as e:
    print(f"  ❌ Send failed: {type(e).__name__}: {e}")
    server.quit()
    raise SystemExit(1)
