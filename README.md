# LeetCode Web Scraper
Scrape LeetCode and automatically upload your solutions to GitHub.

# Installation
Clone this repo:
```bash
git clone https://github.com/Ismail-Mahmoud/lcws.git
```
Go to the project directory:
```bash
cd lcws
```
[Optional] Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```
Install the package:
```bash
pip3 install .
```

# Configuration
Copy [this file](./lcws/config/config.default.toml) to a new file named `config.toml` under the same directory. This new file will be the main config file containing LeetCode and GitHub configurations which will be used to access your LeetCode account and GitHub repo.

### LeetCode
Under `leetcode` section, set the following values:
1. `base_url`: LeetCode base URL (set by default)
2. `login_page`: LeetCode login page (set by default)
3. `user`: Your LeetCode username or email
4. `password`: Your LeetCode password

**Your LeetCode credentials is used by the web scraper to login to your account and fetch submissions*

### GitHub
Under `github` section, set the following values:
1. `api_base_url`: GITHUB API base URL (set by default)
2. `access_token`: Your GitHub access token*
3. `owner`: Your GitHub username
4. `repo`: Name of the repo to which the solution will be uploaded
5. `branch`: Name of the branch to which the solution will be uploaded
6. `directory`: Path of the directory to which the solution will be uploaded (for example, `leetcode/solutions`)

**You can generate your access token [here](https://github.com/settings/personal-access-tokens/new). Select only the target repo and under `Repository permissions`, grant `Read and write` access for `Contents`.*

# Usage
Just run the following command:
```bash
lcws <URL>
```
where `URL` is a valid URL of one of the following:
1. LeetCode problem (`https://leetcode.com/problems/<problem-name>/`). In this case, the last accepted submission will be fetched.
2. LeetCode submission (`https://leetcode.com/problems/<problem-name>/submissions/<submission-id>/`)

For help, run:
```bash
lcws --help
```

# Demo
![a](https://i.imgur.com/8liGxf8.gif)
