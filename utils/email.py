import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import EMAIL_CONFIG
import logging

logger = logging.getLogger(__name__)


def send_job_email(user_email: str, user_name: str, notification: dict, jobs: list):
    if not jobs or not EMAIL_CONFIG['email_user'] or not EMAIL_CONFIG['email_password']:
        logger.info(f"Skipping email to {user_email}: No jobs or email not configured")
        return

    # Build job list HTML
    job_list_html = ""
    for job in jobs:
        job_list_html += f"""
        <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
            <h3 style="margin: 0 0 10px 0; color: #333;">{job.get('title', 'N/A')}</h3>
            <p style="margin: 5px 0;"><strong>Company:</strong> {job.get('company', 'N/A')}</p>
            <p style="margin: 5px 0;"><strong>Location:</strong> {job.get('location', 'N/A')}</p>
            <p style="margin: 5px 0;"><strong>Job Type:</strong> {job.get('job_type', 'N/A')}</p>
            <p style="margin: 5px 0;">
                <a href="{job.get('job_url_direct') or job.get('job_url', '#')}" 
                   style="color: #ff6600; text-decoration: none; font-weight: bold;">
                    View Job →
                </a>
            </p>
        </div>
        """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Joby: {len(jobs)} New {notification['title']} Jobs"
    msg['From'] = f"Joby <noreply@joby.com>"
    msg['To'] = "avraham.bicha@gmail.com"
    msg['Reply-To'] = "noreply@joby.com"


    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #ff6600;">Hello {user_name}! 👋</h2>
        <p>We found <strong>{len(jobs)}</strong> new jobs matching your "{notification['title']}" alert:</p>
        {job_list_html}
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;" />
        <p style="color: #666; font-size: 14px;">
            This is your {notification['frequency']} job alert from <strong>Joby</strong>.
        </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['email_user'], EMAIL_CONFIG['email_password'])
            server.send_message(msg)
        logger.info(f"Email sent to {user_email} for notification: {notification['title']}")
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {e}")
