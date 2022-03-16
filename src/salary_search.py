import aiohttp
from utils import *
import asyncio
from bs4 import BeautifulSoup



async def salary_search(job_title):
	url = 'https://ca.talent.com/salary'
	async with aiohttp.ClientSession() as session:
		params = {
			'job': job_title,
		}
		res = await fetch(session, url, params)
		soup = BeautifulSoup(res, 'html.parser')
		title = soup.find('div', {'class': 'c-card__title'})
		salary = soup.find('div', {'class': 'c-card__stats-mainNumber'})
		salary_info = soup.find('div', {'class': 'c-card__stats-info'})
		region_salaries = soup.find('div', {'id': 'salariesRegions'})
		region_salary = []
		region = []
		if region_salaries:
			region_salary = region_salaries.find_all('div', {'class': 'c-card--progressBar--number'})
			regions = region_salaries.find_all('div', {'class': 'c-card--progressBar--text'})
		if title and salary and salary_info:
			embed = discord.Embed(
			title=title.text,
			description=salary_info.text,
			color=0xA020F0
			)
			embed.add_field(name="Salary", value=f"{salary.text.strip()} / Annual", inline=False)
			for region in regions:
				embed.add_field(name=region.text, value=f"{region_salary[regions.index(region)].text}", inline=False)

			return embed
		else:
			return None
		
if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(salary_search('Software Engineer'))