#!/usr/bin/env python3

"""
mass create repos for teams

example with spreadsheet with usernames in column C, teamname in column D

    python CreateGithubTeamRepos.py my.xlsx ~/.ssh/orgOauth myorg -stem sw -col C D

oauth token must have "admin:org" and public_repo (or repo for private) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""

import pandas
from gitbulk import connect, repo_exists, check_api_limit
from pathlib import Path
from argparse import ArgumentParser

TEAMS = "Team"
NAME = "Name"


def by_name(teams: pandas.DataFrame, stem: str, private: bool, op, sess):
    for _, row in teams.iterrows():
        reponame = f"{stem}{row[TEAMS]:02.0f}-{row[NAME]}"
        if repo_exists(op, reponame):
            continue

        print(f"creating {op.login}/{reponame}")
        op.create_repo(name=reponame, private=private)


def by_num(teams: pandas.DataFrame, stem: str, private: bool, op, sess):
    for teamnum in teams.values:
        reponame = f"{stem}{teamnum}"
        if repo_exists(op, reponame):
            continue

        print("creating", reponame)
        op.create_repo(name=reponame, private=private)


p = ArgumentParser(description="mass create repos for teams")
p.add_argument("fn", help=".xlsx with group info")
p.add_argument("oauth", help="Oauth file")
p.add_argument("orgname", help="Github Organization")
p.add_argument("-stem", help="beginning of repo names", default="")
p.add_argument(
    "-col", help="column(s) for TeamName OR TeamNumber, TeamName", nargs="+", required=True
)
p.add_argument("-private", help="create private repos", action="store_true")
P = p.parse_args()

fn = Path(P.fn).expanduser()

teams = pandas.read_excel(fn, usecols=",".join(P.col)).squeeze().dropna().drop_duplicates()
# %%
op, sess = connect(P.oauth, P.orgname)
check_api_limit(sess)

if teams.ndim == 1:
    by_num(teams, P.stem, P.private, op, sess)
elif teams.shape[1] == 2:
    by_name(teams, P.stem, P.private, op, sess)
