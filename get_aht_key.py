import requests
#import dataprocessin

URL='http://db.accrue.com/login'

PARAMS={'email':'maatouch@accrue.com',
'password':'Accrue'}

auth_token=requests.post(url= URL,params=PARAMS).json()["auth-token"]
print(auth_token)
#auth_token="eX5g3R5xi6DqrLSp9ONXAFU0SDg3HEARkA2-HkzUV3Y"
#auth_token="l7M3_ogo5sM8l_D1_bnCQ_BWeZ8gpL9bcE7zKhl6H6A"

