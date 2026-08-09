from datetime import date, timedelta, datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os

from config import DB_CONFIG, SMTP_CONFIG, REMINDER_DAYS_BEFORE
from database import get_connection

def get_upcoming_due_loans():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    today = date.today()
    # Calculate due dates to check (e.g., 1 and 2 days from now)
    due_dates = [today + timedelta(days=d) for d in REMINDER_DAYS_BEFORE]
    # Build parameterized query joining all four SLiMS tables
    placeholders = ", ".join(["%s"] * len(due_dates))
    query = f"""
        SELECT
            l.loan_id,
            l.item_code,
            l.member_id,
            l.due_date,
            m.member_name,
            m.member_email,
            m.member_phone,
            b.title AS book_title
        FROM loan l
        JOIN member m ON l.member_id = m.member_id
        JOIN item i ON l.item_code = i.item_code
        JOIN biblio b ON i.biblio_id = b.biblio_id
        WHERE l.is_return = 0
        AND l.due_date IN ({placeholders})
        AND m.member_email IS NOT NULL
        AND m.member_email != ''
    """
    cursor.execute(query, due_dates)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def already_sent(conn, member_id, item_code, due_date, channel="email"):
    # Check if we already sent this specific reminder
    cursor = conn.cursor()
    cursor.execute("""
        SELECT log_id FROM reminder_log
        WHERE member_id = %s AND item_code = %s AND due_date = %s AND channel = %s
    """, (member_id, item_code, due_date, channel))
    result = cursor.fetchone()
    cursor.close()
    return result is not None


def log_reminder(conn, member_id, item_code, due_date, channel="email"):
    # Record that we sent this reminder so we never double-send
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reminder_log (member_id, item_code, due_date, sent_at, channel)
        VALUES (%s, %s, %s, %s, %s)
    """, (member_id, item_code, due_date, datetime.now(), channel))
    conn.commit()
    cursor.close()

def send_reminder_email(member_name, member_email, book_title, due_date):
    # Build the email message container
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Library Reminder: '{book_title}' is due on {due_date}"
    msg["From"] = SMTP_CONFIG["email"]
    msg["To"] = member_email

    # Calculate how urgent the reminder is
    days_left = (due_date - date.today()).days
    urgency = "tomorrow" if days_left <= 1 else f"in {days_left} days"

    # HTML email template with book details
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Library Book Return Reminder</h2>
        <p>Dear <strong>{member_name}</strong>,</p>
        <p>This is a friendly reminder that the following book is due <strong>{urgency}</strong>:</p>
        <table style="border-collapse: collapse; margin: 15px 0;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Book Title</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{book_title}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Due Date</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{due_date.strftime('%d %B %Y')}</td>
            </tr>
        </table>
        <p>Please return the book on time to avoid fines.</p>
        <p>Thank you,<br>Library Automated Reminder System</p>
    </body>
    </html>
    """

    # Attach HTML content and send via Gmail SMTP
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
        server.starttls()
        server.login(SMTP_CONFIG["email"], SMTP_CONFIG["password"])
        server.sendmail(SMTP_CONFIG["email"], member_email, msg.as_string())

def send_whatsapp_reminder(member_name, member_phone, book_title, due_date):
    from twilio.rest import Client

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+17372212163")

    client = Client(account_sid, auth_token)

    print(f"  Sending WhatsApp from: {from_number}")    

    days_left = (due_date - date.today()).days
    urgency = "tomorrow" if days_left <= 1 else f"in {days_left} days"

    body = (
        f"Hi {member_name}! Reminder: Your library book "
        f"'{book_title}' is due {urgency} ({due_date.strftime('%d %B %Y')}). "
        f"Please return it on time to avoid fines."
    )

    message = client.messages.create(
        body=body,
        from_=from_number,
        to=f"whatsapp:+91{member_phone}",
    )
    return message.sid

def run_reminder_check():
    # Print timestamp for each check run
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running reminder check...")
    loans = get_upcoming_due_loans()
    print(f"  Found {len(loans)} loan(s) due soon.")
    if not loans:
        print("  No reminders to send.")
        return
    conn = get_connection()
    sent_count = 0
    skipped_count = 0
    whatsapp_count = 0
    for loan in loans:
        if already_sent(conn, loan["member_id"], loan["item_code"], loan["due_date"]):
            skipped_count += 1
            continue
        try:
            send_reminder_email(
                loan["member_name"],
                loan["member_email"],
                loan["book_title"],
                loan["due_date"],
            )
            log_reminder(conn, loan["member_id"], loan["item_code"], loan["due_date"])
            sent_count += 1
            print(f"  Sent email to {loan['member_name']} ({loan['member_email']}) "
                  f"for '{loan['book_title']}' due {loan['due_date']}")
        except Exception as e:
            print(f"  FAILED email to {loan['member_email']}: {e}")

        if loan.get("member_phone") and os.getenv("TWILIO_ACCOUNT_SID"):
            if not already_sent(conn, loan["member_id"], loan["item_code"],
                               loan["due_date"], channel="whatsapp"):
                try:
                    send_whatsapp_reminder(
                        loan["member_name"],
                        loan["member_phone"],
                        loan["book_title"],
                        loan["due_date"],
                    )
                    log_reminder(conn, loan["member_id"], loan["item_code"],
                                loan["due_date"], channel="whatsapp")
                    whatsapp_count += 1
                    print(f"  Sent WhatsApp to {loan['member_name']} "
                          f"({loan['member_phone']})")
                except Exception as e:
                    print(f"  FAILED WhatsApp to {loan['member_phone']}: {e}")
    conn.close()
    print(f"  Done: {sent_count} emails, {whatsapp_count} WhatsApp, "
          f"{skipped_count} skipped.")

if __name__ == "__main__":
    run_reminder_check()