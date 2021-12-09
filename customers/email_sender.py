from datetime import datetime
from email.mime.image import MIMEImage
import smtplib  
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from general import models as gmodels
from customers import models as cmodels


def sendmail(RECIPIENT,BODY_TEXT,BODY_HTML,SUBJECT,customize = None,**kwargs):

    SENDER = 'info@intelbyt.com'  
    SENDERNAME = 'Intelbyt Store'
    RECIPIENT  = ', '.join(RECIPIENT)
    USERNAME_SMTP = "info@intelbyt.com"
    PASSWORD_SMTP = "intelbyt66585617Ca."
    HOST = "mail.intelbyt.com"
    PORT = 465
    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg['To'] = RECIPIENT
    part1 = MIMEText(BODY_TEXT, 'plain')
    part2 = MIMEText(BODY_HTML, 'html')
    msg.attach(part1)
    msg.attach(part2)
    try:
        settings = list(gmodels.General.objects.all())[0]
    except IndexError:
        settings =[]
    try:
        fp = open(settings.logo.path, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<logo>')
        msg.attach(msgImage)
    except Exception:
        pass

    if customize:
        customize(msg,emailid=kwargs['emailid'])
        
    socials = gmodels.SocialLink.objects.all()
    for social in socials:
        try:
            fp = open(social.image.path, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            msgImage.add_header('Content-ID', '<'+social.name+'>')
            msg.attach(msgImage)
        except Exception:
            pass
    try:  
        server = smtplib.SMTP_SSL(HOST, PORT)

        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        server.sendmail(USERNAME_SMTP, RECIPIENT.split(','), msg.as_string())
        server.close()
    except Exception as e:
        print ("Error: ", e)
    else:
        
        print ("Email sent!")
        return True

