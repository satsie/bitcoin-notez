It's no secret that Bitcoin Core has extremely high development standards, and git is no exception. Contributions are expected to have clean, thoughtful commit histories with clear messages.

Of course, this is something that is far easier said than done, especially after multiple rounds of feedback.

## Helpful commands

Below are some helpful commands that are common to Core dev workflows. Values that you need to change are written `$like_this_with_a_dollar_sign`.

To view the commits that are on your current branch, but not the master branch:

    git log --oneline master..

You can then pipe this through `wc` to count the number of commits:

    git log --oneline master.. | wc -l

To view all the code that has been staged:

    git diff --staged

## Links

[Guidelines for how to format commit messages](https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md#committing-patches) (from the Bitcoin Core Developer Docs)

## Cleaning up your commit history

### Deep Dive
Once you've finished a feature, you'll probably want to go back and clean up the commit history. One way to do this is and popping all your commits off so you can start fresh and rebuild the history one commit at a time. To do this you first need to count the number of commits your branch has (git log --oneline master.. | wc -l). Once you have that, you can run:

    git reset HEAD~$number_of_commits

This moves everything back to the working directory. You can run `git status` to double check this.

Next you're faced with the task of taking a diff and turn it into multiple commits. Most are familiar with the `git add <$filename>` command, where you can move entire files to the staging area. But what if you only want to stage parts of a file? Fear not, the hunk is here to help.

<img src="https://people.com/thmb/AYy8DbNsiEfwoSIz-DdlJYPO-ns=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc():focal(986x0:988x2)/fabio--2000-51de6964c0a2466ca4d7a7db227adb90.jpg" width="50%" height="50%">

When used with the `-p` flag, `git add` will open up an interactive flow where it walks you through "hunks" of code from the file's diff (yes, you heard right, I said [hunks not chunks](https://git-scm.com/docs/git-add#Documentation/git-add.txt---patch)) and you can choose to move it to the staging area or not.

`git add -p $filename`

<TODO insert screenshot of what this looks like>

Depending on the code, you may even be able to split hunks! When prompted, use the `s` command. Use `git add --help` to learn more about the other options you can use in this interactive mode:
  
```
               y - stage this hunk
               n - do not stage this hunk
               q - quit; do not stage this hunk or any of the remaining ones
               a - stage this hunk and all later hunks in the file
               d - do not stage this hunk or any of the later hunks in the file
               g - select a hunk to go to
               / - search for a hunk matching the given regex
               j - leave this hunk undecided, see next undecided hunk
               J - leave this hunk undecided, see next hunk
               k - leave this hunk undecided, see previous undecided hunk
               K - leave this hunk undecided, see previous hunk
               s - split the current hunk into smaller hunks
               e - manually edit the current hunk
               ? - print help
```

From there you can proceed as normal with a `git commit` to commit everything that was moved to the staging area.
  
### Workflow: Creating a branch specifically for new commit history
    
During development you may come across situations where you want to preserve old commit history, even if it is just for your own reference. Maybe the history has the removal of code you used to test and debug, or maybe it contains alternate implementations of an algorithm. Either way, it's stuff that you don't want to get rid of completely, and stuff that would be useful to have some record of. <TODO what's the command that does keep commit history, but in a messy and difficult to read way?>
    
Here's a workflow you can use to create a totally new branch for the sole purpose of redoing the commit history.
    
1. Sync your local copy of the repository with the upstream branch. You should be able to do this with the GitHub UI. To make sure nothing went wrong, you can check that the commit hashes on your fork match the upstream repo's.
    
2. Rebase your changes: `git rebase master`. This will prompt you to resolve all conflicts synchronously.*
    
3. Create a new branch. Since the current branch has history we want to preserve, we need to make a different one for the clean commit history. From your current feature branch, run `git checkout -b my_new_branch_name`

4. Flatten all the commits into one: Count the number of commits (`git log --oneline master.. | wc -l`), then pop them off, sending the code back to the working directory: `git reset HEAD~$number_of_commits`. Finish off the process by creating one commit with `git add .` and `git commit`
    
&ast; _If rebasing gets nasty, you can cherry-pick, but make a copy of your branch with first! To do this, branch off of master, then cherry-pick your commits from your feature branch._

### Other things to consider

#### Establishing some idea of what you want your commit history to look like
It can be helpful to first sketch out what you want your new commit history to look like. This way, once you start doing the git stuff you can put all your attention on it. Git can require a lot of focus, especially if you find code changes that you'd like to integrate along the way, or start doing things that cause downstream conflicts.

Here's an example of what such a sketch could look like:
    
    1. Create new enum
    2. Create new data structures and methods for accessing them
    3. Update business logic to use new data structures
    4. Add tests
 
    
# Appendix
    
## Cheat Sheets
    
### Creating a new branch to redo commit history on

1. Use the UI to sync your fork with the upstream one
2. Rebase: `git rebase master`
3. Make a new branch: `git checkout -b my_new_branch_name`
4. Count the number of commits: `git log --oneline | wc -l`
5. Pop the commits off: `git reset HEAD~$number_of_commits`
6. Flatten everything to one commit: `git add .` and `git commit`

    
## Acknowledgements

Special thank you to [@amitiuttarwar](https://github.com/amitiuttarwar) for sharing so many of her wonderful tips and tricks!
