from django.core.management.base import BaseCommand
import lib.vk_api as vk
from progress.bar import Bar
from time import sleep
import json
import math
from pymongo import MongoClient
import pymorphy2


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    posts = {}

    def daemon(self):
        from time import sleep
        from daemonize import Daemonize

        pid = "/tmp/test.pid"

        def do_process():
            user_ids = ['2']
            user_ids.append('1')
            request = vk.request('users.get')
            request.set_param('user_ids', ','.join(user_ids))
            request.set_param('fields', 'hidden,last_seen')
            request.exec()
            print(request.get_response().get_response())

        def main():
            while True:
                do_process()
                # sleep(0.3)

        # daemon = Daemonize(app="test_app", pid=pid, action=main)
        # daemon.start()

        do_process()

    def add_arguments(self, parser):
        parser.add_argument('domain', nargs='+', type=str)

    def progress(self, items):
        sleep(0.3)

    def __init__(self):
        super().__init__()
        client = MongoClient()
        self.db = client.vk_group

    def get_items(self, domain):
        collection = self.db[domain]
        items_cache = collection.find(no_cursor_timeout=True)
        if items_cache.count():
            return items_cache
        request = vk.request('wall.get')
        request.set_param('domain', domain)
        request.set_param('count', 100)
        request.set_param('offset', 0)
        request.set_param('fields', 'hidden,last_seen')
        list = vk.list(request)
        list.set_callback(self.progress)
        list.exec()
        items = list.get_items()
        collection.insert_many(items)
        return items

    def get_likes(self, owner_id, post_id):
        request = vk.request('likes.getList')
        request.set_param('type', 'post')
        request.set_param('owner_id', owner_id)
        request.set_param('item_id', post_id)
        request.set_param('count', 100)
        list = vk.list(request)
        list.set_callback(self.progress)
        list.exec()
        return list.items

    def get_reposts(self, owner_id, post_id):
        request = vk.request('wall.getReposts')
        request.set_param('owner_id', str(owner_id))
        request.set_param('post_id', post_id)
        request.set_param('count', 1000)
        request.exec()
        if request.get_response().is_error():
            collection = self.db['log']
            collection.insert_one({
                'type': 'error',
                'error': request.get_response().get_error(),
            })
            return None
        return request.get_response().get_response()

    def get_comments(self, owner_id, post_id):
        request = vk.request('wall.getComments')
        request.set_param('owner_id', str(owner_id))
        request.set_param('post_id', post_id)
        request.set_param('count', 100)
        request.exec()
        return request.get_response().get_response()

    def bring_likes(self, item):
        if int(item['likes']['count']) > 0:
            likes = self.get_likes(item['owner_id'], item['id'])
            if len(likes) > 0:
                collection = self.db['users_activity']
                for like_user_id in likes:
                    collection.insert_one({
                        'owner_id': int(item['owner_id']),
                        'post_id': int(item['id']),
                        'user_id': int(like_user_id),
                        'type': 'like',
                    })

    def bring_reposts(self, item):
        if int(item['reposts']['count']) > 0:
            reposts = self.get_reposts(item['owner_id'], item['id'])
            if (reposts is not None) & (len(reposts['profiles']) > 0):
                collection = self.db['users_activity']
                for profile in reposts['profiles']:
                    collection.insert_one({
                        'owner_id': int(item['owner_id']),
                        'post_id': int(item['id']),
                        'user_id': int(profile['id']),
                        'type': 'repost',
                    })

    def bring_comments(self, item):
        if int(item['comments']['count']) > 0:
            comments = self.get_comments(item['owner_id'], item['id'])
            if comments['count'] > 0:
                collection = self.db['users_activity']
                for comment in comments['items']:
                    collection.insert_one({
                        'owner_id': int(item['owner_id']),
                        'post_id': int(item['id']),
                        'user_id': int(comment['from_id']),
                        'type': 'comment',
                    })

    def bring_users_activity(self, domain):
        domain = domain[0]
        print('Domain: ' + domain)
        items = self.get_items(domain)
        self.bar = Bar('Progress:', fill='#', max=items.count())
        for item in items:
            self.bar.next()
            sleep(0.3)
            # self.bring_likes(item)
            self.bring_reposts(item)
            # self.bring_comments(item)
        self.bar.finish()

    def bring_users(self):
        collection = self.db['users_activity']
        users_ids_list = collection.distinct('user_id')
        collection = self.db['users_last_seen']
        part_count = math.ceil(len(users_ids_list)/1000)
        bar = Bar('Progress:', fill='#', max=part_count)
        for part in range(0, part_count):
            users_ids = users_ids_list[part: part+1000]
            users_ids = ','.join(str(v) for v in users_ids)
            request = vk.request('users.get')
            request.set_param('user_ids', users_ids)
            request.set_param('fields', 'last_seen,verified,sex,bdate,city,country')
            request.exec()
            response = request.get_response()
            if response.is_error():
                continue
            collection.insert_many(response.get_response())
            bar.next()
        bar.finish()


    def morph_analyzer(self):
        import nltk
        collection_from = self.db['zeus_group']
        collection_to = self.db['morph_analyzer']
        for post in collection_from.find({'reposts.count': {'$gt':0}, 'text': {'$ne': ''}}):
            tokens = nltk.word_tokenize(post['text'])
            collection_to.insert_one({
                'post_id': int(post['id']),
                'tokens': tokens,
            })
            return


    def handle(self, domain, *args, **options):
        #self.bring_users_activity(domain)
        self.morph_analyzer()
