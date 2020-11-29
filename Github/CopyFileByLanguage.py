#!/usr/bin/env python3

"""
mass copy files by language.
Useful for templating CI by language e.g. .github/workflows/ci_python.yml etc.

example with spreadsheet with usernames in column C, teamname in column D

    python CopyFileByLanguage.py examples/ci_python.yml .github/workflows/ci_python.yml Python ~/.ssh/oauth myorg -stem foo-

oauth token must have public_repo (or repo for private) permissions
https://developer.github.com/v3/repos/#oauth-scope-requirements
"""

from pathlib import Path
from argparse import ArgumentParser
import base64

import github
import gitbulk as gb


def main():
    p = ArgumentParser(description="mass copy files by language")
    p.add_argument("copyfn", help="file to copy into repos")
    p.add_argument("targetfn", help="path to copy file into in repos")
    p.add_argument("language", help="coding language to consider (case-sensitive)")
    p.add_argument("oauth", help="Oauth file")
    p.add_argument("userorg", help="Github Username or Organization")
    p.add_argument("-stem", help="beginning of repo names", default="")
    P = p.parse_args()

    language = P.language
    copyfn = Path(P.copyfn).expanduser().resolve(True)
    copy_text = copyfn.read_text()
    target = P.targetfn
    sess = gb.session(P.oauth)
    gb.check_api_limit(sess)
    # %% get user / organization handle
    userorg = gb.user_or_org(sess, P.userorg)
    # %% prepare to loop over repos
    repos = gb.get_repos(userorg)

    to_act = (repo for repo in repos if repo.name.startswith(P.stem))
    for repo in to_act:
        # sometimes a large amount of HTML, CSS, or docs show up as first language.
        langs = repo.get_languages()
        if not langs.get(language):
            continue
        try:
            existing = repo.get_contents(target)
            existing_code = base64.b64decode(existing.content).decode("utf8")
            if existing_code.strip() != copy_text.strip():
                print(repo.full_name, "different from", copyfn)
                repo.update_file(target, "update CI", copy_text, existing.sha)
        except github.GithubException:  # file not exist on remote
            print("copying", copyfn, "to", target, "in", repo.full_name)
            repo.create_file(target, "init CI", copy_text)


if __name__ == "__main__":
    main()
