#!/usr/bin/env python
"""
Set Private GitHub repos for a user/organization with repo names matching pattern

Requires GitHub Oauth login with sufficient permissions "repo:public_repo" to make public private
"repo" permission needed to see private.
"admin:org" Oauth does not work.
It's suggested you create an Oauth key for this, and then disable/delete this key permissions when done
to avoid a security issue.
To do this, including for Organizations, go to your
Username, Settings, Developer Settings, Personal Access Tokens and set repo:public_repo.
For organization private repos, you need "repo" permissions on the Oauth token.

if you get error

    github.GithubException.UnknownObjectException: 404 {'message': 'Not Found',
    'documentation_url': 'https://developer.github.com/v3/repos/#edit'}

that typically means your Oauth key doesn't have adequate permissions.

example:

    python SetPrivate.py myorg ~/.ssh/Oauth foo-
"""
from argparse import ArgumentParser
import gitutils.github_base as gb


def main():
    p = ArgumentParser()
    p.add_argument("userorgname", help="GitHub username / organizations")
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("pattern", help="make private repos with name starting with this string")
    P = p.parse_args()

    # %% authentication
    sess = gb.github_session(P.oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, P.userorgname)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)
    if not repos:
        raise SystemExit(f"no repos for {P.user}")

    to_act = [repo for repo in repos if repo.name.startswith(P.pattern) and not repo.private]
    if not to_act:
        raise SystemExit(f"no repos left matching {P.user}/{P.pattern}")

    print("\ntype affirmative to make PRIVATE", "\n".join([repo.full_name for repo in to_act]))
    if input() != "affirmative":
        raise SystemExit("Aborted")

    for repo in to_act:
        repo.edit(private=True)
        print("private:", repo.full_name)


if __name__ == "__main__":
    main()
