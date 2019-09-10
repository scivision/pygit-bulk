import typing
import re

from gitutils.github_base import check_api_limit, connect_github


def get_collabs(orgname: str, oauth: str = None, pat: str = None) -> typing.Dict[str, typing.List[str]]:
    op, sess = connect_github(oauth, orgname)

    if not check_api_limit(sess):
        raise RuntimeError("GitHub API limit exceeded")

    orgmembers = [u.login for u in op.get_members()]

    collabs = {}
    rpat = re.compile(pat) if pat else None

    repos = op.get_repos()
    for repo in repos:
        if rpat and not rpat.match(repo.name):
            continue

        if not check_api_limit(sess):
            raise RuntimeError("GitHub API limit exceeded")

        collabs[repo.name] = [u.login for u in repo.get_collaborators() if u.login not in orgmembers]

    return collabs
