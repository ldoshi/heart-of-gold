from typing import List, Tuple

import bisect
import getch
import gtts
import mutagen
import os
import time
import vlc

title = """THE THREE LITTLE FOXS"""
author= "Isra"
story = """Once upon a time there were Three little foxes. They left their mothers house and set off to build their own houses. The first little fox decided to build a house of straw, he collected straw, and cut down trees. It took him about an hour or two to finish the house. The second little fox decided to build a house of brick, she gathered mud, shaped it, and then let it dry in the sun. It took her about nine to sixteen hours to finish it. The third little fox decided to build a fortress of stone, he got stone by going to a quarry and using a pickaxe. It took him about three to four days. In the night a big bad wolf (b,b,w) went and blew down the straw house and the first little fox ran to his sister's house, the brick house. Then the b,b,w went and blew down the brick house,the first and second little foxes ran to the FORTRESS OF STONE. Then the b,b,w came and huffed and puffed but the wolf could never get the foxes.  The end.
"""

def generate_story(directory: str, title: str, author: str, story: str, lang: str = "fr", tld: str = "fr") -> None:
    tts = gtts.gTTS(text=f"{title} by {author} {story}", tld=tld, lang=lang, slow=False)
    tts_filepath = os.path.join(directory, f"{title}_{lang}_{tld}.mp3")
    tts.save(tts_filepath)

directory = "/home/lyric/Documents/local-radio/stations/KidsStories"
generate_story(directory, title, author, story)
