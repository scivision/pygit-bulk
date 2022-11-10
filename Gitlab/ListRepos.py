#!/usr/bin/env python3

"""
List all Git repos of a user / organization.

For organization private repos, you will need "repo" Oauth permission.
Restricted "Third-party application access policy"
from organization oauth_application_policy settings is OK.

Without Oauth, you will only see public repos
"""

from argparse import ArgumentParser

import gitbulk.gitlab as gb


def main():
    p = ArgumentParser(description="List user/organization repos")
    p.add_argument("user", help="Git remote username / organization name")
    p.add_argument("oauth", help="Oauth filename", nargs="?")
    P = p.parse_args()

    # %% authentication
    sess = gb.session(P.oauth)
    # %% get user / organization handle
    user = sess.users.list(username=P.user)[0]
    # %% prepare to loop over projects
    repos = user.projects.list()

    for repo in repos:
        print(repo.name)


if __name__ == "__main__":
    main()
