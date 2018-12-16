import smtplib, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def check_keys(smth): 
    if 'firstname' in smth and 'lastname' in smth and 'email' in smth and 'username' in smth and 'city' in smth and 'address' in smth and 'password' in smth and 'confirm_password' in smth:
        if smth['firstname'] != "" and smth['lastname'] != "" and smth['email'] != "" and smth['username'] != "" and smth['city'] != "" and smth['address'] != "" and smth['password'] != "" and smth['confirm_password'] != "":
            if smth['password'] == smth['confirm_password'] and validate_email(smth) and validate_register(smth):
                return True    
    return False

def validate_email(smth):
    return re.match("^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$", smth['email'])

def validate_register(smth):
    return valf(smth['firstname']) and valf(smth['lastname']) and valf(smth['email']) and valf(smth['username']) and valf(smth['city']) and valf(smth['address']) and valf(smth['password']) and valf(smth['confirm_password'])

def valf(field_value):
    return re.match("[a-zA-Z0-9 ]+", field_value)

def check_login(smth):
    if 'username' in smth and 'password' in smth:
        return True
    else:
        return False

def check_transfer(smth):
    if 'PLN' in smth and 'PLN_C' in smth and 'accountnumber' in smth and 'firstname' in smth and 'lastname' in smth and 'city' in smth and 'address' in smth and 'titletransfer' in smth:
        return True
    return False


 
def send_password(email, passord):
    fromaddr = "tagasak@outlook.com"
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Reset Password"
    # 
    body = "Here is your new password: {}".format(passord)
    msg.attach(MIMEText(body, 'plain'))
    # 
    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(fromaddr, "k3Md9Zp5")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


