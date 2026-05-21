import json
import requests


def sendsms(tel_no,message):
    print("sms to be sent to ",tel_no)
     
    url = 'https://portal.zettatel.com/SMSApi/send'
    
    try:
              
                
                #print(tel_no)
        payload = {
                "userid": "mfalme",
                "password": "Mfalme123",
                "senderid": "MFALME",
                "msgType": "text",
                "duplicatecheck": "true",
                "sendMethod": "quick",
                "sms": [
                    {
                        "mobile": [tel_no],
                        "msg": message
                    }
            
                ]
                }

        
        json_payload = json.dumps(payload)

        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, headers=headers, data=json_payload)
    except:
        print("SMS not send :Error :{e}")