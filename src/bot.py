import logging
import discord
from discord import message
from discord.ext import commands
from discord.ext.commands import context
import requests
from requests.api import request
from discord_components import Button, DiscordComponents
import textwrap
import qrcode
import io
import os

from database import create_database, get_admin_key, get_connection, create_user, get_lnurl, get_balance, \
	does_user_exist, get_invoice_key

from apicalls import create_invoice, decode_invoice, pay_invoice


def start_bot(bot_token : str):

	logging.basicConfig(filename='lntipbot.log', filemode='w', level=logging.DEBUG)

	create_database()

	client = commands.Bot(command_prefix = '!', help_command = None)

	@client.event
	async def on_ready():
		print('bot is ready')
		DiscordComponents(client)


	@client.command()
	@commands.dm_only()
	async def help(ctx, *args):
		while True:
			result : int = does_user_exist(ctx.message.author.id)
			if result != 0:
				break

			create_user(ctx.message.author.id)

		if len(args) == 0:
			await start_command(ctx)

	@client.command()
	@commands.dm_only()
	async def start(ctx, *args):
		while True:
			result : int = does_user_exist(ctx.message.author.id)
			if result != 0:
				break

			create_user(ctx.message.author.id)

		if len(args) == 0:
			await start_command(ctx)

	@client.command()
	@commands.check(check_if_message_is_reply)
	async def tip(ctx, *args):
		while True:
			result : int = does_user_exist(ctx.message.author.id)
			if result != 0:
				break

			create_user(ctx.message.author.id)

		if len(args) > 0:
			await tip_command(ctx, *args)

	@client.command()
	@commands.dm_only()
	async def balance(ctx, *args):
		while True:
			result : int = does_user_exist(ctx.message.author.id)
			if result != 0:
				break

			create_user(ctx.message.author.id)

		if len(args) == 0:
			await balance_command(ctx)

	@client.command(aliases=['receive'])
	@commands.dm_only()
	async def invoice(ctx, *args):
		while True:
			result : int = does_user_exist(ctx.message.author.id)
			if result != 0:
				break

			create_user(ctx.message.author.id)
		
		if len(args) == 0:
			await ctx.send(textwrap.dedent("""
			:x: Oops, that didn't work. See below how to use this command.

			**Usage**: *!invoice <amount> [<description>]*
			**Example**: *!invoice 1000 Discord-LightningTipBot deposit
			"""))
		elif len(args) > 0:
			await invoice_command(ctx, *args)
			
	@client.command(aliases=['send'])
	@commands.dm_only()
	async def pay(ctx, *args):
		while True:
			result : int = does_user_exist(ctx.message.author.id)
			if result != 0:
				break

			create_user(ctx.message.author.id)

		if len(args) == 1:
			invoice = str(args[0])
			await pay_command(ctx, invoice)
			interaction = await client.wait_for("button_click", check=lambda inter: inter.custom_id == "pay_btn")

			if interaction is not None:
				try:
					admin_key = get_admin_key(ctx.message.author.id)
					bot_message = await ctx.send(':hourglass: Preparing payment.\nTry to pay invoice, please wait.')
					result = pay_invoice(invoice, admin_key)
					if result == 1:
						balance = get_balance(ctx.message.author.id)
						await ctx.reply(f':white_check_mark: Payment successful.\nYour new balance is {balance} sat')
						await bot_message.delete()
				except Exception as ex:
					print(ex)
			
		else:
			await ctx.reply(textwrap.dedent("""
			:x: Oops, that didn't work. See below how to use this command.

			**Usage**: *!pay <invoice>*
			**Example**: *!pay lnbc21...*
			"""))

	@client.command()
	@commands.dm_only()
	async def donate(ctx, *args):
		while True:
			result : int = does_user_exist(ctx.message.author.id)
			if result != 0:
				break

			create_user(ctx.message.author.id)

		if len(args) != 1:
			await ctx.send(textwrap.dedent("""
		:x: Oops, that didn't work. See below how to use this command.

		**Usage**: *!donate <amount>*
		**Example**: *!donate 1000
		"""))
		elif len(args) == 1:
			amount = int(args[0])
			await donate_command(ctx, amount)

	@client.command()
	@commands.dm_only()
	async def lnurl(ctx, *args):
		while True:
			result : int = does_user_exist(ctx.message.author.id)
			if result != 0:
				break

			create_user(ctx.message.author.id)

		if len(args) == 0:
			lnurl = get_lnurl(ctx.message.author.id)
			await ctx.send(':point_down: Your LNURL:')
			qr_code = create_qr_code(lnurl)

			with io.BytesIO() as image_binary:
				qr_code.save(image_binary, 'PNG')
				image_binary.seek(0)
				await ctx.send(f'*{lnurl}*', file=discord.File(fp=image_binary, filename='lnurl.png'))

	@client.command()
	@commands.dm_only()
	async def paylnurl(ctx, *args):
		while True:
			result : int = does_user_exist(ctx.message.author.id)
			if result != 0:
				break

			create_user(ctx.message.author.id)

		if len(args) == 2:
			lnurl = str(args[0])
			amount = int(args[1])
			message = f'''
			Are you sure you want to send {amount} sat to this lnurl?
			*{lnurl}*

			:information_source: **Info**
			The actual payment can be more expensive than {amount} sat due to fees.

			Please confirm your choise.
			'''
			await ctx.send(textwrap.dedent(message), components=[Button(label='Send', style=3, custom_id="paylnurl_btn"), Button(label='Cancel', style=4, custom_id='cancel_btn')])
			interaction = await client.wait_for("button_click", check=lambda inter: inter.custom_id == "paylnurl_btn")

			if interaction is not None:
				try:
					bot_message = await ctx.send(':hourglass: Preparing payment, please wait.')
					await paylnurl_command(ctx, lnurl, amount)
					await bot_message.delete()
				except Exception as ex:
					print(ex)
					
		elif len(args) != 2:
			await ctx.reply(textwrap.dedent("""
		:x: Oops, that didn't work. See below how to use this command.

		**Usage**: *!paylnurl <lnurl> <amount>*
		**Example**: *!paylnurl LNURL... 1000
		"""))

	# event handler for button clicks
	# just used to send messages
	@client.event
	async def on_button_click(interaction):
		if interaction.custom_id == 'cancel_btn':
			await interaction.respond(content=':x: Payment canceled.')

	# run the bot
	client.run(bot_token)


