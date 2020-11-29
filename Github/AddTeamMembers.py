#!/usr/bin/env python3

"""
mass add team members to Team, optionally creating new Teams

    python AddTeamMembers.py my.xlsx ~/.ssh/orgOauth -stem sw -orgname myorg -col GitHub Team

    python AddTeamMembers.py my.xlsx ~/.ssh/orgOauth -stem sw -orgname myorg -col GitHub Team TeamName

oauth token must have "write:org" and public_repo (or repo for private) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""

import sys
import logging
import pandas
import github
import typing as T
from gitbulk import team_exists, check_api_limit, connect_github
from pathlib import Path
from argparse import ArgumentParser

USERNAME = "GitHub"
TEAMS = "Team"
NAME = "Name"


def main():
    p = ArgumentParser(description="mass add members to Teams, optionally creating new Teams")
    p.add_argument("fn", help=".xlsx with group info")
    p.add_argument("oauth", help="Oauth file")
    p.add_argument("-stem", help="beginning of Team names", default="")
    p.add_argument("-orgname", help="Github Organization", required=True)
    p.add_argument("-col", help="columns for Username, teamname", nargs="+", required=True)
    p.add_argument("-create", help="create Team if not existing", action="store_true")
    p = p.parse_args()

    fn = Path(p.fn).expanduser()

    if fn.suffix in (".xls", ".xlsx"):
        teams = pandas.read_excel(fn, usecols=p.col).squeeze().dropna()
    elif fn.suffix == ".csv":
        teams = pandas.read_csv(fn, usecols=p.col).squeeze().dropna()
    else:
        raise ValueError(f"Unknown file type {fn}")

    if not teams.ndim == 2:
        raise ValueError("need to have member names and team names. Check that -col argument matches spreadsheet.")
    # %%
    op, sess = connect_github(p.oauth, p.orgname)
    check_api_limit(sess)

    failed = adder(teams, p.stem, p.create, op, sess)
    if failed:
        print("Failed:", file=sys.stderr)
        print(failed, file=sys.stderr)


def adder(teams: pandas.DataFrame, stem: str, create: bool, op, sess) -> T.List[T.Tuple[str, str, str]]:

    failed: T.List[T.Tuple[str, str, str]] = []

    for _, row in teams.iterrows():
        if row.size == 3:
            team_name = f"{stem}{row[TEAMS]:02.0f}-{row[NAME].strip().replace(' ', '-')}"
        elif row.size == 2:
            team_name = f"{stem}{row[TEAMS]}"
        else:
            raise ValueError("I expect team number OR team number and team name")

        login = row[USERNAME].strip()
        try:
            user = sess.get_user(login)
        except github.GithubException:
            raise ValueError(f"unknown GitHub username {login}")

        if create:
            if not team_exists(op, team_name):
                print("creating Team", team_name)
                op.create_team(team_name)

        try:
            team = op.get_team_by_slug(team_name)
        except github.GithubException as e:
            logging.error(f"Could not add {user.name} {user.login} to {team.name}. Error: {e}")
            failed.append((user.name, user.login, team.name))
            continue

        try:
            # raises exception if not a member at any level
            team.get_team_membership(user)
        except github.GithubException:
            print(f"adding {user.name} {user.login} to Team {team.name}")
            team.add_membership(user, role="member")

    return failed


if __name__ == "__main__":
    main()
