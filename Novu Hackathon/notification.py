import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import twilio_config
import smtp_config


class NotificationManager:
    @staticmethod
    def send_email_notification(service, next_service_date, owner_email):
        # Email config
        sender_email = smtp_config.SENDER_EMAIL
        sender_password = smtp_config.SENDER_PASSWORD
        smtp_server = smtp_config.SMTP_SERVER
        smtp_port = smtp_config.SMTP_PORT

        # Email connect
        subject = f'{service} Maintenance Reminder'
        message = f'Dear vehicle owner,\n\nThis is a reminder that your {service} is due on {next_service_date}.\n\nPlease schedule an appointment for maintenance.\n\nBest regards,\nYour Automotive Maintenance System'

        # Construct the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = owner_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Connect to the SMTP server
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f'Email notification sent to {owner_email} for {service} maintenance.')
        except Exception as e:
            print(f'Failed to send email notification: {str(e)}')

    @staticmethod
    def send_sms_notification(service, next_service_date, owner_phone_number):
        # SMS config
        account_sid = twilio_config.TWILIO_ACCOUNT_SID
        auth_token = twilio_config.TWILIO_AUTH_TOKEN
        twilio_phone_number = twilio_config.TWILIO_PHONE_NUMBER

        # Twilio client
        client = Client(account_sid, auth_token)

        # Construct the SMS message
        message = f'Dear vehicle owner,\n\nThis is a reminder that your {service} is due on {next_service_date}.\n\nPlease schedule an appointment for maintenance.\n\nBest regards,\nYour Automotive Maintenance System'

        try:
            # Send SMS message
            client.messages.create(
                body=message,
                from_=twilio_phone_number,
                to=owner_phone_number
            )
            print(f'SMS notification sent to {owner_phone_number} for {service} maintenance.')
        except Exception as e:
            print(f'Failed to send SMS notification: {str(e)}')
