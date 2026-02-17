import os
import datetime
import time
import requests

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
CLIENT_LOGINS = os.environ["CLIENT_LOGINS"]  # <-- одна секретка со списком
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
date_str = yesterday.strftime("%Y-%m-%d")

url = "https://api.direct.yandex.com/json/v5/reports"

base_headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
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
        "FieldNames": ["Date", "CampaignName", "Impressions", "Clicks", "Cost"],
        "ReportName": "DirectReport",
        "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
        "DateRangeType": "CUSTOM_DATE",
        "Format": "TSV",
        "IncludeVAT": "NO",
        "IncludeDiscount": "NO"
    }
}

def main():
    client_logins = [x.strip() for x in CLIENT_LOGINS.split(";") if x.strip()]

    for client_login in client_logins:
        headers = dict(base_headers)
        headers["Client-Login"] = client_login

        response = requests.post(url, json=body, headers=headers)

        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            if not lines:
                continue

            headers_row = lines[0].split('\t')
            data_rows = lines[1:]

            for row in data_rows:
                values = row.split('\t')
                if len(values) != len(headers_row):
                    continue

                data = dict(zip(headers_row, values))

                payload = {
                    "client_login": client_login,  # чтобы различать в вебхуке
                    "date": data.get("Date"),
                    "campaign_name": data.get("CampaignName"),
                    "cost": float(data.get("Cost", 0) or 0),
                    "impressions": int(data.get("Impressions", 0) or 0),
                    "clicks": int(data.get("Clicks", 0) or 0),
                    "conversions": 0
                }

                res = requests.post(WEBHOOK_URL, json=payload)
                print(f"[{client_login}] Sent: {payload} | Status: {res.status_code}")
                time.sleep(1)

        else:
            print(f"[{client_login}] Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    main()
