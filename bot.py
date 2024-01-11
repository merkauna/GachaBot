# Work with Python 3.10-3.12
# GACHA BOT VERSION: 1.1.4
import discord
import time
import json
import shutil
from Character import Character
from random import randint
from os.path import exists

TOKEN = ''

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)
UPDATING = False
adminID = 0

characters = []
availchars = []
global user_dict
global user_times
global rares
global rates
global gacha_lock
user_times = {}
rares = [[], [], [], [], [], []]
gacha_lock = False
# Chances of pulling: rates[0] should always be 100.
# Each rate is then the difference between that rate and the next.
# e.g. 1-star rates: 100-50 = 50%... 2-star rates: 50-25 = 25%...
# 6-star rates are from rates[5] to 0.
rates = [100, 55, 30, 15, 6, 2]

signaller = "R!"


def build_char_list():
    global rares
    # Reset images, character list, and rares before rebuilding
    characters.clear()
    availchars.clear()
    rares = [[], [], [], [], [], []]

    # Build images and character list
    with open("charlist.json") as chars_file:
        jchars = json.load(chars_file)
        for charline in jchars:
            newchar = Character(charline)
            characters.append(newchar)

    # Build available character list for rolling
    for char in characters:
        if char.avail:
            availchars.append(char)
    build_rares()


def save_collections():
    # Save a current collection to the json file.
    jdict = json.dumps(user_dict)
    fcollect = open("collections.json", "w")
    fcollect.write(jdict)
    fcollect.close()


def load_collections():
    # Load all collections from the json file.
    global user_dict
    with open("collections.json") as json_file:
        jdict = json.load(json_file)
        user_dict = jdict.copy()
        # Sort the lists
        for key in user_dict:
            sort_list_by_rarity(user_dict[key])


def build_rares():
    newchars = availchars.copy()
    for char in newchars[::-1]:
        if char.rarity == 5:
            rares[5].append(char)
            newchars.remove(char)
        elif char.rarity == 4:
            rares[4].append(char)
            newchars.remove(char)
        elif char.rarity == 3:
            rares[3].append(char)
            newchars.remove(char)
        elif char.rarity == 2:
            rares[2].append(char)
            newchars.remove(char)
        elif char.rarity == 1:
            rares[1].append(char)
            newchars.remove(char)
        elif char.rarity == 0:
            rares[0].append(char)
            newchars.remove(char)


async def rares_list(message):
    length = len(message.content)
    cmd_len = len(signaller + "rares")
    if length != (cmd_len + 2) or not message.content[(cmd_len + 1)].isnumeric():
        await message.channel.send("Type a number 1-5 after !rares, such as '!rares 4' to view 4-stars.")
        return
    num = int(message.content[length-1])
    if num > 5 or num < 1:
        await message.channel.send("Type a number 1-5 after !rares, such as '!rares 4' to view 4-stars.")
        return

    return_list = []
    for char in rares[num-1]:
        return_list.append(char.name)

    msg = ("{} star characters: {}".format(num, return_list).format(message))
    await message.channel.send(msg)


async def print_rates(message):
    r = [0, 0, 0, 0, 0, 0]
    for i in range(0, len(rates)-1):
        r[i] = (rates[i] - rates[i+1])
    r[len(rates)-1] = rates[len(rates)-1]

    msg = ":star::star::star::star::star: Rates: {:.2f}%\n:star::star::star::star: Rates: {:.2f}%\n:star::star::star:" \
          " Rates: {:.2f}%\n:star::star: Rates: {:.2f}%\n:star: Rates: {:.2f}%".format(r[4], r[3], r[2], r[1], r[0]+r[5])
    await message.channel.send(msg)


async def grant_roll(message):
    mentionlist = message.mentions
    if len(mentionlist) == 0:
        await message.channel.send("Mention a user to grant a roll to.")
        return

    grantee = mentionlist[0].id
    if grantee in user_times:
        user_times[grantee] = user_times[grantee] - 3600
        await message.channel.send("Roll granted.")
    else:
        await message.channel.send("That player can roll.")
    return


def chunks(charlist, n):
    n = max(1, n)
    return (charlist[i:i+n] for i in range(0, len(charlist), n))


