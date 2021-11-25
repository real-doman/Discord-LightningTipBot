import requests
import json
import os

def create_user_api(user_id : int):

	admin_invoice_key : str = os.getenv('ADMIN_INVOICE_KEY')
	admin_wallet_user :str = os.getenv('ADMIN_WALLET_USER')
	url = os.getenv('CREATE_USER_API')
	data = {"admin_id": admin_wallet_user, "user_name": str(user_id), "wallet_name": str(user_id) + ' wallet'}
	headers = {"X-Api-Key": admin_invoice_key, "Content-type": "application/json"}

	r = requests.post(url, json=data, headers=headers)
	json_data = r.json()

	return json_data


def create_invoice(amount : int, memo : str, invoice_key : str):

	out = False
	url = os.getenv('PAYMENTS_API')
	data = {"out": out, "amount": amount, "memo": memo}
	headers = {"X-Api-Key": invoice_key}

	r = requests.post(url, json=data, headers=headers)
	json_data = r.json()

	return json_data


def create_lnurl(admin_key : str):

	url = os.getenv('LNURL_API')
	data = {"description": "fund discord wallet", "currency": "sat", "max": 10000000, "min": 1, "comment_chars": 500}
	headers = {"X-Api-Key": admin_key}

	r = requests.post(url, json=data, headers=headers)
	json_data = r.json()

	lnurl : str = json_data['lnurl']

	return lnurl


def pay_invoice(invoice : str, admin_key : str):

	url = os.getenv('PAYMENTS_API')
	data = {"out": True, "bolt11": invoice}
	headers = {"X-Api-Key": admin_key}

	json_data = requests.post(url, json=data, headers=headers).json()

	if 'message' in json_data:
		return 0 # payment failed
	elif 'payment_hash' in json_data:
		return 1 # payment successful


def decode_invoice(invoice : str, invoice_key : str):

	url = os.getenv('PAYMENTS_API') + '/decode'
	data = {"data": invoice}
	headers = {"X-Api-Key": invoice_key}

	r = requests.post(url, json=data, headers=headers)
	decoded_invoice = r.json()

	return decoded_invoice
