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
	content = await page.content()
	soup = BeautifulSoup(content, 'html.parser')
	card_container = soup.find('div', {'class': 'SetsView-resultList'})
	if not card_container:
		return []
	cards = card_container.findAll('div', {'class': 'SearchResultsPage-result'})
	embeds = []
	for i in range(len(cards)):	
		data_item_id = cards[i].get('data-item-id')
		title = cards[i].find('h5', {'class':'SetPreviewCard-title'})
		terms = cards[i].find('span', {'class':'AssemblyPillText'})
		if title and terms and data_item_id:
			title = title.text
			terms = terms.text
			card_url = 'https://quizlet.com/'+data_item_id
			embed = discord.Embed(
				title=title,
				url=card_url,
			)
			embed.add_field(name="Terms", value=terms, inline=False)
			embeds.append(embed)
		
		
	
	return embeds


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(find_content('Chem 101'))
