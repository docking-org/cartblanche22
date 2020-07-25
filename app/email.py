from flask_mail import Message
from flask import render_template, current_app
from app import mail


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_email_chemspace(subject, sender, recipients, text_body, html_body, cc=None, file=None):
    msg = Message(subject, sender=sender, recipients=recipients, cc=cc)
    msg.body = text_body
    msg.html = html_body
    msg.attach('order', 'application/vnd.ms-excel', file)
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[CartBlanche] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def prepare_email_chemspace(user, data, file):
    send_email_chemspace('[CartBlanche] Order information',
                         sender=current_app.config['ADMINS'][0],
                         recipients=[user.email],
                         text_body=render_template('email/order_chemspace.txt',
                                                   data=data),
                         html_body=render_template('email/order_chemspace.html',
                                                   data=data),
                         cc=['munkhzulk1@gmail.com'],
                         file=file)
