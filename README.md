[![Actions Status](https://github.com/scivision/gitedu/workflows/ci/badge.svg)](https://github.com/scivision/gitedu/actions)

# Git EDU

Git and site-specific API (e.g. GitHub) utilities for managing large numbers (100+) of users for education and institutions.
Input / output is often via spreadsheet, as a gateway to APIs of other services such as Blackboard.

Note: Some of these tasks can also be done directly in
[GitHub Education](https://education.github.com/).

For example:

* create repo for each team project (CreateGithubTeamRepos.py)
* mass-add per-project collaborators (AddGithubCollab.py)
* duplicate (mirror) lots of repos (DuplicateGithubRepos.p)

This was moved out of
[GitMC](https://github.com/scivision/gitutils)
due to the site-specific and heavy API use, whereas GitUtils focuses more on plain agnostic Git tasks.


## Mass duplicate GitHub repos

`DuplicateGithubRepos`
based on spreadsheet input, mass duplicate GitHub repos.

## API Key

Python GitHub [API](https://pypi.org/project/PyGithub/)

Most users will need a GitHub API token, as the unauthenticated API access is severly limited.

1. [Generate](https://github.com/settings/tokens) GitHub API token with ONLY the `user:email` permission.
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

    github.GithubException.UnknownObjectException: 404 {'message': 'Not Found',
    'documentation_url': 'https://developer.github.com/v3/repos/#edit'}

that typically means your Oauth key doesn't have adequate permissions.