#!/usr/bin/env python3
"""
List all non-licensed repos (public and private,
if Oauth key has "repo" permission)

Requires GitHub Oauth login with permissions
"repo:public_repo" or "repo" for private repos.
"""
import argparse
import github.GithubException

import pygithubutils as gb


def main(username: str, oauth: str, stem: str):
    # %% authentication
    sess = gb.github_session(P.oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, P.user)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)

    # filter repos
    to_act = (
        repo
        for repo in repos
        if repo.name.startswith(stem)
        and repo.name != ".github"
        and not repo.fork
        and not repo.archived
        and repo.owner.login == userorg.login
    )

    for repo in to_act:
        try:
            repo.get_license()
        except github.GithubException:
            print(repo.full_name)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="List all non-licensed repos")
    p.add_argument("user", help="GitHub username / organizations")
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("-stem", help="list repos with name starting with this string", default="")
    P = p.parse_args()

    main(P.user, P.oauth, P.stem)
