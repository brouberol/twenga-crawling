# -*- coding: utf-8 -*-

"""
Module parsing the http://vaisselle.twenga.fr/theiere.html webpage,
scraping the ten first results in search of the name of the product,
its price, the seller URL and whether the article is in stock.

Executing simply with
$ python crawler.py

The result is a generated index.html webpage, containing the extracted
results.

"""
import codecs
import re
import requests

from os.path import dirname, join
from urllib import urlretrieve

from gevent import monkey
monkey.patch_socket()
from gevent.pool import Pool
from bs4 import BeautifulSoup
from jinja2 import Environment, ChoiceLoader, FileSystemLoader


def soupify_website(url):
    """ Retrieve webpage HTML code and return its 'soup' version. """
    return BeautifulSoup(open(urlretrieve(url)[0]))


def extract_products(soup):
    """ Extract the product list from the HTML soup using a CSS selector. """
    return soup.select('li.ctItem')


def title(soup):
    """ Extract the title from a product soup using a CSS selector. """
    return soup.select('div.pdtInfos > h2')[0].text.replace('\n', '')


def price(soup):
    """ Extract the price from a product soup using a CSS selector. """
    product_price = soup.select('span.price')[0].contents[1].text[:-1]
    product_price = product_price.replace(',', '.').replace('\n', '').strip()
    return product_price


def seller_url(soup):
    """ Extract the decoded seller URL from a product soup using
    a CSS selectior.

    Note: The extracted URLs need to be rot-13 decoded.
    """
    span = soup.select('span.a')[0]  # CSS selector
    uggc_url = span.attrs['data-erl']
    return uggc_url.decode('rot-13')  # return decoded url


def twenga_redirect(url):
    """ Return the last URL in the redirection chain."""
    # Extract redirection URL from HTML code.
    # We have to parse the HTLM, as the requests sends a 200,
    # and the redirection is made by a JS call. Oh boy...
    soup = soupify_website(url)
    script_with_url = [script.text for script in soup.select('script')
        if 'http://r.twenga' in script.text][0]
    match = re.search(r'http://r.twenga[^=]+=[\w]+', script_with_url)
    redirect1 = match.group(0)

    # Follow the redirection URL, and get its redirection point
    # Return it if it can be found. Else, return the last redirection
    # point
    redirect2 = requests.get(redirect1)
    return redirect2.history[0].raw.get_redirect_location()


def in_stock(url):
    """ Analyze the HTML code of the webpage of argument URL, in search
        of terms indicating that the object is (or not) in store.

        If terms indicating that the article is not in store are found,
        return False.
        If terms indicating that the article is in store are found,
        return True.
        If none of these terms are found, return True, as it's nothing
        unusual.
    """
    text = ' '.join([s.lower() for s in soupify_website(url).strings])

    unavailable = ['indisponible', 'plus disponible', 'approvisionnement']
    for term in unavailable:
        if term in text:
            return False

    available = ['en stock']
    for term in available:
        if term in text:
            return True
    return True


def product_features(product):
    """ Extract the title, price, seller URL and stock status of the
        argument product.
    """
    features = {}
    features['title'] = title(product)  # extract title
    features['price'] = price(product)  # extract price
    features['url'] = twenga_redirect(seller_url(product))  # vendor url
    features['in_stock'] = in_stock(features['url'])  # availability
    print "Features extracted!"
    return features


def products_features(products):
    """ Perform the features extraction asynchronously. """
    pool = Pool(10)
    return pool.map(product_features, products)


def render_results(products):
    """ Render an HTML template with the argument results. """
    # add template to Jinja environment
    loader = ChoiceLoader([FileSystemLoader(
        join(dirname(__file__), 'templates'))])
    env = Environment(loader=loader)

    # Render table.html template with products features
    template = env.get_template('table.html')
    return template.render(products=products)


def main():
    twenga_url = "http://vaisselle.twenga.fr/theiere.html"
    soup = soupify_website(twenga_url)
    teapots = extract_products(soup)[:10]  # Extract 10 first teapots
    features = product_features(teapots)   # Extract teapots features
    with codecs.open(
            join(dirname(__file__), 'index.html'), 'w', 'utf-8') as target:
        target.write(render_results(features))  # Render template with features


if __name__ == '__main__':
    main()
