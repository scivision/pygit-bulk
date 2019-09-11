#!/usr/bin/env python
"""
Plot number of commits in GitHub repos for a user/organization with repo names matching pattern

Requires GitHub Oauth login with sufficient permissions "repo:public_repo" or "repo" for private repos.
(admin:org Oauth does not work)

if you get error

    github.GithubException.UnknownObjectException: 404 {'message': 'Not Found',
    'documentation_url': 'https://developer.github.com/v3/repos/#edit'}

that typically means your Oauth key doesn't have adequte permissions.

example

    python PlotCommits.py myorg ~/.ssh/oauth foo-


As a first pass, just shows total LoC changed. Future: plot commit vs. time.
"""
from argparse import ArgumentParser
import typing
from matplotlib.pyplot import figure, show

import gitutils.github_base as gb
import github.GithubException


def main() -> typing.List[str]:
    p = ArgumentParser()
    p.add_argument("user", help="GitHub username / organizations")
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("pattern", help="repos with name starting with this string")
    P = p.parse_args()

    # %% authentication
    sess = gb.github_session(P.oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, P.user)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)
    if not repos:
        raise SystemExit(f"no repos for {P.user}")

    to_act = (repo for repo in repos if repo.name.startswith(P.pattern))

    empty: typing.List[str] = []
    for repo in to_act:
        authors: typing.Dict[str, int] = {}
        try:
            for commit in repo.get_commits():
                if commit.stats.total == 0:
                    continue
                if commit.author.login in authors:
                    authors[commit.author.login] += commit.stats.total
                else:
                    authors[commit.author.login] = commit.stats.total
            ax = figure().gca()
            ax.scatter(authors.keys(), authors.values())
            ax.get_yaxis().get_major_formatter().set_useOffset(False)
            ax.set_ylabel("total LoC changed")
            ax.set_yscale("log")
            ax.set_title(repo.name)
        except github.GithubException as exc:
            if "empty" in exc.data["message"]:
                empty += repo.name

    return sorted(empty)


if __name__ == "__main__":
    empty = main()
    print("\n".join(empty))
    show()
