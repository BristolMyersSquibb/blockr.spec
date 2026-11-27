# Drafts in the browser
Status: review. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): the drafts of unsaved work that the plugin keeps in the browser's own storage where the blockr option `session_autosave` is set, where in the browser they live, what a draft holds, when the plugin writes one, to whom it offers a draft, the drafts button and its dialog, restoring and discarding a draft, when a draft goes, and how long the browser keeps what the plugin stores.
It shapes the Work item of [Session management as a storage plugin](Rewrite-1.6#work) that writes drafts of unsaved work and offers them again.
The save status that says "Saved as draft" or "Autosave failed" is [The controls and dialogs](Rewrite-1.6.3#the-controls)'s.

## What must hold

1. Where `session_autosave` is set, unsaved work survives a crash of R's process, of the page or of the browser, and the same browser offers it again to the same user ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 5).
2. A draft costs no call to a backend, and works with every backend and without one.
3. The plugin offers a draft only to the user who wrote it, in the app that wrote it, where the pages on which nobody is signed in count as one user.
4. Two pages on one record keep their drafts apart, so that neither page's unsaved work overwrites the other's.

## Today

Today's drafts are rack records at reserved keys, written every `session_autosave` seconds where the board holds a block and its content hash differs from the one at the last save or open ([R/draft.R#L1-L151](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L1-L151)).
A record has one draft, which every session that opens it writes and which never expires, and a board that no record holds has one draft for each session, which expires after `session_draft_ttl` days, 7 by default.
A save drops the draft of its session, the drafts notice offers the drafts of sessions and the open record's draft, and Restore reloads the page with `recover`, where the restoring session drops the old draft once its own holds the work ([R/draft.R#L153-L394](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L153-L394)).
The save status says "Saved as draft" or "Autosave failed", in place of a toast for each write.

## Proposal

### Where drafts live

- The plugin keeps its drafts in IndexedDB, in the database `blockr-session` and its object store `drafts`, since localStorage holds 5 MiB for each origin and writes while the page waits, while a board's JSON may be larger and a write at an interval should not hold up the page ([Storage quotas and eviction criteria](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria)).
- So a draft costs no call to a backend, and works with every backend and without one.

### What a draft holds

With illustrative names:

```ts
interface Draft {
  id: string;                      // minted by the page that writes it, as the page starts
  app: string;                     // the page's path on its server, such as "/content/0c1d…/"
  user: string | null;             // the owner that the backend's `user` gave, null where nobody is signed in
  record: { owner: string; key: string; version: string } | null;   // the record that the board was opened from
  name: string;                    // the board's name, for the drafts dialog
  board: string;                   // the text that `core.store.save()` wrote
  written: string;                 // when, in ISO 8601
}
```

- The draft holds the record that its board was opened from, so that restoring it keeps that record the open one, and the app, so that two apps on one server keep their drafts apart (notes).

### Writing a draft

- Where the blockr option `session_autosave` gives an interval in seconds, the plugin's `start`, which follows the board ([Board updates](Rewrite-1.1.2#opening-a-board)), looks at the board at that interval.
  It writes a draft where the board holds a block and its text differs from the version that the plugin opened or saved last, by the hash that the plugin keeps of it ([The storage API](Rewrite-1.6.1#records-and-versions)), and from the draft that it wrote last.
- It writes once more as the page hides, on `visibilitychange`, since a browser may end a hidden page without a word.
- Each page writes one draft of its own, under the id that it minted, so that two pages on one record keep their drafts apart, where today's two sessions write the record's one draft in turn.
- The save status says "Saved as draft" once a write works, and "Autosave failed" once one fails, as where the browser's storage is full, in place of a toast for each write, as today ([The controls and dialogs](Rewrite-1.6.3#the-controls)).
- Under the load lock, the plugin writes no drafts, since restoring one would open another board, which the lock forbids ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).

### Offering and restoring

- As the plugin starts, it offers the drafts of its app that are not its own and whose `user` is the user that the backend's `user` gives, or `null` on a page where nobody is signed in, through the drafts button, such as "2 drafts", which opens the drafts dialog ([The controls and dialogs](Rewrite-1.6.3#the-controls)).
  So a user's draft is never offered to another user, nor to a page on which nobody is signed in, and a draft written while nobody was signed in only to such a page.
- The drafts dialog lists each draft with the key of the record that it was opened from, or the board's name for a board that no record holds, and how long ago it was written, each with Restore and Discard, as today's does.
- Restore opens the draft's board with `core.store.open()`, with no reload, and keeps the record that the draft was opened from as the open record, with the URL moved to it ([The controls and dialogs](Rewrite-1.6.3#the-url)).
  The page takes the draft's id over, so that its next write replaces that draft rather than leaving a second one beside it.
  So Save adds a version to that record, as today, and the URL's `recover` goes ([Records, links and app scripts across the switch](Rewrite-1.6.5#links-made-today)).
- Discard deletes the draft, and the dialog closes once no draft is left.

### When a draft goes

- A draft goes once a save of the page that wrote it lands, once the user discards it, or once it is older than `session_draft_ttl` days, 7 by default.
- The plugin deletes the drafts of its app that are older than that as it starts, whoever wrote them, since nobody can restore them any more.
- Where today's record drafts never expire, every draft here does, since the browser holds them for no backend, which may clear them anyway (below).

### What the browser keeps

- The browser keeps a draft on its own machine, so only that browser can restore it, while today's drafts open on any device (notes).
- In a private window, a draft survives a crash of R's process or of the page, and a reload, and goes as the window closes, since browsers drop the storage of a private window then ([Storage quotas and eviction criteria](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria)).
- Safari deletes what script stored for a site with which the user has not interacted in the last seven days of browsing, which the default of `session_draft_ttl`, 7 days, matches.
- The plugin asks for no persistent storage through `navigator.storage.persist()`, since Firefox asks the user for it in a prompt, while a draft that outlives `session_draft_ttl` has no use.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's drafts are rack records with `draft = TRUE`, written every `session_autosave` seconds when that blockr option is set and kept for `session_draft_ttl` days, 7 by default ([R/draft.R#L1-L30](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L1-L30)).
On Connect, each such write uploads a pin bundle, which Connect deploys as it deploys any content.
Should drafts in the browser prove too narrow, a backend can hold them again, as today's records at reserved keys do.

Connect serves every content item at a path of the server's one host, under its GUID or a vanity path ([Content settings](https://docs.posit.co/connect/user/content-settings/)), and its dashboard shows content in frames that only the same server may embed ([Embedding and cross-origin access](https://docs.posit.co/connect/admin/security/embedding-cors/)).
So the browser keeps one storage for every content item on a server, since it keeps storage by a page's scheme, host and port, and another app on the same server can read the drafts that this one writes.
That adds little, since a page on the same server can already frame this app and read what it shows while the user has it open.
The plugin keys a draft on the page's path as well as on the user, so that two apps on one server keep their drafts apart, while an app reached both under its GUID and under its vanity path keeps two sets.

The first look at the board, as the plugin starts, sets the baseline, as today's first tick does, so that a board that the page opened counts as saved ([R/draft.R#L79-L93](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L79-L93)).

</details>
