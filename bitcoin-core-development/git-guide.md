# Hunks not chunks!

_Notes on how Bitcoin Core is teaching me to use git in new and exciting ways_

-------

It's no secret that Bitcoin Core has extremely high development standards, and git is no exception. All contributions are expected to have clean, thoughtful commit histories with clear messages.

Of course, this is far easier said than done, especially after multiple rounds of feedback on a PR.

This guide begins with some basics then takes a deep dive into a few advanced workflows. However, you can skip the note taking. At the end you'll find some checklists that summarize each of the workflows.

Enjoy!

# Basics

### Rebasing

At some point in a core dev's journey, they will need to master the art of the `rebase` command. While you don't need to know all the in's and out's from the beginning, it's helpful to have a basic idea of what the command does. 

The most common need for a rebase arises when you are working on a feature branch while others are making updates to the master branch. Eventually you will want to merge your feature branch into master and it's good practice to identify and deal with any potential merge conflicts sooner than later. **When you rebase, you rewind all your work (your commits) and replay it on top of the latest copy of the master branch.** 

The end result is similar to that of a merge, but things are much neater. All your commits stay grouped together and there are no merge commits that can often be confusing to parse through.

<!-- TODO: Some diagrams would be nice here! -->

However the `rebase` command can do a lot more! There are plenty of simple ways newcomers can use it to get a feel for things, without having to go through the full flow described above.

For example, `rebase` can be used to edit commit messages, or it can be used to squash two commits into one. Let's see how you'd go about doing that!

Imaging you have a branch with two commits. You will open up the interactive rebase flow with `git rebase -i` (the `-i` stands for 'interactive'), and you will use `HEAD~2` to specify that you want your rebase to apply to the last two commits.

    git rebase -i HEAD~2

From there, you will be shown a list of your two commits with the word `pick` in front of each. If you want to reword a commit message, change `pick` to `reword`. Similarly, if you want to squash a commit into the previous one, change `pick` to `squash`.

<!-- TODO: a screencap of what this looks like -->

Upon exiting this screen, git will guide you through the next steps. This can be an editor for you to change a commit message, or one where the messages from two commits are available for you to either merge or make changes to before squashing commits together.

Lastly you'll want to push your changes, but you need to use the `-f` flag for this. It tells git to do a "force push" since rebasing changes the commit hashes. Only use `git push -f` if you have a full understanding of your changes, because once you do a force push, there's no going back!

If you've never used `git rebase`, a great way to familiarize yourself and practice is by changing a commit message, or squashing a few commits. I strongly encourage readers to try this!

