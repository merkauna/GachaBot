Getting the Code & discord.py
1) download the zip file. unzip it into wherever (keep track of it!)
2) download pycharm (i have the 2022 edition - it should be free)
3) in pycharm, select file->open and navigate to the FOLDER containing bot.py, charlist.json, and Character.py
4) pycharm will probably install python for you - just follow the instructions about the python interpreter. works with at least 3.6 and 3.7
5) find the path to your shiny new python.exe. it will be the file path to your project + "\venv\Scripts\python.exe". copy the full path from the base drive; mine is something like "C:\Users[username]\PycharmProjects\DiscBot\venv\Scripts\python.exe"
6) open up the command prompt. type "cd " and then paste the path you just copied
7) type "pip install -U discord.py"

Creating the Bot:
1) Go to Discord Dev Portal (https://discord.com/developers/applications) and sign in
2) Create an App, name it whatever
3) Under the App Settings on the left, go to Bot and create a Bot.
4) Copy the token under the Bot's name into the TOKEN variable in bot.py
5) Find your Discord ID and copy it to the adminID variable in bot.py (https://www.androidpolice.com/how-to-find-discord-id/)
6) Change the "!" to a different unique bot signal in the function on_message. There's several instances to change unfortunately, Emily has this fixed in her version
7) Fill out characterlist.txt with your characters. Example Characters are given.
8) Back in the dev portal, under OAuth2->URL Generator, select "bot", then "send messages", "send messages in threads", "embed links", "attach files", and "read message history"
9) Copy the link if gives you, paste it in a new tab, and select the server you want to add the bot to. Recommend a test server first. You have to have the right permissions on the server for this.
10) You will probably need to edit launch.bat. You want the path to your python.exe, then the path to your bot.py.

Updating from an Older Version:
1) Make sure you copy over your old collections.json and charlist.json