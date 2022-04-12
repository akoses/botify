import aiohttp
import asyncio
from db import insert_chegg
from utils import build_link
import socket

cookies = {
    'local_fallback_mcid': '30340148750378867108416320809868976133',
    's_ecid': 'MCMID|30340148750378867108416320809868976133',
    'CVID': '526c64e2-b2a8-4bae-945c-f8fa5f911108',
    '_omappvp': 'qaT6ezuI7Yy8sFk25pmjPrAdTYoyRZHxMrktjAywK78MGVqgQ9R99DkKoYAsB0nb13Mkr9WZAVQmzuidKZWM8xSRKRkTf8hn',
    'usprivacy': '1YNY',
    'pxcts': 'c3856251-a239-11ec-afcc-4e57685a5356',
    '_pxvid': 'c3855a89-a239-11ec-afcc-4e57685a5356',
    '_ga': 'GA1.2.2017660448.1647112953',
    'IR_gbd': 'chegg.com',
    '_gcl_au': '1.1.1709949065.1647112953',
    '_cs_c': '0',
    'mdLogger': 'false',
    'kampyle_userid': '17cc-c307-83c4-7a95-c667-9c3c-4319-a794',
    'kampyleUserSession': '1647112953124',
    'kampyleUserSessionsCount': '1',
    'kampyleSessionPageCounter': '1',
    'C': '0',
    'O': '0',
    'optimizelyEndUserId': 'oeu1647112985951r0.4655835668708168',
    'chgmfatoken': '%5B%20%22account_sharing_mfa%22%20%3D%3E%201%2C%20%22user_uuid%22%20%3D%3E%208923e50b-f54b-4bd6-9b72-ad63c41dcf1a%2C%20%22created_date%22%20%3D%3E%202022-03-12T19%3A23%3A41.876Z%20%5D',
    'DFID': 'web|36YVzWiU9puYbhr5VJtN',
    '_sdsat_cheggUserUUID': '8923e50b-f54b-4bd6-9b72-ad63c41dcf1a',
    '8923e50b-f54b-4bd6-9b72-ad63c41dcf1a_TMXCookie': '60',
    '_scid': 'ccdb9f37-f8dd-43dc-886f-ecfa298ee0ad',
    '_rdt_uuid': '1647113294066.14bdbcd0-72e9-41b8-94d7-517c102157e8',
    'opt-user-profile': '05b5a20376ef76fded40aed4c52bc7e0622cf2f7876c8c.88988930%252C21052020077%253A21048420088',
    '_ym_uid': '1647117119538148506',
    '_ym_d': '1647117119',
    'chegg_web_cbr_id': 'a',
    'mcid': '23182884176778419811815175752878131215',
    'forterToken': 'eaa4d497464f423e9dffff4a8ba9c4b3_1647538932781__UDF43_13ck',
    'PHPSESSID': 'd4j4u2r2t4bua2buurko3ct1b4',
    'V': '8d1167618a67f9a2b70df1aaff794e72623372fd8f5619.69919635',
    'id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4OTIzZTUwYi1mNTRiLTRiZDYtOWI3Mi1hZDYzYzQxZGNmMWEiLCJhdWQiOiJDSEdHIiwiaXNzIjoiaHViLmNoZWdnLmNvbSIsImV4cCI6MTY2MzMwODk0MywiaWF0IjoxNjQ3NTM4OTQzLCJlbWFpbCI6ImdxY3RueWNodHFAcHJpdmF0ZXJlbGF5LmFwcGxlaWQuY29tIn0.aIf2iOz1Fhf4OLCfPA5JZoBQN2n_VwvCvK7qZesmmCQtcYNuDfb9Sn0bSFfSV6XAHU4T6r0ioex4REN1LuQnGlrez3TPJ_lEcjgCgAKGb38L1021vXCBrv-5hqRlM8cV_6H_qo0QJYAsVxIMPdSqXl2s8sUnOwr0h_zS8qibu_yIU6mG1-buZnQA9xGX39itRg-txUkUD4xA86uF2Yblbg9G1U_6WdjkxLsCP7vsyUj8fCuz47x64dLN-lAHm7mAk6t4qfD6c600RmG0lcwldL_W-RX3xqw1mmaW89EpsXGghH1cznQQhdZu3FJQcTFNvIufjsYtuuLvvufnIt7UPQ',
    'refresh_token': 'ext.a0.t00.v1.MZNC4hOKYqSGSksfx3Zmi_v8gtQceJxUxgn33wWGsecTwOZRM2sTjVc5uChg1m5PP95wG06nP9StB3G6OPhewZ0',
    'U': 'a37d420cc46fd6bd22c5f5d53c3feb60',
    'OneTrustWPCCPAGoogleOptOut': 'false',
    '_sdsat_authState': 'Soft%20Logged%20In',
    '_pbjs_userid_consent_data': '3524755945110770',
    'connectid': '%7B%22vmuid%22%3A%22Z3_A3dO4NZ9EXPlmqFkiHPWkE7vfzSS6rQsHXkNTcRHLRjupNK8K1TEoFfhamlky9LhIXp9zloWEnUdxejz3FQ%22%2C%22connectid%22%3A%22Z3_A3dO4NZ9EXPlmqFkiHPWkE7vfzSS6rQsHXkNTcRHLRjupNK8K1TEoFfhamlky9LhIXp9zloWEnUdxejz3FQ%22%7D',
    'chegg_web_cbr_qna_id': 'b95',
    'exp': 'C026A%7CA560B%7CA127H',
    'expkey': '100E6E3E31FC084B08BE76622FFA19F8',
    'CSessionID': 'f4fe6dcd-65b7-4be0-9f43-a7f1dc986123',
    'SU': 'a9KxHP0sXCOVfmTAphlyBAYGMuS3U0ds1SRjur_xfSbLuFYlPmbYkKbLSRcalpl-_1FahpiSZji4lBSXhd79yX3yPRcY_byirloyL_zPVJ-K562OgFWk6x7Mbh2flnGa',
    'user_geo_location': '%7B%22country_iso_code%22%3A%22CA%22%2C%22country_name%22%3A%22Canada%22%2C%22region%22%3A%22AB%22%2C%22region_full%22%3A%22Alberta%22%2C%22city_name%22%3A%22Edmonton%22%2C%22postal_code%22%3A%22T6G%22%2C%22locale%22%3A%7B%22localeCode%22%3A%5B%22en-CA%22%2C%22fr-CA%22%5D%7D%7D',
    'sbm_a_b_test': '12-test',
    'CSID': '1649787780003',
    '_lr_geo_location': 'CA',
    'ab.storage.deviceId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1': '%7B%22g%22%3A%22137ee9b9-069f-6cb7-a940-b379b31bc439%22%2C%22c%22%3A1647113291139%2C%22l%22%3A1649787782477%7D',
    'ab.storage.userId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1': '%7B%22g%22%3A%228923e50b-f54b-4bd6-9b72-ad63c41dcf1a%22%2C%22c%22%3A1647113291133%2C%22l%22%3A1649787782478%7D',
    '_gid': 'GA1.2.1674021029.1649787783',
    '_iidt': 'YMFIazUCduZsGRfjzsTz/CZgYFy1Knv7f/A2DRcBENC7knYp9Enzs1H7JlpbkfrsNqzid/nGqManO4LhXHND0+wq94Ce+10=',
    '_vid_t': 'bIXR3yi+n7F6vEIycR4K0w27/ZMUvhe8nqDoT5dAyItSJP6kP/c/Wpa967LmjDBqknt8vc6MmJCdK/gkC1wrfN15adLF2Ps=',
    'schoolapi': 'null',
    '_clck': '1eoylhz|1|f0k|0',
    '_sctr': '1|1649743200000',
    'intlPaQExitIntentModal': 'hide',
    '_sdsat_highestContentConfidence': '{%22course_uuid%22:%221455f8dd-f9c1-4120-9a49-30d60ae7c6fd%22%2C%22course_name%22:%22differential-equations%22%2C%22confidence%22:0.3047%2C%22year_in_school%22:%22college-year-2%22%2C%22subject%22:[{%22uuid%22:%2255cf65ce-de54-4d9b-8e57-d5014b8194b6%22%2C%22name%22:%22differential-equations%22}]}',
    '_cs_cvars': '%7B%221%22%3A%5B%22Page%20Name%22%2C%22Question%20Page%22%5D%2C%222%22%3A%5B%22Experience%22%2C%22desktop%22%5D%2C%223%22%3A%5B%22Page%20Type%22%2C%22pdp%22%5D%2C%224%22%3A%5B%22Auth%20Status%22%2C%22Soft%20Logged%20In%22%5D%7D',
    '_uetsid': '97585e80ba8d11eca534d7e5e75d3c4d',
    '_uetvid': 'c3ffbaa0a23911ecbdf6d3e3a3d1c133',
    '_tq_id.TV-8145726354-1.ad8a': '8765dc695f008252.1647112953.0.1649787820..',
    'IR_14422': '1649787820329%7C0%7C1649787820329%7C%7C',
    '_cs_id': 'c547e945-304e-a495-d9ac-76bf44330443.1647112953.24.1649787823.1649787786.1.1681276953839',
    '_cs_s': '3.5.0.1649789623506',
    '_px3': 'e60365f079e4e01c075281db91fbe2710dc2b23372ff068134a05eda3b0f0f09:DJduLQ78W3Fb0QT55/o+1WsVKA8mzrRyXMdTEbaZHe07Agtfn1/Is0iuxihlx/yyR+KdRdZZqpgUQ+qzrORI8g==:1000:E0Z2QCDCNAARuubd3iaiN4mE8M4NRMQkVTLJ9fqH4AX6EH+wBZEP/ktJ7O2Epy2ZcwGovEt527QnnApep/wHF8BnaHCH+AQ9mEH0PH4qWG+zaXckRrdO4Mx48yQ4qB4DtCQPlE9nd14xl1fNTixxpPy+Dgg/vglnm2Y8YI8cSLIC9+Cln62AbEiRPllli79wHp/SYXeuM2+Y1tUGkZp1KQ==',
    '_px': 'DJduLQ78W3Fb0QT55/o+1WsVKA8mzrRyXMdTEbaZHe07Agtfn1/Is0iuxihlx/yyR+KdRdZZqpgUQ+qzrORI8g==:1000:L0ooX8jkgl7rqb7GqiafAyXnTOPxuoDs76bKWd383shWFsIdHEX3Tn0GBIM8p/HgQmeeM+EfgyVc48asEgviM0qlDEGoWum0Omu6geML+MkyAuZpVMXGJpYNf29MtjZ9AlujyhG5nQoH5FQJSphCTgT4J6eA5WAgoBGpR0kONPH2ewFvTks0wvyU56E8I6f9ZEO6mfNW2WNvRYfxh8Y/+m0TkM6esdVlS6EFCpHNsH0P+x89auIGTyV/MHOTX+DavqQoE0/71tQ9KnKmcPy/mA==',
    'ab.storage.sessionId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1': '%7B%22g%22%3A%2268489d2b-e474-9ff1-71ae-2bfba25adc6f%22%2C%22e%22%3A1649790115012%2C%22c%22%3A1649787782476%2C%22l%22%3A1649788315012%7D',
    'OptanonConsent': 'isIABGlobal=false&datestamp=Tue+Apr+12+2022+12%3A31%3A55+GMT-0600+(Mountain+Daylight+Time)&version=6.18.0&hosts=&consentId=9d7de6ca-cf98-4c82-b37a-1452bf8a89a2&interactionCount=1&landingPath=NotLandingPage&groups=snc%3A1%2Cfnc%3A1%2Cprf%3A1%2CSPD_BG%3A1%2Ctrg%3A1&AwaitingReconsent=false',
}

