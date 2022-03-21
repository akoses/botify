import aiohttp
from bs4 import BeautifulSoup
import json
import discord
from discord.commands import Option
from discord.ext import commands
intents = discord.Intents().all()
bot = commands.Bot(intents=intents)
import os
from dotenv import load_dotenv
load_dotenv()

guild_ids = [939394818428243999]
TOKEN = os.getenv('PEOPLE_SEARCH_TOKEN')

@bot.event
async def on_ready():
	"""
	This event is called when the bot is ready.
	"""
	print(f'{bot.user.name} has connected to Discord!')


@bot.slash_command(name="people", description="Search for people on Linkedin based on their role name and/or company.", guild_ids=[939394818428243999])
async def people_search_discord(ctx,
	job_title: Option(str, "Enter the Job title you are looking for. Ex: Software Developer"),
	company: Option(str, "Enter the company name. Ex: Google") = '',
	page: Option(int, "Enter the page number. Ex: 1") = 1):
	"""Search for people on Linkedin based on their role name and/or company. 
	Args:
		name (str): Name of the role
		company (str): Name of the company

	Returns:
		list: List of people with the given role and/or company.
	"""
	await ctx.defer()
	embeds = await people_search(job_title, company, page)
	if not embeds:
		await ctx.respond("No people found")
	else:
		for embed in embeds:
			await ctx.respond(embed=embed)

cookies = {
    'bcookie': '"v=2&9f4264a2-b613-440c-8fe9-be53f6096047"',
    'bscookie': '"v=1&202101012250377542d666-2562-4deb-8f16-904b8dc76663AQHhtZMLPRc2OQCyNCE5MWZe7B3nikkQ"',
    '_ga': 'GA1.2.449141999.1618350517',
    'timezone': 'America/Edmonton',
    'li_rm': 'AQH4StEFC55CVAAAAX3LvHARTgRkUiuyI4RQSN_rS9BUb8nCcKZa-aG_NsCG17jGqm9bzesHskhTv4l2HwVDf5OpBFDIPQHn3J9abnqXbXp3bxnGye0B_J4DsfMPX24kerCLQA2OSk_MuneHmKhAm-ejg005SOmZNeAvMQIv2glRjujcZ_OLgVLeK0IO1M-_X8cMb_qbQRglXSn3lcOS-EKLcKWjg1_n-FH9j5B-wD4wd5mPoijrkgtrkM6O2yjWInTGOnG91Vm3Fmu9LJ1zxbokSkbhZa-XrDB4Kxg6Jxka_POdKGmNI-56ZKGKnvq3cAHnXPtSOptvKdTVts0',
    '__ssid': 'f4a5a967-01b1-4aac-a35a-846b6ef168a6',
    'dfpfpt': 'c5cba23e727a49dc86d72704905b3d1c',
    'liveagent_oref': 'https://www.linkedin.com/help/lms',
    'liveagent_vc': '2',
    'liveagent_ptid': '8e3006cc-8e0b-4565-96ae-b3819166c337',
    'VID': 'V_2022_01_10_20_178',
    'li_theme': 'light',
    'li_theme_set': 'app',
    'visit': 'v=1&M',
    'g_state': '{"i_p":1648009466292,"i_l":3}',
    'sdsc': '1%3A1SZM1shxDNbLt36wZwCgPgvN58iw%3D',
    'lang': 'v=2&lang=en-us',
    'li_at': 'AQEDATLDxQYEzVHiAAABf6lG5ZwAAAF_zVNpnFYAvB-q9D9lCcTaFB-pFiPeohGHaTFL-TJUhujQKGo44qbWIyUS5JK3JA82ORMZ57gGcYrWc5D_OhVPBT5QuBvnHkIQAL--x6nICbciL1waX-0gtDVN',
    'liap': 'true',
    'JSESSIONID': '"ajax:2511105472856531915"',
    'lidc': '"b=OB58:s=O:r=O:a=O:p=O:g=2523:u=147:x=1:i=1647812470:t=1647837893:v=2:sig=AQGQiU69scXUzb4CG2yGlEsOHngr_iY2"',
}

