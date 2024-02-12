"""
maximum Github username length ~39 characters
"""

import pytest
import random
import string

import gitbulk as pgu

random_username = "".join(random.choice(string.ascii_lowercase) for i in range(32))
OK_username = "microsoft"


def test_bad_username():
    with pytest.raises(ValueError):
        pgu.user_or_org(pgu.session(), random_username)


def test_get_repos():
    try:
        userorg = pgu.user_or_org(pgu.session(), OK_username)
        repos = pgu.get_repos(userorg)
    except ConnectionRefusedError:
        pytest.skip("GitHub API limit exceeded")

    assert repos[0]
