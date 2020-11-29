#!/usr/bin/env python3

"""
Add staff (set of people) to teams matching pattern

    python AddStaffToTeams.py ~/.ssh/orgOauth myorg -stem Foo -staff user1 user2 ...

oauth token must have public_repo (or repo for private) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""

import typing as T
import github
import gitbulk as gb
from argparse import ArgumentParser


def main():
    p = ArgumentParser(description="add staff to teams")
    p.add_argument("oauth", help="Oauth file")
    p.add_argument("orgname", help="Github Organization")
    p.add_argument("-stem", help="repos startin with this", required=True)
    p.add_argument("-staff", help="put matching repos in this team", nargs="+", required=True)
    p = p.parse_args()

    op, sess = gb.connect_github(p.oauth, p.orgname)
    gb.check_api_limit(sess)

    adder(op, sess, p.stem, p.staff)


def adder(op, sess, stem: str, staff: T.Sequence[str]):
    """
    add staff to teams
    """

    # %% get organization handle
    org = sess.get_organization(op.login)
    # %% prepare to loop over repos
    teams = org.get_teams()

    to_act = (t for t in teams if t.name.startswith(stem))

    logins = []
    for s in staff:
        # need to check org membership, otherwise you can accidentally add any Github user
        # even strangers
        try:
            u = sess.get_user(s)
            if org.has_in_members(u):
                logins.append(u)
            else:
                raise ValueError(f"{s} is not a member of {org.name}")
        except github.GithubException:
            raise ValueError(f"{s} is not a member of {org.name}")

    for team in to_act:
        for L in logins:
            if not team.has_in_members(L):
                print(f"{L.login} + Team {team.name}")
                team.add_membership(L, role="member")


if __name__ == "__main__":
    main()
