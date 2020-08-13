from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import urlopen
import time
import sys
import re

RANDOM_URL = "https://en.wikipedia.org/wiki/Special:Random"
TARGET_ARTICLE = "Philosophy"

def strip_parentheses(string):
    """
    Remove parentheses from a string, leaving
    parentheses between <tags> in place
    Args:
        string: the string to remove parentheses from
    Returns:
        the processed string after removal of parentheses
    """
    nested_parentheses = nesting_level = 0
    result = ''
    for c in string:
        # when outside of parentheses within <tags>
        if nested_parentheses < 1:
            if c == '<':
                nesting_level += 1
            if c == '>':
                nesting_level -= 1

        # when outside of <tags>
        if nesting_level < 1:
            if c == '(':
                nested_parentheses += 1
            if nested_parentheses < 1:
                result += c
            if c == ')':
                nested_parentheses -= 1

        # when inside of <tags>
        else:
            result += c

    return result

def get_normal_link(soup):
    """
    Removes unnecessary components and parenthesized text to return
    and returns the first internal link (starting with /wiki/)
    Args:
        soup: the soup object of a wiki article
    Returns:
        the normal link for the article sent
    """
    body = soup.find(id='mw-content-text')
    
    for e in body.find_all(class_=['hatnote', 'thumb', 'navbox', 'vertical-navbox', 'toc', 'IPA']):
        e.replace_with("")

    for e in body.find_all(['table', 'span']): # normal links are not in tables or spans
        e.replace_with("")

    body = BeautifulSoup(strip_parentheses(str(body)), 'html.parser') # remove parenthesized text

    path = body.find('a', href=re.compile('^/wiki/'))['href'] # internal wiki paths start with /wiki/
    url = 'https://en.wikipedia.org{}'.format(path)
    return url

def go_to_philosophy(url):
    """
    Keeps crawling wikipedia articles by starting from a wikipedia article
    and visiting the normal link for every new article till it reaches the
    Philosophy or article, finds a loop or there are no normal links left
    in the article
    Args:
        url: the url for the wiki article to start crawling from
    Returns:
        None
    """
    visited_articles = set()

    while True:
        html = urlopen(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        article_name = soup.find(id='firstHeading').text
        print(article_name)

        # found philosophy
        if article_name == TARGET_ARTICLE:
            print("\n{} found.".format(TARGET_ARTICLE))
            break

        # avoid getting stuck in a loop
        if article_name in visited_articles:
            print("\nLoop found.")
            break

        url = get_normal_link(soup)

        # the article has no outgoing Wikilinks
        if url is None:
            print("\nNo outgoing normal links.")
            break

        visited_articles.add(article_name)

        time.sleep(0.5)
    
    print("Visited {} articles.".format(len(visited_articles)))


if __name__=="__main__":

    # Checking that a correct URL is sent. If not, use a random url. 
    if len(sys.argv) < 2:
        print("The program will crawl wikipedia starting from a random URL.")
        url = RANDOM_URL
    else:
        url = sys.argv[1]
        domain_name = '.'.join(urlparse(url).netloc.split('.')[1:])
        if(domain_name != 'wikipedia.org'):
            url = RANDOM_URL

    # crawl wikipedia
    go_to_philosophy(url)