async def show_character_list(message):
    user_id = str(message.author.id)
    if user_id in user_dict:
        sortedlist = sort_list_by_rarity(squish_dupes((user_dict[user_id])))
        if len(sortedlist) > 30:
            await message.channel.send("Character list too long, sending it to you in a DM!")
            partitions = chunks(sortedlist, 30)
            await message.author.create_dm()
            for part in partitions:
                embed = build_charlist_embed(message, part)
                await message.author.dm_channel.send(embed=embed)
        else:
            embed = build_charlist_embed(message, sortedlist)
            embed.set_author(name = message.author)
            await message.channel.send(embed=embed)
    else:
        await message.channel.send("You have no characters yet!")


def build_charlist_embed(message, sortedlist):
    new_embed = discord.Embed(title="Character List")
    new_embed.set_author(name = message.author)
    new_list = ""
    for char in sortedlist:
        new_list = (new_list + char + "\n")
    new_list = new_list[:-1]
    new_embed.description = new_list
    return new_embed

def squish_dupes(charlist):
    newlist = []
    for char in charlist:
        num_of_dupes = charlist.count(char)
        if num_of_dupes > 1:
            char = "**(" + str(num_of_dupes) + ")** " + char
            newlist.append(char)
        else:
            newlist.append(char)
    newlist = sort_list_by_rarity(list(set(newlist)))
    return newlist

def sort_list_by_rarity(charlist):
    # Sorts a list of characters names by rarity then alphabetical
    newlists = [[], [], [], [], [], []]
    combined = []
    for char in charlist:
        if ":star::star::star::star::star::star:" in char:
            newlists[5].append(char)
        elif ":star::star::star::star::star:" in char:
            newlists[4].append(char)
        elif ":star::star::star::star:" in char:
            newlists[3].append(char)
        elif ":star::star::star:" in char:
            newlists[2].append(char)
        elif ":star::star:" in char:
            newlists[1].append(char)
        elif ":star:" in char:
            newlists[0].append(char)
    for listitem in newlists[::-1]:
        listitem.sort()
        for char in listitem:
            combined.append(char)
    return combined


async def clear_character_list(message):
    user_id = str(message.author.id)
    # The user has a collection to clear
    if user_id in user_dict:
        user_dict.pop(user_id)
        save_collections()
        msg = "{0.author.mention}, your character collection has been cleared.".format(message)
    # The user has no collection to clear
    else:
        msg = "{0.author.mention}, you have no character collection to clear.".format(message)

    await message.channel.send(msg)


async def view_character(message):
    contents = message.content
    userid = str(message.author.id)
    cmd_len = len(signaller + "view")
    # Return if no name was entered after !view
    if len(contents) <= cmd_len:
        msg = "Type a character's name after {1}view. Names are not case sensitive. Add their star count to" \
              "view a character of a specific rarity (e.g. {1}view Character ***). NOTE: if using stars," \
              "character name must match exactly.".format(message, signaller)
        await message.channel.send(msg)
        return

    search_string = contents[cmd_len::].strip().lower()
    count = 0
    for char in characters:
        char_name = char.name.lower()
        star_specified = False

        if "*" in search_string:
            char_name = char_name.replace(":star:", "*")
            star_specified = True
        else:
            char_name = char_name.replace(":star:", "").strip()

        search_result = False
        if star_specified:
            search_result = search_string == char_name
        else:
            search_result = search_string in char_name

        # Skip hidden 6+ star characters
        if char.rarity >= 5:
            if search_string == char_name and userid in user_dict and char.name in user_dict[userid]:
                await message.channel.send(embed=build_embed(char))
                return
            elif search_string == char_name and int(userid) == adminID:
                await message.channel.send(embed=build_embed(char))
                return
            else:
                pass
        elif search_result and char.avail is True:
            await message.channel.send(embed=build_embed(char))
            return
        count = count + 1

    # No matching characters were found
    msg = "Sorry, that does not match any characters. Check your capitalization!".format(message)
    await message.channel.send(msg)
    return


