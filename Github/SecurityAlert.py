#!/usr/bin/env python3

"""
Enable / Disable Security Alerts and Vulnerability PRs for
a user/organization with repo names matching pattern

Requires GitHub Oauth login with permissions
"repo:public_repo" or "repo" for private repos.
"""

import argparse

import gitbulk as gb


def main(username: str, oauth: str, stem: str, disable: bool):
    # %% authentication
    sess = gb.session(oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, username)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)

    to_act = (repo for repo in repos if repo.name.startswith(stem) and not repo.archived)

    for repo in to_act:
        if disable:
            repo.disable_vulnerability_alert()
            repo.disable_automated_security_fixes()
            print("DISABLE: vuln alerts & auto-security PR fixes:", repo.full_name)
        else:
            repo.enable_vulnerability_alert()
            repo.enable_automated_security_fixes()
            print("ENABLE: vuln alerts & auto-security PR fixes:", repo.full_name)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Enable/Disable GitHub security alerts")
    p.add_argument("user", help="GitHub username / organizations")
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument(
        "-disable", help="instead of enabling alerts, disable alerts", action="store_true"
    )
    p.add_argument("-stem", help="act on repos with name starting with this string", default="")
    P = p.parse_args()

    main(P.user, P.oauth, P.stem, P.disable)
