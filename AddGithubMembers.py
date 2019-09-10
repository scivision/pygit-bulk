#!/usr/bin/env python
"""
mass add team members to repos

python CreateGithubTeamRepos.py my.xlsx ~/.ssh/orgOauth -stem sw -orgname myorg -col B C

oauth token must have "write:org" and public_repo (or repo for private) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""
import pandas
from gitutils.github_base import repo_exists, check_api_limit, connect_github
from pathlib import Path
import warnings
from argparse import ArgumentParser

USERNAME = "GitHub"
TEAMS = "Team"


def main():
    p = ArgumentParser()
    p.add_argument("fn", help=".xlsx with group info")
    p.add_argument("oauth", help="Oauth file")
    p.add_argument("-stem", help="beginning of repo names", default="")
    p.add_argument("-orgname", help="Github Organization", required=True)
    p.add_argument("-col", help="columns for Username, teamname", nargs="+", required=True)
    p.add_argument("-private", action="store_true")
    p = p.parse_args()

    fn = Path(p.fn).expanduser()

    teams = pandas.read_excel(fn, usecols=",".join(p.col)).squeeze().dropna()
    if not teams.ndim == 2:
        raise ValueError("need to have member names and team names. Check that -col argument matches spreadsheet.")
    # %%
    op, sess = connect_github(p.oauth, p.orgname)

    name_num(teams, p.stem, p.private, op, sess)


def name_num(teams: pandas.DataFrame, stem: str, private: bool, op, sess):
    for _teamname, row in teams.iterrows():
        if not check_api_limit(sess):
            raise RuntimeError("GitHub API limit exceeded")

        reponame = f'{stem}{row["Team"]}'
        username = row[USERNAME]

        if not repo_exists(op, reponame):
            print("creating", reponame)
            op.create_repo(name=reponame, private=private)

        repo = op.get_repo(reponame)

        if not repo.has_in_collaborators(username):
            try:
                repo.add_to_collaborators(username)
                print(f"{username} invited to {reponame}")
            except Exception:
                warnings.warn(f"failed to invite {username} to {reponame}")


if __name__ == "__main__":
    main()
