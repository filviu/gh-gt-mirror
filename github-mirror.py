#!/usr/bin/env python3

from github import Github		# https://github.com/PyGithub/PyGithub
import requests
import json
import sys
import os

# Gitea
gitea_url = "http://127.0.0.1:3000/api/v1"
gitea_token = open(os.path.expanduser("~/.gitea-api")).read().strip()

# Target organizations to group mirrors
github_target_org = "github"
gist_target_org = "gist"
starred_target_org = "starred"
stargist_target_org = "starred-gists"

# GitHub auth
github_username = "GITHUB_USERNAME"
github_token = open(os.path.expanduser("~/.github-token")).read().strip()

gh = Github(github_token)

session = requests.Session()
session.headers.update({
    "Content-type"  : "application/json",
    "Authorization" : "token {0}".format(gitea_token),
})

print("Mirroring GitHub repos")

r = session.get("{0}/users/{1}".format(gitea_url, github_target_org))

if r.status_code != 200:
    print("Cannot get user details", file=sys.stderr)
    exit(1)

gitea_uid = json.loads(r.text)["id"]

for repo in gh.get_user().get_repos():
    if not repo.fork:

        m = {
            "repo_name"         : repo.full_name.replace("/", "-"),
            "description"       : (repo.description or "not really known")[:255],
            "clone_addr"        : repo.clone_url,
            "mirror"            : True,
            "private"           : repo.private,
            "uid"               : gitea_uid,
        }

        if repo.private:
            m["auth_username"]  = github_username
            m["auth_password"]  = "{0}".format(github_token)

        jsonstring = json.dumps(m)

        print("Mirroring", repo.full_name.replace("/", "-"))

        r = session.post("{0}/repos/migrate".format(gitea_url), data=jsonstring)
        if r.status_code != 201:            # if not CREATED
            if r.status_code == 409:        # repository exists
                continue
            print(r.status_code, r.text, jsonstring)

print("Mirroring GitHub starred repos")

r = session.get("{0}/users/{1}".format(gitea_url, starred_target_org))

if r.status_code != 200:
    print("Cannot get user details", file=sys.stderr)
    exit(1)

gitea_uid = json.loads(r.text)["id"]

for repo in gh.get_user().get_starred():
    if repo.owner.login != github_username:

        m = {
            "repo_name"         : repo.full_name.replace("/", "-"),
            "description"       : (repo.description or "not really known")[:255],
            "clone_addr"        : repo.clone_url,
            "mirror"            : True,
            "private"           : repo.private,
            "uid"               : gitea_uid,
            "topics"            : repo.topics,
        }

        if repo.private:
            m["auth_username"]  = github_username
            m["auth_password"]  = "{0}".format(github_token)

        jsonstring = json.dumps(m)

        print("Mirroring", repo.full_name.replace("/", "-"))

        r = session.post("{0}/repos/migrate".format(gitea_url), data=jsonstring)
        if r.status_code != 201:            # if not CREATED
            if r.status_code == 409:        # repository exists
                continue
            print(r.status_code, r.text, jsonstring)

print("Mirroring Gists")

r = session.get("{0}/users/{1}".format(gitea_url, gist_target_org))

if r.status_code != 200:
    print("Cannot get user id for '{0}'".format(gist_target_org), file=sys.stderr)
    exit(1)

gitea_uid = json.loads(r.text)["id"]

for gist in gh.get_user().get_gists():
    if not gist.forks:

        print("Mirroring", gist.id)
        
        m = {
            "repo_name"     : gist.id,
            "description"   : (gist.description or "not really known")[:255],
            "clone_addr"    : gist.git_pull_url,
            "mirror"        : True,
            "public"        : gist.public,
            "url"           : gist.url,
            "uid"           : gitea_uid,
        }

        if not gist.public:
            m["auth_username"]  = github_username
            m["auth_password"]  = "{0}".format(github_token)

        jsonstring = json.dumps(m)

        r = session.post("{0}/repos/migrate".format(gitea_url), data=jsonstring)
        if r.status_code != 201:            # if not CREATED
            if r.status_code == 409:        # repository exists
                continue
            print(r.status_code, r.text, jsonstring)

print("Mirroring starred gists")

r = session.get("{0}/users/{1}".format(gitea_url, stargist_target_org))

if r.status_code != 200:
    print("Cannot get user id for '{0}'".format(stargist_target_org), file=sys.stderr)
    exit(1)

gitea_uid = json.loads(r.text)["id"]

for gist in gh.get_user().get_starred_gists():
    print("Mirroring", gist.id)

    m = {
        "repo_name"     : gist.id,
        "description"   : (gist.description or "not really known")[:255],
        "clone_addr"    : gist.git_pull_url,
        "mirror"        : True,
        "public"        : gist.public,
        "url"           : gist.url,
        "uid"           : gitea_uid,
    }

    if not gist.public:
        m["auth_username"]  = github_username
        m["auth_password"]  = "{0}".format(github_token)

    jsonstring = json.dumps(m)

    r = session.post("{0}/repos/migrate".format(gitea_url), data=jsonstring)
    if r.status_code != 201:            # if not CREATED
        if r.status_code == 409:        # repository exists
            continue
        print(r.status_code, r.text, jsonstring)
