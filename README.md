## Twenga-crawler

This code was written to crawl the [http://vaisselle.twenga.fr/theiere.html](http://vaisselle.twenga.fr/theiere.html)
website and scrape information about the 10 latest products.

The main difficulty comes from the fact that a great deal of the webiste user interface is only JS based,
and obscure voodoo redirection occur, some triggered by JS, some by a 301 response.
What a noodle soup.

### Install it
Create a new [virtualenv](http://pypi.python.org/pypi/virtualenv), and install all dependancies:

```bash
$ pip install -r requirements
```

Note that gevent requires the `libevent-dev` library to compile properly.

### Execute it
```bash
$ python crawler.py
```

An `index.html` webpage will be generated if all goes well, containing the results of the scraping.
  