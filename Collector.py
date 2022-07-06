from WebsitesDescriptions import *
import concurrent.futures
import SiteScraper
import asyncio


class Website:
    """
    Class object contains all website parameters.
    """
    def __init__(self, site_structure):
        # How to make search requests to site
        self.medicine_search_rule = site_structure['medicine_search_rule']
        # How to iterate over pages
        self.page_search_rule = site_structure['page_search_rule']
        self.site_ref = site_structure['site_ref']
        # How long have scraper to wait between two requests
        self.timeout = site_structure['timeout']
        self.parser = site_structure['parser']

        # Tags on page with drug list. First one is for list of drugs on the page,
        # second is for a single item in list of drugs, third is for title and link
        # and fourth is for number of reviews
        self.drug_tag_list = site_structure['drug_tag_list']
        self.drug_item = site_structure['drug_item']
        self.drug_title = site_structure['drug_title']
        self.drug_reviews_amount = site_structure["drug_reviews_amount"]

        # Tags on page with links to reviews. First one is for list of links,
        # second is for a single item in list, third is for title and link.
        # The last in an int, how many review link are on one page.
        self.review_list_tag_list = site_structure['review_list_tag_list']
        self.review_list_item = site_structure['review_list_item']
        self.review_list_title = site_structure['review_list_title']
        self.review_list_items_on_page = site_structure['review_list_items_on_page']

        # Tags on page with review. Title and body (both are interesting)
        self.review_title = site_structure['review_title']
        self.review_body = site_structure['review_body']

        # If there are some 'drugs' which must be excluded from search,
        # here is banned... list.
        self.banned_refs_to_drugs = site_structure['banned_refs_to_drugs']


# Create Website objects to concentrate all sites parameters
irecommend_website = Website(irecommend_structure)
otzovik_website = Website(otzovik_structure)

# Headers for requests. Needed for scrapers to act like human
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6)AppleWebKit 537.36(KHTML, like Gecko) Chrome",
    "Accept": "text/html,application/xhtml+xml,application/xml; q = 0.9, image / webp, * / *;q = 0.8"}

# Set of possible proxies found by TestCrawler.py.
proxies = set()
# proxies.add('169.57.1.85:8123') -- sample how to add proxy
# proxies.add('170.39.118.187:3128')
proxies.add(None)

# Preferences for iRecommend.ru scraper
irecommend_preferences = {
    'site': irecommend_website,
    'name': 'irecommend',
    'headers': headers,
    'proxies': proxies,

    'medicine_list': [],

    'already_serfed': ["анаферон средство", "виферон", "ингавирин", "валериана средство",
                       "глицин средство", "афлубин", "оксолин", "кагоцел средство",
                       "ацикловир", "гриппферон", "амиксин", "парацетамол",
                       "амизон", "аргоферон", "антигриппин", "афобазол"],

    'to_be_serfed': [],

    'additional_refs_to_drugs': [
                                 ["/content/maz-maz-atsiklovir-zao-verteks", 43],
                                 ["/content/maz-nizhfarm-atsiklovir", 53],
                                 ["/content/maz-dlya-naruzhnogo-primeneniya-atsiklovir-ozon-farmatsevtika", 40],
                                 ["/content/valeriany-ekstrakt-rup-borisovskii-zavod-meditsinskikh-preparatov-tabletki-20-mg", 64],
                                 ["/content/nastoika-gippokrat-nastoika-valeriany", 12],
                                 ["/content/bad-ooo-biokor-vechernee", 33],
                                 ["/content/bad-kosmofarm-glitsin-d3", 100],
                                 ["/content/bad-evalar-glitsin-forte", 142]],
}

# Preferences for Otzovik.com scraper
otzovik_preferences = {
    'site': otzovik_website,
    'name': 'otzovik',
    'headers': headers,
    'proxies': proxies,

    'medicine_list': ["ингавирин"],

    'already_serfed': ["анаферон", "виферон"],

    'to_be_serfed': ["валериана", "глицин", "афлубин", "оксолин", "эргоферон", "антигриппин",
                     "кагоцел", "ацикловир", "гриппферон", "амиксин", "афобазол", "парацетамол", "амизон"],

    'additional_refs_to_drugs': []
}

scrapers_preferences = [otzovik_preferences, irecommend_preferences]
scrapers = list()

# Site scrapers creation. each of them will contain information about website
# and drugs it have to find reviews on
for i in scrapers_preferences:
    scraper = SiteScraper.Scraper(i)
    with open(scraper.name+'_log.txt', 'a+') as f:
        f.close()
    scrapers.append(scraper)


# Asynchronous function to run all scrapers at the same time
async def start_scrapers(loop, executor):
    await asyncio.wait(
        fs={
            loop.run_in_executor(executor, scrapers[0].search_for_medicine),
            loop.run_in_executor(executor, scrapers[1].search_for_medicine)
        },
        return_when=asyncio.ALL_COMPLETED
    )

loop = asyncio.get_event_loop()
# Here you must specify how many scrapers you want to start.
# Max_workers must be bigger than this number
executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(scrapers))
loop.run_until_complete(start_scrapers(loop, executor))

