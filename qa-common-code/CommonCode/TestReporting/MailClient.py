import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from CommonCode.TestExecute.Logging import PrintMessage


def send_mail(subject, html_body, m_from, m_to):
    message = MIMEMultipart()

    message['Subject'] = subject
    message['From'] = m_from
    message['To'] = ', '.join(m_to)

    message_body = MIMEText(html_body, 'html')
    message.attach(message_body)

    PrintMessage('Sending email to {0}'.format(m_to))

    # Send the message via local SMTP server.
    # s = smtplib.SMTP('edi-smtp01.company.com')

    # Setup for Jenkins and AWS
    s = smtplib.SMTP('email-smtp.eu-west-1.amazonaws.com', 587)
    s.starttls()
    s.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))

    # s.set_debuglevel(1)
    s.sendmail(message['From'], m_to, message.as_string())
    s.quit()

    # Code below allows sending emails from windows (keept it for testing purposes)
    # import win32com.client as win32
    # outlook = win32.Dispatch('outlook.application')
    # mail = outlook.CreateItem(0)
    # mail.To = 'robert.deringer@company.com'
    # mail.Subject = subject
    # #mail.Body = 'Message body'
    # mail.HTMLBody = html_body
    #
    # # To attach a file to the email (optional):
    # #attachment  = "Path to the attachment"
    # #mail.Attachments.Add(attachment)
    #
    # mail.Send()
