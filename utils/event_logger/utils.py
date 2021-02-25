import pandas as pd
import sqlalchemy as sql


def result_proxy_to_df(res: sql.engine.ResultProxy) -> pd.DataFrame:
    """
    Convert result proxy (from sql execute) to pandas dataframe (https://stackoverflow.com/a/12060886/1617883)
    """
    df = pd.DataFrame(res.fetchall())
    df.columns = res.keys()
    return df


def process_like_term(search_term: str) -> str:
    """
    Allow "known" wildcards in search term and produce compatible term for SQL
    Known -> SQL    Desc
    _     -> __     skips underscore
    *     -> %      matches any sequence of zero or more characters.
    ?     -> _      matches any single character

    References:
        - https://www.sqlitetutorial.net/sqlite-like/
        - https://stackoverflow.com/a/12060886/1617883
    """
    if '*' in search_term or '_' in search_term:
        return search_term.replace('_', '__').replace('*', '%').replace('?', '_')
    return f'%{search_term}%'
