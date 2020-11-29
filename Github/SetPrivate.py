#!/usr/bin/env python3

"""
Set Private GitHub repos for a user/organization with repo names matching pattern

Requires GitHub Oauth login with sufficient permissions "repo:public_repo" to make public private
"repo" permission needed to see private.

example:

    python SetPrivate.py myorg ~/.ssh/Oauth foo-
"""

from argparse import ArgumentParser
import gitbulk as gb


def main():
    p = ArgumentParser(description="Set Private GitHub repos for a user/organization with repo names matching pattern")
    p.add_argument("userorgname", help="GitHub username / organizations")
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("pattern", help="make private repos with name starting with this string")
    P = p.parse_args()

    # %% authentication
    sess = gb.session(P.oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, P.userorgname)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)

    to_act = [repo for repo in repos if repo.name.startswith(P.pattern) and not repo.private]
    if not to_act:
        raise SystemExit(f"There were no repos left to make private with {P.pattern} in {P.userorgname}")

    print("\ntype affirmative to make PRIVATE", "\n".join([repo.full_name for repo in to_act]))
    if input() != "affirmative":
        raise SystemExit("Aborted")

    for repo in to_act:
        repo.edit(private=True)
        print("private:", repo.full_name)


if __name__ == "__main__":
    main()
