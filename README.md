# Git EDU

Git and site-specific API (e.g. GitHub) utilities for managing large numbers (100+) of users for education and institutions.
Input / output is often via spreadsheet, as a gateway to APIs of other services such as Blackboard.

For example:

* create repo for each team project (CreateGithubTeamRepos.py)
* mass-add per-project collaborators (AddGithubCollab.py)
* duplicate (mirror) lots of repos (DuplicateGithubRepos.p)

This was moved out of [GitUtils](https://github.com/scivision/gitutils) due to the site-specific and heavy API use, whereas GitUtils focuses more on plain agnostic Git tasks.


## Mass duplicate GitHub repos

`DuplicateGithubRepos`
based on spreadsheet input, mass duplicate GitHub repos.
