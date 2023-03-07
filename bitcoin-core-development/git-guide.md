It's no secret that Bitcoin Core has extremely high development standards, and git is no exception. Contributions are expected to have clean, thoughtful commit histories with clear messages.

Of course, this is something that is far easier said than done, especially after multiple rounds of feedback.

Below are some helpful commands that are common to Core dev workflows. Values that you need to change are written `$like_this_with_a_dollar_sign`.

To view the commits that are on your current branch, but not the master branch:

    git log --oneline master..

You can then pipe this through `wc` to count the number of commits:

    git log --oneline master.. | wc -l

Once you've finished a feature, you'll probably want to go back and clean up the commit history. One way to do this is by starting fresh and popping all your commits off so that you can rebuild the history one commit at a time. To do this you first need to use the previous command to count the number of commits your branch has. Once you have that, you can run:

    git reset HEAD~$number_of_commits

This moves everything back to the working directory. You can run `git status` to double check this.

At this point you're probably wondering "how to I take a diff and turn it into multiple commits?" Most are familiar with the `git add <$filename>` command, where you can move entire files to the staging area. But what if you only want to stage parts of a file? Fear not, the hunk is here to help.

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
  
  
  
<TODO add my specific workflows for redoing the commit history for a PR that already exists, and one that you want to preserve the commit history and code for>  
