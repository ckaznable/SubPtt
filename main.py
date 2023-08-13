import json
import PyPtt
import os
import asyncio
import telegram

from dotenv import dotenv_values
from collections import namedtuple
from typing import List


Post = namedtuple('Post', ["id", "title", "index", "url"])

class LastStatus:
    def __init__(self):
        self.data = []

        if not os.path.isfile("last_status"):
            with open("last_status", "w") as f:
                json.dump(self.data, f)
        else:
            with open("last_status", "r") as f:
                self.data = json.load(f)

    def get_boards_list(self):
        list = []
        for board in self.data:
            list.append(board[0])
        return list

    def save(self):
        with open("last_status", "w") as f:
            json.dump(self.data, f)

    def set(self, board, value, condition):
        data = [board, value, condition]
        index = self.find(board, condition)

        if index != None:
            self.data[index] = data
        else:
            self.data.append(data)

    def get(self, i):
        if len(self.data) < i:
            return None
        return self.data[i]

    def find(self, board, condition):
        for i, data in enumerate(self.data):
            if data[0] == board and data[2] == condition:
                return i

def get_post(ptt, board, limit=10, index=0, condition=None):
    newest_index = ptt.get_newest_index(PyPtt.NewIndex.BOARD, board, search_condition=condition, search_type=PyPtt.SearchType.KEYWORD)
    if index >= newest_index:
        return []

    newest_range = limit
    newest_count = 0

    posts = []

    while newest_count < newest_range:
        cur_index = newest_index - newest_count
        newest_count += 1

        if index >= cur_index:
            break

        post = ptt.get_post(board, index=cur_index, search_condition=condition, search_type=PyPtt.SearchType.KEYWORD)

        if not post:
            continue

        if post["post_status"] != PyPtt.PostStatus.EXISTS:
            continue

        if not post["pass_format_check"]:
            continue

        if not post['content']:
            continue

        posts.append(post)

    return posts

def extract_post(post) -> Post:
    return Post(post["aid"], post["title"], post["index"], post["url"])

def extract_posts(posts) -> List[Post]:
    return list(map(extract_post, posts))

async def process(bot, chat_id, posts: List[Post]):
    if len(posts) == 0:
        return None

    batch_size = 10
    batches = [posts[i:i+batch_size] for i in range(0, len(posts), batch_size)]

    for posts in batches:
        text = ""
        for post in posts:
            text += "{}\n{}\n\n".format(post.title, post.url)

        async with bot:
            await bot.send_message(chat_id=chat_id, text=text)

def main():
    config = dotenv_values(".env")
    status = LastStatus()
    ptt = PyPtt.API()
    posts = []

    try:
        bot = telegram.Bot(config.get("tg_bot_token"))
        ptt.login(config.get("username"), config.get("pw"))

        for i, _ in enumerate(status.data):
            board, index, condition = status.get(i)
            if board == None:
                continue

            current_posts = get_post(ptt, board, index=index, condition=condition)
            print("Getting posts from {} with '{}' condition, result: {}".format(board, condition, len(current_posts)))
            posts.extend(extract_posts(current_posts))

            if len(current_posts) > 0:
                status.set(board, current_posts[0][2], condition)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        print("processing {} posts".format(len(posts)))
        task = loop.create_task(process(bot, config.get("tg_bot_chat_id"), posts))
        if not loop.is_running():
            loop.run_until_complete(task)

    finally:
        ptt.logout()
        status.save()

if __name__ == "__main__":
    main()