headers = {
    'authority': 'www.chegg.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'local_fallback_mcid=30340148750378867108416320809868976133; s_ecid=MCMID|30340148750378867108416320809868976133; CVID=526c64e2-b2a8-4bae-945c-f8fa5f911108; _omappvp=qaT6ezuI7Yy8sFk25pmjPrAdTYoyRZHxMrktjAywK78MGVqgQ9R99DkKoYAsB0nb13Mkr9WZAVQmzuidKZWM8xSRKRkTf8hn; usprivacy=1YNY; pxcts=c3856251-a239-11ec-afcc-4e57685a5356; _pxvid=c3855a89-a239-11ec-afcc-4e57685a5356; _ga=GA1.2.2017660448.1647112953; IR_gbd=chegg.com; _gcl_au=1.1.1709949065.1647112953; _cs_c=0; mdLogger=false; kampyle_userid=17cc-c307-83c4-7a95-c667-9c3c-4319-a794; kampyleUserSession=1647112953124; kampyleUserSessionsCount=1; kampyleSessionPageCounter=1; C=0; O=0; optimizelyEndUserId=oeu1647112985951r0.4655835668708168; chgmfatoken=%5B%20%22account_sharing_mfa%22%20%3D%3E%201%2C%20%22user_uuid%22%20%3D%3E%208923e50b-f54b-4bd6-9b72-ad63c41dcf1a%2C%20%22created_date%22%20%3D%3E%202022-03-12T19%3A23%3A41.876Z%20%5D; DFID=web|36YVzWiU9puYbhr5VJtN; _sdsat_cheggUserUUID=8923e50b-f54b-4bd6-9b72-ad63c41dcf1a; 8923e50b-f54b-4bd6-9b72-ad63c41dcf1a_TMXCookie=60; _scid=ccdb9f37-f8dd-43dc-886f-ecfa298ee0ad; _rdt_uuid=1647113294066.14bdbcd0-72e9-41b8-94d7-517c102157e8; opt-user-profile=05b5a20376ef76fded40aed4c52bc7e0622cf2f7876c8c.88988930%252C21052020077%253A21048420088; _ym_uid=1647117119538148506; _ym_d=1647117119; chegg_web_cbr_id=a; mcid=23182884176778419811815175752878131215; forterToken=eaa4d497464f423e9dffff4a8ba9c4b3_1647538932781__UDF43_13ck; PHPSESSID=d4j4u2r2t4bua2buurko3ct1b4; V=8d1167618a67f9a2b70df1aaff794e72623372fd8f5619.69919635; id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4OTIzZTUwYi1mNTRiLTRiZDYtOWI3Mi1hZDYzYzQxZGNmMWEiLCJhdWQiOiJDSEdHIiwiaXNzIjoiaHViLmNoZWdnLmNvbSIsImV4cCI6MTY2MzMwODk0MywiaWF0IjoxNjQ3NTM4OTQzLCJlbWFpbCI6ImdxY3RueWNodHFAcHJpdmF0ZXJlbGF5LmFwcGxlaWQuY29tIn0.aIf2iOz1Fhf4OLCfPA5JZoBQN2n_VwvCvK7qZesmmCQtcYNuDfb9Sn0bSFfSV6XAHU4T6r0ioex4REN1LuQnGlrez3TPJ_lEcjgCgAKGb38L1021vXCBrv-5hqRlM8cV_6H_qo0QJYAsVxIMPdSqXl2s8sUnOwr0h_zS8qibu_yIU6mG1-buZnQA9xGX39itRg-txUkUD4xA86uF2Yblbg9G1U_6WdjkxLsCP7vsyUj8fCuz47x64dLN-lAHm7mAk6t4qfD6c600RmG0lcwldL_W-RX3xqw1mmaW89EpsXGghH1cznQQhdZu3FJQcTFNvIufjsYtuuLvvufnIt7UPQ; refresh_token=ext.a0.t00.v1.MZNC4hOKYqSGSksfx3Zmi_v8gtQceJxUxgn33wWGsecTwOZRM2sTjVc5uChg1m5PP95wG06nP9StB3G6OPhewZ0; U=a37d420cc46fd6bd22c5f5d53c3feb60; OneTrustWPCCPAGoogleOptOut=false; _sdsat_authState=Soft%20Logged%20In; _pbjs_userid_consent_data=3524755945110770; connectid=%7B%22vmuid%22%3A%22Z3_A3dO4NZ9EXPlmqFkiHPWkE7vfzSS6rQsHXkNTcRHLRjupNK8K1TEoFfhamlky9LhIXp9zloWEnUdxejz3FQ%22%2C%22connectid%22%3A%22Z3_A3dO4NZ9EXPlmqFkiHPWkE7vfzSS6rQsHXkNTcRHLRjupNK8K1TEoFfhamlky9LhIXp9zloWEnUdxejz3FQ%22%7D; chegg_web_cbr_qna_id=b95; exp=C026A%7CA560B%7CA127H; expkey=100E6E3E31FC084B08BE76622FFA19F8; CSessionID=f4fe6dcd-65b7-4be0-9f43-a7f1dc986123; SU=a9KxHP0sXCOVfmTAphlyBAYGMuS3U0ds1SRjur_xfSbLuFYlPmbYkKbLSRcalpl-_1FahpiSZji4lBSXhd79yX3yPRcY_byirloyL_zPVJ-K562OgFWk6x7Mbh2flnGa; user_geo_location=%7B%22country_iso_code%22%3A%22CA%22%2C%22country_name%22%3A%22Canada%22%2C%22region%22%3A%22AB%22%2C%22region_full%22%3A%22Alberta%22%2C%22city_name%22%3A%22Edmonton%22%2C%22postal_code%22%3A%22T6G%22%2C%22locale%22%3A%7B%22localeCode%22%3A%5B%22en-CA%22%2C%22fr-CA%22%5D%7D%7D; sbm_a_b_test=12-test; CSID=1649787780003; _lr_geo_location=CA; ab.storage.deviceId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%22137ee9b9-069f-6cb7-a940-b379b31bc439%22%2C%22c%22%3A1647113291139%2C%22l%22%3A1649787782477%7D; ab.storage.userId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%228923e50b-f54b-4bd6-9b72-ad63c41dcf1a%22%2C%22c%22%3A1647113291133%2C%22l%22%3A1649787782478%7D; _gid=GA1.2.1674021029.1649787783; _iidt=YMFIazUCduZsGRfjzsTz/CZgYFy1Knv7f/A2DRcBENC7knYp9Enzs1H7JlpbkfrsNqzid/nGqManO4LhXHND0+wq94Ce+10=; _vid_t=bIXR3yi+n7F6vEIycR4K0w27/ZMUvhe8nqDoT5dAyItSJP6kP/c/Wpa967LmjDBqknt8vc6MmJCdK/gkC1wrfN15adLF2Ps=; schoolapi=null; _clck=1eoylhz|1|f0k|0; _sctr=1|1649743200000; intlPaQExitIntentModal=hide; _sdsat_highestContentConfidence={%22course_uuid%22:%221455f8dd-f9c1-4120-9a49-30d60ae7c6fd%22%2C%22course_name%22:%22differential-equations%22%2C%22confidence%22:0.3047%2C%22year_in_school%22:%22college-year-2%22%2C%22subject%22:[{%22uuid%22:%2255cf65ce-de54-4d9b-8e57-d5014b8194b6%22%2C%22name%22:%22differential-equations%22}]}; _cs_cvars=%7B%221%22%3A%5B%22Page%20Name%22%2C%22Question%20Page%22%5D%2C%222%22%3A%5B%22Experience%22%2C%22desktop%22%5D%2C%223%22%3A%5B%22Page%20Type%22%2C%22pdp%22%5D%2C%224%22%3A%5B%22Auth%20Status%22%2C%22Soft%20Logged%20In%22%5D%7D; _uetsid=97585e80ba8d11eca534d7e5e75d3c4d; _uetvid=c3ffbaa0a23911ecbdf6d3e3a3d1c133; _tq_id.TV-8145726354-1.ad8a=8765dc695f008252.1647112953.0.1649787820..; IR_14422=1649787820329%7C0%7C1649787820329%7C%7C; _cs_id=c547e945-304e-a495-d9ac-76bf44330443.1647112953.24.1649787823.1649787786.1.1681276953839; _cs_s=3.5.0.1649789623506; _px3=e60365f079e4e01c075281db91fbe2710dc2b23372ff068134a05eda3b0f0f09:DJduLQ78W3Fb0QT55/o+1WsVKA8mzrRyXMdTEbaZHe07Agtfn1/Is0iuxihlx/yyR+KdRdZZqpgUQ+qzrORI8g==:1000:E0Z2QCDCNAARuubd3iaiN4mE8M4NRMQkVTLJ9fqH4AX6EH+wBZEP/ktJ7O2Epy2ZcwGovEt527QnnApep/wHF8BnaHCH+AQ9mEH0PH4qWG+zaXckRrdO4Mx48yQ4qB4DtCQPlE9nd14xl1fNTixxpPy+Dgg/vglnm2Y8YI8cSLIC9+Cln62AbEiRPllli79wHp/SYXeuM2+Y1tUGkZp1KQ==; _px=DJduLQ78W3Fb0QT55/o+1WsVKA8mzrRyXMdTEbaZHe07Agtfn1/Is0iuxihlx/yyR+KdRdZZqpgUQ+qzrORI8g==:1000:L0ooX8jkgl7rqb7GqiafAyXnTOPxuoDs76bKWd383shWFsIdHEX3Tn0GBIM8p/HgQmeeM+EfgyVc48asEgviM0qlDEGoWum0Omu6geML+MkyAuZpVMXGJpYNf29MtjZ9AlujyhG5nQoH5FQJSphCTgT4J6eA5WAgoBGpR0kONPH2ewFvTks0wvyU56E8I6f9ZEO6mfNW2WNvRYfxh8Y/+m0TkM6esdVlS6EFCpHNsH0P+x89auIGTyV/MHOTX+DavqQoE0/71tQ9KnKmcPy/mA==; ab.storage.sessionId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%2268489d2b-e474-9ff1-71ae-2bfba25adc6f%22%2C%22e%22%3A1649790115012%2C%22c%22%3A1649787782476%2C%22l%22%3A1649788315012%7D; OptanonConsent=isIABGlobal=false&datestamp=Tue+Apr+12+2022+12%3A31%3A55+GMT-0600+(Mountain+Daylight+Time)&version=6.18.0&hosts=&consentId=9d7de6ca-cf98-4c82-b37a-1452bf8a89a2&interactionCount=1&landingPath=NotLandingPage&groups=snc%3A1%2Cfnc%3A1%2Cprf%3A1%2CSPD_BG%3A1%2Ctrg%3A1&AwaitingReconsent=false',
    'pragma': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
}


async def convert_link(link:str):
    """
    Convert a link in chegg.
    """
    conn = aiohttp.TCPConnector(
        family=socket.AF_INET,
        ssl=False,
    )
    session = aiohttp.ClientSession(headers=headers, cookies=cookies, connector=conn)
    async with session as session:
        async with session.get(link) as response:
            html = await response.text()
            chegg_id = await insert_chegg(html)
            link = build_link(chegg_id)
            return link
            


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(convert_link('https://www.chegg.com/homework-help/questions-and-answers/problem-3-12-marks-consider-following-simple-elegant-sorting-algorithm-somesort-b-e-e-6-1--q92085111'))