async def start_command(ctx):

	user_id : int = ctx.message.author.id

	lnurl = get_lnurl(user_id)
	balance = get_balance(user_id)
	welcome_message = textwrap.dedent(f"""
	Welcome {ctx.message.author.name}.

	:robot: **Wallet**
	This bot is a custodial Bitcoin Lightning wallet that can send tips on Discord.
	To tip, add the bot to a server. The basic unit of this bot are Satoshis (sat).
	100,000,000 sat = 1 Bitcoin.

	:information_source: **Info**
	Your LNURL: *{lnurl}*
	Your balance: *{balance}* sat

	:gear: **Commands**
	*!tip* - Reply to a message to tip: *!tip <amount> [<description>]*
	*!balance* - Check your balance: *!balance*
	*!invoice* - Receive with Lightning invocie: *!invoice <amount> [<description>]*
	*!pay* - Pay a Lightning invoice: *!pay <invoice>*
	*!lnurl* - Show your static LNURL pay link: *!lnurl*
	*!paylnurl* - Send sats to static LNURL pay link: *!paylnurl <lnurl> <amount>*
	*!donate* - Donate to this project: *!donate <amount>*
	*!help* - Show this message: *!help*

	:warning: **Warning**
	This bot is still under development and you could loose your funds using it.
	""")
	await ctx.send(welcome_message)


async def tip_command(ctx, *args):

	sender_id = ctx.message.author.id
	sender_name = ctx.message.author.name

	receiver_id = ctx.message.reference.resolved.author.id
	receiver_name = ctx.message.reference.resolved.author.name

	amount = int(args[0])
	sender_balance = get_balance(sender_id)

	if sender_id == receiver_id:
		await ctx.reply(":x: You can't tip yourself")
	elif sender_balance < amount:
		await ctx.reply(':x: Not enough funds')
	else:
		# check if receiver is already registered
		while True:
			result = does_user_exist(receiver_id)
			if result != 0:
				break
			create_user(receiver_id)

		# to update the balances the receiver creates an invoice,
		# which gets paid automatically by the sender of the tip
		# this happends without user interaction
		result = send_tip(sender_id, receiver_id, amount)

		# this is just UX stuff, the bot sends a message so that the users can follow
		if len(args) > 1 and result == 1:
			memo = ''
			for i in range(1, len(args)):
				memo += args[i] + ' '
			await ctx.reply(f':white_check_mark: Send {amount} sat from {sender_name} to {receiver_name}.\n Reason: {memo}')
		elif len(args) == 1 and result == 1:
			await ctx.reply(f':white_check_mark: Send {amount} sat from {sender_name} to {receiver_name}')
		elif result == 0:
			await ctx.reply(':x: Tip failed, please try again')


def send_tip(sender_id : int, receiver_id : int, amount : int):

	admin_key = get_admin_key(sender_id)
	invoice_key = get_invoice_key(receiver_id)
	
	json_data = create_invoice(amount, 'tip', invoice_key)
	invoice = json_data['payment_request']

	try:
		result = pay_invoice(invoice, admin_key)
		if result != 0: # payment successful
			return 1
		else:
			return 0
	except:
		return 0


