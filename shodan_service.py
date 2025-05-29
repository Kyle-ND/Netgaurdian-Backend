import requests
import os
from datetime import datetime

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

def shodan_scan(ip_address: str):
    try:
        url = f"https://api.shodan.io/shodan/host/{ip_address}?key={SHODAN_API_KEY}"
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": "Shodan API error"}, 500

        data = response.json()
        open_ports = data.get("ports", [])
        hostnames = data.get("hostnames", [])
        vulnerabilities = data.get("vulns", [])
        org = data.get("org", "")
        os_detected = data.get("os", "unknown")

        return {
            "ip": data["ip_str"],
            "open_ports": open_ports,
            "hostnames": hostnames,
            "vulnerabilities": list(vulnerabilities.keys()) if isinstance(vulnerabilities, dict) else vulnerabilities,
            "device_type": org or os_detected,
            "exposed": bool(open_ports),
            "risk_level": "high" if 22 in open_ports or vulnerabilities else "medium",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {"error": str(e)}, 500
