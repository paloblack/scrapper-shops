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
import locale
os.environ["PYTHONIOENCODING"] = "utf-8"
scriptLocale=locale.setlocale(category=locale.LC_ALL, locale="es_ES.UTF-8")
#Create csv

os.remove('crisalida.csv')

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

    with open("crisalida.csv", "a") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Producto','SKU','Precio','Precio Rebajado','Descripcion_corta', 'Imagen','Color','Talla','Disponibilidad'])
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
                print(href)
                name=soup.find('h1')
                print(name)
                price=soup.find('p',{'class':'price'})
                sku=soup.find('span',{'class':'sku'})
                categoria=soup.findAll('a',{'rel':'tag'})
                clean = re.compile('<.*?>')
                categoria= str(categoria)
                categoria = re.sub(clean, '', categoria)
                genero = "mujer"
                try:
                    tipo = categoria.split()[1]
                    tipo = tipo.replace(']', '')
                except Exception:
                    tipo = "No tiene tipo"
                try:
                    descripcion = soup.find('div',{'class':'et_pb_wc_description'})
                    description = descripcion.find('p')
                    description = description.string
                except Exception:
                    description = "<p>No hay Descripcion</p>"
                try:
                    image= soup.find('figure',{'class':'woocommerce-product-gallery__wrapper'}).findAll('img')
                    images = []
                    for img in image:
                        images.append(img.get('data-large_image'))
                    images1 = ','.join(map(str, images))
                except Exception:
                    images1 = "No hay Imagenes"
                #descripcion = soup.find('div',{'class':'woocommerce-product-details__short-description'})
                #description = descripcion.find('p')
                clean = re.compile('<.*?>')
                price= str(price)
                price = re.sub(clean, '', price)
                price1 = price.split()[0]
                try:
                    price2 = price.split()[1]
                except Exception:
                    price2 = None;
                try:
                    result=soup.find('form',{'class':'variations_form'})
                    result=result['data-product_variations']
                    res = json.loads(result)
                    for i in res:
                            variables = i['attributes']
                            if "attribute_pa_color" in variables:
                                color = variables['attribute_pa_color']
                            else:
                                color = "None"
                            if "attribute_pa_talla" in variables:
                                variables = variables['attribute_pa_talla']
                            elif "attribute_talla" in variables:
                                variables = variables['attribute_talla']
                            else:
                                variables = "Talla Única"

                            variables_convertidas = variables
                            if "talla-s-m" in variables_convertidas:
                                variables_convertidas = 'S-M'
                            elif "talla-m-l" in variables_convertidas:
                                variables_convertidas = 'M-L'
                            elif "talla-l-xl" in variables_convertidas:
                                variables_convertidas = 'L-XL'
                            elif "extra-grande" in variables_convertidas:
                                variables_convertidas = 'XL'
                            else:
                                variables_convertidas = variables_convertidas
                            availability_html=i['availability_html']

                            clean = re.compile('<.*?>')
                            availability_html= str(availability_html)
                            availability_html = re.sub(clean, '', availability_html)
                            availability_html=availability_html[0:40]
                            if "1" in availability_html:
                                availability_html='1'
                            elif "2" in availability_html:
                                availability_html='2'
                            elif "3" in availability_html:
                                availability_html='3'
                            elif "4" in availability_html:
                                availability_html='4'
                            elif "Agotado" in availability_html:
                                availability_html='0'
                            else:
                                availability_html='30'

                            writer.writerow([name.string,sku, price1,price2,description, images1,color,variables_convertidas,availability_html])


                except Exception:
                    try:
                        writer.writerow([name.string,sku,price1,price2,description, images1])
                    except Exception:
                        continue
                try:
                    print(name.string,sku,price1,price2,description,images1)
                except Exception:
                    continue

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
        try:
            crawl(link, max_urls=max_urls)
        except Exception:
            continue


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Link Extractor Tool with Python")
    urls = ['https://crisalidadesigner.com/tienda/']
    max_urls=100

    args = parser.parse_args()
    for url in urls:
        crawl(url, max_urls=max_urls)


    print("[+] Total Internal links:", len(internal_urls))
    print("[+] Total External links:", len(external_urls))
    print("[+] Total URLs:", len(external_urls) + len(internal_urls))

    domain_name = urlparse(url).netloc

    # save the internal links to a file
