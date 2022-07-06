from bs4 import BeautifulSoup
from itertools import cycle
import pandas as pd
import requests
import asyncio
import time
import re


def pages_amount(n, k):
    """
    Calculates how many pages are on the site with review refs
    :param n: Amount of reviews
    :param k: Reviews on one page
    :return: number of pages for parse_review_list cycle
    """
    if n % k == 0:
        return int(n/k)
    else:
        return int(n/k + 1)


def my_find(source, tag, params):
    """
    Modified bs4.find function
    :param source: source tag to search in
    :param tag: tag to find
    :param params: dict with tag parameters
    :return: If find returns None, raises AttributeError; else returns find result
    """
    result = source.find(tag, params)
    if not result:
        raise AttributeError
    else:
        return result


def my_find_all(source, tag, params):
    """
    Modified bs4.find_all function
    :param source: source tag to search in
    :param tag: tag to find
    :param params: dict with tag parameters
    :return: If find returns [], raises AttributeError; else returns find result
    """
    result = source.find_all(tag, params)
    if not result:
        raise AttributeError
    else:
        return result


class Scraper:
    """
    Searches for reviews on one site with one proxy, creates dataframe and loads it to file.
    """
    def __init__(self, scraper_preferences):
        self.refs_set = set()
        self.frame = []
        self.count = 0

        self.additional_refs_to_drugs = scraper_preferences['additional_refs_to_drugs']
        self.medicine_list = scraper_preferences['medicine_list']
        self.proxies_len = len(scraper_preferences['proxies'])
        self.proxies = cycle(scraper_preferences['proxies'])
        self.headers = scraper_preferences['headers']
        self.name = scraper_preferences['name']
        self.site = scraper_preferences['site']

    def __str__(self):
        return "Scraper for " + str(self.site.site_ref)

    def put_log(self, message):
        """
        Logs any issue in logfile. For human later watch
        """
        with open(self.name + '_log.txt', 'a+') as f:
            f.write(message + '\n')
            print(message)
        f.close()

    def load_review(self, review_text_list, ref_review):
        """
        :param review_text_list: list containing review content (its title and body).
        :param ref_review: reference to review. Accumulate to avoid duplication.
        :return: 0 if success.
        """
        # Delete all tags, multiple spaces and unexpected symbols
        for i in range(len(review_text_list)):
            i_text = re.sub(r'\<[^>]*\>', ' ', review_text_list[i])
            i_text = re.sub(r'\s+', ' ', i_text)
            i_text = re.sub(r'[^A-zА-я0-9ёЁ ,.?!;:…~%*_+=(){}–/\[\]\n\"\'\-]', '', i_text)
            review_text_list[i] = i_text

        # Append review to excel file with its ref
        review_str = "".join(review_text_list)
        review_frame = pd.DataFrame(data=[{'review': review_str, 'ref': ref_review}])
        self.frame = pd.concat([self.frame, review_frame], ignore_index=True)
        self.frame.to_excel(self.name + '.xlsx', "sheet1")
        self.put_log(str(self.count))
        self.count += 1
        return 0

    def get_request(self, ref):
        """
        Sends a request to server and waits for response. Logs error.
        :param ref: reference to html page.
        :return: response or None object, code (0 if no mistake).
        """
        t = self.site.timeout
        while t < 3000:
            # Wait for a few sec before requesting and iter in cycle of proxies
            proxy = next(self.proxies)
            time.sleep(t/self.proxies_len)
            try:
                print(proxy, t/self.proxies_len)
                response = requests.get(ref, headers=self.headers, proxies={"http": proxy, "https": proxy}, timeout=1)
            except requests.exceptions.ProxyError:
                self.put_log('X: ProxyError ' + proxy)
                continue
            except requests.exceptions.ConnectTimeout:
                self.put_log('X: ConnectTimeout ' + proxy)
                continue
            except requests.exceptions.ConnectionError:
                # Try another time, do not return
                self.put_log('X: ConnectionError ' + str(t) + ' ' + ref)
            except requests.exceptions.MissingSchema:
                self.put_log('X: MissingSchema ' + ref)
                return None, 10
            except requests.exceptions.InvalidHeader:
                self.put_log('X: InvalidHeader ' + ref)
                return None, 11
            except requests.exceptions.RequestException:
                self.put_log('X: OtherRequestError ' + ref)
                return None, 12
            else:
                # We may still get an answer which will not have any useful content.
                # So here returned code is checked
                if 400 < response.status_code < 500:
                    # The mistake is on our side
                    self.put_log('X: IncorrectRequest ' + ref)
                    return None, 400
                elif response.status_code == 507:
                    # Server is not ready to work out request; try another time
                    self.put_log('X: ServerError ' + str(t) + ' ' + ref)
                elif response.status_code == 200:
                    # Successful request, return response
                    return response, 0
            t *= 5
        return None, 1

    def parse_review(self, ref_review):
        """
        Parses review page and gets its content.
        :param ref_review: reference to one review;
        :return None in case of mistake; otherwise 0.
        """
        response, code = self.get_request(ref_review)
        if code == 400:
            # Got 4XX HTTP code, skip this ref, continue scraping
            return 400
        elif code != 0:
            # Unsuccessful request. Stop work, signal – None
            return None

        paragraphs_list = list()
        soup = BeautifulSoup(response.text, self.site.parser)

        # Search for review title and paragraphs in review text
        try:
            title_tag = my_find(soup, self.site.review_title[0], self.site.review_title[1])
            paragraphs_list.append(title_tag.text)
            tag_review = my_find(soup, self.site.review_body[0], self.site.review_body[1])
            paragraphs_list.append(str(tag_review))
            self.put_log(paragraphs_list[0] + ' ' + ref_review)
            self.load_review(paragraphs_list, ref_review)
        except AttributeError:
            self.put_log("X: Error while parsing review page " + ref_review)
            return None
        return 0

    def parse_review_list(self, ref_review_list, reviews_amount):
        """
        Finds references to concrete reviews and calls parse_review() function.
        Supports searching on different pages.
        :param ref_review_list: reference to page containing references' list;
        :param reviews_amount: amount of reviews on current drug.
        :return None in case of mistake; otherwise 0.
        """
        # Use cycle to get reviews refs from all pages
        for i in range(pages_amount(reviews_amount, self.site.review_list_items_on_page) + 1):
            response, code = self.get_request(ref_review_list + self.site.page_search_rule[0]
                                              + str(i) + self.site.page_search_rule[1])
            if response is None:
                # Any mistake on this step is significant. Stop work, signal – None
                return None

            self.put_log(">> _/ Page " + str(i))
            soup = BeautifulSoup(response.text, self.site.parser)

            # Search for refs to reviews; for each call parse_review()
            try:
                tag_list = my_find(soup, self.site.review_list_tag_list[0], self.site.review_list_tag_list[1])
                items_list = my_find_all(tag_list, self.site.review_list_item[0], self.site.review_list_item[1])

                # Search for a ref to single review in list (tag - items_list)
                for item in items_list:
                    title = my_find(item, self.site.review_list_title[0], self.site.review_list_title[1])
                    a = my_find(title, "a", {})
                    # if review reference is already in refs_set, ignore it
                    if a.attrs['href'] in self.refs_set:
                        # self.put_log('Ref duplicated ' + a.attrs['href'])
                        continue
                    else:
                        self.refs_set.add(a.attrs['href'])
                        review = self.parse_review(self.site.site_ref + a.attrs['href'])
                        if review is None:
                            return None
            # my_find() and my_find_all() throw AttributeError is they didn't find anything
            except AttributeError:
                self.put_log("X: Error while parsing review list page " + ref_review)
                return None
        return 0

    def parse_medicine_search(self, ref_search_medicine):
        """
        Finds references to lists of reviews and calls parse_review_list().
        Currently doesn't supports search on different pages (AFAIR, not needed - i tak mnogo).
        :param ref_search_medicine: reference to search results for one medicine.
        :return None in case of mistake; otherwise 0.
        """
        response, code = self.get_request(ref_search_medicine)
        if response is None:
            # Any mistake on this step is significant. Stop work, signal – None
            return None
        soup = BeautifulSoup(response.text, self.site.parser)
        total_reviews_amount = 0

        # Search for refs to lists of drugs' reviews; for each call parse_review_list()
        try:
            tag_list = my_find(soup, self.site.drug_tag_list[0], self.site.drug_tag_list[1])
            items_list = my_find_all(tag_list, self.site.drug_item[0], self.site.drug_item[1])

            # Search for a ref to single drug in list (tag - items_list)
            for item in items_list:
                title = my_find(item, self.site.drug_title[0], self.site.drug_title[1])
                a = my_find(title, "a", {})
                if a.attrs['href'] in self.site.banned_refs_to_drugs:
                    print(a.attrs['href'])
                    continue
                reviews_amount_tag = my_find(item, self.site.drug_reviews_amount[0], self.site.drug_reviews_amount[1])
                reviews_amount = int(re.sub(r'[^0-9]', '', reviews_amount_tag.text))
                total_reviews_amount += reviews_amount
                # Get reviews on one drug
                self.put_log("> Next drug " + self.site.site_ref + a.attrs['href'])
                review_list = self.parse_review_list(self.site.site_ref + a.attrs['href'], reviews_amount)
                if review_list is None:
                    self.put_log("Total reviews: " + str(total_reviews_amount))
                    return None
        # my_find() and my_find_all() throw AttributeError is they didn't find anything
        except AttributeError:
            self.put_log("Total reviews: " + str(total_reviews_amount))
            self.put_log("X: Error while parsing drug list page " + ref_review)
            return None
        self.put_log("Total reviews: " + str(total_reviews_amount))
        return 0

    def search_for_medicine(self):
        """
        self.medicine_list is a list of medicines scraping searches reviews for.
        Forms search URLs and calls parse_medicine_search for each medicine.
        """
        # Create dataframe with all reviews and refs
        # because .xslx does not support appending to file, only rewriting
        self.frame = pd.read_excel(self.name + '.xlsx', names=['review', 'ref'])
        # Apparently load all refs to special set; uses it to ignore duplicates
        for i in range(len(self.frame)):
            self.refs_set.add(self.frame.loc[i, "ref"])

        for medicine in self.medicine_list:
            self.put_log("=" * 30)
            self.put_log(medicine)
            self.put_log("=" * 30)
            result = self.parse_medicine_search(self.site.site_ref
                                                + self.site.medicine_search_rule + re.sub(r' ', '%20', medicine))
            self.put_log("Reviews got: " + str(self.count))
            self.count = 0
            if result is None:
                return None

        for item in self.additional_refs_to_drugs:
            self.put_log("> Next drug " + self.site.site_ref + item[0])
            review_list = self.parse_review_list(self.site.site_ref + item[0], item[1])
            if review_list is None:
                return None

        return 0
