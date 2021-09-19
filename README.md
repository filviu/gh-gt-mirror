# Mirror GitHub and Gists to Gitea

Migrated from a Gist here for a better future :)

A very crude update to:

https://jpmens.net/2019/04/15/i-mirror-my-github-repositories-to-gitea/ and https://gist.github.com/jpmens/7690644643723577c8d1ee0450d0d82a

Among the modifications is the ability to clone to different organizations.

## Usage

Until I have time to actually make it use a config file you have to:

1. Create a `~/.gitea-api` file with the Gitea API key.
2. Create a `~/.github-token` file with the GitHub token.
3. Edit organizations to your liking
```
github_target_org = "github"
gist_target_org = "gist"
starred_target_org = "starred"
stargist_target_org = "starred-gists"
```
4. Edit `github_username` with your github username.

## Future

I'm using this script daily and intend to eventually improve it. PRs welcome.

