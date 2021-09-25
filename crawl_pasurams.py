from enum import Enum
import html2text
import re
import scrapy

import sys


TVM_PAGE_CHECK = '//div[contains(@class, "category-line")]/a[contains(text(), "thiruvAimozhi")]'
ENTRY_TITLE = '//h2[contains(@class, "entry-title")]'
ENTRY_CONTENT = '//div[contains(@class, "entry-content")]'
LINKS = '//div[contains(@class, "entry-content")]//li/a[contains(@href, "divyaprabandham.koyil.org")]'

COMMENTATORS = {
    '6000': 'thirukkurukaippirAn piLLAn',
    '9000': 'nanjIyar',
    '12000' : 'vAdhi kEsari azhagiya maNavALa jIyar',
    '24000' : 'periyavAchchAn piLLai',
    '36000' : 'nampiLLai'
}

INTRO_HEADING_COMMENTATOR_TEMPLATE = '//strong[contains(., "Highlights from %s‘s introduction")]'
PASURAM_HEADING = '//h3[(. = "pAsuram")]/*'
AUDIO_HEADING = '//h3/a[text() = "Listen"]'
PADA_URAI_HEADING = '//h3[starts-with(., "Word-by-Word meanings")]/*'
TRANSLATION_HEADING = '//h3[starts-with(., "Simple trans")]/*'
COMMENTARIES_HEADING = '//h3[starts-with(., "vyAkyAnams (comm")]/*'
HEADING_COMMENTATOR_TEMPLATE = '//strong[contains(., "Highlights from %s‘s vyAkyAnam")]'
PASURAM_PAGE_END = '//p[(. = "In the next article we will enjoy the next pAsuram.")]'


def create_xpaths():
    this_module = sys.modules[__name__]

    for c in ['6000', '9000', '12000', '24000', '36000']:
        commentator_name = COMMENTATORS[c]
        # Create global variable, i.e., INTRO_HEADING_6000 = <appropriate xpath>
        setattr(this_module, 'INTRO_HEADING_' + c, INTRO_HEADING_COMMENTATOR_TEMPLATE % commentator_name)
        setattr(this_module, 'HEADING_' + c, HEADING_COMMENTATOR_TEMPLATE % commentator_name)

create_xpaths()

PASURAM_PAGE = [
    ['marker', INTRO_HEADING_6000 ],
    ['content', 'intro_6000' ],
    ['marker', INTRO_HEADING_9000 ],
    ['content', 'intro_9000' ],
    ['marker', INTRO_HEADING_12000 ],
    ['content', 'intro_12000' ],
    ['marker', INTRO_HEADING_24000 ],
    ['content', 'intro_24000' ],
    ['marker', INTRO_HEADING_36000 ],
    ['content', 'intro_36000' ],
    ['marker', PASURAM_HEADING ],
    ['content', 'pasuram'], # todo: split into roman and non-roman if exists
    #['content', 'pasuram_roman'],
    ['marker', AUDIO_HEADING, 'optional'],
    ['marker', PADA_URAI_HEADING ],
    ['content', 'pada_urai'],
    ['marker', TRANSLATION_HEADING ], # //h3[starts-with(., "vyAk")]/preceding::node()
#    ['content', 'translation'],
    ['marker', COMMENTARIES_HEADING ],
    ['marker', HEADING_6000 ],
    ['content', '6000'],
    ['marker', HEADING_9000 ],
    ['content', '9000'],
    ['marker', HEADING_24000 ],
    ['content', '24000'],
    ['marker', HEADING_36000 ],
#    ['content', '36000'],
#    ['marker', PASURAM_PAGE_END ] # //p[starts-with(., "In the next")]/preceding::node()
]

    
def xpath_from_until(from_expr, until_expr):
    # Kayessian formula.
    ns1 = from_expr + '/../following-sibling::node()'
    ns2 = until_expr + '/../preceding-sibling::node()'
    return '%s[count(. | %s) = count(%s)]' % (ns1, ns2, ns2)


class PageType(Enum):
    PASURAM = 1
    PATHIKAM = 2
    PATTHU = 3
    
def pathikam_number(title):
    pattern = re.compile('\s([0-9]+\\.[0-9]+)\s')
    try:
        return pattern.search(title).group(1) + '.0'
    except AttributeError or IndexError:
        return None


def patthu_number(title):
    pattern = re.compile('([0-9]+)th centum')
    try:
        return pattern.search(title).group(1) + '.0.0'
    except AttributeError or IndexError:
        return None

def _page_type_and_number(title):
    number = _pasuram_number(title)
    if number:
        return PageType.PASURAM, number
    
    number = pathikam_number(title)
    if number:
        return PageType.PATHIKAM, number
    
    if 'centum' in title:
        return PageType.PATTHU, patthu_number(title)

    raise ValueError('Can\'t decipher type of: ' + title)


def get_to_expr(content, i):
    to_expr = PASURAM_PAGE[i + 1]
    assert to_expr[0] == 'marker'
    if len(to_expr) == 3 and to_expr[2] == 'optional':
        if not content.xpath(to_expr[1]):
            to_expr = PASURAM_PAGE[i + 2]
            assert to_expr[0] == 'marker'
    return to_expr

