import requests
from bs4 import BeautifulSoup
import urllib.parse
import discord
import aiohttp
from utils import fetch

async def find_jobs(job_title: str):

	async with aiohttp.ClientSession() as session:
		params = {
			'q': job_title,
		}
		res = await fetch(session, 'https://ca.indeed.com/jobs', params)
		soup = BeautifulSoup(res, 'html.parser')
		
		res = soup.find_all('a', {'class': ['tapItem', 'fs-unmask', 'result']}) 
		embeds = []
		for job in res:
			title = job.find('h2', {'class': 'jobTitle'})
			company = job.find('span', {'class':'companyName'})
			location = job.find('div', {'class':'companyLocation'})
			if title and company and location:
				embed = discord.Embed(
					title=title.text,
					url=f'https://ca.indeed.com{job.get("href")}',
					
				)
				embed.add_field(name="Company", value=company.text, inline=False)
				embed.add_field(name="Location", value=location.text, inline=False)
				embeds.append(embed)
		return embeds[:5]
