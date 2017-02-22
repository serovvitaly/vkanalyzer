from django.core.management.base import BaseCommand
import lib.vk_api as vk
from progress.bar import Bar
from time import sleep


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
        self.bar.next()

    def handle(self, domain, *args, **options):
        self.bar = Bar('Progress:', fill='#', max=239)
        domain = domain[0]
        print('Domain: ' + domain)
        request = vk.request('wall.get')
        request.set_param('domain', domain)
        request.set_param('count', 100)
        request.set_param('offset', 0)
        request.set_param('fields', 'hidden,last_seen')
        list = vk.list(request)
        list.set_callback(self.progress)
        list.exec()
        for item in list.get_items():
            post_id = item['id']
            likes = item['likes']['count']
            reposts = item['reposts']['count']
            comments = item['comments']['count']
            #if likes < 1 & reposts < 1 & comments < 1:
                #continue
            #self.posts[post_id] = {
            #    'likes': likes,
            #    'reposts': reposts,
            #    'comments': comments,
            #}
        self.bar.finish()
        print(len(self.posts))
