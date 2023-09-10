import pprint as pp
import urllib

from bs4 import BeautifulSoup

from curler import SeleniumCurler


class DDGQuerier:
    def __init__(self,
                 ensemble_results: bool = True,
                 top_k: int = 10):
        self.ensemble_results = ensemble_results
        self.top_k = top_k
        self.__curler = None

    @property
    def curler(self):
        if self.__curler is None:
            self.__curler = SeleniumCurler()
        return self.__curler
    
    def get_links_from_ddg_source(self, ddg_source: str) -> list[str]:
        soup = BeautifulSoup(ddg_source, 'html.parser')
        ols = soup.find_all('ol', class_='react-results--main')
        if not ols:
            raise RuntimeError('No results found (no OL)')
        links = []
        for ol in ols:
            # iterate over li elements, stopping at self.top_k
            for li in soup.find_all('li'):
                if len(links) >= self.top_k:
                    break
                if li.get('data-layout') == 'ad':
                    continue
                link = li.find('a', attrs={'data-testid': 'result-title-a'})
                if link is None: continue
                link = link.get('href')
                links.append(link)
            else:
                raise RuntimeError('No results found (no LIs)')
        return links
    
    def prep_query(self, query: str) -> list[str]:
        query = query.strip()
        query = urllib.parse.quote(query, safe='')
        if self.ensemble_results:
            query += '+site%3Awikipedia.org+OR+site%3Astackoverflow.com'
            return [query]
        else:
            return [
                query + '+site%3Awikipedia.org',
                query + '+site%3Astackoverflow.com'
            ]

    def __call__(self, query: str) -> list[str]:
        queries = self.prep_query(query)
        links = []
        for query in queries:
            ddg_url = f'https://duckduckgo.com/?t=h_&q={query}&ia=web'
            ddg_source = self.curler.urlget(ddg_url)
            links += self.get_links_from_ddg_source(ddg_source)
        return links


def main():
    ddg_querier = DDGQuerier(ensemble_results=True)
    while True:
        query = input('Query: ')
        results = ddg_querier(query)
        pp.pprint(results)


if __name__ == '__main__':
    main()