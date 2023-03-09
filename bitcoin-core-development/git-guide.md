# Hunks not chunks!

_A friendly guide to git for Bitcoin Core newcomers_

-------

It's no secret that Bitcoin Core has extremely high development standards, and git is no exception. All contributions are expected to have clean, thoughtful commit histories with clear messages.

Of course, this is far easier said than done, especially after multiple rounds of feedback on a PR.

# Basics

### Helpful commands

Below are some helpful commands common to Core dev workflows. Values that you need to change are written `$like_this_with_a_dollar_sign`.

To view the commits that are on your current branch, but not the master branch:

    git log --oneline master..

You can then pipe this through `wc` to count the number of commits:

    git log --oneline master.. | wc -l

To view all code that has been staged:

    git diff --staged
    
To create a patch from uncommitted changes (a good way to back up your code!):

    git diff > my_patch_name.patch

To stash changes in your working directory (this is helpful if you want to do some rebasing but are getting conflicts)

    git stash

To pop the stashed code back into the working directory

    git stash pop
    
To force push (use this after rebases, ⚠️ but only if you know what you are doing! This can be a dangerous command ⚠️):

    git push -f

### Links

[Guidelines for how to format commit messages](https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md#committing-patches) (from the Bitcoin Core Developer Docs)

# Changing commit history

From rewriting commit history, to making edits on specific commits, git makes it possible to change your commit history in ways you may not have thought were possible. 

## Completely redoing commit history

### The process explained

Once you've finished a feature, you'll probably want to go back and clean up the commit history. The naive way of doing this is to make a new branch off master and manually start copying code over, stopping frequently to make commits. While this is certainly one way to get the job done, learning just a few extra commands can make your life a lot easier. It not only reduces your chances of forgetting or dulicating code from the feature branch, but it  also builds a strong foundation for more advanced things you may want to do later, like making edits to particular commits. 

So another way to rewrite your commit history is by rewinding all your commits, thus returning the code to an uncommitted, un-staged state in the working directory. From there, you can start fresh and thoughtfully rebuild the history one commit at a time. 

To do this you first need to count the number of commits your branch has (`git log --oneline master.. | wc -l`). Once you have that, you can run:

    git reset HEAD~$number_of_commits

This moves everything back to the working directory. You can double check this with `git status`.

Next is the task of turning a giant diff into multiple commits. Most are familiar with the `git add <$filename>` command, where you can move entire files to the staging area. But what if you only want to stage parts of a file? Fear not, the hunk is here to help.

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
    
When you're happy with your work, you can do a special force push to get it up to the remote repository: `git push -f`. But make sure everything is the way you want it because there is no way to undo things once they have been forced pushed!
  
### Workflow: Creating a branch specifically for new commit history
    
Being able to completely rework your commit history is really helpful but you may come across situations where you want to preserve old history, even if it is just for your own reference. Maybe the history has a record of some code you used to test and debug, or maybe it contains alternate implementations for an algorithm. Either way, it's stuff that you don't want to get rid of completely, and stuff that would be useful to have some record of. It's true that nothing is ever completely lost with `git reflog`, but that command can require you to do some archaeology in order to retrieve what's needed.  
    
Here's a workflow you can use to create a totally new branch for the sole purpose of redoing the commit history.
    
1. Sync your local copy of the repository with the upstream branch. You should be able to do this with the GitHub UI. To make sure nothing went wrong, you can check that commit hashes on your fork match those in the upstream repo.
    
2. Rebase your changes: `git rebase master`. This will prompt you to resolve all conflicts synchronously.*
    
3. Create a new branch. Since the current branch has history we want to preserve, we need to make a different one for the clean commit history. From your current feature branch, run `git checkout -b my_new_branch_name`

4. Flatten all the commits into one: Count the number of commits (`git log --oneline master.. | wc -l`), then pop them off, sending the code back to the working directory: `git reset HEAD~$number_of_commits`. From here you can either leave everything in your local working directory, or, if you would like to push everything up to the remote repositoy (maybe so you can come back later and work on the commit history), finish the process by creating one commit with `git add .` and `git commit`.
    
&ast; _If rebasing gets nasty, you can cherry-pick, but make a copy of your branch with first! To do this, branch off of master, then cherry-pick your commits from your feature branch._
    
### Other things to consider

#### Establishing some idea of what you want your commit history to look like
It can be helpful to first sketch out what you want your new commit history to look like. This way, once you start doing the git stuff you can put all your attention on it. Git can require a lot of focus, especially if you find code changes that you'd like to integrate along the way, or start doing things that cause downstream conflicts.

Here's an example of what such a sketch could look like:
    
    1. Create new enum
    2. Create new data structures and methods for accessing them
    3. Update business logic to use new data structures
    4. Add tests

## Editing specific commits
    
### The process explained
    
Once feedback starts flowing, there's a good chance you'll want to edit specific commits. This is especially great for small changes that are unlikely to cause downstream conflicts like code comments, new tests, and slight modifications to variable names.

One way to do this is to make your changes as normal, creating a new commit. Then you'll squash that new commit into a specific one in your history.

First, make your changes as you would for any normal commit. Next find the hash of the commit that you need to change. You can use the GitHub UI or `git log --oneline master..`. You can also use `git blame` to pinpoint exactly what commit changed a particular line of code.

Next add the changes to the staging area: `git add $some_file_name`

Once all the changes have made it to the staging area, use `git commit --fixup $some_commit_hash`. This will create a new commit that fixes up another one <TODO: check the git docs for a better description of this>
    
Now we have a new commit with the edits, but we don't want it to be separate. We want it to be part of the original commit. To do that we need to rebase.
    
_Note: At this point you may need to do a `git stash` to temporarily get any unstaged code out of the way. The working directory needs to be clean in order for a rebase to work. Later, when you need to bring the stashed changes back, you can use `git stash pop`._
    
Once again we need to count the number of commits, so we know how many commits back the rebase has to go: `git log --oneline master.. | wc -l`

Then go ahead and run the rebase command: `git rebase -i --autosquash HEAD~${number_of_commits}` This will open up an interactive rebase flow. The default settings should be good and you shouldn't need to do anything special here. <TODO: explain autosquash>
    
Lastly push up the changes with a `git push -f`!
    
# Appendix
    
## Cheat Sheets
    
### Creating a new branch to redo commit history on

1. Use the UI to sync your fork with the upstream one
2. Rebase: `git rebase master`
3. Make a new branch: `git checkout -b my_new_branch_name`
4. Count the number of commits: `git log --oneline | wc -l`
5. Pop the commits off: `git reset HEAD~$number_of_commits`
6. Flatten everything to one commit: `git add .` and `git commit`

### Redoing commit history
    
If all changes have not been moved back to the working directory, do that first:

1. Count the number of commits: `git log --oneline master.. | wc -l`
2. Pop the commits off: `git reset HEAD~$number_of_commits`

Once everything is in the working directory,
    
1. `git diff` to view what needs to be committed
2. `git add -p $some_file_name` to stage hunks of code
3. `git diff --staged` then `git commit`
4. `git push -f`

### Making edits to a specific commit

1. Make your changes as normal and move them to the staging area (`git add .` / `git add $some_file_name` / `git add -p $some_file_name`).
2. Find the hash of the commit you want to modify (use the GitHub UI / `git log --oneline master..` / or `git blame`)
3. Double check everything that is in the staging area is correct `git diff --staged`
4. Make a fixup commit: `git commit --fixup $some_commit_hash`
5. [optional] Clear the working directory if needed: `git stash`
6. Count the number of commits: `git log --oneline master.. | wc -l`
7. Rebase: git rebase -i --autosquash HEAD~${number_of_commits}
8. Force push: `git push -f`
9. [optional] Bring back any stashed changes: `git stash pop`
    
## Acknowledgements

Special thank you to [@amitiuttarwar](https://github.com/amitiuttarwar) for sharing so many of her wonderful tips and tricks!
