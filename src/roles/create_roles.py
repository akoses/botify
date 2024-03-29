"""
This module creates all the roles needed to instantiate the application.
This should only be used once.
"""

import discord
import os
import roles as r
from dotenv import load_dotenv
load_dotenv()
GUILD_ID = 939394818428243999
async def create_roles(client:discord.Client):
	"""
	Create all the roles needed to instantiate the application.
	This should only be used once.
	"""

	#pylint: disable=no-member
	for role, c_values in r.ROLE_TO_COLOUR.items():
		guild = await client.fetch_guild(GUILD_ID)
		if role not in guild.roles:
			colour = discord.Color.from_rgb(c_values[0], c_values[1], c_values[2])
			guild = await client.fetch_guild(GUILD_ID)
			await guild.create_role(name=role, colour=colour, hoist=True)
			print(f"Created role {role}")


cli = discord.Client()

@cli.event
async def on_ready():
	"""
	This event is called when the bot is ready.
	"""
	await create_roles(cli)
	await cli.close()

cli.run(os.getenv("DISCORD_TOKEN"))

