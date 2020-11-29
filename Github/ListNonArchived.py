#!/usr/bin/env python3

"""
List all non-archived repos (public and private,
if Oauth key has "repo" permission)

Requires GitHub Oauth login with permissions
"repo:public_repo" or "repo" for private repos.
"""

import argparse

import gitbulk as gb


def main(username: str, oauth: str, stem: str):
    # %% authentication
    sess = gb.session(P.oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, P.user)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)

    to_act = (repo for repo in repos if repo.name.startswith(stem) and not repo.archived)

    for repo in to_act:
        print(repo.full_name)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="List all non-archived repos")
    p.add_argument("user", help="GitHub username / organizations")
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("-stem", help="list repos with name starting with this string", default="")
    P = p.parse_args()

    main(P.user, P.oauth, P.stem)
