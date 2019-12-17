#!/usr/bin/env python3

r"""
clone_all_git_repos.py
-John Taylor
Dec 17 2019

A quick-n-dirty way to clone your public and private GitHub repositories.

Manually save the HTML contents of this URL to 'repo1.html'
https://github.com/YourGithubUsername?tab=repositories

On the web page, advanced to the second page of repositories and save its HTML contents
to 'repo2.html'

Repeat for repo3.html, repo4.html, etc.

change the 'repo_user' variable below

To actually clone the repositories, you can then run something like:
python3 clone_all_git_repos.py | sh
python3 clone_all_git_repos.py | cmd

"""

import glob
import re

# change this user...
repo_user = "jftuga"

repo_name_re = re.compile("<a href=\"/%s/(.*?)\" itemprop=\"name codeRepository\" >" % (repo_user),re.I|re.S|re.M)
clone_cmd = "git clone https://github.com/%s/__REPO__.git" % (repo_user)

def output_clone_cmd(repo_name:str):
    result = clone_cmd.replace("__REPO__", repo_name)
    print(result)

def extract_repo_names_from_page(html:str) -> list:
    results = repo_name_re.findall(html)
    return results

def main():
    pages = glob.glob("repo*.html")
    pages.sort()
    #print(pages)
    all_repo_names = []
    for page in pages:
        with open(page) as fp:
            html = fp.read()
        repo_names_on_page = extract_repo_names_from_page(html)
        for repo_name in repo_names_on_page:
            all_repo_names.append(repo_name)

    print()
    for repo_name in all_repo_names:
        output_clone_cmd(repo_name)



if "__main__" == __name__:
    main()

