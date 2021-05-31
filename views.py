from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin
from tornado.httpclient import AsyncHTTPClient
from models import Urls
import bs4
import re
import urllib.parse

TAGS = ['a', 'applet', 'area', 'base', 'blockquote', 'body', 'del', 'form', 'frame', 'head', 'iframe', 'img',
        'input', 'ins', 'link', 'object', 'q', 'script', 'audio', 'button', 'command', 'embed', 'html', 'input',
        'source', 'track', 'video', 'meta']
ATTRIBUTES = {'href', 'codebase', 'cite', 'background', 'action', 'longdesc', 'profile', 'src', 'usemap', 'classid',
              'data', 'formaction', 'icon', 'manifest', 'poster', 'srcset', 'archive'}
PATTERN = '^(https?:\/\/|\/)'


class URLParserHandler(RequestHandler, SessionMixin):
    def initialize(self):
        self.url = ''
        self.clean_url = ''
        self.url_tags = []
        self.urls_set = set()

    async def get(self):
        with self.make_session() as session:
            self.url = self.get_argument('url')
            self.clean_url = f'{urllib.parse.urlparse(self.url).scheme}://{urllib.parse.urlparse(self.url).netloc}'
            http = AsyncHTTPClient()
            response = await http.fetch(self.url)
            if response:
                soup = bs4.BeautifulSoup(response.body)
                tags = soup.find_all(TAGS)
                for tag in tags:
                    self.parse_tag(tag)
                session.add_all(self.url_tags)
                session.commit()

    def parse_tag(self, tag):
        for attribute in tag.attrs:
            if attribute in ATTRIBUTES and re.match(PATTERN, tag.attrs[attribute]):
                self.build_url_for_insertion(tag, tag.attrs, attribute)
                break

    def build_url_for_insertion(self, tag, attribute_dict, url_attribute):
        parsed_url = urllib.parse.urlparse(attribute_dict[url_attribute])
        full_url = f'{attribute_dict[url_attribute]}' if parsed_url.scheme else f'{self.clean_url}{parsed_url.path}'
        get_tag = self.build_tag_retrieval(attribute_dict, tag.name)
        if full_url not in self.urls_set:
            self.urls_set.add(full_url)
            self.url_tags.append(Urls(from_domain=self.url,
                                      full_url=full_url,
                                      get_tag=get_tag))

    @staticmethod
    def build_tag_retrieval(attribute_dict, tag_name):
        if 'id' in attribute_dict:
            return f'#{attribute_dict["id"]}'
        tag_retrieval = f'{tag_name}'
        for attribute in attribute_dict:
            tag_retrieval += f'[{attribute}="{attribute_dict[attribute]}"]'
        return tag_retrieval
