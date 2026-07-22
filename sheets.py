import gspread
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_NAME, WORKSHEET_NAME
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

import os
import json
from google.oauth2.service_account import Credentials

if os.path.exists("credentials.json"):
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES,
    )
else:
    credentials_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES,
    )

client = gspread.authorize(creds)
spreadsheet = client.open(SPREADSHEET_NAME)
worksheet = spreadsheet.worksheet(WORKSHEET_NAME)


def add_work_hours(date, worker, hours):
    """Додає новий запис."""
    worksheet.append_row([date, worker, hours])


def already_sent_today(worker):
    """Перевіряє, чи вже записував працівник години сьогодні."""
    today = datetime.now().strftime("%d.%m.%Y")

    rows = worksheet.get_all_values()

    for row in rows[1:]:
        if len(row) >= 2:
            if row[0] == today and row[1] == worker:
                return True

    return False


def get_month_hours(worker):
    """Повертає суму годин працівника за поточний місяць."""
    month = datetime.now().strftime("%m.%Y")

    total = 0

    rows = worksheet.get_all_values()

    for row in rows[1:]:
        if len(row) < 3:
            continue

        date = row[0]
        name = row[1]

        if not date.endswith(month):
            continue

        if name != worker:
            continue

        try:
            total += float(str(row[2]).replace(",", "."))
        except:
            pass

    return total