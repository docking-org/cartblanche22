from flask_mail import Message
from flask import render_template, current_app
from cartblanche.app import mail


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
               text_body= "Dear " + user.username + ",\n\n" +
                            "To reset your password, visit the following link:\n" +
                            current_app.config['BASE_URL'] + "/reset_password/" + token + "\n\n" +
                            "If you did not make this request then simply ignore this email and no changes will be made.\n\n" +
                            "Sincerely,\n" +
                            "The Cartblanche Team",
                
                html_body="<p>Dear " + user.username + ",</p>" +
                            "<p>To reset your password <a href=\"" + current_app.config['BASE_URL'] + "/reset_password/" + token + "\">click here</a>.</p>" +
                            "<p>Alternatively, you can paste the following link in your browser's address bar:</p>" +
                            "<p>" + current_app.config['BASE_URL'] + "/reset_password/" + token + "</p>" +
                            "<p>If you have not requested a password reset simply ignore this message.</p>" +
                            "<p>Sincerely,</p>" +
                            "<p>The Cartblanche Team</p>"
                )

def prepare_email_chemspace(user, data, file):
    send_email_chemspace('[CartBlanche] Order information',
                         sender=current_app.config['ADMINS'][0],
                         recipients=[user.email],
                         text_body=render_template('email/order_chemspace.txt',
                                                   data=data),
                         html_body=render_template('email/order_chemspace.html',
                                                   data=data),
                         cc=[''],
                         file=file)


def send_search_log(data):
    send_email('[CartBlanche] zincsearch error',
               sender=current_app.config['ADMINS'][0],
               # recipients=['munkhzulk@gmail.com', 'munkhzulk1@gmail.com'],
               recipients=['jir322@gmail.com', 'khtang015@gmail.com', 'ben@tingle.org'],
               text_body=render_template('email/zincerror.txt', data=data),
               html_body=render_template('email/zincerror.html', data=data))
