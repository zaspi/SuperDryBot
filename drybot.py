from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import json
import requests

# Here we put the telegram bot token
updater = Updater(token='YOUR BOT TOKEN HERE')
dispatcher = updater.dispatcher

# The way I do it is to make a class object with all the data we will need to process a card request and
# send it to the chat. Maybe not all the data, but most of it. I haven't checked, and I definitely hackjobbed a lot
# of this shit together over time.
class Card(object):
    def __init__(self, json):
        self.name = json['data'][0]['name']

        # If Scryfall returns a dual sided card or whatever the hell has two "sides", the JSON will be formatted
        # differently. This will let us catch the other side of the card if there is one, and make sure we
        # add that one too
        try:
            self.image = json['data'][0]['image_uris']['normal']
        except KeyError:
            self.image = json['data'][0]['card_faces'][0]['image_uris']['normal']
            self.image2 = json['data'][0]['card_faces'][1]['image_uris']['normal']

        self.commanderban = json['data'][0]['legalities']['commander']
        self.pioneerban = json['data'][0]['legalities']['pioneer']
        self.edhrec = json['data'][0]['related_uris']['edhrec']
        self.regprice = json['data'][0]['prices']['usd']
        self.foilprice = json['data'][0]['prices']['usd_foil']
        self.scryfall = json['data'][0]['scryfall_uri']
        self.rulingsURI = json['data'][0]['rulings_uri']
        if self.commanderban == "banned" or self.commanderban == "not_legal":
            self.bantxt = "\U0001F6D1 Commander"
        else:
            self.bantxt = "\U00002705 Commander"
        if self.pioneerban == "banned" or self.pioneerban == "not_legal":
            self.bantxtpioneer = "\U0001F6D1 Pioneer"
        else:
            self.bantxtpioneer = "\U00002705 Pioneer"
        if self.regprice == None:
            self.regprice = "?"
        else:
            pass
        if self.foilprice == None:
            self.foilprice = "?"
        else:
            pass

    # MTGassist URL creation
        self.mtgassist = "https://www.mtgassist.com/search.php?name="
        self.mtgassist += str(self.name.replace(" ","+"))

    # Make the bot message and use either Py-telegram-bot (or something) OR telegrams native python module
        try:
            self.bot_msg_back = f"<a href = \"{self.image2}\"><b>{self.name}</b></a>"
            self.bot_msg = f"<a href = \"{self.image}\"><b>{self.name}</b></a>\n\U0001F4A9 ${self.regprice}  \U00002728 ${self.foilprice}\n{self.bantxt}\n{self.bantxtpioneer}\n\n<a href = \"{self.scryfall}\">Scryfall</a> / <a href = \"{self.edhrec}\">EDHRec</a> / <a href=\"{self.mtgassist}\">MTGAssist</a>"
        except AttributeError:
            self.bot_msg = f"<a href = \"{self.image}\"><b>{self.name}</b></a>\n\U0001F4A9 ${self.regprice}  \U00002728 ${self.foilprice}\n{self.bantxt}\n{self.bantxtpioneer}\n\n<a href = \"{self.scryfall}\">Scryfall</a> / <a href = \"{self.edhrec}\">EDHRec</a> / <a href=\"{self.mtgassist}\">MTGAssist</a>"

class Random_Card(object):
    def __init__(self, json):
        self.regprice = json['prices']['usd']
        self.name = json['name']
        self.image = json['image_uris']['normal']
        self.commanderban = json['legalities']['commander']
        self.edhrec = json['related_uris']['edhrec']
        # 🇺🇸 #1? Well, 💲 #1.
        self.foilprice = json['prices']['usd_foil']
        self.scryfall = json['scryfall_uri']
        self.pioneerban = json['legalities']['pioneer'] 
        if self.commanderban == "banned" or self.commanderban == "not_legal":
            self.bantxt = "\U0001F6D1 Commander"
        else:
            self.bantxt = "\U00002705 Commander"
        if self.pioneerban == "banned" or self.pioneerban == "not_legal":
            self.bantxtpioneer = "\U0001F6D1 Pioneer"
        else:
            self.bantxtpioneer = "\U00002705 Pioneer"
        if self.regprice == None:
            self.regprice = "?"
        else:
            pass
        if self.foilprice == None:
            self.foilprice = "?"
        else:
            pass
        self.mtgassist = "https://www.mtgassist.com/search.php?name="
        self.mtgassist += str(self.name.replace(" ","+"))
        #Make the bot message and use either Py-telegram-bot (or something) OR telegrams native python module
        self.bot_msg = f"<a href = \"{self.image}\"><b>{self.name}</b></a>\n\U0001F4A9 ${self.regprice}  \U00002728 ${self.foilprice}\n{self.bantxt}\n{self.bantxtpioneer}\n\n<a href = \"{self.scryfall}\">Scryfall</a> / <a href = \"{self.edhrec}\">EDHRec</a> / <a href=\"{self.mtgassist}\">MTGAssist</a>"

# Simple helper function. Feed it a search term, it will return the JSON of the results
# from Scryfall.
def search_scryfall(scrysearch):
    scryfall_params = dict(
    q=str(scrysearch)
    )
    json = requests.get(url="https://api.scryfall.com/cards/search", params=scryfall_params)
    json = json.json()
    return json

# function to see if we are dealing with one or multiple cards.
# outputs a list of card names if multple, zero if one card
def check_multiple(json):
    namelist = []
    if len(json['data']) == 1:
        return 0
    else:
        for x in json['data']:
            name = str(x['name'])
            namelist.append(name)
        return namelist