async def balance_command(ctx):

	balance = get_balance(ctx.message.author.id)
	await ctx.send(f'**Your balance:** {balance} sat')


async def invoice_command(ctx, *args):

	amount = int(args[0])
	memo = ''

	if len(args) > 1:
		for i in range(1, len(args)):
			memo += args[i] + ' '
	else:
		memo = 'Discord-LightningTipBot deposit'

	invoice_key = get_invoice_key(ctx.message.author.id)
	
	json_data = create_invoice(amount, memo, invoice_key)
	invoice_string : str = str(json_data['payment_request'])

	qr_code = create_qr_code(invoice_string)
	
	with io.BytesIO() as image_binary:
		qr_code.save(image_binary, 'PNG')
		image_binary.seek(0)
		await ctx.send(f'*{invoice_string}*', file=discord.File(fp=image_binary, filename='invoice.png'))


def create_qr_code(string : str):

	try:
		qr_code = qrcode.make(string)
		return qr_code
	except Exception as ex:
		print(ex)


async def pay_command(ctx, invoice : str):

	invoice_key = get_invoice_key(ctx.message.author.id)
	
	decoded_invoice = decode_invoice(invoice, invoice_key)
	invoice_amount : int = int(decoded_invoice['amount_msat'] / 1000)
	description : str = decoded_invoice['description']
	node_id_receiver : str = decoded_invoice['payee']

	message = f'''
	Are you sure you want to pay this invoice?
	*{invoice}*

	**Amount**: {invoice_amount} sat
	**Description**: {description}
	**Destination node (Pubkey)**: {node_id_receiver}

	:information_source: **Info**
	The actual payment can be more expensive than {invoice_amount} sat due to fees.

	Please confirm your choise.
	'''
	await ctx.send(textwrap.dedent(message), components=[Button(label='Send', style=3, custom_id="pay_btn"), Button(label='Cancel', style=4, custom_id='cancel_btn')])


async def donate_command(ctx, amount : int):

	balance = get_balance(ctx.message.author.id)
	if balance < amount:
		await ctx.send(':x: Not enough funds')
	elif balance >= amount:
		# user pays invoice to tip me
		admin_invoice_key = os.getenv('ADMIN_INVOICE_KEY')
		invoice : str = str(create_invoice(amount, f'donation from {ctx.message.author.name}', admin_invoice_key)['payment_request'])

		admin_key = get_admin_key(ctx.message.author.id)
		result = pay_invoice(invoice, admin_key)

		if result == 0:
			await ctx.reply(':x: Donation failed')
		elif result == 1:
			await ctx.reply(':fireworks: Thank you for your donation.')


async def paylnurl_command(ctx, lnurl : str, amount : int):
	"""
	to pay LNURL:
	1) decode LNURL
	2) call the decoded url
	3) receive response and call the callback url with "?amount=1234" (in msat)
	4) receive invoice, pay invoice
	"""
	amount_msat = int(amount * 1000)

	# 1) decode LNURL 
	invoice_key = get_invoice_key(ctx.message.author.id)
	try:
		decoded_url : str = str(decode_invoice(lnurl, invoice_key)['domain'])

		# 2) call the decoded url
		json_data = requests.get(url=decoded_url).json()
		callback_url = str(json_data['callback'])
		max_sendable = int(json_data['maxSendable'] / 1000)
		min_sendable = int(json_data['minSendable'] / 1000)
	except Exception as ex:
		print(ex)
		await ctx.send(':x: Failed to decode LNURL')
	
	if amount < min_sendable or amount > max_sendable:
		await ctx.reply(f':x: This LNURL expects an amount between {min_sendable} and {max_sendable} sat')
	elif amount >= min_sendable and amount <= max_sendable:

		# 3) call the callback_url and receive response with invoice
		try:
			json_data = requests.get(f'{callback_url}?amount={amount_msat}').json()
			invoice = str(json_data['pr'])
		except Exception as ex:
			print(ex)
			await ctx.send(':x: Failed to receive an invoice.\nPayment failed.')

		# 4) pay invoice
		if get_balance(ctx.message.author.id) < amount:
			await ctx.send(':x: Not enough funds')
		elif get_balance(ctx.message.author.id) >= amount:
			try:
				admin_key = get_admin_key(ctx.message.author.id)
				result = pay_invoice(invoice, admin_key)
				if result == 0:
					await ctx.send(':x: Payment failed')
				elif result == 1:
					balance = get_balance(ctx.message.author.id)
					await ctx.send(f':white_check_mark: Payment successful.\nYour new balance is {balance} sat')
			except Exception as ex:
				print(ex)
				await ctx.send(':x: Payment failed')
	
	
# do all checks below
def check_if_message_is_reply(ctx):

	result = ctx.message.reference

	if result is None:
		return 0
	else:
		return 1
