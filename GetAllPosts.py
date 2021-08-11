from telethon import TelegramClient, events, sync
from telethon.tl.types import InputMessagesFilterPhotos
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (PeerChannel)
import psycopg2
import re
import json

api_id = ""
api_hash = ""

client = TelegramClient('session_name', api_id, api_hash)
client.start()
channel_username = ''

history = client(GetHistoryRequest(
    peer=channel_username,
    offset_id=0,
    offset_date=None,
    add_offset=0,
    limit=20,
    max_id=0,
    min_id=0,
    hash=0
))

conn = psycopg2.connect(dbname='MyDB', user='postgres', 
                            password='pas3ord', host='localhost')

def insert_into_db(message, name, id_tg):
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM posts WHERE tg_id = %s", [id_tg])
        new = cursor.fetchone()
        if new:
            return False
        cursor.execute("INSERT INTO posts(id, description, name, tg_id) values (DEFAULT, %s, %s, %s) RETURNING id", (message, name, id_tg))
        id_of_new_row = cursor.fetchone()[0]

        conn.commit()

        cursor.close()

        return id_of_new_row
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        

def insert_into_db_photos(id_of_post, path_of_photo):
    try:
        cursor = conn.cursor()

        cursor.execute("INSERT INTO photos(id, post_id, path) values (DEFAULT, %s, %s) RETURNING id", (id_of_post, path_of_photo))
        id_s = cursor.fetchone()[0]

        conn.commit()

        print(id_s)

        cursor.close()

        return id_s
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def check_first_last_middle_name(string):
    string = string.capitalize()
    try:
        cursor = conn.cursor()

        looking_for = r"[А-Я]"
        if re.findall(looking_for, string) and (string[-3:] == ("вна") or string[-3:] == ("вич")):
            variable = (string, )
            return variable

        cursor.execute("SELECT name as t FROM russian_names WHERE name LIKE '%s' UNION SELECT surname as t FROM russian_surnames WHERE surname LIKE '%s'" % (string, string))
        variable = cursor.fetchone()
        if variable:
            return variable

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        cursor.close()


def split_message(message):
    splitted = message.message.split()
    name = ""

    if len(splitted) > 3:
        for i in splitted[:8]:
            i = re.sub(r'[^\w\s]', '', i) 
            const = check_first_last_middle_name(i)
            if const and len(const[0]) > 3:
                name += ''.join(const) + " "
            if len(name.split()) == 3:
                return name

        if len(name.split()) == 1 or len(name.split()) == 0:
            name = None
            return name


def save(path, post, id, message):
    if message.grouped_id:
        client.download_media(message=message, file="{}_{}".format(id, message.id))
    else:
        client.download_media(message=message, file="{}".format(id))
    insert_into_db_photos(post, photo_path)

common_id = 0
messages = history.messages
for message in messages:
    print(message)
    if message.media == None:
        continue

    if message.grouped_id and message.message != "":
        common_id = message.id
        name = split_message(message)
        if name:
            post = insert_into_db(message.message, name, common_id)

            if post:
                photo_path= "{}".format(common_id)
                save(photo_path, post, common_id, message)
                continue

    if message.grouped_id and message.message == "":
        photo_path= "{}".format(common_id, message.grouped_id)
        save(photo_path, post, common_id, message)
        continue

    name = split_message(message)

    if name:
        post = insert_into_db(message.message, name, message.id)

        if post:
            photo_path= "{}".format(message.id)
            save(photo_path, post, message.id, message)

conn.close()