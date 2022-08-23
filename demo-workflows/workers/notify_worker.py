import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def email_smtp_notify(task):

    server = task['inputData']['smtp_server']
    port = task['inputData']['smtp_port']
    sender_username = task['inputData']['username']
    sender_password = task['inputData']['password']
    to =  task['inputData']['to']
    subject =  task['inputData']['subject']
    body = task['inputData']['body']
    
    message = MIMEMultipart()
    message['From'] = sender_username
    message['To'] = to
    message['Subject'] = subject
    message.attach(MIMEText(str(body), 'plain'))
    
    try:
        smtp_server = smtplib.SMTP_SSL(server, port)
        smtp_server.ehlo()
        smtp_server.login(sender_username, sender_password)
        smtp_server.sendmail(sender_username, to, message.as_string())
        smtp_server.close()
    
        return {'status': 'COMPLETED', 'output': {'url': "email_notify", 'response_code': 200, 'response_body': "Email sent successfully"}, 'logs': []}
        
    except Exception as ex:
        return {'status': 'FAILED', 'output': {'url': "email_notify", 'response_code': 500, 'response_body': "Failed to send email"}, 'logs': []}

def start(cc):
    print('Starting Notify workers')

    cc.register('NOTIFY_email_smtp', {
        "description": '{"description": "Send email via smtp protocol", "labels": ["BASICS","NOTIFY"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "inputKeys": [
            "smtp_server",
            "smtp_port",
            "username",
            "password",
            "to",
            "subject",
            "body"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, email_smtp_notify)