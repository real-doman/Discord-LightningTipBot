# Discord-LightningTipBot

This repository can be used to host your own Lightning Tip Bot for Discord servers.

## Requirements

* Python 3.5 and higher
* Discord Bot Token
* Lightning Node with [LNbits](https://github.com/lnbits/lnbits-legend)
* public https domain pointing to your lnbits

Here is an englisch [video tutorial](https://www.youtube.com/watch?v=ZIvExdnN1PQ&t) for the last requirement. An alternative is to use my [lnbits instance](https://lightningtipbot.com), than you run the bot yourself, but still using my Lightning Node. Just create a wallet and fill in the relevant data in the `.env` file later.

## Local development

You can clone this repository and run the bot by yourself.
  
  * Cloning this repository with
   ```
   git clone https://github.com/d-hoffi/Discord-LightningTipBot
   cd Discord-LightningTipBot
   ```
   * Create a Python3 virtual environment using:
   ```
   python3 -m venv bot-env
   source bot-env/bin/activate
   ```
   * Installing all requirements
   ```
   pip install -r requirements.txt
   ```

Make sure your virtual environment is activated every time you run the bot.
You can get out of the environment by running `deactivate`.

Edit the `.env` file and fill in your data. If you need help with that have a look [here](https://github.com/CodelsLaw/Discord-LightningTipBot/blob/main/docs/guide/env-file.md).
Afterwards you can run the bot with
```
python src/main.py
```

If you don't want to run the bot by yourself, you can add my bot [here](https://discord.com/api/oauth2/authorize?client_id=895724341591953528&permissions=43008&scope=bot)

## Warning

This Bot is a custodial Lightning Wallet. If not self hosted all funds will be controlled by someone else, so be careful with it.
Also it is still on an early stage of development, keep that in mind while using it.
I am also happy about improvements or feedback in general.
