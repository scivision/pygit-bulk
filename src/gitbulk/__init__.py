"""
GitHub API utilities

Note: the "fine-grained" Oauth didn't work for organizations in Nov 2022.
The "classic" Oauth does work for organizations.
"""


from pathlib import Path
from datetime import datetime
import logging
import typing as T
import pandas

import github

from .get import get_collabs

__version__ = "1.1.0"

__all__ = [
    "repo_exists",
    "team_exists",
    "check_api_limit",
    "connect",
    "session",
    "get_repos",
    "user_or_org",
    "read_repos",
    "get_collabs",
]


def check_api_limit(g: github.Github | None = None) -> None:
    """
    https://developer.github.com/v3/#rate-limiting
    don't hammer the API, avoiding 502 errors

    No penalty for checking rate limits

    Parameters
    ----------
    g : optional
        GitHub session
    """
    if g is None:
        g = session()

    api_limits = g.rate_limiting  # remaining, limit
    api_remaining, api_max = api_limits
    treset = datetime.utcfromtimestamp(g.rate_limiting_resettime)  # local time

    if api_remaining == 0:
        raise ConnectionRefusedError(
            f"GitHub rate limit exceeded: {api_remaining} / {api_max}. Try again after {treset} UTC."
        )
    # it's not elif !
    if api_remaining < 10:
        logging.warning(
            ResourceWarning(
                f"approaching GitHub API limit, {api_remaining} / {api_max} remaining until {treset} UTC."
            )
        )
    else:
        logging.info(f"GitHub API limit: {api_remaining} / {api_max} remaining until {treset} UTC.")


def session(oauth: Path | str | None = None) -> github.Github:
    """
    setup Git remote session

    Parameters
    ----------

    oauth : pathlib.Path, optional
        path to file containing Oauth hash

    Results
    -------
    g : github.Github
        Git remote session handle
    """
    inp = Path(oauth).expanduser().read_text().strip() if oauth else None
    # no trailing \n allowed

    return github.Github(inp)


def connect(oauth: Path, orgname: str | None = None) -> tuple:
    """
    retrieve organizations or users

    Parameters
    ----------
    oauth : pathlib.Path
        file containing Oauth hash
    orgname : str
        organization name or username

    Results
    -------
    op : github.AuthenticatedUser.AuthenticatedUser or github.Organization.Organization
        handle to organization or user
    sess : github.Github
        Git remote session
    """

    sess = session(oauth)
    guser = sess.get_user()

    if orgname:
        assert isinstance(guser, github.AuthenticatedUser.AuthenticatedUser)

        for org in guser.get_orgs():
            if org.login == orgname:
                return org, sess
    else:
        assert isinstance(guser, github.Organization.Organization)
        return guser, sess

    raise ValueError(f"Organization {org} authentication could not be established")


def repo_exists(user: github.AuthenticatedUser.AuthenticatedUser, repo_name: str) -> bool:
    """
    Does a particular GitHub repo exist?

    Parameters
    ----------
    user : github.AuthenticatedUser.AuthenticatedUser or github.Organization.Organization
        GitHub user or organizaition handle
    repo_name : str
        repo_name under user

    Results
    -------
    exists : bool
        GitHub repo exists
    """
    exists = False
    try:
        repo = user.get_repo(repo_name)
        if repo.name:
            exists = True
    except github.GithubException as e:
        logging.info(str(e))

    return exists


def team_exists(user: github.AuthenticatedUser.AuthenticatedUser, team_name: str) -> bool:
    """
    Does a particular GitHub team exist?

    Parameters
    ----------
    user : github.AuthenticatedUser.AuthenticatedUser or github.Organization.Organization
        GitHub user or organizaition handle
    team_name : str
        team name

    Results
    -------
    exists : bool
        GitHub team exists
    """
    exists = False
    try:
        teams = user.get_teams()
        names = [t.name for t in teams]
        exists = team_name in names
    except github.GithubException as e:
        logging.info(str(e))

    return exists


def last_commit_date(sess: github.Github, name: str) -> datetime | None:
    """
    What is the last commit date to this repo.

    Equivalent to:

        git show -s --format=%cI HEAD


    Parameters
    ----------
    sess : github.Github
        GitHub session
    name : str
        name of GitHub repo e.g. pymap3d

    Results
    -------
    time : datetime.datetime
        time of last repo modification
    """

    repo = sess.get_repo(name)
    if not repo_isempty(repo):
        return repo.pushed_at

    return None


def repo_isempty(repo: github.Repository.Repository) -> bool:
    """
    is a GitHub repo empty?

    Parameters
    ----------
    repo : github.Repository
        handle to GitHub repo

    Results
    -------
    empty : bool
        GitHub repo empty
    """
    try:
        repo.get_contents("/")
        empty = False
    except github.GithubException as e:
        logging.error(f"{repo.name} is empty. \n")
        empty = True
        logging.info(str(e))

    return empty


def user_or_org(g: github.Github, user: str) -> T.Any:
    """
    Determines if user is a GitHub organization or standard user.
    This is relevant to getting private repos.

    Parameters
    ----------
    g: github.Github
        Github session handle
    user: str
        username or organization name

    Returns
    -------
    h: github.NamedUser.NamedUser or github.Organization.Organization
        the handle to the Organization or Username.
    """
    try:
        g.search_users(f"user:{user}")[0]
    except github.GithubException as e:
        raise ValueError(f"{user} not found on GitHub\n{e}")

    try:
        return g.get_organization(user)
    except github.GithubException:
        return g.get_user(user)


def read_repos(fn: Path, sheet: str) -> dict[str, str]:
    """
    make pandas.Series of email/id, Git url from spreadsheet

    Parameters
    ----------
    fn : pathlib.Path
        path to Excel spreadsheet listing usernames and repos to duplicate
    sheet : str
        name of Excel sheet to use

    Results
    -------
    repos : dict
        all the repos to duplicate
    """

    # %% get list of repos to duplicate
    fn = Path(fn).expanduser()
    repos = pandas.read_excel(fn, sheet_name=sheet, index_col=0, usecols="A, D").squeeze()
    repos.dropna(how="any", inplace=True)

    return repos.to_dict()


def get_repos(userorg: github.NamedUser.NamedUser) -> T.Iterable[github.Repository.Repository]:
    """
    get list of Repositories for a user or organization

    Parameters
    ----------
    userorg: github.NamedUser.NamedUser or github.Organization.Organization
        username or organization handle

    Returns
    -------
    repos: list of github.Repository
        all repos for a username / orgname

    https://docs.github.com/en/free-pro-team@latest/rest/reference/repos#list-repositories-for-the-authenticated-user--parameters
    """
    return userorg.get_repos(type="all")
