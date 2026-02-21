# Idempotency
Idempotency is relatively generic: for a given logical operation, use a key so multiple attempts are equivalent to one. The variations are mostly about scope and keys.

You still have domain choices (granularity of the key, time windows, what “same effect” means), but the pattern is reusable.



# Reconciliation
Reconciliation is more domain-specific because it depends on:

- what entities you’re reconciling,
- which sources of truth you have,
- and how much you trust each of them.

The general pattern is always:
collect states from different systems → match them → classify mismatches → either auto-correct, flag-and-escalate, or send to manual review. How much you automate versus escalate depends on the risk of being wrong in that particular scenario.”


> “Given two or more imperfect, delayed, possibly buggy views of reality, decide:
* what actually happened,
* what our books should say,
* and what risk/exposure we now hold.” 

That always depends on:
* What entities exist? (payments, trades, balances, positions, claims…)
* What are the sources of truth?
  - Our ledger
  - Provider ledger
  - Blockchain
  - Bank statements
  - Clearing files
* Who do we trust, and for what?
(you might trust an exchange for trade matching, but trust the chain/bank for actual funds)

* What’s an acceptable mismatch?
(timing delays vs real loss vs fraud)


Reconciliation is less generalizable so we can’t just say “reconciliation works the same everywhere” because:
* The matching logic is different.
* The resolution rules are different.
* The risk profile is different.
But the **meta-patterns** do repeat.

## The general shape of reconciliation
Even though details are domain-specific, most reconciliation systems boil down to the same skeleton:

1. Collect data from multiple sources
* Internal records (what we think happened)
* External records (what provider/exchange/bank says)
* Possibly independent records (blockchain, clearinghouse, etc.)

2. Match entities
* Try to line up internal operations with external ones:
  * by IDs, amounts, timestamps, counterparties, metadata

3. Classify differences
* ✅ Match & consistent → “OK / Settled”
* ⏱️ Temporarily off (timing, small rounding) → “Pending / Expected”
* ⚠️ Real mismatch → “Suspicious / Disputed / Loss”

4. Apply resolution strategy
* Fully automated:
  * Adjust internal ledger if mismatch is clear + low risk
* Automated with flagging:
  * Fix state, but also log and alert
* Flag & escalate only:
* Do not auto-correct, just raise to ops/risk
* Manual only:
  * Human intervention (for high-value / high-risk mismatches)


