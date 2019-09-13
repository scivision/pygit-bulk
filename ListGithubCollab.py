#!/usr/bin/env python
"""
Lists collaborators for GitHub repo or repos starting with pattern.

oauth token must have "read:org" (and "repo" for private repos) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""
from argparse import ArgumentParser
from gitedu.get import get_collabs
from gitutils.github_base import check_api_limit, connect_github


def main():
    p = ArgumentParser()
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("orgname", help="Github organization name")
    p.add_argument("-stem", help="reponame starts with")
    p.add_argument("-regex", help="regex pattern of reponame")
    P = p.parse_args()

    op, sess = connect_github(P.oauth, P.orgname)
    if not check_api_limit(sess):
        raise RuntimeError("GitHub API limit exceeded")

    collabs = get_collabs(op, sess, P.stem, P.regex)

    for k, v in collabs.items():
        print(k, v)


if __name__ == "__main__":
    main()
