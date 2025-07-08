import requests
import json
import os
with open(os.path.join(os.path.dirname(__file__),"security_key.json")) as f:
    creds=json.load(f)
API_URL="http://20.244.56.144/evaluation-service/logs"
STACKS={"backend","frontend"}
LEVELS={"debug","info","warn","error","fatal"}
PACKAGE={"cache","controller","cron_job","db","domain","handler","repository","route","service"}
def Log(stack:str,level:str,package:str,message:str):
    """
    Send a log entry to the remote logging API.
    """
    stack=stack.lower()
    level=level.lower()
    package=package.lower()
    if stack not in STACKS:
        raise ValueError(f"Invalid stack: {stack}. Stack must be one of {STACKS}")
    if level not in LEVELS:
        raise ValueError(f"Invalid level: {level}. Level must be one of {LEVELS}")
    if package not in PACKAGE:
        raise ValueError(f"Invalid package: {package}. Package must be one of {PACKAGE}")
    if not message or len(message.strip()) < 10:
        raise ValueError("Log message must be specific and descriptive (at least 10 characters).")
    payload={
        "stack":stack,
        "level":level,
        "package":package,
        "message":message.strip(),
    }
    headers = {
        "Content-Type": "application/json",
            "Authorization": f"Bearer {creds['access_token']}",
        }
    try:
        response=requests.post(API_URL,json=payload,headers=headers,timeout=5)
        response.raise_for_status()
    except Exception as e:
        print(f"[LOGGING ERROR] Failed to send log to API: {e}")
        
# if __name__=='__main__':
#     Log('backend','error','controller','logger initialized')