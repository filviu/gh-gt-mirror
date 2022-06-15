# Mirror GitHub Repositories and Gists to Gitea

## Usage

### Docker

Docker is the prefered way to run the service. Define a `docker-compose.yml` file and (optionally) an `.env` file. The preffered way is to keep at least the API TOKENS in the `.env` file. Shocking enough the folder example holds example files for compose and env.

`.env`

```ini
GITEA_API_URL=http://gitea.example.com:3000/api/v1
GITEA_API_TOKEN=aabbccddeeffgghhiijj1234567890

GITHUB_API_TOKEN=ghp_aabbccddeeffgghhiijj1234567890
```

`docker-compose.yml`
```yaml
version: '3'

services:
  ghmirror:
    image: filviu/gh-gt-mirror
    environment:
      GITEA_API_URL: ${GITEA_API_URL}
      GITEA_API_TOKEN: ${GITEA_API_TOKEN}
      GITHUB_USERNAME: filviu
      GITHUB_API_TOKEN: ${GITHUB_API_TOKEN}
      GITHUB_ONLY_OWNER: "false"
      GITHUB_MIRROR_FORKS: "false"
      GITHUB_FILTER_ORGS: work-organization
      GITHUB_TARGET_ORG: github
      GITHUB_STARRED_ORG: github_starred
      GIST_TARGET_ORG: gist
      GISTSTAR_TARGET_ORG: gist_starred
      CRON_SCHEDULE: 0 3 * * *
    restart: always

```

Then simply run it.

```bash
docker-compose up -d
```

### Command line

Install the **pygithub** dependency. One way would be:

```bash
python3 -m pip install pygithub
```

The following environment variables are expected:

```bash
GITEA_API_URL=http://gitea.example.com:3000/api/v1
GITEA_API_TOKEN=aabbccddeeffgghhiijj1234567890

GITHUB_USERNAME=github_username
GITHUB_API_TOKEN=ghp_aabbccddeeffgghhiijj1234567890

GITHUB_ONLY_OWNER=false
GITHUB_MIRROR_FORKS=false
GITHUB_FILTER_ORGS=work-organization

# if any of these target organizations are not defined then
# repositories in the category are not mirrored
GITHUB_TARGET_ORG=github
GIST_TARGET_ORG=github_starred
GIST_TARGET_ORG=gist
GISTSTAR_TARGET_ORG=gist_starred
```

Export them and then run the script `python github-mirror.py`. It works but it's not the intended use case.

## Past & Future

Started as a crude update to: https://jpmens.net/2019/04/15/i-mirror-my-github-repositories-to-gitea/ and https://gist.github.com/jpmens/7690644643723577c8d1ee0450d0d82a

Among the modifications was the ability to mirror to different organizations depending on type. Eventually grew into it's own repository and now a docker image.

I'm using this script daily and intend to eventually improve it. PRs welcome.
