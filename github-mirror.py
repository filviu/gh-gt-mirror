#!/usr/bin/env python3

from github import Github         # https://github.com/PyGithub/PyGithub
from pprint import pprint

import os
import sys
import requests
import json
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def needenv(name):
    val = os.environ.get(name)
    if val is None:
        sys.exit('{} is required.'.format(name))
    return val

# Gitea
gitea_api_url = needenv('GITEA_API_URL')
gitea_token = needenv('GITEA_API_TOKEN')

# Target organizations to group mirrors
github_target_org = os.getenv('GITHUB_TARGET_ORG')
github_starred_org = os.getenv('GITHUB_STARRED_ORG')
gist_target_org = os.getenv('GIST_TARGET_ORG')
giststar_target_org = os.getenv('GISTSTAR_TARGET_ORG')

# GitHub auth
github_username = needenv('GITHUB_USERNAME')
github_token = needenv('GITHUB_API_TOKEN')

# filtering
github_only_owner = os.getenv('GITHUB_ONLY_OWNER','False').lower() in ('true', '1', 't', 'yes')
github_mirror_forks = os.getenv('GITHUB_MIRROR_FORKS', 'False').lower() in ('true', '1', 't', 'yes')
github_filter_orgs = os.getenv('GITHUB_FILTER_ORGS',"").split(',')

gh = Github(github_token)

session = requests.Session()
session.headers.update({
    "Content-type"  : "application/json",
    "Authorization" : "token {0}".format(gitea_token),
})

if github_target_org:
    logging.info("Mirroring GitHub repos to \"%s\"", github_target_org)
    r = session.get("{0}/users/{1}".format(gitea_api_url, github_target_org))

    if r.status_code != 200:
        logging.error("Cannot get user details")
        exit(1)

    gitea_uid = json.loads(r.text)["id"]

    
    for repo in gh.get_user().get_repos():
        # Best thing I could think of to get away with nested ifs
        if github_only_owner and repo.owner.login != github_username:
            logging.info("Skipping \"%s\" because it is not owned by \"%s\" and GITHUB_ONLY_OWNER is set", repo.full_name, github_username)
            continue
        if repo.owner.login in github_filter_orgs:
            logging.info("Skipping \"%s\" because \"%s\" is a filtered organization", repo.full_name, repo.owner.login)
            continue
        if not github_mirror_forks and repo.fork:
            logging.info("Skipping \"%s\" because it is a fork and GITHUB_MIRROR_FORKS is false", repo.full_name)
            continue

        m = {
            "repo_name"         : repo.full_name.replace("/", "-"),
            "repo_owner"        : github_target_org,
            "description"       : (repo.description or "not really known")[:255],
            "clone_addr"        : repo.clone_url,
            "mirror"            : True,
            "private"           : repo.private,
            "uid"               : gitea_uid,
        }

        if repo.private:
            m["auth_username"]  = github_username
            m["auth_token"]  = github_token

        jsonstring = json.dumps(m)

        logging.info("Mirroring \"%s\"", repo.full_name)
        r = session.post("{0}/repos/migrate".format(gitea_api_url), data=jsonstring)
        if r.status_code != 201:            # if not CREATED
            if r.status_code == 409:        # repository exists
                continue
            logging.info(r.status_code, r.text, jsonstring)
else:
    logging.info("Skipping GitHub repositories because GITHUB_TARGET_ORG is not set")

if github_starred_org:
    logging.info("Mirroring GitHub starred repos to \"%s\"", github_starred_org)

    r = session.get("{0}/users/{1}".format(gitea_api_url, github_starred_org))

    if r.status_code != 200:
        logging.error("Cannot get user details")
        exit(1)

    gitea_uid = json.loads(r.text)["id"]

    for repo in gh.get_user().get_starred():
        if repo.owner.login != github_username:

            m = {
                "repo_name"         : repo.full_name.replace("/", "-"),
                "repo_owner"        : github_starred_org,
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

            logging.info("Mirroring \"%s\"", repo.full_name)

            r = session.post("{0}/repos/migrate".format(gitea_api_url), data=jsonstring)
            if r.status_code != 201:            # if not CREATED
                if r.status_code == 409:        # repository exists
                    continue
                logging.info(r.status_code, r.text, jsonstring)
else:
    logging.info("Skipping GitHub starred repos because GITHUB_STARRED_ORG is not set")

if gist_target_org:
    logging.info("Mirroring Gists to \"%s\"", gist_target_org)

    r = session.get("{0}/users/{1}".format(gitea_api_url, gist_target_org))

    if r.status_code != 200:
        logging.error("Cannot get user id for '{0}'".format(gist_target_org))
        exit(1)

    gitea_uid = json.loads(r.text)["id"]

    for gist in gh.get_user().get_gists():
        if not gist.forks:

            m = {
                "repo_name"     : gist.id,
                "repo_owner"    : gist_target_org,
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

            logging.info("Mirroring gist \"%s\"", gist.id)

            r = session.post("{0}/repos/migrate".format(gitea_api_url), data=jsonstring)
            if r.status_code != 201:            # if not CREATED
                if r.status_code == 409:        # repository exists
                    continue
                logging.info(r.status_code, r.text, jsonstring)
else:
    logging.info("Skipping Gists because GIST_TARGET_ORG is not set")

if giststar_target_org:
    logging.info("Mirroring starred gists to \"%s\"", giststar_target_org)

    r = session.get("{0}/users/{1}".format(gitea_api_url, giststar_target_org))

    if r.status_code != 200:
        logging.error("Cannot get user id for '{0}'".format(giststar_target_org))
        exit(1)

    gitea_uid = json.loads(r.text)["id"]

    for gist in gh.get_user().get_starred_gists():

        m = {
            "repo_name"     : gist.id,
            "repo_owner"    : giststar_target_org,
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

        logging.info("Mirroring gist \"%s\"", gist.id)

        r = session.post("{0}/repos/migrate".format(gitea_api_url), data=jsonstring)
        if r.status_code != 201:            # if not CREATED
            if r.status_code == 409:        # repository exists
                continue
            logging.info(r.status_code, r.text, jsonstring)
else:
    logging.info("Skipping starred gists because GISTSTAR_TARGET_ORG is not set")