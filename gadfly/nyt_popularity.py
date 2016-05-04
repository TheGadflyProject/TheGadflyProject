from urllib.parse import urlencode
import requests
import json
import datetime
import operator


def get_nyt_popularity(term):
    nyt_url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?"
    today = datetime.date.today()
    one_month_ago = today - datetime.timedelta(days=30)
    default_vars = {
        "q": term,
        "begin_date": one_month_ago.strftime("%Y%m%d"),
        "end_date": today.strftime("%Y%m%d"),
        "sort": "newest",
        "api-key": "85bbd9fd3773d8f0534912780e355199:12:75094806"
    }

    res = requests.get(nyt_url + urlencode(default_vars))
    meta_dict = {"hits": 0}
    if res:
        res_dict = json.loads(res.content.decode(encoding='UTF-8'))
        meta_dict = res_dict.get("response").get("meta")
    return meta_dict.get('hits')


def most_popular_terms(term_list, n=3):
    term_popularity = {}
    for term in term_list:
        term_popularity[term] = get_nyt_popularity(term)
    sorted_terms = sorted(term_popularity.items(),
                          key=operator.itemgetter(1),
                          reverse=True)
    return sorted_terms[:n]
