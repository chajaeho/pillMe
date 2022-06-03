import base64
import hashlib
import hmac
import time


class SendSMS(object):
    def __init__(self):
        naver = getattr(base, 'auth')['naver']
        url = 'https://sens.apigw.ntruss.com'
        uri = f'/sms/v2/services/{snaver[""]}/messages'

    def make_signature(self, timestamp):
       secret_key = bytes(self.naver[SMS_SECRET_KEY], 'UTF-8')
       message = "POST "+uri+"\n"+timestamp+"\n"+naver[SMS_ACCESS_KEY]
       message = bytes(message, 'UTF-8') 
       signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
       
       return signingKey
    
    def send_SMS(phone_number, userNAME, userPW): 
        timestamp = str(int(time.time()*1000))
        context = {
            'type': 'SMS',
            'contentType': 'COMM',
            'countryCode': '82',
            'from': '01071118169',
            'content': f'{userNAME}님의 비밀번호는 [{userPW}]입니다.',
            'messages': [{
                'to': phone_number
            }]
        }
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': naver[SMS_ACCESS_KEY],
            'x-ncp=apigw-signature-v2': make_signature(timestamp=timestamp)
        }
        response = requests.post(url+uri, headers=headers, json=context)

        if not response.ok:
            raise ValidationError(response.reason)

        return True
    


