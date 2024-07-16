# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


from scrapers.models import Quote


class GrScrapersPipeline(object):
    def process_item(self, item, spider):
        try:
            quote = Quote(text=item.get('text'), author=item.get('author'))
            quote.save()
            return item
        except Exception as error:
            print("An exception occurred:", error)

