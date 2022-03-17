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
    'referer': 'https://www.chegg.com/auth?action=login&redirect=https%3A%2F%2Fwww.chegg.com%2Fhomework-help%2Fquestions-and-answers%2Fproblem-3-12-marks-consider-following-simple-elegant-sorting-algorithm-somesort-b-e-e-6-1--q92085111',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cookie': '_omappvp=qqxwSvY3UIuzQH4q3Vw27dzkTAJn1GnL6jurKLZ6nTNSxZAnPaAo1tIlqipUR3deu6ewNGwKHpdyaZv7RJQmC3AUgCmH3XSt; _scid=8dfe89ce-ff8a-407e-87c5-a1aeabadc199; sbm_mcid=31848328009018304912344591009324274206; sbm_sbm_id=0100007F25706B603A00538D02F9871B; sbm_dma=0; sbm_gaid=31121576.1617653798; usprivacy=1YNY; C=0; O=0; opt-user-profile=98c954431a1a85792dc518646073bc836204447d980506.28413743%252C21052020077%253A21048420088; user_geo_location=%7B%22country_iso_code%22%3A%22CA%22%2C%22country_name%22%3A%22Canada%22%2C%22region%22%3A%22AB%22%2C%22region_full%22%3A%22Alberta%22%2C%22city_name%22%3A%22Sherwood+Park%22%2C%22postal_code%22%3A%22T8A%22%2C%22locale%22%3A%7B%22localeCode%22%3A%5B%22en-CA%22%2C%22fr-CA%22%5D%7D%7D; local_fallback_mcid=29820974251136910418771571381804159706; s_ecid=MCMID|29820974251136910418771571381804159706; mcid=29820974251136910418771571381804159706; _sdsat_authState=Logged%20Out; chgmfatoken=%5B%20%22account_sharing_mfa%22%20%3D%3E%201%2C%20%22user_uuid%22%20%3D%3E%208923e50b-f54b-4bd6-9b72-ad63c41dcf1a%2C%20%22created_date%22%20%3D%3E%202022-03-13T00%3A22%3A42.645Z%20%5D; DFID=web|IT2KiQPC7POeYDaBdWFB; _iidt=W73oKsnkbW2PBtQD0C538rfQ5rmXnep8L7dMdFQ910YJpIC+CyF0Ku2cKhvPEENaKG8uNo+pZSou5g==; _vid_t=p/0YtEsE2xok9NJK56ohO7vwH3M2dSng2Uw+JppO/WsHoR01qW3igd58LBiF+mOTmT/FcUeVvVpCwg==; chegg_web_cbr_qna_id=b; userData=%7B%22authStatus%22%3A%22Logged%20Out%22%2C%22attributes%22%3A%7B%22uvn%22%3A%2225a494b98ec14756b02f7ec8c40cd2c5622d39508ed569.63698289%22%7D%7D; CVID=5c23c74c-636c-4441-b0cb-98d5eab68ce1; hwh_order_ref=%2Fhomework-help%2Fquestions-and-answers%2Fproblem-3-12-marks-consider-following-simple-elegant-sorting-algorithm-somesort-b-e-e-6-1--q92085111; CSID=1647528409785; OptanonConsent=isIABGlobal=false&datestamp=Thu+Mar+17+2022+08%3A46%3A50+GMT-0600+(Mountain+Daylight+Time)&version=6.18.0&hosts=&consentId=6223bc2f-a115-46d8-b9c1-261a3376fb1c&interactionCount=1&landingPath=NotLandingPage&groups=snc%3A1%2Cfnc%3A1%2Cprf%3A1%2CSPD_BG%3A1%2Ctrg%3A1&AwaitingReconsent=false; CSessionID=a2965f31-2580-473e-a163-e3702d0a6aa0; schoolapi=null; forterToken=77ae73d595b04692a438718dc44ef2c3_1647528429259_381_dUAL9_13ck; PHPSESSID=cn6qado9jhei81ib5u8q7fk3mm; V=6e1b645aef6ed65a245e8e01e641be43623349f72f6581.14041269; id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4OTIzZTUwYi1mNTRiLTRiZDYtOWI3Mi1hZDYzYzQxZGNmMWEiLCJhdWQiOiJDSEdHIiwiaXNzIjoiaHViLmNoZWdnLmNvbSIsImV4cCI6MTY2MzI5ODQ0MCwiaWF0IjoxNjQ3NTI4NDQwLCJlbWFpbCI6ImdxY3RueWNodHFAcHJpdmF0ZXJlbGF5LmFwcGxlaWQuY29tIn0.U2rPWT1YR43JxJJnriJecqsivZWg98Yq8p3VJ_2h84gHmKFWGpL4kaoIUpv5QonNqI_zLXXbRO0nSzfGH6s1IRXIRjBh7kd_3Hug0bNJotfGpeZeUYgRdW0GiMOPYxJF21tf_hGVSthI0N4NmJWQGBnV_9VPSaKcTyAU83rADLz0wSAFxai-DL6i8tKg2xd4QQvBQQZXBLh0EQZXZBh7l0_yJ4wTLzWe4B0kvXuJBjgO2DjFoOgfMJrZhjo68uyF095X-wEbW7_VeTNl347zzYiEF2IRGBnAhieBo_GOscO7iEIQZ1mIFMLXqDV562g3XAWOhF00349zBKHKetszHA; access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjhUTkU0cWwxNTRxekZieTBBakxDdSJ9.eyJodHRwczovL3Byb3h5LmNoZWdnLmNvbS9jbGFpbXMvYXBwSWQiOiJOc1lLd0kwbEx1WEFBZDB6cVMwcWVqTlRVcDBvWXVYNiIsImlzcyI6Imh0dHBzOi8vY2hlZ2ctcHJvZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8c2NsfDg5MjNlNTBiLWY1NGItNGJkNi05YjcyLWFkNjNjNDFkY2YxYSIsImF1ZCI6WyJjaGVnZy1vaWRjIiwiaHR0cHM6Ly9jaGVnZy1wcm9kLnVzLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2NDc1Mjg0NDAsImV4cCI6MTY0NzUyOTg4MCwiYXpwIjoiM1RaYmhmc1p3ZGVIYmhvVk14T3ZaR2IzN01jdmMwbzgiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIGFkZHJlc3MgcGhvbmUgb2ZmbGluZV9hY2Nlc3MiLCJndHkiOiJwYXNzd29yZCJ9.IrmxZUMroytxLGv7bPV0cDCxHYQ-8BdXLdhKJejlJBGbCgvP5a4xim7yMXvm1BJuVQu5BJIiwkzVtJ51-bT3MKovt3HQO-ghjisefkocbRWT5XZOa9vysd1FKCopCgy2fP0Y-Nn1hJQvMO4KvNw5VTCfiGjLLC4Vw3MfH7WPPsZ3KFIKisrRH_K6XJsnFNizaPbofRN6LSMlNFJkq3SB9v8vZT1G0zZHTxMhzvn9BvT-Uo11ULs_qNWccmxsuwqL2MiS3uI_mCrs8FUueVIWR1vA7xotjrESUdThC3vJEOHLJnvJvZvpLLPregJJBB9qI1rKjqo1XcalbBcmRrtHXw; access_token_expires_at=1647529881; refresh_token=ext.a0.t00.v1.MQWO_Fmt9wblbCri70lhfkdSlTOb0eIH2t19rDtEMmKLJTgJ94GANZxskuPVceWM1AwerxYySKmeG6luHGkOyk4; SU=lBNrFweEm4YKnoje8g7ugGwpKJ4xsh9pwl-0B6a11OOorwSsM2m0btgaCenyk0us1G6wJ2d2w0fJQ4yWlgcFPJ9i1AixDQiwNFpO4HJsL1Ru6OOuT_P7ru6KhnGQspET; U=a37d420cc46fd6bd22c5f5d53c3feb60; intlPaQExitIntentModal=hide; exp=A803B%7CC026A%7CA560B%7CA127H; expkey=4D08E64B5321D223F489C187C98F17D8',
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

