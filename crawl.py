import html2text
import re
import scrapy

PASURAM_PAGE_CHECK = '//div[contains(@class, "category-line")]/a[contains(text(), "thiruvAimozhi")]'
ENTRY_TITLE = '//h2[contains(@class, "entry-title")]'
ENTRY_CONTENT = '//div[contains(@class, "entry-content")]'
PASURAM = './p[preceding-sibling::h3[1][strong[text() = "pAsuram"]]]'
PADA_URAI = './p[preceding-sibling::h3[1][strong[starts-with(text(), "Word-by-")]]]'
LINKS = '//div[contains(@class, "entry-content")]//li/a[contains(@href, "divyaprabandham.koyil.org")]'


def _title_to_number(title):
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
        #,
        'http://divyaprabandham.koyil.org/index.php/2015/03/thiruvaimozhi-1st-centum/'
#        'http://divyaprabandham.koyil.org/index.php/2015/11/thiruvaimozhi-2nd-centum/',
#        'http://divyaprabandham.koyil.org/index.php/2016/07/thiruvaimozhi-3rd-centum/',
        #'http://divyaprabandham.koyil.org/index.php/2016/11/thiruvaimozhi-4th-centum/',
        #'http://divyaprabandham.koyil.org/index.php/2017/05/thiruvaimozhi-5th-centum/',
        #'http://divyaprabandham.koyil.org/index.php/2017/10/thiruvaimozhi-6th-centum/',
        #'http://divyaprabandham.koyil.org/index.php/2018/07/thiruvaimozhi-7th-centum/',
        #'http://divyaprabandham.koyil.org/index.php/2019/01/thiruvaimozhi-8th-centum/',
        #'http://divyaprabandham.koyil.org/index.php/2019/06/thiruvaimozhi-9th-centum/',
        #'http://divyaprabandham.koyil.org/index.php/2019/10/thiruvaimozhi-10th-centum/'
    ]


    def parse(self, response):
        page_check = response.xpath(PASURAM_PAGE_CHECK)
        #print(page_check.get())
        if not page_check.get():
            return

        links = response.xpath(LINKS)
        yield from response.follow_all(links, self.parse)

        for entry_content in response.xpath(ENTRY_CONTENT):
            converter = html2text.HTML2Text()
        converter.ignore_links = True

        title = converter.handle(entry_content.xpath(ENTRY_TITLE).get()).strip('\n').rstrip('\n')
        number = _title_to_number(title)
        print(number)

        if not number:
            return

        pasuram_elems = entry_content.xpath(PASURAM).getall()
        pasuram = None
        pasuram_roman = None
        if len(pasuram_elems) == 1:
            pr = pasuram_elems[0]
        elif len(pasuram_elems) == 2:
            p = pasuram_elems[0]
            pr = pasuram_elems[1]
            pasuram = converter.handle(p).strip('\n').rstrip('\n')

        pasuram_roman = converter.handle(pr).strip('\n').rstrip('\n')


        pada_urai = converter.handle(entry_content.xpath(PADA_URAI).get()).strip('\n').rstrip('\n')

        yield {
            'number': number,
            'pasuram': pasuram,
            'pasuram_roman': pasuram_roman,
            'pada_urai': pada_urai
        }