def multiple_results_list(json):
    bot_msg = f"Type /card and the name of one of the following:\n\n"
    multi = ''
    # iterate over each item output from check_multiple function. list() here might be redundant? print out links to scryfall for each card
    for x in list(check_multiple(json)):
        multi = search_scryfall(x)['data'][0]['scryfall_uri']
        name = search_scryfall(x)['data'][0]['name']
        bot_msg += f"<a href = \"{multi}\">{name}</a>\n"
    return bot_msg

### ALL BOT COMMANDS HAVE "_call" IN THEIR FUNCTION NAMES ###

# This bot command feeds the user a simple text message that contains
# helpful scryfall usage hints
def syntax_call(update: Updater, context: CallbackContext):
    syntax1 = """Syntax guide. Guide is of the form\n
Description - syntax:[option1/option2/etc] - (example search)\n"""

    syntax2 = """You may also use >, <, >=, <=, and != in place of :
to check for ranges rather than specifics, and you may add a minus (-)
preceding a term to negate it. (-t:legendary = cards not legendary)"""

    syntax2 = """Color - c:[w/u/b/r/g /c /m] - (/c angel c>wb)
Type - t:[merfolk/etc] - (/c name t:dragon)
Text - o:[card text] - (/c o:tap o:sacrifice)
Mana - m:[(x)/w/u/b/r/g] - (/c t:dragon m:2rr)\n
Use this same format for any of the extra commands below:"""

    syntax3 = """is:[fuzzy] / e:set / if:format / usd:price
ft:flavor border:Border
is:[foil/nonfoil/gilded/etched]
lang:language / t:dragon or t:merfolk"""

    update.message.reply_html(syntax1, False)
    update.message.reply_html(syntax2, False)
    update.message.reply_html(syntax3, False)

# This is the main command most users will ask the bot for. It finds a card and crafts a nice
# message with prices, name and an image to send back to the user in telegram.    
def c_call(update: Updater, context: CallbackContext):
    # Strip out the "/c " from the message the user sends otherwise scryfall will freak out
    card_search_input = str(update.message.text[3:])
    json = search_scryfall("!\""+card_search_input+"\"")
    # Let's see if we can get an exact match first and if so, send a message with that one.
    # This helps the bot to send the correct message if the card's name is part of some other card's name.
    # Without this section, the bot can't choose between the two cards.
    try:
        query = Card(json)
        #Python wrapper just introduces pretty function calls in place of the Telegram module chaos. Can be used interchangably
        update.message.reply_html(query.bot_msg, False)
        try:
            update.message.reply_html(query.bot_msg_back, False)
        except AttributeError:
            pass
    
    # No exact match? We get KeyError. NBD, just continue on
    except KeyError:
        json = search_scryfall(card_search_input)
        if check_multiple(json) != 0:
            bot_msg = multiple_results_list(json)
            update.message.reply_html(bot_msg, False)
    #clear bot history, otherwise mutliples in subsequent requests sum together 
            bot_msg = ''
    #if only one card great, instantiate a Card and backfill with JSON crap we stole from the internet
        else:
            query = Card(json)
            #Python wrapper just introduces pretty function calls in place of the Telegram module chaos. Can be used interchangably
            update.message.reply_html(query.bot_msg, False)
            try:
                update.message.reply_html(query.bot_msg_back, False)
            except AttributeError:
                pass

def rulings_call(update: Updater, context: CallbackContext):
    card_search_input = str(update.message.text[3:])
    json = search_scryfall("!\""+card_search_input+"\"")
    try:
        query = Card(json)
        #Python wrapper just introduces pretty function calls in place of the Telegram module chaos. Can be used interchangably
        json = requests.get(url=str(query.rulingsURI)).json()
        bot_msg = ''
        for rulings in json['data']:
            rule = str(rulings['comment'])
            bot_msg += f"{rule}\n\n"
        update.message.reply_html(bot_msg, False)
    except AttributeError:
            pass
    except KeyError:
        json = search_scryfall(card_search_input)
        if check_multiple(json) != 0:
            bot_msg = multiple_results_list(json)
            update.message.reply_html(bot_msg, False)
    #clear bot history, otherwise mutliples in subsequent requests sum together 
            bot_msg = ''
        #if only one card great, instantiate a Card and backfill with JSON crap we stole from the internet
        else:
            query = Card(json)
            json = requests.get(url=str(query.rulingsURI)).json()
            bot_msg = ''
            for rulings in json['data']:
                rule = str(rulings['comment'])
                bot_msg += f"{rule}\n\n"
            update.message.reply_html(bot_msg, False)

def random_call(update: Updater, context: CallbackContext):
#Repeate of similar stupid shit for card_call function
#Scryfall random result has diffierent JSON structure
    json = requests.get(url="https://api.scryfall.com/cards/random")
    json = json.json()
    try:
        card = Random_Card(json)
        if card.regprice == "?":
            del card
            random_call(update, context)
        elif float(card.regprice) < 0.75:
            del card
            random_call(update, context)
        else:
            pass
    except KeyError:
        del card
        random_call(update, context)
    #Python wrapper just introduces pretty function calls in place of the Telegram module chaos. Can be used interchangably
    update.message.reply_html(card.bot_msg, False)

c_image_handler = CommandHandler('c', c_call)
random_handler = CommandHandler('random', random_call)
rulings_handler = CommandHandler('r', rulings_call)
syntax_handler = CommandHandler('syntax', syntax_call)
dispatcher.add_handler(rulings_handler)
dispatcher.add_handler(c_image_handler)
dispatcher.add_handler(random_handler)
dispatcher.add_handler(syntax_handler)
updater.start_polling()