#!/usr/bin/env python
"""
Plot number of commits in GitHub repos for a user/organization with repo names matching pattern

Requires GitHub Oauth login with sufficient permissions "repo:public_repo" or "repo" for private repos.


example

    python PlotCommits.py myorg ~/.ssh/oauth foo-


As a first pass, just shows total LoC changed. Future: plot commit vs. time.
"""
import argparse
import typing
from pathlib import Path

try:
    from matplotlib.pyplot import figure, show
except ImportError:
    figure = show = None

import pygithubutils.base as gb
import github.GithubException


def main(user: str, oauth: Path, pattern: str, only_empty: bool) -> typing.List[str]:
    # %% authentication
    sess = gb.github_session(oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, user)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)

    to_act = (repo for repo in repos if repo.name.startswith(pattern))

    empty: typing.List[str] = []
    for repo in to_act:
        print(f"examining {repo.name}", end="\r")
        authors: typing.Dict[str, int] = {}
        try:
            for commit in repo.get_commits():
                if only_empty:
                    break
                if not commit.stats:  # GitHub API bug?
                    continue
                if commit.stats.total == 0:
                    continue
                if not commit.author:  # GitHub API bug?
                    continue
                if commit.author.login in authors:
                    authors[commit.author.login] += commit.stats.total
                else:
                    authors[commit.author.login] = commit.stats.total
            if not only_empty:
                ax = figure().gca()
                ax.scatter(authors.keys(), authors.values())
                ax.get_yaxis().get_major_formatter().set_useOffset(False)
                ax.set_ylabel("total LoC changed")
                ax.set_yscale("log")
                ax.set_title(repo.name)
        except github.GithubException as exc:
            if "empty" in exc.data["message"]:
                empty.append(repo.name)
    print()  # flush stdout \r

    return sorted(empty)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("userorg", help="GitHub username / organizations")
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("pattern", help="repos with name starting with this string")
    p.add_argument("--empty", help="don't plot, just print out empty repos", action="store_true")
    P = p.parse_args()

    only_empty = P.empty or show is None

    empty = main(P.userorg, P.oauth, P.pattern, only_empty)
    print("\n".join(empty))
    show()
