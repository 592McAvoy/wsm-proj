import xml.sax
import mwparserfromhell 

def process_article(title, text):
    """Process a wikipedia article to extract plain text and links"""
    
    # Create a parsing object
    wikicode = mwparserfromhell.parse(text)

    strip_wiki = wikicode.strip_code().strip()
    strip_wiki = strip_wiki.replace('\r','')
    strip_wiki = strip_wiki.replace('\n','')
    # print(strip_wiki)
    

    # Extract internal wikilinks
    # wikilinks = [x.title.strip_code().strip() for x in wikicode.filter_wikilinks()]

    # Extract external links
    # exlinks = [x.url.strip_code().strip() for x in wikicode.filter_external_links()]

    # Find approximate length of article
    # text_length = len(wikicode.strip_code().strip())

    return (title, strip_wiki) #, wikilinks, exlinks)


class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ('title', 'text', 'timestamp'):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)

        if name == 'page':
            self._pages.append(process_article(self._values['title'], self._values['text']))
            # self._pages.append((self._values['title'], self._values['text']))
