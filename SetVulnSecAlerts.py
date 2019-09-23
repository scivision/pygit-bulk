#!/usr/bin/env python
"""
Enables Security Alerts and Vulnerability PRs for a user/organization with repo names matching pattern

Requires GitHub Oauth login with sufficient permissions "repo:public_repo" or "repo" for private repos.

This requires PyGithub > 1.43.8, added in https://github.com/PyGithub/PyGithub/commit/8abd50e225767c63c5f61231095fee0c8684d7b4
"""
import argparse
import pygithubutils.base as gb


def main(username: str, oauth: str, stem: str):
    # %% authentication
    sess = gb.github_session(P.oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, P.user)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)

    to_act = (repo for repo in repos if repo.name.startswith(stem) and not repo.archived and not repo.get_vulnerability_alert())

    for repo in to_act:
        repo.enable_vulnerability_alert()
        repo.enable_automated_security_fixes()
        print("enable vuln alerts and auto-security PR fixes:", repo.full_name)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("user", help="GitHub username / organizations")
    p.add_argument("oauth", help="Oauth filename")
    p.add_argument("-stem", help="act on repos with name starting with this string", default="")
    P = p.parse_args()

    main(P.user, P.oauth, P.stem)
