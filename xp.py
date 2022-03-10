"""
XP Generation for each level 
"""
import os
import discord
from db import get_xp_levels, set_xp_levels, set_role
from dotenv import load_dotenv

from roles.roles import get_level_to_role , ROLE_TO_ENTRIES

load_dotenv()
LEVELS_CHANNEL = int(os.getenv('LEVELS_CHANNEL'))

ACTION_TO_XP = {
	"MESSAGE": 30,
	"APPLY": 100,
	"ATTEND_EVENT": 100,
	"POST_JOB": 500,
	"POST_EVENT": 500,
	"TRIVIA": 500,
	"REFERRAL": 1000,
	"WIN_GAME": 10000
}

MAX_XP = 18604330

def xp_less_50(n:int):
	"""Generate xp for levels 1-49

	Args:
		n (int): level

	Returns:
		int: The EXP required to reach the next level
	"""
	return int((n**3*(100 - n))/50)

def xp_50_to_68(n:int):
	"""Generate xp for levels 50-67

	Args:
		n (int): level

	Returns:
		int: The EXP required to reach the next level
	"""
	return int((n**3*(150 - n))/100)

def xp_68_to_98(n:int) -> int:
	"""Generate xp for levels 68-97

	Args:
		n (int):level 

	Returns:
		int: The EXP required to reach the next level
	"""
	return int((n**3*(1911 - 10*n)/3)/500)

def xp_98_to_100(n:int) -> int:
	"""
	Generate xp for levels 98-100

	Args:
		n (int): level
	Returns:
		int: The EXP required to reach the next level
	"""
	return int((n**3*(160 - n))/100)


def get_xp(n:int) -> int:
	"""
	Generate xp for a given level
	
	Args:
		n (int): level
	Returns:
		int: The EXP required to reach the next level
	"""
	if n < 50:
		return xp_less_50(n)
	elif n < 68:
		return xp_50_to_68(n)
	elif n < 98:
		return xp_68_to_98(n)
	elif n <= 100:
		return xp_98_to_100(n)


def get_xp_total(n:int) -> int:
	"""
	Get the total xp needed for a given level
	"""
	max_xp = 0
	for i in range(1, n + 1):
		max_xp += get_xp(i)
	return max_xp

def get_level_from_xp(xp:int) -> int:
	"""
	Get the level from a given xp
	"""
	i = 1 
	while xp > get_xp_total(i):
		i += 1
	return i - 1

async def show_new_level(bot, level:int, discord_id:int, new_role:bool, role=None):
	channel =  bot.get_channel(LEVELS_CHANNEL)

	if new_role:
		await channel.send(f"**{bot.get_user(discord_id).mention} has reached level {level} and is now a {role}!**")
	else:
		await channel.send(
			f"**{bot.get_user(discord_id).mention} has reached level {level}!**"
		)

async def assign_xp(bot, payload, discord_id:int, xp_amount = 0):

	"""
	Assign xp to a user
	"""
	if xp_amount == 0:
		xp = ACTION_TO_XP[payload]
	else:
		xp = xp_amount
	total_xp, level = get_xp_levels(discord_id)
	total_xp += xp
	
	new_level = get_level_from_xp(total_xp)
	entries = 0
	if new_level > level:
		new = False
		new_role = None
		if new_level % 10 == 0:
			entries = ROLE_TO_ENTRIES[new_level]
			new = True
			old_role = discord.utils.get(bot.guilds[0].roles, name=get_level_to_role(level))
			new_role = discord.utils.get(bot.guilds[0].roles, name=get_level_to_role(new_level))
			if new_role:
				await bot.guilds[0].get_member(discord_id).add_roles(new_role)
			if old_role:
				await bot.guilds[0].get_member(discord_id).remove_roles(old_role)
			await set_role(discord_id, new_role)

		
		await show_new_level(bot, new_level, discord_id, new, new_role)
	set_xp_levels(discord_id, total_xp, new_level, entries=entries)


def xp_to_next_level(xp:int) -> int:
	"""
	Get the xp needed to reach the next level
	"""
	level = get_level_from_xp(xp)
	return get_xp_total(level + 1) - xp

def percentage_to_next_level(xp:int) -> float:
	"""
	Get the percentage of xp needed to reach the next level
	"""
	level = get_level_from_xp(xp)
	if xp > MAX_XP:
		xp = MAX_XP

	return abs(get_xp_total(level) - xp)/get_xp(level)*100

def curr_xp_for_level(xp:int, level:int) -> int:
	"""
	Get the current xp for a given level

	"""
	return xp - get_xp_total(level)

def test():
	"""Test the xp generator"""
	curr_xp = MAX_XP - 1000000
	for i in range(1, 101):
		print(i, get_xp(i), get_xp_total(i))


if __name__ == "__main__":
	test()


