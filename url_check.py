import requests
import os
from dotenv import load_dotenv

def check_link(url):
    try:
        if not url:
            return {"error": "URL is required"}, 400

        load_dotenv()
        VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_KEY")

        if not VIRUSTOTAL_API_KEY:
            return {"error": "VirusTotal API key not found"}, 500

        virustotal_url = "https://www.virustotal.com/api/v3/urls"
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}
        scan_result = requests.post(virustotal_url, headers=headers, data={"url": url})
        print(scan_result.text)

        if scan_result.status_code != 200:
            return {"error": "Failed to initiate scan", "details": scan_result.text}, 502

        scan_json = scan_result.json()
        scan_id = scan_json.get("data", {}).get("id")
        if not scan_id:
            return {"error": "Scan ID not found"}, 502

        result_url = f"https://www.virustotal.com/api/v3/analyses/{scan_id}"
        result_response = requests.get(result_url, headers=headers)

        if result_response.status_code != 200:
            return {"error": "Failed to fetch analysis results", "details": result_response.text}, 502

        stats = result_response.json().get("data", {}).get("attributes", {}).get("stats", {})

        if not stats:
            return {"error": "No stats found"}, 502

        result = "malicious" if stats.get("malicious", 0) > 0 or stats.get("suspicious", 0) > 0 else "safe"
        return {"url": url, "result": result, "stats": stats}, 200

    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}, 500
