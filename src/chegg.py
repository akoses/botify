import aiohttp
import asyncio
from db import insert_chegg
from utils import build_link
import socket

cookies = {
    '_omappvp': 'qaT6ezuI7Yy8sFk25pmjPrAdTYoyRZHxMrktjAywK78MGVqgQ9R99DkKoYAsB0nb13Mkr9WZAVQmzuidKZWM8xSRKRkTf8hn',
    'usprivacy': '1YNY',
    '_pxvid': 'c3855a89-a239-11ec-afcc-4e57685a5356',
    '_ga': 'GA1.2.2017660448.1647112953',
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
    '_scid': 'ccdb9f37-f8dd-43dc-886f-ecfa298ee0ad',
    '_rdt_uuid': '1647113294066.14bdbcd0-72e9-41b8-94d7-517c102157e8',
    '_ym_uid': '1647117119538148506',
    '_ym_d': '1647117119',
    'forterToken': 'eaa4d497464f423e9dffff4a8ba9c4b3_1647538932781__UDF43_13ck',
    'V': '8d1167618a67f9a2b70df1aaff794e72623372fd8f5619.69919635',
    'id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4OTIzZTUwYi1mNTRiLTRiZDYtOWI3Mi1hZDYzYzQxZGNmMWEiLCJhdWQiOiJDSEdHIiwiaXNzIjoiaHViLmNoZWdnLmNvbSIsImV4cCI6MTY2MzMwODk0MywiaWF0IjoxNjQ3NTM4OTQzLCJlbWFpbCI6ImdxY3RueWNodHFAcHJpdmF0ZXJlbGF5LmFwcGxlaWQuY29tIn0.aIf2iOz1Fhf4OLCfPA5JZoBQN2n_VwvCvK7qZesmmCQtcYNuDfb9Sn0bSFfSV6XAHU4T6r0ioex4REN1LuQnGlrez3TPJ_lEcjgCgAKGb38L1021vXCBrv-5hqRlM8cV_6H_qo0QJYAsVxIMPdSqXl2s8sUnOwr0h_zS8qibu_yIU6mG1-buZnQA9xGX39itRg-txUkUD4xA86uF2Yblbg9G1U_6WdjkxLsCP7vsyUj8fCuz47x64dLN-lAHm7mAk6t4qfD6c600RmG0lcwldL_W-RX3xqw1mmaW89EpsXGghH1cznQQhdZu3FJQcTFNvIufjsYtuuLvvufnIt7UPQ',
    'U': 'a37d420cc46fd6bd22c5f5d53c3feb60',
    'OneTrustWPCCPAGoogleOptOut': 'false',
    'exp': 'C026A%7CA560B%7CA127H',
    'sa-user-id': 's%253A0-940543cd-6e3e-4b37-5134-0c5d689c1fe4.W5hyXWs2aENyOzBhKUeYPHwPLiYu1snpdHXSFbsnb1s',
    'sa-user-id-v2': 's%253A0-8f56e81d-d0cc-4ae9-643f-010868cd55f9%2524ip%252424.65.95.200.d02tX3m%252B9%252Fr4uNkfai8Zziyk2jTZun73T1Kq3tzuVgU',
    'chegg_web_cbr_qna_id': 'b75',
    'PHPSESSID': '5361440ed7b1fc6e345e977e9c112794',
    'CSessionID': 'b1401e4f-5dd0-4c91-868d-996156fed73f',
    'SU': 'Mx9RPU1Gx-IYPXS0tt7uL0_t0KNLktbxYP8RO-lOREln1-cjX5cbq0-TNuKhFAtKlIu2B8wKTkj1KRbpZyyNjf2JoWv3E1wA04Wm7nbpVEHU5bvH6b0WT4EaqGVhWZ4j',
    'user_geo_location': '%7B%22country_iso_code%22%3A%22CA%22%2C%22country_name%22%3A%22Canada%22%2C%22region%22%3A%22AB%22%2C%22region_full%22%3A%22Alberta%22%2C%22city_name%22%3A%22Sherwood+Park%22%2C%22postal_code%22%3A%22T8A%22%2C%22locale%22%3A%7B%22localeCode%22%3A%5B%22en-CA%22%2C%22fr-CA%22%5D%7D%7D',
    'expkey': '4F928D13FB5E31DDA93D9D86BFA1807C',
    'intlPaQExitIntentModal': 'hide',
    'CVID': '49e13173-1e91-4f82-8e96-00e67024a47a',
    'CSID': '1653643392064',
    'pxcts': 'a28c4694-dd9e-11ec-bbfb-70555575756b',
    '_sdsat_authState': 'Soft%20Logged%20In',
    '_sdsat_cheggUserUUID': '8923e50b-f54b-4bd6-9b72-ad63c41dcf1a',
    'sbm_a_b_test': '12-test',
    '_px3': 'ed54d19a09bf385fc6c7eae630802a0667c17e1d254b81608bcbe64ea4b3f215:IMNAcKFX+VchZ244DIKjmB+hZQ75f3txjAi2wFCg5tjGdMttFfNMwTXj7Ed/9kKfkJ0mj0lWb9WKQLbZu4S5RA==:1000:1PLtSbjwKfg5Z2IpK6otgin0lB7HRSVErSZyBqLC0/ADdaCjaK6lS94JS6QQV5befwbbju6ZMHMknSQj6U2liflPEBOtNoihx9iFRcyEEXgQKou7IGEYsFB1CQnHdQxtoD+SQICzJ5gElPlHm+yVXQy+pKfBXvp8petmqSjmzhtigamMb0Y3haNDk3erlWbjFW8JT7aZSAhJ3q0JYTEEYw==',
    '_px': 'IMNAcKFX+VchZ244DIKjmB+hZQ75f3txjAi2wFCg5tjGdMttFfNMwTXj7Ed/9kKfkJ0mj0lWb9WKQLbZu4S5RA==:1000:YhIeOJAfpuoyvybbl+La4SsPXrRXv4npvmzk6bWSacgvLgmk3OLQ5r2sLo80KFmTGhZIEYru3TWkr9oVhYJpbU+RGo2LtK6+a2s6v1wKPr+hQkYcujFsBgVytaKLMiga3U5UxUtvgkbHYT1259saGKyKQh5oAwPSppaDCqtCIUf/DBC9fpmPLvR+miVB8uR0cRzukf6n6uApHcN2l9w8FT3iu3s5QnDDwoTAzSpNDp2eIMpQb1eu0FRTHrKaZ7fvAf9IrOTZiV2gyUDgawYIaQ==',
    'ab.storage.deviceId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1': '%7B%22g%22%3A%22137ee9b9-069f-6cb7-a940-b379b31bc439%22%2C%22c%22%3A1647113291139%2C%22l%22%3A1653643395848%7D',
    'ab.storage.userId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1': '%7B%22g%22%3A%228923e50b-f54b-4bd6-9b72-ad63c41dcf1a%22%2C%22c%22%3A1647113291133%2C%22l%22%3A1653643395848%7D',
    'ab.storage.sessionId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1': '%7B%22g%22%3A%22a13c1454-602f-f3fd-b5e3-2ee9d08cd60a%22%2C%22e%22%3A1653645195871%2C%22c%22%3A1653643395844%2C%22l%22%3A1653643395871%7D',
    'OptanonConsent': 'isIABGlobal=false&datestamp=Fri+May+27+2022+03%3A23%3A16+GMT-0600+(Mountain+Daylight+Time)&version=6.18.0&hosts=&consentId=9d7de6ca-cf98-4c82-b37a-1452bf8a89a2&interactionCount=1&landingPath=NotLandingPage&groups=snc%3A1%2Cfnc%3A1%2Cprf%3A1%2CSPD_BG%3A1%2Ctrg%3A1&AwaitingReconsent=false',
    '_lr_geo_location': 'CA',
    'local_fallback_mcid': '16385827555940440758496209399563339851',
    's_ecid': 'MCMID|16385827555940440758496209399563339851',
    'mcid': '16385827555940440758496209399563339851',
    '_sdsat_highestContentConfidence': '{%22course_uuid%22:%221455f8dd-f9c1-4120-9a49-30d60ae7c6fd%22%2C%22course_name%22:%22differential-equations%22%2C%22confidence%22:0.3047%2C%22year_in_school%22:%22college-year-2%22%2C%22subject%22:[{%22uuid%22:%2255cf65ce-de54-4d9b-8e57-d5014b8194b6%22%2C%22name%22:%22differential-equations%22}]}',
    '_gid': 'GA1.2.1524539550.1653643397',
    '8923e50b-f54b-4bd6-9b72-ad63c41dcf1a_TMXCookie': '60',
    'schoolapi': 'null',
    '_gat': '1',
    '_uetsid': 'a4b2e920dd9e11ecb565adeb45b8b772',
    '_uetvid': 'c3ffbaa0a23911ecbdf6d3e3a3d1c133',
    'IR_gbd': 'chegg.com',
    'IR_14422': '1653643398019%7C0%7C1653643398019%7C%7C',
    '_tq_id.TV-8145726354-1.ad8a': '8765dc695f008252.1647112953.0.1653643398..',
    '_tt_enable_cookie': '1',
    '_ttp': '1d2f3327-cab6-4765-b345-f5b2f4040345',
    '_cs_cvars': '%7B%221%22%3A%5B%22Page%20Name%22%2C%22Question%20Page%22%5D%2C%222%22%3A%5B%22Experience%22%2C%22desktop%22%5D%2C%223%22%3A%5B%22Page%20Type%22%2C%22pdp%22%5D%2C%224%22%3A%5B%22Auth%20Status%22%2C%22Soft%20Logged%20In%22%5D%7D',
    '_cs_id': 'c547e945-304e-a495-d9ac-76bf44330443.1647112953.29.1653643401.1653643401.1.1681276953839',
    '_cs_s': '1.0.0.1653645201567',
    '_clck': '1eoylhz|1|f1t|0',
    '_sctr': '1|1653631200000',
    '_clsk': '1le5pvg|1653643402346|1|0|b.clarity.ms/collect',
    '_iidt': '31jsTsnAv2fMyG2ljGxRqdrRNBIOr22HlWiJ2sA/teOO4ndanfVvTUSGxJ7UkrlNEEQGhICj9gUOAeHhWGhFNW3ECsv/drM=',
    '_vid_t': 'GaM21r7aEQ20e+m1hWI0T5nUYaaLbohcOqraGV6S45iudSIVCnl6JN1IuHADb+fbMhIjbvZVx/U13nbQBP6FgJHIJZG4vjs=',
    'DFID': 'web|36YVzWiU9puYbhr5VJtN',
}

