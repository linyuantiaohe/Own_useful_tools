import smtplib
# 输入Email地址和口令:
from email.mime.text import MIMEText
msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
from_addr = 'alwaysgg@163.com'
password = 'blue0916'
# 输入收件人地址:
to_addr = '925869803@qq.com'
# 输入SMTP服务器地址:
smtp_server = 'smtp.163.com'


server = smtplib.SMTP(smtp_server, 25) # SMTP协议默认端口是25
server.set_debuglevel(1)
server.login(from_addr, password)
server.sendmail(from_addr, [to_addr], msg.as_string())
server.quit()