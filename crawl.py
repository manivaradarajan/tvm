from enum import Enum
import html2text
import re
import scrapy

TVM_PAGE_CHECK = '//div[contains(@class, "category-line")]/a[contains(text(), "thiruvAimozhi")]'
ENTRY_TITLE = '//h2[contains(@class, "entry-title")]'
ENTRY_CONTENT = '//div[contains(@class, "entry-content")]'

COMMENTATORS = {
    '6000': 'thirukkurukaippirAn piLLAn',
    '9000': 'nanjIyar',
    '12000' : 'vAdhi kEsari azhagiya maNavALa jIyar',
    '24000' : 'periyavAchchAn piLLai',
    '36000' : 'nampiLLai'
}


def xpath_from_until(from_expr, until_expr):
    # Kayessian formula.
    return '%s[count(. | %s) = count(%s)]' % (from_expr, until_expr, until_expr)


def xpath_intro_6000():
    return xpath_from_until(
        INTRO_TEMPLATE_FROM % COMMENTATORS['6000'],
        INTRO_TEMPLATE_FROM % COMMENTATORS['9000'])


def xpath_intro_9000():
    return xpath_from_until(
        INTRO_TEMPLATE_FROM % COMMENTATORS['9000'],
        INTRO_TEMPLATE_FROM % COMMENTATORS['12000'])


def xpath_intro_12000():
    return xpath_from_until(
        INTRO_TEMPLATE_FROM % COMMENTATORS['12000'],
        INTRO_TEMPLATE_FROM % COMMENTATORS['24000'])


def xpath_intro_24000():
    return xpath_from_until(
        INTRO_TEMPLATE_FROM % COMMENTATORS['24000'],
        INTRO_TEMPLATE_FROM % COMMENTATORS['36000'])


def xpath_intro_36000():
    return xpath_from_until(
        INTRO_TEMPLATE_FROM % COMMENTATORS['24000'],
        PASURAM_HEADING)


# PATTHU pages
OVERVIEW = './p[preceding-sibling::h3[1][contains(text(), "Highlights")]]'

# PATHIKAM pages
OVERVIEW_RAW = '//h3/..'

LINKS = '//div[contains(@class, "entry-content")]//li/a[contains(@href, "divyaprabandham.koyil.org")]'


class PageType(Enum):
    PASURAM = 1
    PATHIKAM = 2
    PATTHU = 3
    

def pasuram_number(title):
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

    
def page_type_and_number(title):
    number = pasuram_number(title)
    if number:
        return PageType.PASURAM, number
    
    number = pathikam_number(title)
    if number:
        return PageType.PATHIKAM, number
    
    if 'centum' in title:
        return PageType.PATTHU, patthu_number(title)

    raise ValueError('Can\'t decipher type of: ' + title)


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = [
        #'http://divyaprabandham.koyil.org/index.php/2015/03/thiruvaimozhi-1-1-1-uyarvara-uyarnalam'
#        'http://divyaprabandham.koyil.org/index.php/2018/11/thiruvaimozhi-7-9-2-en-solli-nirpan/'
#        'http://divyaprabandham.koyil.org/index.php/2019/06/thiruvaimozhi-9-1-kondapendir/'
        'http://divyaprabandham.koyil.org/index.php/2015/03/thiruvaimozhi-1st-centum/',
        'http://divyaprabandham.koyil.org/index.php/2015/11/thiruvaimozhi-2nd-centum/',
        'http://divyaprabandham.koyil.org/index.php/2016/07/thiruvaimozhi-3rd-centum/',
        'http://divyaprabandham.koyil.org/index.php/2016/11/thiruvaimozhi-4th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2017/05/thiruvaimozhi-5th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2017/10/thiruvaimozhi-6th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2018/07/thiruvaimozhi-7th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2019/01/thiruvaimozhi-8th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2019/06/thiruvaimozhi-9th-centum/',
        'http://divyaprabandham.koyil.org/index.php/2019/10/thiruvaimozhi-10th-centum/'
    ]

    
    def parse(self, response):
        page_check = response.xpath(TVM_PAGE_CHECK)
        if not page_check.get():
            return

#        links = response.xpath(LINKS)
#        yield from response.follow_all(links, self.parse)

        entry_content = response.xpath(ENTRY_CONTENT)
        converter = html2text.HTML2Text()
        converter.ignore_links = True

        title = converter.handle(entry_content.xpath(ENTRY_TITLE).get()).strip('\n').rstrip('\n')
        page_type, number = page_type_and_number(title)

        print(number)

        if page_type == PageType.PASURAM:
            p = self._process_pasuram(number, entry_content, converter)
            yield p
        elif page_type == PageType.PATHIKAM:
            p = self._process_pathikan(number, entry_content, converter)
            yield p
        elif page_type == PageType.
            
        
    def _process_pasuram(self, number, entry_content, converter):
        pasuram_elems = entry_content.xpath(PASURAM).getall()
        pasuram = None
        pasuram_roman = None

        #print("elems =", pasuram_elems)
        if len(pasuram_elems) == 1:
            pr = pasuram_elems[0]
        elif len(pasuram_elems) == 2:
            p = pasuram_elems[0]
            pr = pasuram_elems[1]
            pasuram = converter.handle(p).strip('\n').rstrip('\n')

        pasuram_roman = converter.handle(pr).strip('\n').rstrip('\n')

        pada_urai = converter.handle(entry_content.xpath(PADA_URAI).get()).strip('\n').rstrip('\n')
        return {
            'number': number,
            'pasuram': pasuram,
            'pasuram_roman': pasuram_roman,
            'pada_urai': pada_urai
        }






