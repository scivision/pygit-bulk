#!/usr/bin/env python3

"""
mass add team members to repos, optionally creating new repos

    python AddRepoMembers.py my.xlsx ~/.ssh/orgOauth -stem sw -orgname myorg -col GitHub Team

    python AddRepoMembers.py my.xlsx ~/.ssh/orgOauth -stem sw -orgname myorg -col GitHub Team TeamName

oauth token must have "write:org" and public_repo (or repo for private) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""

import pandas
import github
from gitbulk import repo_exists, team_exists, check_api_limit, connect
from pathlib import Path
from argparse import ArgumentParser

USERNAME = "GitHub"
TEAMS = "Team"
NAME = "Name"


def main():
    p = ArgumentParser(description="mass add team members to repos, optionally creating new repos")
    p.add_argument("fn", help=".xlsx with group info")
    p.add_argument("oauth", help="Oauth file")
    p.add_argument("-stem", help="beginning of repo names", default="")
    p.add_argument("-orgname", help="Github Organization", required=True)
    p.add_argument("-col", help="columns for Username, teamname", nargs="+", required=True)
    p.add_argument("-private", help="create private repos", action="store_true")
    p.add_argument("-create", help="create repo if not existing", action="store_true")
    p = p.parse_args()

    fn = Path(p.fn).expanduser()

    if fn.suffix in (".xls", ".xlsx"):
        teams = pandas.read_excel(fn, usecols=p.col).squeeze().dropna()
    elif fn.suffix == ".csv":
        teams = pandas.read_csv(fn, usecols=p.col).squeeze().dropna()
    else:
        raise ValueError(f"Unknown file type {fn}")

    if not teams.ndim == 2:
        raise ValueError(
            "need to have member names and team names. Check that -col argument matches spreadsheet."
        )
    # %%
    op, sess = connect(p.oauth, p.orgname)
    check_api_limit(sess)

    adder(teams, p.stem, p.private, p.create, op, sess)


def adder(teams: pandas.DataFrame, stem: str, private: bool, create: bool, op, sess):
    for _, row in teams.iterrows():
        if row.size == 3:
            repo_name = f"{stem}{row[TEAMS]:02.0f}-{row[NAME]}"
        elif row.size == 2:
            repo_name = f"{stem}{row[TEAMS]}"
        else:
            raise ValueError("I expect team number OR team number and team name")

        login = row[USERNAME].strip()
        try:
            user = sess.get_user(login)
        except github.GithubException:
            raise ValueError(f"unknown GitHub username {login}")

        if create:
            if not repo_exists(op, repo_name):
                print("creating repository", repo_name)
                op.create_repo(name=repo_name, private=private)

            # NOTE: for now, each team has one repo of same name as team
            if not team_exists(op, repo_name):
                print("creating Team", repo_name)
                op.create_team(repo_name, op.get_repo(repo_name))

        team = op.get_team_by_slug(repo_name)
        try:
            # raises exception if not a member at any level
            team.get_team_membership(user)
        except github.GithubException:
            print(f"adding {user.name} {user.login} to Team {team.name}")
            team.add_membership(user, role="member")


if __name__ == "__main__":
    main()
