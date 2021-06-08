from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin, as_future
from tornado.httpclient import AsyncHTTPClient
from models import Urls
import bs4
import re
from urllib.parse import urlparse
import validators

TAGS = ['a', 'applet', 'area', 'base', 'blockquote', 'body', 'del', 'form', 'frame', 'head', 'iframe', 'img',
        'input', 'ins', 'link', 'object', 'q', 'script', 'audio', 'button', 'command', 'embed', 'html', 'input',
        'source', 'track', 'video', 'meta']
ATTRIBUTES = {'href', 'codebase', 'cite', 'background', 'action', 'longdesc', 'profile', 'src', 'usemap', 'classid',
              'data', 'formaction', 'icon', 'manifest', 'poster', 'srcset', 'archive'}
PATTERN = '^(https?:\/\/|\/)'


def validate_url(url):
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        raise ValueError('The specified URL is not valid, please enter a valid URL including scheme')


class URLParserHandler(RequestHandler, SessionMixin):
    def initialize(self):
        self.url = ''
        self.clean_url = ''
        self.url_tags = []
        self.urls_set = set()

    async def get(self):
        with self.make_session() as session:
            self.url = self.get_argument('url')
            validate_url(self.url)
            self.clean_url = f'{urlparse(self.url).scheme}://{urlparse(self.url).netloc}'
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
        parsed_url = urlparse(attribute_dict[url_attribute])
        if parsed_url.scheme:
            full_url = f'{self.clean_url}{parsed_url.path}'
        else:
            full_url = attribute_dict[url_attribute].split('?')[0]
        get_tag = self.build_tag_retrieval(attribute_dict, tag.name)
        if full_url not in self.urls_set:
            self.urls_set.add(full_url)
            self.url_tags.append(Urls(from_domain=self.url,
                                      complete_url=full_url,
                                      get_tag=get_tag))

    @staticmethod
    def build_tag_retrieval(attribute_dict, tag_name):
        if 'id' in attribute_dict:
            return f'#{attribute_dict["id"]}'
        tag_retrieval = f'{tag_name}'
        for attribute in attribute_dict:
            tag_retrieval += f'[{attribute}="{attribute_dict[attribute]}"]'
        return tag_retrieval


class ExtractElement(RequestHandler, SessionMixin):
    def initialize(self):
        self.url = ''
        self.uri = ''

    async def get(self):
        with self.make_session() as session:
            params = self.request.arguments
            if 'url' not in params or 'uri' not in params:
                raise ValueError(
                    'Please specify the domain you want to extract the URI from as well as the complete URI')
            self.url = params['url'][0].decode('utf-8')
            self.uri = params['uri'][0].decode('utf-8')
            validate_url(self.url)
            validate_url(self.uri)
            get_tag = session.query(Urls).filter(Urls.from_domain == self.url).filter(
                Urls.complete_url == self.uri).first()
            if get_tag:
                http = AsyncHTTPClient()
                response = await http.fetch(self.url)
                if response:
                    soup = bs4.BeautifulSoup(response.body)
                    return str(soup.find(get_tag))
