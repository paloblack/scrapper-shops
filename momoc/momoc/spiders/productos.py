import scrapy
from bs4 import BeautifulSoup
import re
from HarveyNorman.items import HarveyNormanItem


class OscarSpiders(scrapy.Spider):
    name = 'HarveyNormanspider'
    allowed_domains = ['HarveyNorman.com.au']
    start_urls = ['https://www.HarveyNorman.com.au/']

    def __init__(self):
        self.declare_xpath()

        #All the XPaths the spider needs to know go here
    def declare_xpath(self):
        self.getAllCategoriesXpath = "//div[@id='wrapper']/div[1]/div[1]/div[1]/div[1]/div[@class='col-md-3']/ul/li/a/@href"
        self.getAllSubCategoriesXpath = "//*[@id='content']/div[2]/div[1]/div/div[2]/div/div/div/div[2]/div/a/@href"
        self.getAllItemsXpath = "//*[@id='category-grid']/div/div/div[3]/a/@href"
        self.TitleXpath  = "//*[@id='overview']/div[1]/h1/span[1]/text()"
        self.CategoryXpath = "//*[@id='breadcrumbs']/li/a/text()"
        self.PriceXpath = "//div[@class='product-view-sales']//span[@class='price']/text()"
        self.FeaturesXpath = "//*[@id='tab-content-product-description']/div/div[3]/ul/li/text()"
        self.BackupFeaturesXpath = "//*[@id='tab-content-product-description']/div/div[contains (@class, 'long-description')]//p/text()"
        self.DescriptionXpath = "//*[@id='tab-content-product-description']/div/div[contains(@class,'description')][1]/p//text()"
        self.SpecsNameXpath = "//*[@id='product-attribute-specs-table']/tbody/tr/th/text()"
        self.SpecsXpath = "//*[@id='product-attribute-specs-table']/tbody/tr/td/text()"

    #From the main page, call parse_category on each category link
    def parse(self, response):
        for href in response.xpath(self.getAllCategoriesXpath):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url=url,callback=self.parse_category, dont_filter=True)

    #From each category page, call parse_subcategory on each subcategory link
    def parse_category(self,response):
        for href in response.xpath(self.getAllSubCategoriesXpath):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url,callback=self.parse_subcategory, dont_filter=True)

    #From each subcategory page, call parse_main_item on each product page link
    def parse_subcategory(self,response):
        for href in response.xpath(self.getAllItemsXpath):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url,callback=self.parse_main_item, dont_filter=True)

        #call parse_subcategory on the next page
        next_page = response.xpath("//*[@id='toolbar-btm']/div/div[4]/div/ol/li[3]/a/@href").extract_first()
        if next_page is not None:
            url = response.urljoin(next_page)
            yield scrapy.Request(url, callback=self.parse_subcategory, dont_filter=True)


    def parse_main_item(self,response):
        item = HarveyNormanItem()

        #grab each element using XPath, then clean and format text.

        Title = response.xpath(self.TitleXpath).extract()
        Title = self.cleanText(self.parseText(self.listToStr(Title)))

        Category = response.xpath(self.CategoryXpath).extract()
        Category = ','.join(map(str, Category[1:]))
        Category = self.cleanText(self.parseText(Category))

        Price = response.xpath(self.PriceXpath).extract()
        Price = self.cleanText(self.parseText(self.listToStr(Price)))

        Features = response.xpath(self.FeaturesXpath).extract()
        if Features is None:
            Features = response.xpath(self.BackupFeaturesXpath).extract()
        Features = self.cleanText(self.parseText(self.listToStr(Features)))

        Description = response.xpath(self.DescriptionXpath).extract()
        Description = self.cleanText(self.parseText(self.listToStr(Description)))

        SpecsName = response.xpath(self.SpecsNameXpath).extract()
        SpecsName = ','.join(map(str, SpecsName))
        SpecsName = self.cleanText(self.parseText(SpecsName))

        Specs = response.xpath(self.SpecsXpath).extract()
        Specs = ','.join(map(str, Specs))
        Specs = self.cleanText(self.parseText(Specs))

        #Put each element into its item attribute.
        item['Title']           = Title
        item['Category']        = Category
        item['Price']           = Price
        item['Features']        = Features
        item['Description']     = Description
        item['SpecsName']       = SpecsName
        item['Specs']           = Specs
        return item

    #Methods to clean and format text to make it easier to work with later
    def listToStr(self,MyList):
        dumm = ""
        MyList = [i.encode('utf-8') for i in MyList]
        for i in MyList:dumm = "{0}{1}".format(dumm,i)
        return dumm

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text()
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text
