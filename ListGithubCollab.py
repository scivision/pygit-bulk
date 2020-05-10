#!/usr/bin/env python
"""
Lists collaborators for GitHub repo or repos starting with pattern.

Optionally with -xls use a spreadsheet filename and column to find Github usernames
that haven't accepted their invite yet (assuming you sent it previously).

    python ListGithubCollab.py ~/.ssh/oauth myowg -stem foo- -xls users.xlsx C

oauth token must have "read:org" (and "repo" for private repos) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""
from argparse import ArgumentParser
import pandas
from pathlib import Path
import itertools

from pygithubutils import check_api_limit, connect_github, get_collabs


def main(P):
    op, sess = connect_github(P.oauth, P.orgname)
    if not check_api_limit(sess):
        raise RuntimeError("GitHub API limit exceeded")

    return get_collabs(op, sess, P.stem, P.regex)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("orgname", help="Github organization name")
    p.add_argument("-stem", help="reponame starts with")
    p.add_argument("-regex", help="regex pattern of reponame")
    p.add_argument("-xls", help="spreadsheet filename and column to find missing usernames (who isn't signed up)", nargs=2)
    P = p.parse_args()

    collabs = main(P)

    for k in sorted(collabs.keys()):
        print(k, collabs[k])

    if P.xls:
        xlsfn = Path(P.xls[0]).expanduser()
        required = pandas.read_excel(xlsfn, usecols=P.xls[1]).squeeze().tolist()
        present = list(itertools.chain.from_iterable(collabs.values()))

        missing = set(required).difference(present)
        print("Missing:\n", missing)
