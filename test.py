# from datetime import datetime
# tipo1 = "2020-04-27 12:41:46"
# tipo1str = datetime.strptime("{}:23".format(tipo1), '%Y-%m-%d %H:%M:%S:%f')
# print(tipo1str)

import json
import requests, base64


# def enviarSms():
#     usrPass = "administracion@texcargo.cl:dc98pr83".encode()
#     print(usrPass)
#     b64Val = base64.b64encode(usrPass)
#     print(b64Val)
#
#     url = "https://api.labsmobile.com/json/send"
#
#     payload = {"message": "Sms de prueba pa", "tpoa": "Sender", "recipient": [{"msisdn": "56988514994"}]}
#     headers = {
#         'Content-Type': "application/json",
#         'Authorization': "Basic %s" % b64Val,
#         'Cache-Control': "no-cache"
#     }
#
#     response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
#
#     print(response.text)
#
#
def enviarSms(telf, registro):
    url = "https://api.labsmobile.com/get/send.php?username=administracion@texcargo.cl&password=dc98pr83&message=TexCargo te invita a verificar el status de tu paquete visitando: https://tuenvioweb.apps.com.pe/tracking.php?id={}&msisdn={}&sender=34609033163".format(
        registro, telf)
    print(url)

    response = requests.request("GET", url)

    print(response.text)

enviarSms("51965778450", 123456)