import os
from dotenv import load_dotenv

from bot import start_bot

def main():
    
    try:
        load_dotenv()
    except Exception as e:
        print('No configuration file found\n' + e)
        exit(1)

    try:
        bot_token = os.getenv('BOT_TOKEN')
    except KeyError:
        print('The environment variable BOT_TOKEN is not defined')
        exit(1)

    try:
        os.getenv('PAYMENTS_API')
    except:
        print('The environment variable PAYMENTS_API is not defined')
        exit(1)

    try:
        os.getenv('LNURL_API')
    except:
        print('The environment variable LNURL_DOMAIN is not defined')
        exit(1)

    try:
        os.getenv('CREATE_USER_API')
    except:
        print('The environment variable CREATE_USER_API is not defined')
        exit(1)

    try:
        os.getenv('ADMIN_INVOICE_KEY')
    except:
        print('The environment variable ADMIN_INVOICE_KEY is not defined')
        exit(1)

    try:
        os.getenv('ADMIN_KEY')
    except:
        print('The environment variable ADMIN_KEY is not defined')
        exit(1)

    try:
        os.getenv('ADMIN_WALLET_USER')
    except:
        print('The environment variable ADMIN_WALLET_USER is not defined')
        exit(1)

    try:
        os.getenv('GET_WALLET_DETAILS_API')
    except:
        print('The environment variable GET_WALLET_DETAILS_API is not defined')
        exit(1)
        
    start_bot(bot_token)

if __name__ == "__main__":
    main()