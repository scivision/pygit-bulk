"""
How many total GitHub stars do you have?
"""

from __future__ import annotations
from time import sleep
from pathlib import Path
import github
import logging

from .base import check_api_limit, session, get_repos, user_or_org


def repo_prober(
    user: str,
    oauth: Path | None = None,
    branch: str | None = None,
    starsonly: bool = False,
    verbose: bool = False,
) -> tuple[list[tuple[str, int, int]], list[tuple[str, int]]]:
    """
    probe all GitHub repos for a user to see how much forks of each repo are ahead.
    Discover if there is an actively developed fork of your GitHub repos

    Parameters
    ----------
    user : str
        GitHub username
    oauth : pathlib.Path, optional
        file containing GitHub Oauth hash
    branch : str, optional
        Git branch to examine
    starsonly: bool, optional
        far faster to only count forks and stars
    verbose : bool, optional
        verbosity

    Results
    -------
    counts : list of tuple of str, int, int
        forks and stars for each repo
    ahead : list of tuple of str, int
        forked with repos with number of commits they're ahead of your repo
    """
    # %% authentication
    sess = session(oauth)
    check_api_limit(sess)
    userorg = user_or_org(sess, user)
    # %% prepare to loop over repos
    repos = get_repos(userorg)

    counts: list[tuple[str, int, int]] = []
    ahead: list[tuple[str, int]] = []

    for repo in repos:
        if not starsonly:
            ahead += fork_prober(repo, sess, ahead, branch, verbose)

        counts.append((repo.name, repo.forks_count, repo.stargazers_count))  # type: ignore
        # FIXME: bug in PyGithub fixed by https://github.com/PyGithub/PyGithub/pull/1513

        check_api_limit(sess)

    return counts, ahead


def fork_prober(
    repo: github.Repository.Repository,
    sess: github.Github,
    ahead: list[tuple[str, int]],
    branch: str | None = None,
    verbose: bool = False,
) -> list[tuple[str, int]]:
    """
    check a GitHub repo for forks

    Parameters
    ----------
    repo :
        handle to GitHub repo
    sess :
        handle to GitHub session
    ahead : list of tuple of str, int
        forked with repos with number of commits they're ahead of your repo
    branch : str, optional
        Git branch to examine
    verbose : bool, optional
        verbosity

    Results
    -------
    ahead : list of tuple of str, int
        forked with repos with number of commits they're ahead of your repo
    """
    check_api_limit(sess)

    b = repo.default_branch if not branch else branch

    try:
        master = repo.get_branch(b)
    except github.GithubException as e:
        logging.error(f"{repo.full_name}  {e}")
        return ahead

    forks = repo.get_forks()
    for fork in forks:
        sleep(0.1)  # don't hammer the API, avoiding 502 errors

        check_api_limit(sess)

        try:
            fmaster = fork.get_branch(b)
        except github.GithubException as e:
            if (
                e.data["message"] == "Not Found"
            ):  # repo/branch that they deleted  FIXME: should we check their default branch?
                continue

            logging.error(f"{repo.full_name} {fork.full_name}  {e}")
            continue

        try:
            comp = repo.compare(master.commit.sha, fmaster.commit.sha)
        except github.GithubException as excp:
            # if excp.data["message"].startswith("No common ancestor"):
            #     continue

            logging.error(f"{repo.full_name} {fork.full_name}  {excp}")
            continue

        if comp.ahead_by:
            ahead.append((fork.full_name, comp.ahead_by))
            print(f"{fork.full_name} ahead by {comp.ahead_by}", end="")
            if verbose and comp.behind_by:
                print(f"behind by {comp.behind_by}", end="")
            print()

    return ahead
