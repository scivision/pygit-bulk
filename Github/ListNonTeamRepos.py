#!/usr/bin/env python3

"""
List repos in an organization not belonging to any team

    python ListNonTeamRepos.py ~/.ssh/orgOauth myorg

oauth token must have public_repo (or repo for private) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""

import typing as T
from argparse import ArgumentParser

import github
import gitbulk as gb


def main():
    p = ArgumentParser(description="List organziation repos not in any team")
    p.add_argument("oauth", help="Oauth file")
    p.add_argument("orgname", help="Github Organization")
    p.add_argument("-stem", help="repos startin with this")
    p.add_argument("-put_team", help="put matching repos in this team")
    p = p.parse_args()

    op, sess = gb.connect_github(p.oauth, p.orgname)
    gb.check_api_limit(sess)

    lister(op, sess, p.stem, p.put_team)


def lister(op, sess, stem: str | None = None, put_team: str | None = None):
    """
    list matching repos
    optionally, add to specified EXISTING team
    """

    if put_team and not gb.team_exists(op, put_team):
        raise ValueError(f"Team {put_team} does not exist in {op.login}")

    # %% get user / organization handle
    userorg = gb.user_or_org(sess, op.login)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)

    to_act: T.Iterable[github.Repository.Repository]
    if stem:
        to_act = (repo for repo in repos if repo.name.startswith(stem))
    else:
        to_act = repos

    for repo in to_act:
        teams = repo.get_teams()
        if teams.totalCount == 0:
            if put_team:
                print(repo.name, "=>", put_team)
                team = op.get_team_by_slug(put_team)
                team.add_to_repos(repo)
            else:
                print(repo.name)


if __name__ == "__main__":
    main()
