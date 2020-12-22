import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import urllib.request
import re
import json
import csv
import pandas as pd
import os

#Create csv

os.remove('product_data.csv')

# init the colorama module
colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()

total_urls_visited = 0


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`

    with open("product_data.csv", "a") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Producto','Descripcion', 'Precio', 'Imagen','Talla','Disponibilidad'])
        urls = set()
        # domain name of the URL without the protocol
        domain_name = urlparse(url).netloc
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            # join the URL if it's relative (not absolute link)
            if '/producto/' in href:
                href = urljoin(url, href)
                parsed_href = urlparse(href)
                # remove URL GET parameters, URL fragments, etc.
                href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
                if not is_valid(href):
                    # not a valid URL
                    continue
                if href in internal_urls:
                    # already in the set
                    continue
                if domain_name not in href:
                    # external link
                    continue
                data=urllib.request.urlopen(href)
                soup = BeautifulSoup(data, 'html.parser')
                name=soup.find('h1',{'class':'product_title'})
                price=soup.find('p',{'class':'price'})
                image=soup.findAll('img',{'class':'attachment-shop_thumbnail'})
                descripcion = soup.find('div',{'class':'woocommerce-product-details__short-description'})
                description = descripcion.find('p')
                images = []
                for img in image:
                    images.append(img.get('src'))
                clean = re.compile('<.*?>')
                price= str(price)
                price = re.sub(clean, '', price)
                try:
                    result=soup.form['data-product_variations']
                    res = json.loads(result)
                    for i in res:
                            print(i['attributes'])
                            print(i['availability_html'])
                            variables = i['attributes']
                            availability_html=i['availability_html']
                            clean = re.compile('<.*?>')
                            availability_html= str(availability_html)
                            availability_html = re.sub(clean, '', availability_html)
                            writer.writerow([name.string,description.string, price.split(), images,list(variables.values()),availability_html])
                except KeyError:
                    writer.writerow([name.string,description.string, price.split(), images])
                print(name.string,description.string,price.split(),images)

                urls.add(href)
                internal_urls.add(href)
        return urls


def crawl(url, max_urls=100):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls=max_urls)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Link Extractor Tool with Python")
    urls = ['https://www.momocshoes.com/es/']
    max_urls=100

    args = parser.parse_args()
    for url in urls:
        crawl(url, max_urls=max_urls)

    print("[+] Total Internal links:", len(internal_urls))
    print("[+] Total External links:", len(external_urls))
    print("[+] Total URLs:", len(external_urls) + len(internal_urls))

    domain_name = urlparse(url).netloc

    # save the internal links to a file
