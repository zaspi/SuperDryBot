# SuperDryBot
Super Dry Bot is a hackjob python script that serves up Scryfall results for Magic: The Gathering cards in a lovely telegram bot.

![image](https://user-images.githubusercontent.com/103873632/170420979-29859034-ace7-4579-99f0-7e96c98cbd2b.png)

This code sucks. It does work though. Just plug in your Telegram bot token, stick the bot in your group chat (or message it directly) and away you go! I don't expect anyone to run this code outright. More to use it as a jumping-off point.

![image](https://user-images.githubusercontent.com/103873632/170423564-ba460e17-055c-48ab-8da0-7af63fb2018d.png)

It supports most regular magic cards and most dual faced cards and multi-modal cards. I say most because given how many cards there are, I'm sure there will be some edge cases I missed. Trigger commands are:

/c - Search Scryfall, return a nicely formatted result. Supports standard Scryfall syntax. [/c akroma's will], [/c is:shockland c:red], etc

/random - Return random result from Scryfall

/syntax - Quick reference to the most used Scryfall syntaxes

/rulings - Returns a Scryfall result but only prints rulings. Faster than googling it. Never lose a game to a drunk bar patron again!

Poop emoji denotes regular card price. Sparkly emoji denotes foil prices. Both in USD, though this can be changed easily.

The code comments are all over the place, more a place for scratching out my thoughts than they are actual guidance.
I would not heed them if I were you. This bot was built around python-telegram-bot and will likely require its installation for use.
This is a repository for a personal project; I hope you don't expect much out of it. 

MIT Licensed.
