# import os
# from django.core.mail import get_connection, EmailMessage
# from dotenv import load_dotenv
# import socket

# # 设置socket超时
# socket.setdefaulttimeout(10)  # 10秒超时

# # 重新加载环境变量
# load_dotenv()

# # 打印环境变量检查
# print("Environment variables check:")
# print(f"EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER')}")
# print(f"EMAIL_HOST_PASSWORD length: {len(os.getenv('EMAIL_HOST_PASSWORD') or '')}")

# try:
#     # 创建邮件连接
#     connection = get_connection(
#         backend='django.core.mail.backends.smtp.EmailBackend',
#         host='smtp.gmail.com',
#         port=587,
#         use_tls=True,
#         username=os.getenv('EMAIL_HOST_USER'),
#         password=os.getenv('EMAIL_HOST_PASSWORD'),
#         timeout=10
#     )
    
#     print("Connection created, attempting to send email...")
    
#     # 创建测试邮件
#     email = EmailMessage(
#         '测试邮件',
#         '这是一封来自Django的测试邮件',
#         os.getenv('EMAIL_HOST_USER'),
#         ['jh730@duke.edu'],
#         connection=connection
#     )
    
#     # 发送邮件
#     result = email.send()
#     print(f"邮件发送结果: {result}")
    
# except Exception as e:
#     print(f"发送失败: {str(e)}")
#     print(f"错误类型: {type(e)}")

from django.core.mail import send_mail
from django.conf import settings

try:
    print("Testing email with console backend...")
    result = send_mail(
        subject='Test Email',
        message='This is a test email',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=['jh730@duke.edu'],
        fail_silently=False
    )
    print(f"Email sent (console): {result}")
except Exception as e:
    print(f"Error: {str(e)}")
