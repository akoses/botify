import aiohttp
import asyncio
from db import insert_chegg
from utils import build_link

headers = {
    'authority': 'www.chegg.com',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://www.chegg.com/homework-help/questions-and-answers/problem-3-12-marks-consider-following-simple-elegant-sorting-algorithm-somesort-b-e-e-6-1--q92085111',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cookie': '_omappvp=qqxwSvY3UIuzQH4q3Vw27dzkTAJn1GnL6jurKLZ6nTNSxZAnPaAo1tIlqipUR3deu6ewNGwKHpdyaZv7RJQmC3AUgCmH3XSt; _scid=8dfe89ce-ff8a-407e-87c5-a1aeabadc199; sbm_mcid=31848328009018304912344591009324274206; sbm_sbm_id=0100007F25706B603A00538D02F9871B; sbm_dma=0; sbm_gaid=31121576.1617653798; usprivacy=1YNY; C=0; O=0; opt-user-profile=98c954431a1a85792dc518646073bc836204447d980506.28413743%252C21052020077%253A21048420088; CVID=3a82db98-b1e7-4745-b844-7de1a1d7c774; user_geo_location=%7B%22country_iso_code%22%3A%22CA%22%2C%22country_name%22%3A%22Canada%22%2C%22region%22%3A%22AB%22%2C%22region_full%22%3A%22Alberta%22%2C%22city_name%22%3A%22Sherwood+Park%22%2C%22postal_code%22%3A%22T8A%22%2C%22locale%22%3A%7B%22localeCode%22%3A%5B%22en-CA%22%2C%22fr-CA%22%5D%7D%7D; local_fallback_mcid=29820974251136910418771571381804159706; s_ecid=MCMID|29820974251136910418771571381804159706; mcid=29820974251136910418771571381804159706; hwh_order_ref=%2Fhomework-help%2Fquestions-and-answers%2Fproblem-3-12-marks-consider-following-simple-elegant-sorting-algorithm-somesort-b-e-e-6-1--q92085111; CSID=1647130929991; OptanonConsent=isIABGlobal=false&datestamp=Sat+Mar+12+2022+17%3A22%3A10+GMT-0700+(Mountain+Standard+Time)&version=6.18.0&hosts=&consentId=6223bc2f-a115-46d8-b9c1-261a3376fb1c&interactionCount=1&landingPath=NotLandingPage&groups=snc%3A1%2Cfnc%3A1%2Cprf%3A1%2CSPD_BG%3A1%2Ctrg%3A1&AwaitingReconsent=false; CSessionID=cfb65a38-db13-4dbe-94d5-bf6377c234e8; schoolapi=null; _sdsat_authState=Logged%20Out; forterToken=77ae73d595b04692a438718dc44ef2c3_1647130938052_372_dUAL9_13ck; PHPSESSID=suhnpc5fbgid77i53i302jvcff; V=25a494b98ec14756b02f7ec8c40cd2c5622d39508ed569.63698289; chgmfatoken=%5B%20%22account_sharing_mfa%22%20%3D%3E%201%2C%20%22user_uuid%22%20%3D%3E%208923e50b-f54b-4bd6-9b72-ad63c41dcf1a%2C%20%22created_date%22%20%3D%3E%202022-03-13T00%3A22%3A42.645Z%20%5D; DFID=web|IT2KiQPC7POeYDaBdWFB; _iidt=W73oKsnkbW2PBtQD0C538rfQ5rmXnep8L7dMdFQ910YJpIC+CyF0Ku2cKhvPEENaKG8uNo+pZSou5g==; _vid_t=p/0YtEsE2xok9NJK56ohO7vwH3M2dSng2Uw+JppO/WsHoR01qW3igd58LBiF+mOTmT/FcUeVvVpCwg==; id_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImdxY3RueWNodHFAcHJpdmF0ZXJlbGF5LmFwcGxlaWQuY29tIiwiaXNzIjoiaHViLmNoZWdnLmNvbSIsInN1YiI6Ijg5MjNlNTBiLWY1NGItNGJkNi05YjcyLWFkNjNjNDFkY2YxYSIsImF1ZCI6IkNIR0ciLCJpYXQiOjE2NDcxMzEwMTQsImV4cCI6MTY2MjY4MzAxNCwicmVwYWNrZXJfaWQiOiJhcHcifQ.1OQCevIPolmgOrdgaZW3uWBpyBdIFjqIKZ_iNYe4uSqbc_02fsCN1dhq-Vo8BmPKHkrDroZHR75bXTJxioPPdMHO8QnZR70zLI8YLCrtHaZg4fUUfvfrd1pAUWF_frQQ4LGujWn8LyuoMGjw1y1qdqQcxJTmEi4FII3BCa0oTv3fCeh-WZQvhvRvOwMyxFt_ihWQA_ydVy1giVDJkesjHC2mhf9NkOwGAmxnr9zU0UkDVeqJjDjpzcIDLbLWCfoplvDu4t8fql7OtEo6zXwDRtVdEoL6-HeVodlJ6i4Ny-WDTAuzVlws3wH9iQQwAfGPnaJIsD6j5IS4O0rP9Sv9Cg; access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwczovL3Byb3h5LmNoZWdnLmNvbS9jbGFpbXMvYXBwSWQiOiJOc1lLd0kwbEx1WEFBZDB6cVMwcWVqTlRVcDBvWXVYNiIsImlzcyI6Imh1Yi5jaGVnZy5jb20iLCJzdWIiOiI4OTIzZTUwYi1mNTRiLTRiZDYtOWI3Mi1hZDYzYzQxZGNmMWEiLCJhdWQiOlsiY2hlZ2ctb2lkYyIsImh0dHBzOi8vY2hlZ2ctcHJvZC51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjQ3MTMxMDE0LCJleHAiOjE2NDcxMzI0NTQsImF6cCI6IjNUWmJoZnNad2RlSGJob1ZNeE92WkdiMzdNY3ZjMG84Iiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBhZGRyZXNzIHBob25lIG9mZmxpbmVfYWNjZXNzIiwiZ3R5IjoicGFzc3dvcmQiLCJyZXBhY2tlcl9pZCI6ImFwdyIsImNoZ2hyZCI6dHJ1ZSwiY2hnbWZhIjp0cnVlfQ.kk-koELGdcbv-Yp36yJMKjdX6iCLuIF441gP8HwAiNXCrWeowwJhHact_zcTi47JsJroHGbByWQUR0lzXAJemafMGRolFwlEAJQMApqLRZYiq5m1ACkzmoW9LCXPEMvvrqmfpOgK26Myu-bMeJ5RR57iacDrMQE3QWLMempOKajO1EU5IDoS3VBdx4htDSfjtF466iUX1OEcxF64jltUU2JliicXNNwVKJAMdIJ1j2RHZRQBm8BSS_i3is6db5JrpZJwIMGvM1XOYbYKL4WJf2-KEgK38kilviFpodPSaZRiYJSi8mq4BK42uRrT7SBF8_JzYJFrGjfMhEPmulj20w; access_token_expires_at=1647132454; refresh_token=ext.a0.t00.v1.MUvKQzy6QMG9Gd5cMmqQeUTuXu0lvMuYoQezreYg8QFcwiPYD5EJtLRfY0OtECQy64RTaaCG4FPsoAzp02BIEWs; SU=ck_14lKhD56unHKNR4N57pUiphuUDoJN0guQN8LNygIk7HRlDWoHi2te29ITzysToOWZ39dsqHhsNPFWxgeIE-zxLANx-DE3jSfWqOIObfXzCTkAcWs_hjURO9IHfznk; U=a37d420cc46fd6bd22c5f5d53c3feb60; chegg_web_cbr_qna_id=b; intlPaQExitIntentModal=hide; exp=A803B%7CC026A%7CA560B%7CA127H; expkey=4D08E64B5321D223F489C187C98F17D8',
}




async def convert_link(link:str):
	"""
	Convert a link in chegg.
	"""
	session = aiohttp.ClientSession(headers=headers)
	async with session as session:
		async with session.get(link) as response:
			html = await response.text()
			chegg_id = await insert_chegg(html)
			link = build_link(chegg_id)
			return link


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(convert_link('https://www.chegg.com/homework-help/questions-and-answers/problem-3-12-marks-consider-following-simple-elegant-sorting-algorithm-somesort-b-e-e-6-1--q92085111'))

