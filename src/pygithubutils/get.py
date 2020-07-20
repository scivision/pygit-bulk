import typing
import re

import github


def get_collabs(
    op: github.Organization.Organization, sess: github.Github, stem: str = None, regex: str = None
) -> typing.Dict[str, typing.List[str]]:
    """
    get collaborators of a GitHub repo

    Parameters
    ----------

    stem: str, optional
        repo names starts with
    regex: str, optional
        regex pattern

    Return
    ------

    collabs: dict of list of str
        collaborators on all repos selected in organization
    """
    orgmembers = [u.login for u in op.get_members()]

    collabs = {}
    rpat = re.compile(regex) if regex else None

    for repo in op.get_repos():
        if rpat and not rpat.match(repo.name):
            continue
        elif stem and not repo.name.startswith(stem):
            continue

        collabs[repo.name] = [u.login for u in repo.get_collaborators() if u.login not in orgmembers]

    return collabs