headers = {
    'authority': 'www.chegg.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    # Requests sorts cookies= alphabetically
    # 'cookie': '_omappvp=qaT6ezuI7Yy8sFk25pmjPrAdTYoyRZHxMrktjAywK78MGVqgQ9R99DkKoYAsB0nb13Mkr9WZAVQmzuidKZWM8xSRKRkTf8hn; usprivacy=1YNY; _pxvid=c3855a89-a239-11ec-afcc-4e57685a5356; _ga=GA1.2.2017660448.1647112953; _gcl_au=1.1.1709949065.1647112953; _cs_c=0; mdLogger=false; kampyle_userid=17cc-c307-83c4-7a95-c667-9c3c-4319-a794; kampyleUserSession=1647112953124; kampyleUserSessionsCount=1; kampyleSessionPageCounter=1; C=0; O=0; optimizelyEndUserId=oeu1647112985951r0.4655835668708168; chgmfatoken=%5B%20%22account_sharing_mfa%22%20%3D%3E%201%2C%20%22user_uuid%22%20%3D%3E%208923e50b-f54b-4bd6-9b72-ad63c41dcf1a%2C%20%22created_date%22%20%3D%3E%202022-03-12T19%3A23%3A41.876Z%20%5D; _scid=ccdb9f37-f8dd-43dc-886f-ecfa298ee0ad; _rdt_uuid=1647113294066.14bdbcd0-72e9-41b8-94d7-517c102157e8; _ym_uid=1647117119538148506; _ym_d=1647117119; forterToken=eaa4d497464f423e9dffff4a8ba9c4b3_1647538932781__UDF43_13ck; V=8d1167618a67f9a2b70df1aaff794e72623372fd8f5619.69919635; id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4OTIzZTUwYi1mNTRiLTRiZDYtOWI3Mi1hZDYzYzQxZGNmMWEiLCJhdWQiOiJDSEdHIiwiaXNzIjoiaHViLmNoZWdnLmNvbSIsImV4cCI6MTY2MzMwODk0MywiaWF0IjoxNjQ3NTM4OTQzLCJlbWFpbCI6ImdxY3RueWNodHFAcHJpdmF0ZXJlbGF5LmFwcGxlaWQuY29tIn0.aIf2iOz1Fhf4OLCfPA5JZoBQN2n_VwvCvK7qZesmmCQtcYNuDfb9Sn0bSFfSV6XAHU4T6r0ioex4REN1LuQnGlrez3TPJ_lEcjgCgAKGb38L1021vXCBrv-5hqRlM8cV_6H_qo0QJYAsVxIMPdSqXl2s8sUnOwr0h_zS8qibu_yIU6mG1-buZnQA9xGX39itRg-txUkUD4xA86uF2Yblbg9G1U_6WdjkxLsCP7vsyUj8fCuz47x64dLN-lAHm7mAk6t4qfD6c600RmG0lcwldL_W-RX3xqw1mmaW89EpsXGghH1cznQQhdZu3FJQcTFNvIufjsYtuuLvvufnIt7UPQ; U=a37d420cc46fd6bd22c5f5d53c3feb60; OneTrustWPCCPAGoogleOptOut=false; exp=C026A%7CA560B%7CA127H; sa-user-id=s%253A0-940543cd-6e3e-4b37-5134-0c5d689c1fe4.W5hyXWs2aENyOzBhKUeYPHwPLiYu1snpdHXSFbsnb1s; sa-user-id-v2=s%253A0-8f56e81d-d0cc-4ae9-643f-010868cd55f9%2524ip%252424.65.95.200.d02tX3m%252B9%252Fr4uNkfai8Zziyk2jTZun73T1Kq3tzuVgU; chegg_web_cbr_qna_id=b75; PHPSESSID=5361440ed7b1fc6e345e977e9c112794; CSessionID=b1401e4f-5dd0-4c91-868d-996156fed73f; SU=Mx9RPU1Gx-IYPXS0tt7uL0_t0KNLktbxYP8RO-lOREln1-cjX5cbq0-TNuKhFAtKlIu2B8wKTkj1KRbpZyyNjf2JoWv3E1wA04Wm7nbpVEHU5bvH6b0WT4EaqGVhWZ4j; user_geo_location=%7B%22country_iso_code%22%3A%22CA%22%2C%22country_name%22%3A%22Canada%22%2C%22region%22%3A%22AB%22%2C%22region_full%22%3A%22Alberta%22%2C%22city_name%22%3A%22Sherwood+Park%22%2C%22postal_code%22%3A%22T8A%22%2C%22locale%22%3A%7B%22localeCode%22%3A%5B%22en-CA%22%2C%22fr-CA%22%5D%7D%7D; expkey=4F928D13FB5E31DDA93D9D86BFA1807C; intlPaQExitIntentModal=hide; CVID=49e13173-1e91-4f82-8e96-00e67024a47a; CSID=1653643392064; pxcts=a28c4694-dd9e-11ec-bbfb-70555575756b; _sdsat_authState=Soft%20Logged%20In; _sdsat_cheggUserUUID=8923e50b-f54b-4bd6-9b72-ad63c41dcf1a; sbm_a_b_test=12-test; _px3=ed54d19a09bf385fc6c7eae630802a0667c17e1d254b81608bcbe64ea4b3f215:IMNAcKFX+VchZ244DIKjmB+hZQ75f3txjAi2wFCg5tjGdMttFfNMwTXj7Ed/9kKfkJ0mj0lWb9WKQLbZu4S5RA==:1000:1PLtSbjwKfg5Z2IpK6otgin0lB7HRSVErSZyBqLC0/ADdaCjaK6lS94JS6QQV5befwbbju6ZMHMknSQj6U2liflPEBOtNoihx9iFRcyEEXgQKou7IGEYsFB1CQnHdQxtoD+SQICzJ5gElPlHm+yVXQy+pKfBXvp8petmqSjmzhtigamMb0Y3haNDk3erlWbjFW8JT7aZSAhJ3q0JYTEEYw==; _px=IMNAcKFX+VchZ244DIKjmB+hZQ75f3txjAi2wFCg5tjGdMttFfNMwTXj7Ed/9kKfkJ0mj0lWb9WKQLbZu4S5RA==:1000:YhIeOJAfpuoyvybbl+La4SsPXrRXv4npvmzk6bWSacgvLgmk3OLQ5r2sLo80KFmTGhZIEYru3TWkr9oVhYJpbU+RGo2LtK6+a2s6v1wKPr+hQkYcujFsBgVytaKLMiga3U5UxUtvgkbHYT1259saGKyKQh5oAwPSppaDCqtCIUf/DBC9fpmPLvR+miVB8uR0cRzukf6n6uApHcN2l9w8FT3iu3s5QnDDwoTAzSpNDp2eIMpQb1eu0FRTHrKaZ7fvAf9IrOTZiV2gyUDgawYIaQ==; ab.storage.deviceId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%22137ee9b9-069f-6cb7-a940-b379b31bc439%22%2C%22c%22%3A1647113291139%2C%22l%22%3A1653643395848%7D; ab.storage.userId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%228923e50b-f54b-4bd6-9b72-ad63c41dcf1a%22%2C%22c%22%3A1647113291133%2C%22l%22%3A1653643395848%7D; ab.storage.sessionId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%22a13c1454-602f-f3fd-b5e3-2ee9d08cd60a%22%2C%22e%22%3A1653645195871%2C%22c%22%3A1653643395844%2C%22l%22%3A1653643395871%7D; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+27+2022+03%3A23%3A16+GMT-0600+(Mountain+Daylight+Time)&version=6.18.0&hosts=&consentId=9d7de6ca-cf98-4c82-b37a-1452bf8a89a2&interactionCount=1&landingPath=NotLandingPage&groups=snc%3A1%2Cfnc%3A1%2Cprf%3A1%2CSPD_BG%3A1%2Ctrg%3A1&AwaitingReconsent=false; _lr_geo_location=CA; local_fallback_mcid=16385827555940440758496209399563339851; s_ecid=MCMID|16385827555940440758496209399563339851; mcid=16385827555940440758496209399563339851; _sdsat_highestContentConfidence={%22course_uuid%22:%221455f8dd-f9c1-4120-9a49-30d60ae7c6fd%22%2C%22course_name%22:%22differential-equations%22%2C%22confidence%22:0.3047%2C%22year_in_school%22:%22college-year-2%22%2C%22subject%22:[{%22uuid%22:%2255cf65ce-de54-4d9b-8e57-d5014b8194b6%22%2C%22name%22:%22differential-equations%22}]}; _gid=GA1.2.1524539550.1653643397; 8923e50b-f54b-4bd6-9b72-ad63c41dcf1a_TMXCookie=60; schoolapi=null; _gat=1; _uetsid=a4b2e920dd9e11ecb565adeb45b8b772; _uetvid=c3ffbaa0a23911ecbdf6d3e3a3d1c133; IR_gbd=chegg.com; IR_14422=1653643398019%7C0%7C1653643398019%7C%7C; _tq_id.TV-8145726354-1.ad8a=8765dc695f008252.1647112953.0.1653643398..; _tt_enable_cookie=1; _ttp=1d2f3327-cab6-4765-b345-f5b2f4040345; _cs_cvars=%7B%221%22%3A%5B%22Page%20Name%22%2C%22Question%20Page%22%5D%2C%222%22%3A%5B%22Experience%22%2C%22desktop%22%5D%2C%223%22%3A%5B%22Page%20Type%22%2C%22pdp%22%5D%2C%224%22%3A%5B%22Auth%20Status%22%2C%22Soft%20Logged%20In%22%5D%7D; _cs_id=c547e945-304e-a495-d9ac-76bf44330443.1647112953.29.1653643401.1653643401.1.1681276953839; _cs_s=1.0.0.1653645201567; _clck=1eoylhz|1|f1t|0; _sctr=1|1653631200000; _clsk=1le5pvg|1653643402346|1|0|b.clarity.ms/collect; _iidt=31jsTsnAv2fMyG2ljGxRqdrRNBIOr22HlWiJ2sA/teOO4ndanfVvTUSGxJ7UkrlNEEQGhICj9gUOAeHhWGhFNW3ECsv/drM=; _vid_t=GaM21r7aEQ20e+m1hWI0T5nUYaaLbohcOqraGV6S45iudSIVCnl6JN1IuHADb+fbMhIjbvZVx/U13nbQBP6FgJHIJZG4vjs=; DFID=web|36YVzWiU9puYbhr5VJtN',
    'pragma': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
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
