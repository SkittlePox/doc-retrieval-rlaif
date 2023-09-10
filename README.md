# Synthetic Document Retrieval Reward Model

Ensuring LLMs are truthful is difficult. We present a reward model that rewards LLMs for 
completions by evaluating them against documents from Wikipedia and 
Stack Exchange, which are collected via DuckDuckGo search.


## Important methods
`ddg_querier.py`:: `get_documents`

Turns a query `str` into a list of document contents `list[str]`. Documents, by default, are the top 10 results from DuckDuckGo when searching the query input, restricted by `site:wikipedia.org OR site:stackoverflow.com`


## Using the reward model

Instantiate it. Call `get_reward` on a query and a completion. The reward model will return a reward `float` between 0 and 1. Record the completions and rewards in a csv, and run `revise.py` to generate revised completions.