def process_pasuram_page(content):
    #print(content.get())
    converter = html2text.HTML2Text()
    converter.ignore_links = True

    title = converter.\
        handle(content.xpath(ENTRY_TITLE).get()).strip('\n').rstrip('\n')
    page_type, number = _page_type_and_number(title)
    assert page_type == PageType.PASURAM
    
    page_contents = {}
    page_contents['number'] = number
    for i, elem in enumerate(PASURAM_PAGE):
        if elem[0] == 'content':
            #print(i, elem)
            tag = elem[1]
            from_expr = PASURAM_PAGE[i - 1]
            #print('from', from_expr)
            to_expr = get_to_expr(content, i)
            #print('from', to_expr)

            xpath_expr = xpath_from_until(from_expr[1], to_expr[1])
            selection = content.xpath(xpath_expr)
            if not selection:
                print(xpath_expr)
            #print('selection', converter.handle(selection.get()))

            page_contents[tag] = converter.handle(''.join(selection.getall())).strip('\n').rstrip('\n')

    # translation from 12000
    from_expr = '//h3[starts-with(., "Simple")]/following-sibling::node()'
    to_expr = '//h3[starts-with(., "vyA")]/preceding-sibling::node()'
    xpath_expr = '%s[count(. | %s) = count(%s)]' % (from_expr, to_expr, to_expr)
    #print('trans', xpath_expr)
    selection = content.xpath(xpath_expr)
    page_contents['translation'] = converter.handle(''.join(selection.getall())).strip('\n').rstrip('\n')

    # 36000
    from_expr = '//strong[contains(., "Highlights from nampiLLai‘s vyAkyAnam")]/following::node()'
    to_expr = '//p[contains(., "In the next article")]/preceding::node()'
    xpath_expr = '%s[count(. | %s) = count(%s)]' % (from_expr, to_expr, to_expr)
    #print('36000', xpath_expr)
    selection = content.xpath(xpath_expr)
    page_contents['36000'] = converter.handle(''.join(selection.getall())).strip('\n').rstrip('\n')

    return page_contents


def _pasuram_number(title):
    """
    Extracts pasuram numerical triplet from title string.

    :param title: in the format 'thiruvAimozhi - x.y.z - first words'
    :return: (patthu, pathikam, paasuram)
    """
    pattern = re.compile('[0-9]+\\.[0-9]+\\.[0-9]+')
    try:
        return pattern.search(title).group(0)
    except AttributeError or IndexError:
        return None


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = [
        #'http://divyaprabandham.koyil.org/index.php/2015/03/thiruvaimozhi-1-1-1-uyarvara-uyarnalam'
        #'http://divyaprabandham.koyil.org/index.php/2018/11/thiruvaimozhi-7-9-2-en-solli-nirpan/'
        #'http://divyaprabandham.koyil.org/index.php/2019/02/thiruvaimozhi-8-3-3-alumalar/',
        #'http://divyaprabandham.koyil.org/index.php/2019/02/thiruvaimozhi-8-3-5-kodiyar-mada/',
        #'http://divyaprabandham.koyil.org/index.php/2019/03/thiruvaimozhi-8-4-1-varkada-aruvi/',
        #'http://divyaprabandham.koyil.org/index.php/2019/03/thiruvaimozhi-8-4-3-en-amar-peruman/',
        #'http://divyaprabandham.koyil.org/index.php/2019/02/thiruvaimozhi-8-2-nangal/',
        #'http://divyaprabandham.koyil.org/index.php/2019/02/thiruvaimozhi-8-3-angumingum/',
        #'http://divyaprabandham.koyil.org/index.php/2019/03/thiruvaimozhi-8-4-varkada/',
        'http://divyaprabandham.koyil.org/index.php/2015/03/thiruvaimozhi-1st-centum/',
        'http://divyaprabandham.koyil.org/index.php/2015/11/thiruvaimozhi-2nd-centum/',
        'http://divyaprabandham.koyil.org/index.php/2016/07/thiruvaimozhi-3rd-centum/',
        'http://divyaprabandham.koyil.org/index.php/2016/11/thiruvaimozhi-4th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2017/05/thiruvaimozhi-5th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2017/10/thiruvaimozhi-6th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2018/07/thiruvaimozhi-7th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2019/01/thiruvaimozhi-8th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2019/06/thiruvaimozhi-9th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2019/10/thiruvaimozhi-10th-centum/',
    ]

        
    def _tvm_page(self, response):
        return 'thiruvAimozhi' in response.xpath(ENTRY_TITLE).get()

    
    def parse(self, response):
        if not self._tvm_page(response):
            return

        links = response.xpath(LINKS)
        yield from response.follow_all(links, self.parse)

        entry_content = response.xpath(ENTRY_CONTENT)
        converter = html2text.HTML2Text()
        converter.ignore_links = True

        title = converter.handle(entry_content.xpath(ENTRY_TITLE).get()).strip('\n').rstrip('\n')
        page_type, number = _page_type_and_number(title)
        if page_type != PageType.PASURAM:
            return

        p = process_pasuram_page(entry_content)
        yield p







    
            
        
            

