import sys
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import subprocess
from subprocess import PIPE

set_mode = sys.argv[1]
Your_Mail_Address = '<GMAIL ADDRESS>'
Application_Password = '<GMAIL PASSWORD>'
From_Mail_Address = '<SENDER VALUE>'
To_Mail_Address = Your_Mail_Address


def sendmail (URL):
    smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(Your_Mail_Address, Application_Password)
    msg = MIMEText ('Please copy this URL to Hakoirimusume\'s Webhook.\nngrok URL : '+URL+'\n\nLINE Developer : https://developers.line.biz/console/channel/xxxxxxxxxx/messaging-api')
    msg['Subject'] = 'You need to set Hakoirimusume\'s Webhook URL.'
    msg['From'] = From_Mail_Address
    msg['To'] = To_Mail_Address
    msg['Date'] = formatdate()
    smtpobj.sendmail(Your_Mail_Address, To_Mail_Address, msg.as_string())
    smtpobj.close()

f = open('./auth', 'w')
f.write('0')
f.close()
if set_mode == '--reset':
    f = open('./user_list', 'w')
    f.write('')
    f.close()
    f = open('./go_away', 'w')
    f.write('')
    f.close()
proc1 = subprocess.run('ngrok http 21212 --region jp', shell=True, stdout=PIPE, stderr=PIPE, text=True)
sendmail('www.test.url')
proc2 = subprocess.run('python3 ./main.py', shell=True, stdout=PIPE, stderr=PIPE, text=True)
print(">>proc1\n" + proc1.stdout)
