from google_auth_oauthlib.flow import InstalledAppFlow
import os
import logging

# 设置日志
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
REDIRECT_URI = os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:40080/')

try:
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    creds = flow.run_local_server(
        port=40080,
        host='localhost',
        open_browser=True
    )
    
    # 保存凭证
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    logger.info("Token generated and saved successfully!")
except Exception as e:
    logger.error(f"Error during token generation: {str(e)}")
    raise

# import os
# import base64
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

# # 设置 OAuth 2.0 权限范围（需用户授权）
# SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# def get_gmail_credentials():
#     creds = None
#     # 检查是否已有 token.json
#     tokenPath = 'token.json'
#     if os.path.exists(tokenPath):
#         creds = Credentials.from_authorized_user_file(tokenPath, SCOPES)
    
#     # 如果 token 无效或未生成，触发授权流程
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())  # 刷新令牌
#         else:
#             # 加载 credentials.json 启动授权
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', 
#                 SCOPES
#             )
#             creds = flow.run_local_server(port=40080)  # 自动打开浏览器授权
        
#         # 保存令牌供后续使用
#         with open('token.json', 'w') as token_file:
#             token_file.write(creds.to_json())
    
#     return creds

# def send_email_via_api(receiver_name, receiver_email, ride_id, driver_nickname):
#     creds = get_gmail_credentials()
#     service = build('gmail', 'v1', credentials=creds)
    
#     raw_message = (
#         "From: mattyhuan7@gmail.com\n"
#         f"To: {receiver_email}\n"
#         "Subject: Rideshare: Your ride is confirmed!\n\n"
#         f"Hi, {receiver_name}, Your ride #{ride_id} is confirmed by {driver_nickname}"
#     )
#     encoded_message = base64.urlsafe_b64encode(raw_message.encode("utf-8")).decode("utf-8")
    
#     # 发送邮件
#     service.users().messages().send(
#         userId="me",
#         body={"raw": encoded_message}
#     ).execute()
#     print("email sent successfully")
    
# if __name__ == "__main__":
#     send_email_via_api("12345", "930656601@qq.com", 11, "driver_nickname")
