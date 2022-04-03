from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
import textwrap
import sys
import re

if (sys.version_info[0] < 3):
    import urllib2
    import urllib
    import HTMLParser
else:
    import html
    import urllib.request
    import urllib.parse

agent = {'User-Agent': "Mozilla/5.0 (Android 9; Mobile; rv:67.0.3) Gecko/67.0.3 Firefox/67.0.3"}


def unescape(text):
    if (sys.version_info[0] < 3):
        parser = HTMLParser.HTMLParser()
    else:
        parser = html
    return (parser.unescape(text))


def search_synonym(to_search, wrap_len="80"):
    base_link = "https://www.sinonimos.com.br/%s"
    link = base_link % (to_search)
    if (sys.version_info[0] < 3):
        request = urllib2.Request(link, headers=agent)
        raw_data = urllib2.urlopen(request).read()
    else:
        request = urllib.request.Request(link, headers=agent)
        raw_data = urllib.request.urlopen(request).read()
    data = raw_data.decode("iso-8859-1")
    expr = r'((?<=(<span>))(\w|\d|\n|[A-Za-zÀ-ÖØ-öø-ÿ]| )+?(?=(<\/span>))|(?<=(class=\"sinonimo\">))(\w|\d|\n|[A-Za-zÀ-ÖØ-öø-ÿ])+?(?=(<\/a>)))'

    return re.findall(expr, data)
    
class SynonymsExtension(Extension):
    def __init__(self):
        super(SynonymsExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def create_result(self, row):
        return ExtensionResultItem(icon='images/icon.png',
                                   name=row[0],
                                   description=row[0],
                                   on_enter=CopyToClipboardAction(row[0]))


    def on_event(self, event, extension):
        query = event.get_argument() or str()
        
        if len(query.strip()) == 0:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='No input',
                                    on_enter=HideWindowAction())
            ])
        
        re_result = search_synonym(query, extension.preferences["wrap"])
            
        items = list(map(lambda x: ExtensionResultItem(icon='images/icon.png',
                                                       name=x[0],
                                                       description=x[0],
                                                       on_enter=CopyToClipboardAction(x[0])), re_result))

        return RenderResultListAction(items)

if __name__ == '__main__':
    SynonymsExtension().run()