Lastly, to learn more about rebasing, a good place to start is the [git docs](https://git-scm.com/docs/git-rebase).  

### Helpful commands

Below are some commands common to Core dev workflows. Values that you need to change are written `$like_this_with_a_dollar_sign`.

1. To view the commits that are on your current branch, but not (your copy of) the master branch:
    ```
    git log --oneline master..
    ```
    
2. You can then pipe through `wc` to count the number of commits:
    ```
    git log --oneline master.. | wc -l
    ```
    
3. To view all staged code:
    ```
    git diff --staged
    ```
    
4. To create a patch from uncommitted changes:

    _a good way to back up your code!_
    ```
    git diff > my_patch_name.patch
    ```
    
5. To stash changes in your working directory (this is helpful if you want to do some rebasing but are getting conflicts)
    ```
    git stash
    ```

6. To pop the stashed code back into the working directory
    ```
    git stash pop
    ```

7. To force push:
    
    _(use this after rebases, ⚠️ but only if you know what you are doing! This can be a dangerous command ⚠️)_
    ```
    git push -f
    ```

### Links

- [Guidelines for how to format commit messages](https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md#committing-patches) (from the Bitcoin Core Developer Docs)
    <!-- TODO: a TLDR; on this -->

# Changing commit history

From rewriting commit history, to making edits on specific commits, git makes it possible to change your commit history in ways you may not have thought were possible. 

## Completely redoing commit history

Once you've finished a feature, you'll probably want to go back and clean up the commit history. The naive way of doing this is to make a new branch off master and manually start copying code over, stopping frequently to make commits. While this is certainly one way to get the job done, learning just a few extra commands can make your life a lot easier. It not only reduces your chances of forgetting or dulicating code from the feature branch, but it  also builds a strong foundation for more advanced things you may want to do later, like making edits to particular commits. 

So another way to rewrite your commit history is by rewinding all your commits, thus returning the code to an uncommitted, un-staged state in the working directory. From there, you can start fresh and thoughtfully rebuild the history one commit at a time. 

To do this you first need to count the number of commits your branch has (`git log --oneline master.. | wc -l`). Once you have that, you can run:

    git reset HEAD~$number_of_commits

This moves everything back to the working directory. You can double check this with `git status`.

Next is the task of turning a giant diff into multiple commits. Most are familiar with the `git add <$filename>` command, where you can move entire files to the staging area. But what if you only want to stage parts of a file? Fear not, the hunk is here to help.

<p align="center"><img src="https://github.com/satsie/bitcoin-notez/blob/master/bitcoin-core-development/images/fabio.jpeg" width=50%></p>


When used with the `-p` flag, `git add` will open up an interactive flow where it walks you through "hunks" of code from the file's diff (yes, you heard right, I said [hunks not chunks](https://git-scm.com/docs/git-add#Documentation/git-add.txt---patch)) and you can choose to move it to the staging area or not.

`git add -p $filename`

![](https://github.com/satsie/bitcoin-notez/blob/master/bitcoin-core-development/images/git-add-hunk.png)

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
        
Once feedback starts flowing, there's a good chance you'll want to edit specific commits. This is especially great for small changes that are unlikely to cause downstream conflicts like code comments, new tests, and slight modifications to variable names.

One way to do this is to make your changes as normal, creating a new commit. Then you'll squash that new commit into a specific one in your history.

First, make your changes as you would for any normal commit. Next find the hash of the commit that you need to change. You can use the GitHub UI or `git log --oneline master..`. You can also use `git blame` to pinpoint exactly what commit changed a particular line of code.

Next add the changes to the staging area: `git add $some_file_name`

Once all the changes have made it to the staging area, use `git commit --fixup $some_commit_hash`. This will create a new commit that fixes up another one <!-- TODO: check the git docs for a better description of this -->
    
Now we have a new commit with the edits, but we don't want it to be separate. We want it to be part of the original commit. To do that we need to rebase.
    
_Note: At this point you may need to do a `git stash` to temporarily get any unstaged code out of the way. The working directory needs to be clean in order for a rebase to work. Later, when you need to bring the stashed changes back, you can use `git stash pop`._
    
Once again we need to count the number of commits, so we know how many commits back the rebase has to go: `git log --oneline master.. | wc -l`

Then go ahead and run the rebase command: `git rebase -i --autosquash HEAD~${number_of_commits}` This will open up an interactive rebase flow. The default settings should be good and you shouldn't need to do anything special here. <!-- TODO: explain autosquash -->
    
Lastly push up the changes with a `git push -f`!
    
# Appendix
    
## Cheat Sheets

Handy little checklists that cover workflows described above!

### Creating a new branch to redo commit history on

1. Use the UI to sync your fork with the upstream one.
2. Pull the results down locally:`git checkout master` and `git pull`
3. Go back to your feature branch and rebase your changes on top the latest copy of master: `git checkout $my_feature_branch` and `git rebase master`
4. Make a new branch: `git checkout -b my_new_branch_name`
5. Count the number of commits: `git log --oneline | wc -l`
6. Pop the commits off: `git reset HEAD~$number_of_commits`
7. Flatten everything to one commit: `git add .` and `git commit`

### Redoing commit history
    
If all changes have not been moved back to the working directory, do that first:

1. Count the number of commits: `git log --oneline master.. | wc -l`
2. Pop the commits off: `git reset HEAD~$number_of_commits`

Once everything is in the working directory,
    
1. `git diff` to view what needs to be committed
2. `git add -p $some_file_name` to stage hunks of code
3. `git diff --staged` then `git commit`
4. After all the changes in the diff have been accounted for and put into commits, force push with `git push -f`

### Making edits to a specific commit

1. Make your changes as normal and move them to the staging area (`git add .` / `git add $some_file_name` / `git add -p $some_file_name`).
2. Find the hash of the commit you want to modify (use the GitHub UI / `git log --oneline master..` / or `git blame`)
3. Double check everything in the staging area is correct `git diff --staged`
4. Make a fixup commit for the specific commit you want to edit: `git commit --fixup $some_commit_hash`
5. [optional] If there's anything still in the working directory, stash it: `git stash`
6. Count the number of commits (should be one greater than what you began with): `git log --oneline master.. | wc -l`
7. Rebase: `git rebase -i --autosquash HEAD~${number_of_commits}`
8. Force push: `git push -f`
9. [optional] Bring back any stashed changes: `git stash pop`
    
## Acknowledgements

Special thank you to [@amitiuttarwar](https://github.com/amitiuttarwar) for sharing so many of her wonderful tips and tricks!