def perform_roll():
    rarity = 0
    rarity_pick = randint(0, 100)
    if rates[0] >= rarity_pick > rates[1]:
        rarity = 0
    elif rates[1] >= rarity_pick > rates[2]:
        rarity = 1
    elif rates[2] >= rarity_pick > rates[3]:
        rarity = 2
    elif rates[3] >= rarity_pick > rates[4]:
        rarity = 3
    elif rates[4] >= rarity_pick > rates[5]:
        rarity = 4
    elif rates[5] >= rarity_pick > 0:
        rarity = 5

    # Randomly acquire character
    value = randint(0, len(rares[rarity]) - 1)
    pullchar = rares[rarity][value]
    return pullchar


def add_to_collection(message, char_to_add):
    userid = str(message.author.id)
    if userid in user_dict:
        char_list = user_dict[userid]
        char_list.append(char_to_add.name)
        user_dict[userid] = sort_list_by_rarity(char_list)
    else:
        char_list = [char_to_add.name]
        user_dict[userid] = sort_list_by_rarity(char_list)
    return


async def gacha(message):
    # Check if the user can roll yet
    global user_times
    global gacha_lock
    if not check_time(message):
        wait_time = (user_times[message.author.id] - time.time()) / 60
        await message.channel.send("Please wait {:3.1f} minutes.".format(wait_time))
        return
    if gacha_lock == True:
        await message.channel.send("Please wait, I'm really stressed right now :(")
        return

    gacha_lock = True
    global user_dict
    pulled_character = perform_roll()

    # Tell what character was rolled, embed image if there is one
    msg = "You got a character!"
    await message.channel.send(msg, embed=build_embed(pulled_character))

    # Add the character to the player's collection and save it
    add_to_collection(message, pulled_character)
    save_collections()

    # Give user a new wait timer
    user_times[message.author.id] = time.time() + 3600
    gacha_lock = False


def build_embed(character):
    embed = discord.Embed(title=character.name)
    embed.colour = get_rarity_color(character)
    if character.desc is not None:
        embed.description = character.desc
    if character.img is not None:
        embed.set_image(url=character.img)
    if character.title is not None:
        embed.set_author(name=character.title)
    return embed


def get_rarity_color(character):
    color = discord.Colour.light_gray()
    match character.rarity:
        case 1:
            color = discord.Colour.green()
        case 2:
            color = discord.Colour.blue()
        case 3:
            color = discord.Colour.purple()
        case 4:
            color = discord.Colour.gold()
        case 5:
            color = discord.Colour.dark_red()
    return color


async def new_sacrifice(message):
    # Check if user has a character to sacrifice
    userid = str(message.author.id)
    if userid not in user_dict:
        await message.channel.send("You need a character to perform a sacrifice.")
        return
    else:
        charlist = user_dict[userid]

    # Get the sacrifice name
    sac_name = message.content
    cmd_length = len(signaller + "sacrifice ")

    if len(sac_name) < cmd_length:
        sac_cmd = signaller + "sacrifice"
        char_cmd = signaller + "charlist"
        await message.channel.send("Hi {0.author.mention}! Sacrificing a character will remove it "
                                   "from your collection, but will reduce the time until your next roll "
                                   "depending on the character's rarity. 6-Stars will reset your timer, "
                                   "5-stars will reduce it by 50 minutes, 4-stars 40 minutes, etc."
                                   "\nType {1} to view your collection.\nType {2} "
                                   "[Character Name] to sacrifice a specific character.".format(message, sac_cmd, char_cmd))
        return
    else:
        sac_name = sac_name[cmd_length::]

    # Remove the character if it is in their collection
    removed = None
    for char in charlist:
        cmpname = char.replace(":star:", "").strip()
        sac_lower = sac_name.lower()
        cmpname = cmpname.lower()
        if sac_lower == cmpname:
            removed = char
            charlist.remove(char)
            break
    if removed is None:
        await message.channel.send("That character was not found. Check your capitalization and make sure"
                                   " you're typing out the character's full name (without the stars).")
        return

    # Chop off time depending on rarity
    userid = int(userid)
    time_to_remove = 0
    if userid in user_times:
        if ":star::star::star::star::star::star:" in removed:
            time_to_remove = 3600
        elif ":star::star::star::star::star:" in removed:
            time_to_remove = 3000
        elif ":star::star::star::star:" in removed:
            time_to_remove = 2400
        elif ":star::star::star:" in removed:
            time_to_remove = 1800
        elif ":star::star:" in removed:
            time_to_remove = 1200
        elif ":star:" in removed:
            time_to_remove = 600
        user_times[userid] = user_times[userid] - time_to_remove
    save_collections()
    msg = "{} sacrificed. {} minutes off your roll timer!".format(removed, time_to_remove / 60)
    await message.channel.send(msg)
    return


