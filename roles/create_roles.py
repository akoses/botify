"""
This module creates all the roles needed to instantiate the application.
This should only be used once.
"""

import discord
import os
import roles as r
from dotenv import load_dotenv
load_dotenv()

async def create_roles(client:discord.Client):
	"""
	Create all the roles needed to instantiate the application.
	This should only be used once.
	"""

	#pylint: disable=no-member
	for role, c_values in r.ROLE_TO_COLOUR.items():
		if role not in client.guilds[0].roles:
			colour = discord.Color.from_rgb(c_values[0], c_values[1], c_values[2])
			await client.guilds[0].create_role(name=role, colour=colour, hoist=True)
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

