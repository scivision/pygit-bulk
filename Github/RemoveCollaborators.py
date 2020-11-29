#!/usr/bin/env python3

"""
Set all collaborator permission to "read" for a user/organization with repo names matching pattern.

Requires GitHub Oauth login with sufficient permissions "repo:public_repo".
"""

from argparse import ArgumentParser
import logging
import webbrowser

import gitbulk as gb


def main():
    p = ArgumentParser(description='Set all collaborator permission to "read"')
    p.add_argument("user", help="GitHub username / organizations")
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("pattern", help="modify repos with name starting with this string")
    p.add_argument("--omit", help="dont consider these admins", nargs="+")
    P = p.parse_args()

    # %% authentication
    sess = gb.session(P.oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, P.user)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)

    to_modify = [repo for repo in repos if repo.name.startswith(P.pattern)]

    print("\ntype affirmative to remove all collaborators from\n", "\n".join([repo.full_name for repo in to_modify]))
    modify = input() == "affirmative"

    for repo in to_modify:
        gb.check_api_limit(sess)

        collabs = repo.get_collaborators()

        admins = [c.login for c in collabs if c.login not in P.omit]
        if not admins:
            continue

        print("admins", repo.full_name, " ".join(admins))
        if modify:
            if repo.archived:
                logging.error(f"could not remove collabs from archived {repo.full_name}")
                webbrowser.open_new_tab("https://github.com/" + repo.full_name + "/settings")
                continue

            for admin in admins:
                repo.remove_from_collaborators(admin)


if __name__ == "__main__":
    main()
