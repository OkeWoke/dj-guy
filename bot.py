import discord
import logging
import datetime
import aiosqlite
import sqlite3
from yt_client import youtube_client

logging.basicConfig(level=logging.INFO)

MUSIC_CHANNEL_ID = 877491388697178112
YT_PLAYLIST_ID = "PLcBws2O16vK4HlwjfMdzQBHlRntASuEXw"

def create_db():
    db_con = sqlite3.connect('app.db')
    cur = db_con.cursor()
    cur.execute('''CREATE TABLE music
                    (MusicID INTEGER PRIMARY KEY,
                     datetimeAdded DATETIME,
                     title VARCHAR(300),
                     url VARCHAR(300)
                    )''')
    cur.close()

async def db_insert(datetime, title, url):
    db_con = await aiosqlite.connect('app.db')
    await db_con.execute("INSERT INTO music (datetimeAdded, title, url) VALUES (?, ?, ?)", (datetime, title, url))
    await db_con.commit()
    await db_con.close()
    logging.info("Inserted into DB")
    
async def db_ifExists(url):
    db_con = await aiosqlite.connect('app.db')
    cursor = await db_con.execute("SELECT * FROM music WHERE url = ?", (url,))
    row = await cursor.fetchone()

    if row is None:
        return False
    return True

class AndyBot(discord.Client):

    async def on_ready(self):
        self.yt_client = youtube_client()
        print("Logged on as {0}".format(self.user))

    async def on_message(self, message):
        if message.channel.id == MUSIC_CHANNEL_ID:
            result, ids = youtube_client.get_video_ids(message.content)
            if result:
                for id in ids:
                    url = "https://youtu.be/"+id
                    exists = await db_ifExists(url) # Check if we already have this video in the database...
                    if not exists:
                        title = self.yt_client.add_video_to_playlist(YT_PLAYLIST_ID, id)
                        await db_insert(datetime.datetime.now(), title, url)


if __name__ == "__main__": 
    secret_file = open("secrets.txt", "r")
    token = secret_file.readline()
    secret_file.close()

    intents = discord.Intents(guilds=True, messages=True)
    client = AndyBot(intents=intents)
    client.run(token)