import os
import datetime
import time
import requests

# ===== Загружаем секреты из env =====
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
CLIENT_LOGIN = os.environ["CLIENT_LOGIN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# ===== Параметры даты =====
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
date_str = yesterday.strftime("%Y-%m-%d")


url = "https://api.direct.yandex.com/json/v5/reports"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Client-Login": CLIENT_LOGIN,
    "Accept-Language": "ru",
    "processingMode": "auto",
    "returnMoneyInMicros": "false",
    "skipReportHeader": "true",
    "skipReportSummary": "true"
}
body = {
    "params": {
        "SelectionCriteria": {
            "DateFrom": date_str,
            "DateTo": date_str
        },
        "FieldNames": [
            "Date",
            "CampaignName",
            "Impressions",
            "Clicks",
            "Cost"
        ],
        "ReportName": "DirectReport",
        "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
        "DateRangeType": "CUSTOM_DATE",
        "Format": "TSV",
        "IncludeVAT": "NO",
        "IncludeDiscount": "NO"
    }
}

def main():
    response = requests.post(url, json=body, headers=headers)

    if response.status_code == 200:
        lines = response.text.strip().split('\n')
        headers_row = lines[0].split('\t')
        data_rows = lines[1:]

        for row in data_rows:
            values = row.split('\t')
            if len(values) != len(headers_row):
                continue

            data = dict(zip(headers_row, values))

            payload = {
                "date": data.get("Date"),
                "campaign_name": data.get("CampaignName"),
                "cost": float(data.get("Cost", 0) or 0),
                "impressions": int(data.get("Impressions", 0) or 0),
                "clicks": int(data.get("Clicks", 0) or 0),
                "conversions": 0
            }

            res = requests.post(WEBHOOK_URL, json=payload)
            print(f"Sent: {payload} | Status: {res.status_code}")
            time.sleep(1)

    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    main()
