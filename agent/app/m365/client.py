import requests

GRAPH = "https://graph.microsoft.com/v1.0"

class M365Client:
    def __init__(self, access_token: str):
        self.h = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    def me(self):
        r = requests.get(f"{GRAPH}/me", headers=self.h, timeout=30)
        r.raise_for_status()
        return r.json()

    def send_mail(self, to_email: str, subject: str, body_text: str):
        payload = {
            "message": {
                "subject": subject,
                "body": {"contentType": "Text", "content": body_text},
                "toRecipients": [{"emailAddress": {"address": to_email}}],
            },
            "saveToSentItems": True,
        }
        r = requests.post(f"{GRAPH}/me/sendMail", headers=self.h, json=payload, timeout=30)
        r.raise_for_status()
        return True
