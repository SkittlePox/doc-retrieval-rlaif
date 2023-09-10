import pprint as pp
import urllib

from bs4 import BeautifulSoup

from curler import SeleniumCurler


class DDGQuerier:
    """
    Query DuckDuckGo for a query, returning a list of links to the top
    results. If ensemble_results is True, then the results from
    wikipedia.org and stackoverflow.com will be combined. Otherwise,
    they will be returned separately.
    """

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
        """
        Given the source of a DuckDuckGo search results page, return a
        list of the top links.

        Args:
            ddg_source (str): The source of a DuckDuckGo search results
                page.

        Returns:
            list[str]: A list of the top links.

        Raises:
            RuntimeError: If no results are found. Indicates that
                selenium is not correctly configured in the local
                environment. Often this relates to issues with 
                minimization.
        """
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
        """
        Given a query, return a list of queries to be used in the
        DuckDuckGo search. If ensemble_results is True, then the
        results from wikipedia.org and stackoverflow.com will be
        combined. Otherwise, they will be returned separately.
        """
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
        """
        Given a query, return a list of links to the top results.

        Args:
            query (str): The query to search for.

        Returns:
            list[str]: A list of links to the top results.
        """
        queries = self.prep_query(query)
        links = []
        for query in queries:
            ddg_url = f'https://duckduckgo.com/?t=h_&q={query}&ia=web'
            ddg_source = self.curler.urlget(ddg_url)
            links += self.get_links_from_ddg_source(ddg_source)
        return links

def main():
    """Interactive session with DDG Querier"""
    ddg_querier = DDGQuerier(ensemble_results=True)
    while True:
        query = input('Query: ')
        results = ddg_querier(query)
        pp.pprint(results)


if __name__ == '__main__':
    main()