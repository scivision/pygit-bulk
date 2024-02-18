from time import sleep
from pathlib import Path
import subprocess
import logging
import tempfile
from datetime import datetime
import webbrowser
import shutil
import functools

from .base import connect, check_api_limit, last_commit_date, repo_exists


@functools.cache
def git_exe() -> str:
    """
    Find git executable
    """

    if not (git := shutil.which("git")):
        raise ImportError("Git not found")
    return git


def repo_dupe(repos: dict[str, str], oauth: Path, orgname: str | None = None, stem: str = ""):
    """
    Duplicate GitHub repos AND their wikis

    Parameters
    ----------
    repos: dict of str, str
        GitHub username, reponame to duplicate
    oauth: pathlib.Path
        GitHub Oauth token  https://github.com/settings/tokens
    orgname: str
        create repos under Organization instead of username
    stem: str
        what to start new repo name with
    """
    # %% authenticate
    op, sess = connect(oauth, orgname)

    username = op.login

    # %% prepare to loop over repos
    for email, oldurl in repos.items():
        check_api_limit(sess)

        oldurl = oldurl.replace("https", "ssh")
        oldname = "/".join(oldurl.split("/")[-2:]).split(".")[0]

        oldtime = last_commit_date(sess, oldname)
        if oldtime is None:
            continue

        mirrorname = stem + email

        gitdupe(oldurl, oldtime, username, mirrorname, op)
        gitdupe(oldurl, None, username, mirrorname, op, iswiki=True)

        sleep(0.1)


def gitdupe(
    oldurl: str,
    oldtime: datetime | None,
    username: str,
    mirrorname: str,
    op,
    iswiki: bool = False,
):
    if iswiki:
        oldurl += ".wiki.git"
        mirrorname += ".wiki.git"
        try:
            subprocess.check_call(
                [git_exe(), "ls-remote", "--exit-code", oldurl], stdout=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            logging.error(f"{oldurl} has no Wiki")
            return

    newname = f"{username}/{mirrorname}"
    newurl = f"ssh://github.com/{newname}"

    if not iswiki:
        exists = repo_exists(op, mirrorname)
        if exists:
            newrepo = op.get_repo(mirrorname)
            if newrepo.pushed_at >= oldtime:
                return

    else:
        try:
            subprocess.check_call(
                [git_exe(), "ls-remote", "--exit-code", newurl],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except subprocess.CalledProcessError:
            exists = True

    print("\n", oldurl, "\n")

    with tempfile.TemporaryDirectory() as d:
        tmprepo = Path(d)
        # 1. bare clone
        cmd = [git_exe(), "clone", oldurl] if iswiki else ["git", "clone", "--bare", oldurl]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, cwd=tmprepo)

        # 2. create new repo
        if not exists:
            op.create_repo(name=mirrorname, private=True, has_wiki=True)

        # 3. mirror to new repo

        if iswiki:
            dupewiki(tmprepo, oldurl, newurl)
        else:
            pwd = tmprepo / (oldurl.split("/")[-1])
            pwd = pwd.with_suffix(".git")

            cmd = [git_exe(), "push", "--mirror", newurl]
            subprocess.check_call(cmd, cwd=pwd)


def dupewiki(prepo: Path, oldurl: str, newurl: str):
    """
    Note: GitLab API has Wiki included, but at this time, GitHub API does not cover Wiki
    """
    pwd = prepo / (oldurl.split("/")[-1]).split(".git")[0]

    subprocess.check_call(
        [git_exe(), "remote", "set-url", "origin", newurl], cwd=pwd, stdout=subprocess.DEVNULL
    )

    browseurl = newurl
    browseurl = browseurl.replace("ssh", "https").replace(".wiki.git", "/wiki")
    webbrowser.open_new_tab(browseurl)
    sleep(10.0)  # TODO: use suprocess.run() instead of webbrowser

    subprocess.check_call([git_exe(), "push", "-f"], cwd=pwd)
