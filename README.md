[![Build Status](https://travis-ci.com/scivision/gitedu.svg?branch=master)](https://travis-ci.com/scivision/gitedu)

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

