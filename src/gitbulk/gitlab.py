import gitlab
from pathlib import Path


def session(oauth: Path = None, url: str = "https://gitlab.com") -> gitlab.Gitlab:
    """
    setup Git remote session

    https://python-gitlab.readthedocs.io/en/stable/api-usage.html#gitlab-gitlab-class

    Parameters
    ----------

    oauth : pathlib.Path, optional
        file containing Oauth hash
    url : str, optional
        URL of gitlab instance

    Results
    -------
    g : gitlab.Gitlab
        Git remote session handle
    """
    if oauth:
        oauth = Path(oauth).expanduser()
        g = gitlab.Gitlab(private_token=oauth.read_text().strip())  # no trailing \n allowed
    else:  # unauthenticated
        g = gitlab.Gitlab(url)

    return g
