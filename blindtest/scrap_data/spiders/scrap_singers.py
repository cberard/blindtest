from scrapy import Request, Spider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})


class Singer(Spider):

    name = "get_singers"

    def start_requests(self):
        url = "https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Auteur-compositeur-interpr%C3%A8te_fran%C3%A7ais"
        yield Request(url=url, callback=self.get_singers)

    def get_singer_info(self, singer_response, name):
        general_singer_infos = singer_response.css("div.infobox.infobox_v3 table tr")
        general_topics = general_singer_infos.css("tr")
        singer_info = dict(name=name)
        for general_topic in general_topics:
            topic = (
                " ".join(general_topic.css("th *::text").getall())
                .replace("\n", "")
                .strip()
            )
            info = (
                " ".join(general_topic.css("td *::text").getall())
                .replace("\n", "")
                .strip()
            )
            singer_info[topic] = info
        yield singer_info

    def get_singers(self, response):
        singers = response.css("div.mw-category-group li a")
        for singer_response in singers:
            singer_page = singer_response.css("a::attr(href)").get()
            singer_name = singer_response.css("a::text").get()
            if singer_page is not None:
                next_page = response.urljoin(singer_page)
                yield Request(
                    next_page,
                    callback=self.get_singer_info,
                    cb_kwargs=dict(name=singer_name),
                )
            else:
                yield dict(name=singer_name)
        next_page = (
            response.xpath("//*[contains(text(), 'page suivante')]")
            .css("a::attr(href)")
            .get()
        )
        if next_page is not None:
            yield Request(
                response.urljoin(next_page), callback=self.get_singers,
            )


def crawl_singer(dest_path):
    process = CrawlerProcess(settings={"FEEDS": {dest_path: {"format": "json"}}})
    process.crawl(Singer)
    process.start()
