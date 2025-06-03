from leakcheck import LeakCheckAPI_Public
from flask import g
from DB_Manager import log_incident
import datetime

def check_email_breaches(email):

    try:
        public_api = LeakCheckAPI_Public()

        result = public_api.lookup(query=email)
        sources = result["sources"]
        for source in sources:
            try:

                description = f"Your email [{email}] has been exposed to '{source["name"]}' on {source["date"]}"
                date = str(datetime.datetime.now())
                log_incident(g.user["id"], "email breach", description, source["name"], 5, date)
                print("logged:", source)
            except Exception as e:
                continue
        return {"breaches found": result["found"]}, 200
    
    
    except Exception as e:

        return {"failed to scan email": f"{str(e)}"}, 500
