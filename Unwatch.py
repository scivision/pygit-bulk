#!/usr/bin/env python
"""
Unwatch repos for your Github user (that made the Oauthkey),
where the repos are in an organization with repo names matching pattern

Requires GitHub Oauth login with sufficient permissions "repo:public_repo" or "repo" for private org repos.

example:

    python Unwatch.py ~/.ssh/Oauth orgname -stem pattern

If "-stem" is omitted, all repos in "orgname" are unwatched.
"""
import argparse
from pathlib import Path

import pygithubutils.base as gb


def main(oauth: Path, orgname: str, stem: str):
    # %% authentication
    user, sess = gb.connect_github(oauth)
    gb.check_api_limit(sess)
    # %% get organization handle
    org = gb.user_or_org(sess, orgname)
    # %% prepare to loop over repos
    repos = gb.get_repos(org)

    to_act = [repo for repo in repos if user.has_in_watched(repo) and repo.name.startswith(stem)]
    if not to_act:
        raise SystemExit(f"There were no repos left to unwatch with {stem} in {orgname}")

    print("\ntype affirmative to UNWATCH", "\n".join([repo.full_name for repo in to_act]))
    if input() != "affirmative":
        raise SystemExit("Aborted")

    for repo in to_act:
        user.remove_from_watched(repo)
        print("UnWatched:", repo.full_name)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("orgname", help="Github organization name to unwatch repos from")
    p.add_argument("-stem", help="unwatch repos starting with orgname/stem", default="")
    P = p.parse_args()

    main(P.oauth, P.orgname, P.stem)
