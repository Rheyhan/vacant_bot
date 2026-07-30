from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from discord import SyncWebhook, Embed, Color

# Send email function
def send_email(text: str = "", EMAIL_CREDENTIALS: dict = None):
    '''
    Sends an email notification with the provided text using the specified email credentials.

    Parameters
    ----------
    text : str
        The content of the email to be sent.
    EMAIL_CREDENTIALS : dict
        A dictionary containing the email credentials (email and password).
    '''
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(EMAIL_CREDENTIALS["email"], EMAIL_CREDENTIALS["password"])

    message = MIMEMultipart("alternative")
    message["Subject"] = "VACANT BOT Error Notification"
    message["From"] = EMAIL_CREDENTIALS["email"]
    message["To"] = EMAIL_CREDENTIALS["send_to_email"]
    text = f"""\
    Hi, this is an automated email from your syntax :3.
    Some error has occurred in the vacant bot, please check the log for more details.
    {text}
    """

    part1 = MIMEText(text, "plain")
    message.attach(part1)
    s.sendmail(EMAIL_CREDENTIALS["email"], EMAIL_CREDENTIALS["send_to_email"], message.as_string())
    s.close()

# Send post to Discord
def send_post_on_discord(job: dict, WEBHOOK_URL: str):
    '''
    Sends a job posting to a Discord channel using a webhook.

    Parameters
    ----------
    job : dict
        A dictionary containing job details such as position, company name, location, experience needed, last updated date, view count, AI match reasoning, and post link.
    
    WEBHOOK_URL : str
        The Discord webhook URL to send the job posting to.
    '''
    try:
        # Initialize the synchronous webhook
        webhook = SyncWebhook.from_url(WEBHOOK_URL)
        
        position = job.get("Position", "New Job Opportunity")
        if isinstance(position, list):
            position = ", ".join(position) if position else "New Job Opportunity"

        reason = job.get("Reason", "No reason provided.")
        if len(reason) > 1024:
            reason = reason[:1021] + "..."

        embed = Embed(
            title=position,
            description=f"**{job.get('Nama_Perusahaan', 'Unknown Company')}**",
            color=Color.brand_green(),
        )

        if job.get("Icon"):
            embed.set_thumbnail(url=job["Icon"])

        embed.add_field(name="Location", value=job.get("Location", "N/A"), inline=True)
        embed.add_field(name="Experience", value=job.get("Experience_Needed", "N/A"), inline=True)
        embed.add_field(name="Last_Updated", value=job.get("Last_Updated", "N/A"), inline=True)
        embed.add_field(name="Views", value=job.get("View_Count", "N/A"), inline=True)
        embed.add_field(name="AI Match Reasoning", value=reason, inline=False)
        embed.add_field(name="Job Post Link", value=f"[Click Here]({job['Post_link']})", inline=False)
        
        # Send it directly
        webhook.send(embed=embed)

    except Exception as exc:
        print(f"Error sending to Discord: {exc}")