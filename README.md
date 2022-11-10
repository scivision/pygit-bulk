# Git Bulk operations

![Actions Status](https://github.com/scivision/pygit-bulk/workflows/ci/badge.svg)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/scivision/pygit-bulk.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/scivision/pygit-bulk/context:python)

Git remote (GitHub, GitLab) API utilities for managing large numbers (10..1000) of users and repositories for education and institutions.
For very large number of repos say 1000+, it may be more useful and fast to use the GraphQL GitHub v4 API.
Input / output is often via spreadsheet, as a gateway to APIs of other services such as Blackboard.
This repository helps us avoid having to use
[GitHub Education](https://education.github.com/).

For example:

* create repo for each team project (CreateGithubTeamRepos.py)
* mass-add per-project collaborators (AddGithubCollab.py)
* duplicate (mirror) lots of repos (DuplicateGithubRepos.p)

We also maintain Python-based Git
[utilities](https://github.com/scivision/gitmc)
useful for managing large numbers of local Git repositories on a computer.

API access via:

* GitHub v3 API: [PyGithub](https://pypi.org/project/PyGithub/)
* GitLab v4 API: [Python-Gitlab](https://python-gitlab.readthedocs.io/)

Note: Scripts for each remote Git service are located under:

* [GitHub](./Github) We have many more GitHub scripts as GitHub is more popular
* [GitLab](./Gitlab) will add more here as users desire

## Popularity

An important feature in

```sh
python CountGithubForks.py username
```
is showing which forks of your repos have had changes "ahead of" the parent repo.

---

Count how many total GitHub stars a GitHub account has:

```sh
python CountGithubStars.py username
```

That will take a couple seconds even for large numbers of repos.


## Mass duplicate GitHub repos

`DuplicateGithubRepos`
based on spreadsheet input, mass duplicate GitHub repos.

## API Key

Users will need a GitHub API token, as the unauthenticated API access is severely limited.

1. [Generate](https://github.com/settings/tokens) GitHub API token with permission appropriate to the PyGitHub Utilities script being used.
2. Copy that text string to a secure location on your computer.

### permissions

For public repos, "public_repo" is needed.
For private repos, "repo" is needed.

"admin:org" Oauth does not work.

It's suggested you create an Oauth key for this, and then disable/delete this key permissions when done
to avoid a security issue.
To do this, including for Organizations, go to your
Username, Settings, Developer Settings, Personal Access Tokens and set repo:public_repo.
For organization private repos, you need "repo" permissions on the Oauth token.

if you get error

```
github.GithubException.UnknownObjectException: 404 {'message': 'Not Found',
'documentation_url': 'https://developer.github.com/v3/repos/#edit'}
```

that typically means your Oauth key doesn't have adequate permissions.
