import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, date
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
with open("creds.json", "r") as f:
    credentials_dict = json.load(f)
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)

# Fetch sheet data
sheet = client.open('tape_calibration_log').sheet1
data = sheet.get_all_values()

# Build message for expiring entries
message = ''
for idx, row in enumerate(data[1:], start=2):
    if row[9] == 'FALSE' and row[6] != '':
        try:
            target_date = datetime.strptime(row[5], "%Y-%m-%d").date()
            days_remaining = (target_date - date.today()).days
            if days_remaining <= 5:
                message += f"Tape Number: {row[0]}, EPF Number: {row[1]}, Department: {row[2]}, Name: {row[3]}, Exp. Date: {row[5]} ({days_remaining} days left)\n"
        except Exception as e:
            print(f"Error in row {idx}: {e}")

# Send email if needed
if message != '':
    full_message = f"""This is an automated alert for tape calibrations nearing expiration:\n\n{message}"""
    msg = MIMEText(full_message)
    msg['Subject'] = '⚠️ Tape Calibration Expiry Alert'
    msg['From'] = os.environ['EMAIL_USER']
    msg['To'] = os.environ['EMAIL_TO']

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.environ['EMAIL_USER'], os.environ['EMAIL_PASS'])
        smtp.send_message(msg)
