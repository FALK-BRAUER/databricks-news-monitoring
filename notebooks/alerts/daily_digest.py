# Databricks notebook source
# MAGIC %md
# MAGIC # Daily CTO/VP Opportunity Digest
# MAGIC
# MAGIC Sends email with top opportunities from the past 24 hours

# COMMAND ----------

%pip install sendgrid

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

from pyspark.sql.functions import *
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import json

print("✓ Libraries imported")

# COMMAND ----------

# Configuration
RECIPIENT_EMAIL = "falk.brauer@me.com"
FROM_EMAIL = "noreply@databricks.com"  # Change to your verified sender
SENDGRID_API_KEY = dbutils.secrets.get(scope="aws", key="SENDGRID_API_KEY")  # Add this to secrets

# COMMAND ----------

# MAGIC %md
# MAGIC ## Get Yesterday's Opportunities

# COMMAND ----------

# Get opportunities from last 24 hours
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

opportunities = spark.table("workspace.news_monitoring.gold_cto_opportunities") \
    .filter(col("ingestion_date") >= yesterday) \
    .filter(col("opportunity_score") >= 5) \
    .orderBy(desc("opportunity_score")) \
    .limit(10)

opp_count = opportunities.count()

print(f"Found {opp_count} opportunities from last 24 hours")

# COMMAND ----------

# Get company leads
company_leads = spark.table("workspace.news_monitoring.gold_company_leads") \
    .filter(col("last_mentioned") >= yesterday) \
    .filter(col("total_signals") >= 2) \
    .orderBy(desc("total_signals")) \
    .limit(10)

company_count = company_leads.count()

print(f"Found {company_count} companies with signals")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Build HTML Email

# COMMAND ----------

def build_email_html(opportunities_df, companies_df):
    """Build HTML email content"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #2563eb; }}
            h2 {{ color: #1e40af; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }}
            .opportunity {{ background: #f8fafc; padding: 15px; margin: 15px 0; border-left: 4px solid #3b82f6; }}
            .score {{ background: #3b82f6; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold; }}
            .signals {{ color: #059669; font-size: 0.9em; }}
            .company-lead {{ background: #fef3c7; padding: 12px; margin: 10px 0; border-left: 4px solid #f59e0b; }}
            a {{ color: #2563eb; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Your Daily CTO/VP Opportunity Digest</h1>
            <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>

            <h2>🔥 Top Opportunities (Last 24 Hours)</h2>
    """

    # Add opportunities
    if opportunities_df.count() > 0:
        for row in opportunities_df.collect():
            companies = ", ".join(row.mentioned_companies[:3]) if row.mentioned_companies else "N/A"
            signals = ", ".join(row.opportunity_signals) if row.opportunity_signals else ""
            funding = f"{row.funding_round} - ${row.funding_amount_usd/1000000:.1f}M" if row.funding_amount_usd else row.funding_round or ""

            html += f"""
            <div class="opportunity">
                <p><span class="score">Score: {row.opportunity_score}</span></p>
                <h3>{row.title}</h3>
                <p><strong>Region:</strong> {row.region.upper()} | <strong>Companies:</strong> {companies}</p>
                {f'<p><strong>Funding:</strong> {funding}</p>' if funding else ''}
                <p class="signals"><strong>Signals:</strong> {signals}</p>
                <p><a href="{row.url}" target="_blank">Read Article →</a></p>
            </div>
            """
    else:
        html += "<p><em>No new high-priority opportunities in the last 24 hours.</em></p>"

    # Add company leads
    html += "<h2>🏢 Companies to Watch</h2>"

    if companies_df.count() > 0:
        for row in companies_df.collect():
            signals_desc = []
            if row.funding_signals > 0:
                signals_desc.append(f"💰 {row.funding_signals} funding signals")
            if row.expansion_signals > 0:
                signals_desc.append(f"🌍 {row.expansion_signals} expansion signals")
            if row.leadership_signals > 0:
                signals_desc.append(f"👔 {row.leadership_signals} leadership changes")

            html += f"""
            <div class="company-lead">
                <h3>{row.company}</h3>
                <p><strong>Region:</strong> {row.region.upper()} | <strong>Total Signals:</strong> {row.total_signals}</p>
                <p>{' | '.join(signals_desc)}</p>
                {f'<p><strong>Latest Funding:</strong> {row.latest_funding_round}</p>' if row.latest_funding_round else ''}
                <p><a href="https://www.google.com/search?q={row.company.replace(' ', '+')}+careers" target="_blank">Search Careers →</a></p>
            </div>
            """
    else:
        html += "<p><em>No new company signals in the last 24 hours.</em></p>"

    # Footer
    html += f"""
            <div class="footer">
                <p>💡 <strong>Next Steps:</strong></p>
                <ul>
                    <li>Research these companies on LinkedIn</li>
                    <li>Check their career pages for senior tech roles</li>
                    <li>Set up Google Alerts for top companies</li>
                    <li>Connect with their leadership on LinkedIn</li>
                </ul>
                <p><strong>Dashboard:</strong> <a href="https://dbc-5a365369-15d1.cloud.databricks.com">View in Databricks</a></p>
                <p style="color: #9ca3af; font-size: 0.8em;">Automated daily digest from your News Monitoring Platform</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html

email_html = build_email_html(opportunities, company_leads)

print("✓ Email HTML generated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Send Email

# COMMAND ----------

def send_digest_email(recipient, html_content):
    """Send email via SendGrid"""

    subject = f"🎯 Daily CTO/VP Digest - {opp_count} Opportunities | {datetime.now().strftime('%b %d')}"

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=recipient,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✓ Email sent successfully!")
        print(f"  Status code: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ Error sending email: {str(e)}")
        return False

# Only send if there are opportunities
if opp_count > 0 or company_count > 0:
    send_digest_email(RECIPIENT_EMAIL, email_html)
    print(f"\n📧 Daily digest sent to {RECIPIENT_EMAIL}")
else:
    print("\n📭 No opportunities today - email not sent")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

summary = {
    "date": datetime.now().isoformat(),
    "opportunities_found": opp_count,
    "companies_found": company_count,
    "email_sent": opp_count > 0 or company_count > 0
}

print("\n" + "="*80)
print("DAILY DIGEST SUMMARY")
print("="*80)
print(json.dumps(summary, indent=2))
print("="*80)
