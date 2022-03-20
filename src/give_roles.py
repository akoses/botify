import os
import discord

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
client = discord.Client(intents=intents)

async def give_roles(members):
	"""
	Give roles to the members
	"""
	for member in members:
		if member.id == client.user.id:
			continue
		
		role = discord.utils.get(member.guild.roles, name='Lower Year Student')
		try:
			await member.add_roles(role)
			print(f"{member.name} has been given the role {role.name}")
		except Exception as e:
			pass
		

@client.event
async def on_ready():
	"""
	This event is called when the bot is ready.
	"""
	
	print(f'{client.user.name} has connected to Discord!')
	members = client.guilds[0].members
	await give_roles(members)
	await client.close()

client.run(TOKEN)