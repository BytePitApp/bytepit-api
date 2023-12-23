import os
from azure.communication.email import EmailClient


client = EmailClient.from_connection_string(os.environ.get("COMMUNICATION_SERVICES_CONNECTION_STRING"))


async def send_verification_email(email, token):
    message_html = f"""
    <html>
        <head>
            <style>
                body, table, td, p, h1, a {{
                    text-align: center;
                    margin: 0 auto;
                }}

                h1 {{
                    color: #4338CA;
                    font-size: 40px;
                    margin-bottom: 20px;
                }}

                .button-link, .button-link:link, .button-link:visited, .button-link:hover, .button-link:active {{
                    background-color: #4338CA;
                    border: none;
                    color: white !important;
                    padding: 15px 32px;
                    text-decoration: none;
                    font-size: 16px;
                    border-radius: 5px;
                    display: inline-block;
                    margin-top: 20px;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td>
                        <h1>BytePit</h1>
                        <h3>Please confirm your email by clicking on the button:</h3>
                        <a href="http://bytepit.cloud/confirm-email/{token}" class="button-link">CONFIRM</a>
                    </td>
                </tr>
            </table>
        </body>
    </html>

    """
    message = {
        "senderAddress": "DoNotReply@bytepit.cloud",
        "recipients": {"to": [{"address": email}]},
        "content": {
            "subject": "BytePit - Confirm your email",
            "html": message_html,
            "plaintext": "Please confirm your email by clicking on the link: http://bytepit.cloud/confirm-email/{token}",
        },
    }
    try:
        poller = client.begin_send(message)
        result = poller.result()
    except Exception as e:
        print(e)
        return False
    return True