headers = {
    'authority': 'www.linkedin.com',
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
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    # Requests sorts cookies= alphabetically
    'cookie': 'bcookie="v=2&9f4264a2-b613-440c-8fe9-be53f6096047"; bscookie="v=1&202101012250377542d666-2562-4deb-8f16-904b8dc76663AQHhtZMLPRc2OQCyNCE5MWZe7B3nikkQ"; _ga=GA1.2.449141999.1618350517; timezone=America/Edmonton; li_rm=AQH4StEFC55CVAAAAX3LvHARTgRkUiuyI4RQSN_rS9BUb8nCcKZa-aG_NsCG17jGqm9bzesHskhTv4l2HwVDf5OpBFDIPQHn3J9abnqXbXp3bxnGye0B_J4DsfMPX24kerCLQA2OSk_MuneHmKhAm-ejg005SOmZNeAvMQIv2glRjujcZ_OLgVLeK0IO1M-_X8cMb_qbQRglXSn3lcOS-EKLcKWjg1_n-FH9j5B-wD4wd5mPoijrkgtrkM6O2yjWInTGOnG91Vm3Fmu9LJ1zxbokSkbhZa-XrDB4Kxg6Jxka_POdKGmNI-56ZKGKnvq3cAHnXPtSOptvKdTVts0; __ssid=f4a5a967-01b1-4aac-a35a-846b6ef168a6; dfpfpt=c5cba23e727a49dc86d72704905b3d1c; liveagent_oref=https://www.linkedin.com/help/lms; liveagent_vc=2; liveagent_ptid=8e3006cc-8e0b-4565-96ae-b3819166c337; VID=V_2022_01_10_20_178; li_theme=light; li_theme_set=app; visit=v=1&M; g_state={"i_p":1648009466292,"i_l":3}; sdsc=1%3A1SZM1shxDNbLt36wZwCgPgvN58iw%3D; lang=v=2&lang=en-us; li_at=AQEDATLDxQYEzVHiAAABf6lG5ZwAAAF_zVNpnFYAvB-q9D9lCcTaFB-pFiPeohGHaTFL-TJUhujQKGo44qbWIyUS5JK3JA82ORMZ57gGcYrWc5D_OhVPBT5QuBvnHkIQAL--x6nICbciL1waX-0gtDVN; liap=true; JSESSIONID="ajax:2511105472856531915"; lidc="b=OB58:s=O:r=O:a=O:p=O:g=2523:u=147:x=1:i=1647812470:t=1647837893:v=2:sig=AQGQiU69scXUzb4CG2yGlEsOHngr_iY2"',
}



async def people_search(role:str, company:str="", page:int=1):
	"""Search for people on linkedin based on their name and/or company. 

	Args:
		role (str): Name of the role
		company (str): Name of the company
		page (int): Linkedin Page

	Returns:
		list: List of people with the given role and/or company.
	"""
	params = {
		'geoUrn': '["101174742"]',
    	'keywords': f"{role} {company}",
    	'origin': 'GLOBAL_SEARCH_HEADER',
    	'page': f'{page}',
    	'sid': 'tQ0',
	}

	async with aiohttp.ClientSession(headers=headers) as session:
		async with session.get('https://www.linkedin.com/search/results/people/', params=params) as res:
			content = await res.text()

			soup = BeautifulSoup(content, 'html.parser')
			people = soup.find_all('code', id=lambda x: x and x.startswith('bpr-guid'))
			data = people[-1]
			people = []
			dict_data = json.loads(data.text)
			
			try:
				people_list = dict_data['included']
				for element in people_list:
					if 'title' in element:
						person = dict()
						person['name'] = element['title']['text']
						person['description'] = element['primarySubtitle']['text']
						person['url'] = element['navigationContext']['url']
						image_dict = element['image']['attributes'][0]['detailDataUnion']['nonEntityProfilePicture']
						if 'vectorImage' in image_dict:
							image = image_dict['vectorImage']['rootUrl']
							image += image_dict['vectorImage']['artifacts'][0]['fileIdentifyingUrlPathSegment']
							person['image'] = image
						embed = discord.Embed(title=person['name'], description=person['description'], url=person['url'])
						if 'image' in person:
							embed.set_thumbnail(url=person['image'])
						people.append(embed)
				return people
			except KeyError:
				return []



if __name__ == '__main__':
	bot.run(TOKEN)