def check_time(message):
    global user_times
    # Allow admin to bypass time restriction
    if message.author.id == adminID:
        return True

    current = time.time()
    if message.author.id in user_times:
        if current >= user_times[message.author.id]:
            return True
        else:
            return False
    else:
        return True


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    # When bot starts, form the character lists and load collections.
    build_char_list()
    load_collections()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # nothing happens if bot is updating
    if message.content.startswith(signaller) and UPDATING and message.author.id != adminID:
        await message.channel.send("Bot is currently updating!")
        return

    # ---------------
    # Parse commands
    # ---------------
    # !help
    if message.content == signaller + 'help':
        msg = "Hello {0.author.mention}, here are the commands you can use:\n" \
              "{1}help - Shows this help page and the commands\n" \
              "{1}gacha - Roll a random character and add it to your collection\n" \
              "{1}charlist - Check your collection of characters\n" \
              "{1}sacrifice - Reduce your roll timer by sacrificing characters from your collection\n" \
              "{1}rares [number] - Check the characters available at a specific rarity\n" \
              "{1}rates - Check the percentage rates for rolling each rarity of character\n" \
              "{1}clear-collection - Clear your collection of characters\n" \
              "{1}view [Character Name] - View a character's image and description".format(message, signaller)
        await message.channel.send(msg)
        return
    # !gacha
    if message.content == signaller + 'gacha':
        await gacha(message)
    # !charlist
    if message.content == signaller + 'charlist':
        await show_character_list(message)
    # !clear-collection
    if message.content == signaller + 'clear-collection':
        await clear_character_list(message)
    # !view [character]
    if message.content.startswith(signaller + "view"):
        await view_character(message)
    # !rares [rarity]
    if message.content.startswith(signaller + "rares"):
        await rares_list(message)
    # !rates
    if message.content == signaller + "rates":
        await print_rates(message)
    # !sacrifice
    if message.content.startswith(signaller + "sacrifice"):
        await new_sacrifice(message)

    # ---Administrative commands---
    admin_c = [signaller + "rebuild", signaller + "grantroll", signaller + "shutdown"]
    for msg in admin_c:
        if message.content.startswith(msg) and message.author.id != adminID:
            await message.channel.send("Invalid or admin-only command.")

    # !rebuild
    if message.content == signaller + 'rebuild' and message.author.id == adminID:
        build_char_list()
        load_collections()
        await message.channel.send("Character list and collections have been rebuilt.")
    # !grantroll
    if message.content.startswith(signaller + "grantroll") and message.author.id == adminID:
        await grant_roll(message)
    # !shutdown
    if message.content.startswith(signaller + "shutdown") and message.author.id == adminID:
        await message.channel.send("Bot is shutting down.")
        await client.close()


if exists("Configuration\\UserSettings.json"):
    with open("Configuration\\UserSettings.json") as json_file:
        user_set = json.load(json_file)
        # Technically only checks for default values
        # TODO: Check for invalid values as a whole
        if user_set[0].get("adminID") == "Default" or user_set[0].get("Token") == "Default":
            print("Error: Token or AdminID not set! Please place these values in "
                  "Configuration\\UserSettings.json and run again.")
            exit()
        adminID = int(user_set[0].get("adminID"))
        TOKEN = user_set[0].get("Token")
else:
    if exists("Configuration\\UserDefaults.json"):
        shutil.copy("Configuration\\UserDefaults.json", "Configuration\\UserSettings.json")
        print("Error: Token or AdminID not set! Please place these values in "
              "Configuration\\UserSettings.json and run again.")
    else:
        print("Error: Configuration\\UserSettings and Configuration\\UserDefaults both missing. "
              "Please contact support.")
    exit()


client.run(TOKEN)
