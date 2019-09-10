#!/usr/bin/env python
"""
mass create repos for teams

example with spreadsheet with usernames in column C, teamname in column DeprecationWarning

python CreateGithubTeamRepos.py my.xlsx ~/.ssh/orgOauth -stem sw -orgname myorg -col C D

oauth token must have "admin:org" and public_repo (or repo for private) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""
import pandas
from gitutils.github_base import connect_github, repo_exists, check_api_limit
from pathlib import Path
from argparse import ArgumentParser


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

    teams = pandas.read_excel(fn, usecols=",".join(p.col)).squeeze().dropna().drop_duplicates()
    # %%
    op, sess = connect_github(p.oauth, p.orgname)

    name_num(teams, p.stem, p.private, op, sess)


def name_num(teams: pandas.DataFrame, stem: str, private: bool, op, sess):
    for teamname, teamnum in teams.items():
        if not check_api_limit(sess):
            raise RuntimeError("GitHub API limit exceeded")

        if teams.ndim == 2:
            reponame = f"{stem}{teamnum:02d}-{teamname}"
        elif teams.ndim == 1:
            reponame = f"{stem}{teamnum}"
        else:
            raise ValueError("not sure the format of teams / xlsx")

        if repo_exists(op, reponame):
            continue

        print("creating", reponame)
        op.create_repo(name=reponame, private=private)


if __name__ == "__main__":
    main()
