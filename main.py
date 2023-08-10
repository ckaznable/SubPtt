import json
import PyPtt
import os
from dotenv import dotenv_values
from collections import namedtuple
from typing import List

Post = namedtuple('Post', ["id", "title", "index"])

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
            continue

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
    return Post(post["aid"], post["title"], post["index"])

def extract_posts(posts) -> List[Post]:
    return list(map(extract_post, posts))

def process(posts: List[Post]):
    for post in posts:
        print(post.title, post.id, post.index)

if __name__ == "__main__":
    config = dotenv_values(".env")
    status = LastStatus()
    ptt = PyPtt.API()
    posts = []

    try:
        ptt.login(config.get("username"), config.get("pw"))

        for i, data in enumerate(status.data):
            board, index, condition = status.get(i)
            if board == None:
                continue

            print("Getting posts from {} with '{}' condition".format(board, condition))
            posts.extend(extract_posts(get_post(ptt, board, index=index, condition=condition)))

            if len(posts) > 0:
                status.set(board, posts[0][2], condition)

        process(posts)

    finally:
        ptt.logout()
        status.save()
