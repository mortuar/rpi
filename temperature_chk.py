#!/usr/bin/python3
"""
This script would check temperature and in case is above tresshold will send warning over email.

"""
__author__ = "mortuar"

import os
import re
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from settings import mail_user, mail_password, fromaddr, toaddr, smtp_server

# script must be run from root account
if os.geteuid() != 0:
    exit("This script must be run as root.")

## Initial setup
# define servers hostname
host=os.uname()[1]

# simple logging setup
logging.basicConfig(
    filename='/opt/app/logs/temperature.log', 
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(message)s',
)

# default threshold
thresshold = str(70)

# run temperature check in OS shell
output = os.popen('vcgencmd measure_temp').read()
search = re.findall ('[0-9]+\S[0-9]+' ,output.rstrip())
temperature = (search[0])

## Main
def mail_construct():
    # constructing email message
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = ("High temperature detected - {}".format(host))
    body = ("Detected temperature is: {}".format(temperature))
    msg.attach(MIMEText(body, 'plain'))
    return msg

def check_temp():
    # send email in case temperature is above threshold
    if temperature > thresshold:
        server = smtplib.SMTP(smtp_server)
        server.connect(smtp_server)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login( mail_user, mail_password)
        text = mail_construct().as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        message=("High temperature detected: {}".format(temperature))
        print (message)
        logging.warning(message)
        logging.info("Email sent")       
    else:
        message=("Temperature is OK: {}".format(temperature))
        print (message)
        logging.info(message)
        
# run program
check_temp()