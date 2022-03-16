import discord
import os
from utils import *
from xp import assign_xp
from db import *
import json

TRIVIA_CHANNEL = int(os.getenv('TRIVIA_CHANNEL'))

class LinkView(discord.ui.View):
	def __init__(self, url, label, timeout=None):
		super().__init__(timeout=timeout)
		self.url = url
		self.label = label
		self.add_item(
			discord.ui.Button(label=self.label, url=self.url)
		)


class EventButton(discord.ui.Button):
	def __init__(self, event_id, event_name):
		super().__init__(
			label="Attend Event",
			style=discord.enums.ButtonStyle.primary,
			custom_id=str(event_id),
		)
		self.id = event_id
		self.name = event_name
	
		
class JobButton(discord.ui.Button):
	def __init__(self, job_id, job_name):
		super().__init__(
			label="Track Application",
			style=discord.enums.ButtonStyle.primary, 
			custom_id=str(job_id),
		)
		self.id = job_id
		self.name = job_name


class CollegeRequestView(discord.ui.View):
	def __init__(self, college_data):
		super().__init__(timeout=None)
		self.college = college_data
	
	@discord.ui.button(label="Approve", style=discord.enums.ButtonStyle.success)
	async def approve(self, button, interaction):
		await create_college_fn(interaction.guild, self.college)
		await interaction.response.edit_message(content="College has been approved.", delete_after=10, view=None, embed=None)
	@discord.ui.button(label="Deny", style=discord.enums.ButtonStyle.danger)
	async def deny(self, button, interaction):
		await interaction.response.edit_message(content="College denied.", delete_after=10, view=None, embed=None)
		await interaction.user.send("Your college request has been denied.")


class TriviaView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=30)

	@discord.ui.button(label="Start",style=discord.ButtonStyle.primary)
	async def callback(self, button, interaction):
		trivia = json.loads(await redisClient.get("trivia"))
		question, correct, answers = trivia['question'], trivia['correct'], trivia['answers']
		
		answers.append(correct)
		random.shuffle(answers)
		
		answerView = AnswerView()

		for i, answer in enumerate(answers):
			button = TriviaButton(answer, correct, i)
			answerView.add_item(button)
		
		await interaction.response.edit_message(content=question, view=answerView)
		await redisClient.sadd("trivia-players", str(interaction.user.id))
		

class AnswerView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=10)


class TriviaButton(discord.ui.Button):
	def __init__(self, answer, correct, index):
		super().__init__(
            label=answer,
            style=discord.enums.ButtonStyle.secondary,
        )
		self.correct = correct

	async def callback(self, interaction):
		prize = int(await redisClient.get('trivia-prize'))
		if self.correct == self.label:
			await interaction.response.edit_message(content="That's correct! You've just won ${} coins! Come back tomorrow to play again.".format(prize), view=None)
			await bot.get_channel(TRIVIA_CHANNEL).send(content="{} got the trivia question of the day correct!".format(interaction.user.mention))
			await set_user_balance(prize, interaction.user.id)
		else:
			await interaction.response.edit_message(content="That's incorrect! The correct answer is {}. You could have won ${} coins. Come back tomorrow to play again.".format(self.correct, prize), view=None)
			await bot.get_channel(TRIVIA_CHANNEL).send(content="Oof {} got the trivia question of the day wrong.".format(interaction.user.mention))
		await assign_xp(bot, "TRIVIA", interaction.user.id)
		

