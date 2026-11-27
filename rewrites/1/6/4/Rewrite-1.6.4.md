# Drafts in the browser
Status: review. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): the drafts of unsaved work that the plugin keeps in the browser's own storage, where in the browser they live, what a draft holds, when the plugin writes one, to whom it offers a draft, the drafts button and its dialog, restoring and discarding a draft, when a draft goes, and how long the browser keeps what the plugin stores.
It shapes the Work item of [Session management as a storage plugin](Rewrite-1.6#work) that writes drafts of unsaved work and offers them again.
The save status that says "Saved as draft" or "Autosave failed" is [The controls and dialogs](Rewrite-1.6.3#the-controls)'s.

## What must hold

1. Outside the load lock, unsaved work survives a crash of R's process, of the page or of the browser, with no blockr option to set, and the same browser offers it again to the same user ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 5).
2. A draft costs no call to a backend, and works with every backend and without one.
3. The plugin offers a draft only to the user who wrote it, in the app that wrote it, where the pages on which nobody is signed in count as one user.
4. Two pages on one record keep their drafts apart, and so do two boards that one page opens in turn, so that no board's unsaved work overwrites another's.

## Today

Today, drafts are off unless an app sets the blockr option `session_autosave` to an interval in seconds ([R/draft.R#L1-L29](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L1-L29)).
Today's drafts are rack records at reserved keys, written at that interval where the board holds a block and its content hash differs from the hash of what the session last opened, saved or wrote as a draft ([R/draft.R#L31-L151](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L31-L151)).
A record has one draft, which every session that opens it writes and which never expires, and a board that no record holds has one draft for each session, which expires after `session_draft_ttl` days, 7 by default.
A save drops the draft of its session, the drafts notice offers the drafts of sessions and the open record's draft, and Restore reloads the page with `recover`, where the restoring session drops the old draft once its own holds the work ([R/draft.R#L153-L394](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L153-L394)).
The save status says "Saved as draft" or "Autosave failed", in place of a toast for each write.

## Proposal

### Where drafts live

- The plugin keeps its drafts in IndexedDB, in the database `blockr-session` and its object store `drafts`.
  It does not use localStorage, which holds 5 MiB for each origin and blocks the page while it writes: a board's JSON may be larger, and a write after a change should not hold up the page ([Storage quotas and eviction criteria](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria)).
  Nor does it use sessionStorage, which keeps what a tab stored for that tab alone, and only until the tab closes ([Window: sessionStorage property](https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage)).
- So a draft costs no call to a backend, and works with every backend and without one.

### What a draft holds

With illustrative names:

```ts
interface Draft {
  id: string;                      // minted by the page that writes it, as the board opens
  app: string;                     // the page's path on its server, such as "/content/0c1d…/"
  user: string | null;             // the owner that the backend's `user` gave, null where nobody is signed in
  record: { owner: string; key: string; version: string } | null;   // the open record, null for a board that no record holds
  name: string;                    // the board's name, for the drafts dialog
  board: string;                   // the text that `core.store.save()` wrote
  written: string;                 // when, in ISO 8601
}
```

- The draft holds the open record, so that restoring it makes that record the open one again, and the app, so that two apps on one server keep their drafts apart (notes).

### Writing a draft

- The plugin writes drafts in every app outside the load lock (below), since a draft in the browser costs no call to a backend, while each of today's writes is one (notes).
  So the blockr options `session_autosave` and `session_draft_ttl` go ([Records, links and app scripts across the switch](Rewrite-1.6.5#app-scripts)), and every draft expires after 7 days (below).
  An option that turns drafts off can come later, should a deployment need one, as where several people share one browser and nobody signs in, since the plugin then offers one person's drafts to the next.
- The plugin's `start`, which follows the board ([Board updates](Rewrite-1.1.2#opening-a-board)), looks at the board once a second has passed without a change, so that a burst of changes costs one look.
  It looks at no interval, unlike today's ticks, so a page that nobody uses does nothing.
- The page mints a draft's id as each board opens, in the plugin's `start`, whether it opens a record, New or a draft, and writes that board's draft under it.
  So two pages on one record keep their drafts apart, where today's two sessions write the record's one draft in turn.
  A page that opens another board also leaves the draft of the board before in place, and offers it with the others.
- The plugin keeps the text that `core.store.save()` writes for the board as it opened, once every plugin's `start` has run on it (notes), and again once a save lands.
  So a board that nobody has changed leaves no draft, whether R sent it or a record held it.
- At each look, the plugin writes the board's text as the board's draft where the board holds a block and the text differs from the text that the plugin keeps, unless the draft holds that text already.
  So where another page deleted the draft, by a Restore or a Discard, or as it expired, the plugin writes it again at its next look, while the board still holds that work (notes).
- Where the board's text is the kept text again, as after an undo back to it, the plugin deletes the draft, since no work is unsaved.
  It does the same where the board holds no block, which leaves nothing to restore.
  The save status then says again how long ago the open version was saved.
- The plugin keeps no text for a draft that it restores, since the work that the draft holds is saved nowhere else, so the work stays in a draft until a save lands.
  Save then adds a version, since the restored board is no version that the plugin opened or saved ([The storage API](Rewrite-1.6.1#records-and-versions)).
- The plugin writes no draft before it knows who the user is (below), so that no draft carries the wrong `user`.
- The plugin looks once more as the page hides, on `visibilitychange`, since a browser may end a hidden page without a word, and again as the page shows, so that a draft that another page deleted meanwhile comes back once its own page is in use again.
- It also looks once more before it opens another board, whether a record, New or a draft, so that the draft of the board before holds all of its work.
- The save status says "Saved as draft" once a write works, and "Autosave failed" once one fails, as where the browser's storage is full, in place of a toast for each write, as today ([The controls and dialogs](Rewrite-1.6.3#the-controls)).
- Under the load lock, the plugin writes no drafts and leaves out the drafts button, since restoring a draft would open another board, which the lock forbids ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).

### Offering and restoring

- The plugin offers drafts once it knows who the user is, from the backend's `user`, or that nobody is signed in.
  It offers the drafts of its app that are not its own and whose `user` is that user, or `null` where nobody is signed in, through the drafts button, such as "2 drafts", which opens the drafts dialog ([The controls and dialogs](Rewrite-1.6.3#the-controls)).
- So a user's draft is never offered to another user, nor to a page on which nobody is signed in, and a draft written while nobody was signed in only to such a page.
- The offer holds the drafts of every record, not only the open record's.
  Today's notice offers the draft of a record only once that record is open.
- The offer also holds the drafts of pages that are still open, as today's notice holds the drafts of sessions that still run ([R/draft.R#L292-L313](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L292-L313)), since not every page can tell whether the page that wrote a draft is still open (notes).
  So a second page lists the unsaved work of the first, and a draft that the user restores or discards there comes back at the first page's next look, while that page still holds the work (above).
- The drafts dialog lists the drafts, the latest first, each with Restore and Discard, as today's does.
  A row names the draft's record by its key, with its owner before it where another user owns it, as the workflows menu names a record ([The controls and dialogs](Rewrite-1.6.3#the-controls)), or else the board's name, and says how long ago the draft was written.
- Restore opens the draft's board with `core.store.open()`, with no reload, and makes the draft's record the open record, with the URL moved to it ([The controls and dialogs](Rewrite-1.6.3#the-url)).
  So Save adds a version to that record, as today, and the URL's `recover` goes ([Records, links and app scripts across the switch](Rewrite-1.6.5#links-made-today)).
- The plugin then looks at the board at once, which writes it as a draft under the id that the page minted as the board opened, and deletes the draft that it restored once that write has worked, as today's restoring session drops the old draft once its own holds the work.
  So the work stays in a draft throughout, and no two pages write one draft, as they would if the page took the restored draft's id over while the page that wrote it is still open.
- While the plugin saves or opens a board, Restore greys out, as every control that opens a board does, so that a late save never moves the URL to another board ([The controls and dialogs](Rewrite-1.6.3#saving)).
- A draft that does not open leaves the open board as it was, and the plugin tells the user why, as for a record ([The controls and dialogs](Rewrite-1.6.3#opening)).
- Discard deletes the draft, and the dialog closes once no draft is left.

### When a draft goes

- A draft goes once its page saves the board, once the board is back where it opened or was last saved, or holds no block (above), once the user restores or discards it, or once it was last written more than 7 days ago.
- As the plugin starts, it deletes the drafts of its app that were last written longer ago than that, whoever wrote them, since no page offers them any more.
- Every draft expires, while today's drafts of records never do.
  A draft here belongs to one board that one page opened, so drafts pile up, as today's drafts of sessions do, which expire for that reason.

### What the browser keeps

- The browser keeps a draft on its own machine, so only that browser can restore it, while today's drafts open on any device (notes).
- In a private window, a draft survives a reload and a crash of R's process or of the page, but goes once the private session ends, since browsers usually delete what a private session stored then ([Storage quotas and eviction criteria](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria#private_browsing)).
- Safari deletes what a site's script stored once the user has not interacted with the site in seven days of browsing ([Storage quotas and eviction criteria](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria#proactive_eviction)).
  So Safari keeps a draft for at least about the 7 days that the plugin keeps it, today's default of `session_draft_ttl`, but would delete one before any longer expiry ran out.
- The plugin asks for no persistent storage through `navigator.storage.persist()`, since Firefox asks the user for it in a prompt, while a draft that outlives its 7 days has no use.

## Open questions

None.

<details><summary>Notes for implementers</summary>

On Connect, each of today's draft writes uploads a pin bundle, which Connect deploys as it deploys any content ([R/draft.R#L116-L130](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L116-L130)).
Should drafts in the browser prove too narrow, a backend can hold them again, as today's records at reserved keys do.

Connect serves every content item at a path of the server's one host, under its GUID or a vanity path ([Content settings](https://docs.posit.co/connect/user/content-settings/)), and its dashboard shows content in frames that only the same server may embed ([Embedding and cross-origin access](https://docs.posit.co/connect/admin/security/embedding-cors/)).
So the browser keeps one storage for every content item on a server, since it keeps storage by a page's scheme, host and port, and another app on the same server can read the drafts that this one writes.
That adds little, since a page on the same server can already frame this app and read what it shows while the user has it open.
The plugin keys a draft on the page's path as well as on the user, so that two apps on one server keep their drafts apart, while an app reached both under its GUID and under its vanity path keeps two sets.

The plugin takes the text that it compares a board with once every plugin's `start` has run on that board, since a `start` may change the board as it opens, as the DAG's gives a position to each block that lacks one ([The DAG's state](Rewrite-1.3.1#starting-on-a-board)).
Taken before that, the text of the board that R sent would differ from the board at the first look, and every page that opened that board would leave a draft.
Today's first tick takes its hash at the session's first flush, before the user can have changed anything ([R/draft.R#L79-L93](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L79-L93)).

The page draws a draft's id from random bytes, as blockr.core draws its UUIDs, since `crypto.randomUUID()` exists only in a secure context, which a page served over plain HTTP to a host other than localhost lacks ([srcts/store/ids.ts#L107-L111](https://github.com/BristolMyersSquibb/blockr.core/blob/6141ff4d28cf6ed1d782b1c797612dcb1056f36e/srcts/store/ids.ts#L107-L111)).

Where each page held a Web Lock named for its draft's id, the other pages could ask the Web Locks API which pages are still open, and leave their drafts out of the offer ([Web Locks API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Locks_API)).
That API exists only in a secure context, as `crypto.randomUUID()` does, so the plugin offers every draft on every page.
Such a lock can come later for the pages that have the API, and the pages that lack it would still offer every draft.

A page that stays hidden while another page deletes its draft writes the draft again only once it shows again or its board changes.
So where the browser closes first, a discarded draft stays discarded, as the user asked in the other page, and a restored one lives on in the copy that the restoring page wrote.

The store never changes a board in place ([State in JS](Rewrite-1#principles)), so a look at which `core.store.board()` returns the object that the last look read, as when the page hides or shows with no change since, needs neither `core.store.save()` nor a comparison.
Such a look only checks, where the board holds unsaved work, that the board's draft is still in the browser, by one read of its id.

</details>
