#!/usr/bin/env python3

"""
Archive GitHub repos for a user/organization with repo names matching pattern.

It is NOT possible to unarchive via API, you would have to UNarchive by hand:
https://developer.github.com/v3/repos/#input

Requires GitHub Oauth login with
permissions "repo:public_repo" or "repo" for private repos.
"""

from argparse import ArgumentParser

import gitbulk.base as gb


def main():
    p = ArgumentParser(description="Set GitHub repos to Archive matching pattern")
    p.add_argument("user", help="GitHub username / organizations")
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("pattern", help="archive repos with name starting with this string")
    P = p.parse_args()

    # %% authentication
    sess = gb.session(P.oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, P.user)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)

    to_act = [repo for repo in repos if repo.name.startswith(P.pattern) and not repo.archived]
    if not to_act:
        raise SystemExit(f"There were no repos left to archive with {P.pattern} in {P.user}")

    print("NOTE: presently, you can only UNarchive through the website manually.")
    print("\ntype yes to ARCHIVE (make read-only)", "\n".join([repo.full_name for repo in to_act]))
    if input() != "yes":
        raise SystemExit("Aborted")

    for repo in to_act:
        repo.edit(archived=True)
        print("archived", repo.full_name)


if __name__ == "__main__":
    main()
