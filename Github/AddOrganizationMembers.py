#!/usr/bin/env python3

"""
mass add users to organization

    python AddOrganizationMembers.py my.xlsx ~/.ssh/orgOauth -orgname myorg -col Username

oauth token must have "write:org" and public_repo (or repo for private) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""

import pandas
import github
from gitbulk import check_api_limit, connect
from pathlib import Path
from argparse import ArgumentParser


def main():
    p = ArgumentParser(description="mass add team members to repos, optionally creating new repos")
    p.add_argument("fn", help=".xlsx with group info")
    p.add_argument("oauth", help="Oauth file")
    p.add_argument("-orgname", help="Github Organization", required=True)
    p.add_argument("-col", help="column for GitHub Username", required=True)
    p = p.parse_args()

    fn = Path(p.fn).expanduser()

    if fn.suffix in (".xls", ".xlsx"):
        users = pandas.read_excel(fn, usecols=p.col).squeeze().dropna()
    elif fn.suffix == ".csv":
        users = pandas.read_csv(fn, usecols=p.col).squeeze().dropna()
    else:
        raise ValueError(f"Unknown file type {fn}")

    if not users.ndim == 1:
        raise ValueError("need to have member names. Check that -col argument matches spreadsheet.")
    # %%
    op, sess = connect(p.oauth, p.orgname)
    check_api_limit(sess)

    adder(users, op, sess)


def adder(users: pandas.DataFrame, op, sess):
    members = [m.login for m in op.get_members()]
    invited = [m.login for m in op.invitations()]

    for u in users:
        login = u.strip()
        if login in members or login in invited:
            continue

        try:
            user = sess.get_user(login)
        except github.GithubException:
            raise ValueError(f"unknown GitHub username {login}")

        op.add_to_members(user)
        print(f"invited: {login}")


if __name__ == "__main__":
    main()
