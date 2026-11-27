# Drafts in the browser
Status: draft. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): the drafts of unsaved work that the plugin keeps in the browser's own storage where the blockr option `session_autosave` is set, what a draft holds, when the plugin writes one, to whom it offers a draft, the drafts button and its dialog, restoring and discarding a draft, when a draft goes, and how long the browser keeps what the plugin stores.
It shapes the Work item of [Session management as a storage plugin](Rewrite-1.6#work) that writes drafts of unsaved work and offers them again.
The save status that says "Saved as draft" or "Autosave failed" is [The controls and dialogs](Rewrite-1.6.3#the-controls)'s.

## What must hold

1. Where `session_autosave` is set, unsaved work survives a crash of R's process, of the page or of the browser, and the same browser offers it again to the same user ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 5).
2. A draft costs no call to a backend, and works with every backend and without one.
3. The plugin offers a draft only to the user who wrote it, in the app that wrote it.

## Proposal

- Where the blockr option `session_autosave` gives an interval in seconds, the plugin writes a draft of unsaved work at that interval to the browser's own storage, from its class's `start`, which follows the board ([Board updates](Rewrite-1.1.2#opening-a-board)).
- A draft holds the JSON board, the record that the board was opened from, if any, the app, the user who is signed in, if any, and the time it was written.
- So a draft costs no call to a backend, and works with every backend and without one.
- A later page offers the drafts of the same app and the same user through the drafts button, which says how many wait, such as "2 drafts" ([The controls and dialogs](Rewrite-1.6.3#the-controls)), and opens the drafts.
- The draft that the user restores opens with `core.store.open()`, with no reload, and the record that it was opened from stays the open record, so that Save adds a version to that record, as today.
  So the URL's `recover` goes ([Records, links and app scripts across the switch](Rewrite-1.6.5#links-made-today)).
- A draft goes once the work it holds is saved, once the user discards it, or once it is older than `session_draft_ttl` days, 7 by default.
- The browser keeps a draft on its own machine, so only that browser can restore it, while today's drafts open on any device (notes).

## Open questions

- Which of the browser's stores holds the drafts, and under which keys: settled with what a draft holds, IndexedDB being the likely store, since it has room for a large board.
- How two tabs on one record keep their drafts apart, and which of them a later page offers: settled with the draft's keys.
- To whom a draft is offered where nobody signs in, as on a page off Connect: it blocks the draft's keys, and the user's choice settles it.
- Whether the plugin asks the browser to keep its storage through `navigator.storage.persist()`, and what a private window keeps: settled by what each browser does.

<details><summary>Notes for implementers</summary>

Today's drafts are rack records with `draft = TRUE`, written every `session_autosave` seconds when that blockr option is set and kept for `session_draft_ttl` days, 7 by default ([R/draft.R#L1-L30](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L1-L30)).
On Connect, each such write uploads a pin bundle, which Connect deploys as it deploys any content.
Should drafts in the browser prove too narrow, a backend can hold them again, as today's records at reserved keys do.

Connect serves every content item at a path of the server's one host, under its GUID or a vanity path ([Content settings](https://docs.posit.co/connect/user/content-settings/)), and its dashboard shows content in frames that only the same server may embed ([Embedding and cross-origin access](https://docs.posit.co/connect/admin/security/embedding-cors/)).
So the browser keeps one storage for every content item on a server, since it keeps storage by a page's scheme, host and port, and another app on the same server can read the drafts that this one writes.
That adds little, since a page on the same server can already frame this app and read what it shows while the user has it open.
The plugin keys a draft on the page's path as well as on the user, so that two apps on one server keep their drafts apart.

</details>
