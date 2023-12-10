class Character:
    def __init__(self, char):
        # name, title, image, description, rarity, availability

        # name
        self.name = char.get("name")

        # title
        if "None" in char.get("title"):
            self.title = None
        else:
            self.title = char.get("title")

        # rarity
        self.rarity = int(char.get("rarity")) - 1
        # add rarity to name
        self.name = self.name + " " + ":star:" * (self.rarity + 1)

        # image
        if "None" in char.get("img"):
            self.img = None
        else:
            self.img = char.get("img")

        # description
        if "None" in char.get("desc"):
            self.desc = None
        else:
            self.desc = char.get("desc").replace("^", "\n")

        # availability
        if "True" in char.get("avail"):
            self.avail = True
        else:
            self.avail = False
