import os
from azure.communication.email import EmailClient
from azure.core.credentials import AzureKeyCredential

# Authentication
key = AzureKeyCredential("4GhT4z2rGEnNQuK8E1mPag9G2CmM37nHx10NUFxuLmp96A4C2cUiJQQJ99AKACULyCpDyPWLAAAAAZCSQasT")
endpoint = "https://neunet-communication-service.unitedstates.communication.azure.com/"
email_client = EmailClient(endpoint, key)

# Construct Email
message = {
    "content": {
        "subject": "This is the test subject",
        "plainText": "This is the test body",
        "html": "<html><h1>This is the body</h1></html>"
    },
    "recipients": {
        "to": [
            {"address": "hemant.singh@ideaxdesign.com", "displayName": "Recipient Name"}
        ]
    },
    "senderAddress": "DoNotReply@ideaxdesign.com"
}

# Send Email
try:
    poller = email_client.begin_send(message)
    print("Email send operation initiated.")
    result = poller.result()
    print(f"Result: {result}")
except Exception as ex:
    print(f"Error sending email: {ex}")
