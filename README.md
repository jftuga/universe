# Universe

[Universe - Manifest](https://rawgit.com/jftuga/universe/master/gh-manifest.html)

## Add New Files

- cd universe
- git add * # (or other file mask) (you can also use 'git add --all')
- git commit -am "initial commit" # or for one file: git commit filename -m "my comment"
- git push or to push only one branch: git push origin BranchName


## Remove Files

- git rm file.xyz # this also deletes the file from the local file system!
- git commit -am "rm" 
- git push

## Revert The Last Change

- git revert HEAD
- git push
- see also: https://www.atlassian.com/git/tutorials/undoing-changes/git-revert/

## Delete A Branch

- https://help.github.com/articles/viewing-branches-in-your-repository/
- click on the Branch Tab
- On the subsequent click the trash can icon next to the branch you wish to remove

## Review Operations

- git log
- git log --pretty=oneline

## Tagging

- commit & push your change
- git log --pretty=oneline # to find the commit version checksum
- git tag -a v1.01 111aabb...bb222 -m "example.py v1.01"
- git push origin --tags
- see also: https://git-scm.com/book/en/v2/Git-Basics-Tagging



