#!/usr/bin/env python
"""
Lists collaborators for GitHub repo or repos starting with pattern.

"""
from argparse import ArgumentParser
from gitedu import get_collabs

PAT = r'^19\-\d\d\-'


def main():
    p = ArgumentParser()
    p.add_argument('orgname', help='Github organization name')
    p.add_argument('-a', '--oauth', help='Oauth filename')

    p = p.parse_args()

    collabs = get_collabs(p.orgname, p.oauth, PAT)

    print(collabs)


if __name__ == '__main__':
    main()
