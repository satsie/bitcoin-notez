# Summary

[@larryruane](https://github.com/larryruane) and I have been working on ways to test [PR #26172](https://github.com/bitcoin/bitcoin/pull/26172), a bug fix for a boolean that was accidentally reversed in [PR #25717](https://github.com/bitcoin/bitcoin/pull/25717).

To no one's surprise, eviction can be really tricky to test! While a solution was beyond reach for my current level of Bitcoin Core understanding, I felt it important to document our findings, especially for anyone else that may want to tackle this.

# Background

I'm going to refer to [PR #26172](https://github.com/bitcoin/bitcoin/pull/26172), the code we were trying to test, as "Larry's bug fix". 

Larry's bug fix was for an earlier PR, [#25717](https://github.com/bitcoin/bitcoin/pull/25717), which implements an additional headers sync to protect against DoS attacks. Understanding of this PR is actually not completely necessary, but I have included notes for posterity.

## [PR-25717] p2p: Implement anti-DoS headers sync 

You can perform a DoS attack on a new node by flooding it with low difficulty headers. 

At the time of writing, there are these things called checkpoints, which change every release. They protect against this attack, but only up to a certain point. They only help if the low difficulty headers from the attack have a height lower than known checkpoint values.

This PR introduces a new strategy to protect all nodes, regardless if they have reached the checkpoint or not:

> Before permanently saving a header, download the rest of the chain to check that it belongs to a chain that has sufficiently high work (either nMinimumChainWork or something comparable to the current tip).

`headerssync.h` has a lot of great comments on how this PR works. 

This results in ***downloading headers twice***:
- once to verify the work on the entire chain
- a second time to permanently store the headers.

The first download phase is called “pre synchronization” (presync). We can check the amount of  work so far by looking at the nBits value on the header.

***When we do the second download, how can we be sure we are looking at the same headers as the first time? What’s stopping a peer from giving us the main chain the first time, and an alternate low work chain the second?***

***Answer:*** _We store commitments to the headers during the first download. These get validated in the second download._

There are tradeoffs on the size and frequency of the commitments. The PR chose particular values that would:
1. Minimize the p2p memory usage an attacker could take
2. Bind two values: First, the expected amount of permanent memory we’d use if the attacker succeeded. Second, the memory growth we’d get from the honest chain. If the attacker did succeed, set the parameters such that the amount of memory we’d use will be well below the memory growth we’d get from the honest chain.

The commitments use 1 byte for every N headers. Even for very long chains, a reasonable choice for N would take up very little memory.

This PR should allow the removal of checkpoints in the future. 

It’s true this PR slows down initial headers sync. The obvious reason is we download headers twice before storing. However, this also results in general latency on the headers sync with the initial peer. This means we’re more likely to receive a new block while waiting for the headers sync to finish. If that happens, a headers sync with all the peers that announced the block is triggered.

## [PR-26127] Larry's bug fix 

In a follow up PR, Larry fixed some logic that was accidentally reversed: [PR #26172](https://github.com/bitcoin/bitcoin/pull/26172)

In `net_processing.cpp`, the value of `received_new_header` in `ProcessHeadersMessage()` was accidentally being set to false. For peers that have sent new blocks, the boolean should actually be true.

To get into more detail, `received_new_header` should be true if the new header we just got is not in our BlockManger. It means the peer gave us a  header we haven’t seen before.

***How is received_new_header used?***

***Answer:*** At the end of `ProcessHeadersMessage()`, it’s passed to `UpdatePeerStateForReceivedHeaders()`, which updates the state (`CNodeState`) we keep for each peer. If `received_new_header` is true, we set the `m_last_block_announcement` of the peer’s state (`CNodeState`) to the current time. 

`m_last_block_annoucement` is the time of the latest block announcement.

***Correct behavior:*** `m_last_block_announcement` should only be updated (to the current time) for the **one** peer that provided the latest header.

Without Larry’s fix, the behavior is mostly flipped. All the **other peers** are updated to the current time (even though they were not the ones that gave us the new header). 

This can be tested by reversing Larry’s fix, and adding additional log statements when `m_last_block_announcement` is updated.

stickies-v [tested the bug fix manually](https://github.com/bitcoin/bitcoin/pull/26172#pullrequestreview-1120675663) and observed that `m_last_block_announcement` was not accurate without Larry’s fix. He alluded to this impacting eviction.

***Impact:*** the wrong timestamps appear in CNodeState::m_last_block_announcement which can ultimately lead to the wrong peer selected for eviction




