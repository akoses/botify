
from bs4 import BeautifulSoup
import urllib
import asyncio
import discord
from pyppeteer import launch

async def find_content(question:str):
	
	base_url = 'https://quizlet.com/search'
	params = {
		'query':question,
		'type':'sets',
	}
	
	query = urllib.parse.urlencode(params)
	browser = await launch(options={'args': ['--no-sandbox']})
	page = await browser.newPage()
	await page.setUserAgent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36");
	url = base_url+'?'+ query
	await page.goto(url, {'waitUntil': 'networkidle2'})
	page_source = await page.content()
	soup = BeautifulSoup(page_source, 'html.parser')
	contents = soup.find_all('div', {'class':'SearchResultsPage-result'})
	embeds = []
	for content in contents:
		title = content.find('h5', {'class':'SetPreviewCard-title'})
		terms = content.find('span', {'class':'AssemblyPillText'})
		url = content.find('a', {'class':['AssemblyLink']})
		if title and terms and url:
			embed = discord.Embed(
				title=title.text,
				url=url.get("href"),
			)
			embed.add_field(name="Terms", value=terms.text, inline=False)
			
			embeds.append(embed)
	
	await browser.close()
	return embeds


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(find_content('Ualberta BIOL 108'))
