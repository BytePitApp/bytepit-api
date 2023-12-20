import os

from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig

connection_config = ConnectionConfig(
    MAIL_USERNAME="bytepit.progi@gmail.com",
    MAIL_PASSWORD=os.environ.get("EMAIL_PASSWORD"),
    MAIL_FROM="bytepit.progi@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="BytePit",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


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

    message = MessageSchema(
        subject="BytePit - Confirm your email", recipients=[email], body=message_html, subtype=MessageType.html
    )

    fm = FastMail(connection_config)
    await fm.send_message(message)
    return True
