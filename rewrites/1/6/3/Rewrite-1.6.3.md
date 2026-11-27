# The controls and dialogs: opening, saving, New and the URL
Status: review. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): the storage controls that every frontend draws for the plugin, with their rows and states, the dialogs of the plugin's own, opening a record as the page starts and later, saving, the key chooser and the rule that a key follows, New, how the URL follows the open record, the controls where the plugin has no backend or may not save, the avatar and the plugin's notifications.
It shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that let a plugin open the board that R sent, rebuild session management with its controls and its dialogs, offer Save, Open and New where the plugin has no backend, and open the record that a URL names.
The operations behind the controls are [The storage API](Rewrite-1.6.1)'s, and the drafts button with its dialog is [Drafts in the browser](Rewrite-1.6.4)'s.

## What must hold

1. Every control and dialog of today's piece of the navbar has its place among the storage controls or in a dialog of the plugin's own, but for what [Session management as a storage plugin](Rewrite-1.6#today) drops with its reason, and every frontend draws the controls with its own components ([Plugins](Rewrite-1.1.12#storage)).
2. Opening a record, saving, "Save as new workflow…" and New reload no page ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 1).
3. The URL names the open record by its key, its owner and its version, in `id`, `user` and `version`, from the moment the record opens and after each save ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 3).
4. A board that no record holds asks for a key at its first save, and Save adds a version only to the record that the plugin opened ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 4).
5. A key that one backend takes, every backend takes, so that a record moves between backends under its key.

## Today

Today's piece of the navbar is the record's name with the workflows menu, the drafts notice, the save status and the Save menu ([R/ui.R#L6-L184](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/ui.R#L6-L184)).
A row of the workflows menu shows a record's name and how long ago it was saved, with an icon that opens it in a new tab ([R/server.R#L1331-L1355](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1331-L1355)).
The Save menu holds "Save…" before the first save, and Save, "Save as new workflow…" and Download after it, beside the last three versions, each with how long ago it was saved and a mark on the open one ([R/server.R#L742-L839](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L742-L839)).
The dialog "Choose a workflow ID" asks for the key in a field "Workflow ID" with the hint "Must be unique.", and "Save as new workflow…" suggests the key with `-copy`, then `-copy-2` and on, where one is taken ([R/server.R#L1439-L1481](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1439-L1481)).
Today's sharing panel sets the visibility to Private, Restricted, Logged-in or Public, lists the users that a record is shared with, each with Remove, and searches users to share with ([R/server.R#L871-L1161](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L871-L1161)).
Deleting a record or a version asks the browser's `confirm()` first ([R/server.R#L1621](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1621), [#L1933](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1933)).

## Proposal

### The controls

The plugin's storage controls are those of today's piece of the navbar, in today's order, each one of core's three kinds ([Plugins](Rewrite-1.1.12#storage)).
For a record that the user owns, saved five minutes ago, with two drafts waiting, `controls()` gives, with illustrative ids:

```ts
[
  { kind: "menu", id: "workflows", label: "sales-review", items: [
    { kind: "button", id: "open-1", label: "sales-review", tooltip: "Saved 5 mins ago", run },   // the ten most recent records
    { kind: "button", id: "open-2", label: "jane/q3-cohorts", tooltip: "Saved 2 days ago", run },
    { kind: "button", id: "all", label: "All workflows…", run },
    { kind: "button", id: "new", label: "New workflow", run },
    { kind: "button", id: "new-tab", label: "New in a new tab", run },
  ] },
  { kind: "button", id: "drafts", label: "2 drafts", run },
  { kind: "status", id: "status", text: "5 mins ago", tooltip: "Saved at 09:24" },
  { kind: "menu", id: "save", label: "Save", items: [
    { kind: "button", id: "save", label: "Save", shortcut: "Mod+S", run },
    { kind: "button", id: "save-as", label: "Save as new workflow…", shortcut: "Mod+Shift+S", run },
    { kind: "button", id: "download", label: "Download", run },
    { kind: "menu", id: "versions", label: "Version history", items: [
      { kind: "button", id: "version-1", label: "5 mins ago (open)", run },   // the last three versions
      { kind: "button", id: "all-versions", label: "All versions…", run },
    ] },
    { kind: "button", id: "share", label: "Share…", run },
  ] },
  { kind: "status", id: "avatar", text: "JD", tooltip: "Jane Doe" },
]
```

- The workflows menu is named after the open record's key, or "Untitled workflow" before the first save.
  Its rows are the ten records of the latest saves among those that `list_records` gives, each labeled with its key, and with its owner before it, as `jane/q3-cohorts`, where another user owns it, as pins names a pin, with how long ago it was saved as its tooltip.
  Until the listing comes, and where it fails, the menu holds its last three rows alone.
- The drafts button shows while any draft waits, as "1 draft" or "2 drafts", and opens the drafts ([Drafts in the browser](Rewrite-1.6.4)).
- The save status reads "Not saved" before the first save, "Just now" after a save, and then how long ago the open version was saved, such as "5 mins ago", with the time of the save as its tooltip, and "Saved as draft" or "Autosave failed" where the plugin writes drafts.
  The plugin's `subscribe()` calls back each minute, so that the frontend draws the status again.
- The Save menu holds "Save…" alone before the first save, and Save, "Save as new workflow…", Download, "Version history" and "Share…" after it, as today's does.
  "Version history" is a menu of its own, with the last three versions, each labeled with how long ago it was saved and the open one marked "(open)", and "All versions…".
  "Share…" shows where the backend's capabilities give `sharing` or `visibility` and the user owns the record.
- Save and "Save as new workflow…" carry the shortcuts Mod+S and Mod+Shift+S, which every frontend binds ([Plugins](Rewrite-1.1.12#storage)).
- The controls call a record a workflow, as today's do, and the DAG's panel is named "Workflow", as today's extension is ([Client-drawn DAG](Rewrite-1.3#proposal)), since both name the user's board ([Glossary](Glossary)).
- The workflows menu names the record by its key rather than by the board's name, which no storage plugin keys a record on, and a dock app leaves the board's name out of its bar, so that the bar shows one name ([The dock's navbar](Rewrite-1.2.5#the-docks-own-parts)).
  Core's basic frontend heads its toolbar with the board's name, beside the workflows menu, so that it shows both, since the board's name and the record's key name different things ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
- A row of the workflows menu opens its record in place, since a control has no second action, while the dialog behind "All workflows…" keeps the link that opens a record in a new tab.
- The search over records lives in that dialog alone, as today's second search does, since core's three kinds of control hold no text field, and a menu holds a fixed set of rows, so the workflows menu loads no more rows as it scrolls ([Plugins](Rewrite-1.1.12#storage)).
- Under the load lock, which fixes the app to its opening board, the workflows menu gives way to a status with the record's key, since each of its rows opens a board, and the dialogs leave out Load and Upload, while saving stays ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).

### The avatar

- For the user whom the backend's `user` gives, a status with the user's initials follows those controls, in place of today's avatar, a navbar item of its own ([R/avatar.R#L23-L53](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/avatar.R#L23-L53)), while `avatar_navbar_item()` returns the navbar item that places that status apart.
  Its tooltip is the user's name.
- A dock app that appends that item to its `navbar`, as today's appends the avatar, keeps the status after the options button, where today's avatar sits ([The dock's navbar](Rewrite-1.2.5#what-the-bar-holds)).
- The plugin takes the initials from the backend, which gives in R's folder the user under whom R runs ([The storage API](Rewrite-1.6.1#who-the-user-is)).

### The dialogs

- The plugin draws what its controls cannot hold in dialogs of its own, with blockr.ui's components ([Plugins](Rewrite-1.1.12#storage)).
- "All workflows…" opens the records, and "All versions…" opens them with the open record's versions shown, as today's "Manage Workflows" does.
  A search field filters the records by their key and their owner, ignoring case, and the table shows ten rows, and ten more as it scrolls to its end, from the listing that the plugin already holds ([The storage API](Rewrite-1.6.1#listing-and-search)).
  Each row shows the record's key, its owner where another user owns it, and how long ago it was saved, with Load, which opens it in place, a link that opens it in a new tab, Download, and Delete, and it expands to its versions, each with the same four.
  A selection with select-all, which takes every record that the search leaves, deletes or downloads the records that it holds, and Upload adds records from files.
- Delete asks first, in a dialog of blockr.ui's that names the record or the version, since a deleted record or version does not come back, where today's asks through the browser's `confirm()`.
- Download gives a record or a version as its JSON board, in a file named after its key, and several as a zip file, which the browser builds itself.
- Upload takes one or several files, and stores each as a record under a key made from the file's name, as the key chooser makes one from the board's name (below), with `-copy` where the user holds that key already, so that an upload never adds a version to another record (condition 4).
  It stores a JSON board once `core.store.check()` passes it, and a file of today's stack as it is, which converts as it opens ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today)).
- "Share…" opens the sharing settings ([Connect from the browser](Rewrite-1.6.2#sharing)): the access, as Private, Restricted, Logged-in or Public, as today's panel sets it, where Private is `acl` with no shares, and for Restricted the users whom the record is shared with, each with Remove, and a search of users that shares the record with the user picked.
  The dialog leaves out what the backend's capabilities do not give: the access without `visibility`, the shares without `sharing`, and the search without `user_discovery` ([The storage API](Rewrite-1.6.1#the-operations)).
- Save before the first save and "Save as new workflow…" open the key chooser, as today's "Choose a workflow ID" does, with its field "Workflow ID".
  At the first save, the field suggests a key made from the board's name, such as `sales-review` for "Sales review", where today's suggests the board's id, so that the two names start out alike, and "Save as new workflow…" suggests the open record's key with `-copy`, then `-copy-2` and on, as today.

### The key

- A key is one or more letters, digits, hyphens and underscores, `[-_A-Za-z0-9]+`, which is what Connect takes through pins, the strictest of the backends, so that a key that one backend takes, every backend takes (notes).
- The key chooser makes a key from a name by turning it to lower case, dropping accents, turning every run of other characters into one hyphen and trimming hyphens from its ends, and falls back to `workflow` where nothing is left.
- As the user types, the key chooser says where a key breaks the rule, and where the user holds a record of that key among the listing, so that Save stays greyed out until the key fits.
  Since another page may take the key in the meantime, the failure `key_taken` of `create_record` has the last word, and the chooser then stays open and says so ([The storage API](Rewrite-1.6.1#failures)).

### Opening

- A URL that names a record makes the plugin's `storage.load()` resolve with the text of that record's board.
  Core opens that board in place of the script's board, before anything is drawn or evaluated ([Drawing the board](Rewrite-1.1.8#starting-the-page)), so `rack_loader()` goes.
  Where the record does not load, core opens the script's board and tells the user why, where today's loader gives a cleared board without a word.
- A record that the user opens later, from a menu or a dialog, opens through `core.store.open()`, with no reload.
  A record that does not open leaves the open board as it was, and the plugin tells the user why through a notification.
- A page whose URL names no record opens the script's board as R sent it ([Defining a board in R](Rewrite-1.1.3#the-opening-board)), where today's loader clears its blocks, so a deployment that wants an empty start serves an empty board.
- The plugin sets no board's name as a record opens, where today's sets it from the record's title, since the record holds the board with the name it was saved with.
- Under the load lock, core calls no `storage.load()`, and the controls leave out what opens a board ([Plugins](Rewrite-1.1.12#storage)).

### New

- "New workflow" opens the board that R sent again, through what `CoreApi` gives plugins to open it ([Drawing the board](Rewrite-1.1.8#opening-a-board)), with no reload, and drops the record from the URL, so that it gives what a page whose URL names no record gives, blocks included, as today's New does in an app that passes no loader to `serve()`, while today's `rack_loader()` clears them ([Backlog](Backlog#an-empty-new-and-new-in-cores-storage-plugin)).
- "New in a new tab" opens the app's URL without a record in a new tab.

### Saving

- The controls save the JSON board that `core.store.save()` writes ([Serialization](Rewrite-1.1.4#files)).
- Save adds a version to the record that the plugin opened, unless the board is the one that the plugin opened or saved last, which it tells by a hash of the board's text ([The storage API](Rewrite-1.6.1#records-and-versions)), and which it reports as "No changes to save", as today.
- A board that no record holds asks for a key at its first save, which creates the record and fails where the key is taken ([The storage API](Rewrite-1.6.1#records-and-versions)).
- "Save as new workflow…" creates a record under a key that the user picks, and moves the URL to it.
  It opens nothing, since the board on the page is the one that the new record holds.
- One save runs at a time: Save greys out while a save runs, and the save status says "Saving…" until it ends.
  A save that fails leaves the record as it was, and the plugin tells the user why through a notification, while the status keeps the time of the last save that worked.

### The URL

- As a record opens, and as a save adds a version, the plugin replaces the URL in place, through `history.replaceState()`, with the record's `id`, `user` and `version`, keeping the URL's other parameters, as today's `updateQueryString()` replaces it before its reload ([R/utils.R#L141-L144](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/utils.R#L141-L144)).
  So Back leaves the app, as it does today, rather than opening the record before, which could drop unsaved work.
- The URL names `user` only where another user owns the record, and `version` only where the open version is not the latest, as today's does ([R/utils.R#L158-L171](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/utils.R#L158-L171)).
- New drops the record from the URL (above).

### Without a backend

- Where the plugin has no backend, as on Connect for a visitor without a key, such as one who is not signed in, or where a service refuses with `unauthorized`, its controls are Save, which saves a download, Open, which opens an upload, and "New workflow", beside the drafts button.
- A status says why no records show, with a tooltip that names what is missing: a Connect sign-in, a sign-in to the service, or the blockr option `session_mgmt_backend`.
  Where the service gives its `sign_in`, a button "Sign in" beside the status opens it in a new tab, since a status runs nothing ([The storage API](Rewrite-1.6.1#who-the-user-is)).
- Where the backend's capability `saving` is false, as on Connect for a visitor with the Viewer role, the controls list and open records as with a backend, while Save saves a download, "Save as new workflow…" and Delete are left out, and the status says that the user's role saves no records ([Connect from the browser](Rewrite-1.6.2#what-a-visitors-role-allows)).
- Open converts a file of today's stack through R, as an upload does ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today)).

### Notifications

- The plugin's notifications, such as "Saved workflow" with the key, "No changes to save", "Deleted version" and every failure of the backend, with the message that the failure carries, go through `core.notifications.notify()`, which the frontend shows as toasts ([Plugins](Rewrite-1.1.12#storage)).
- A failure that the plugin shows itself, such as `key_taken` in the key chooser, raises no notification ([Notifications, logging and tracing](Rewrite-1.1.14#taking-a-calls-notifications)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's avatar relies on the dock taking no room for a navbar item whose output renders nothing, which is among the coupling listed in [Client-drawn dock](Rewrite-1.2), while as one of the plugin's controls it is left out wherever the backend gives no user ([The dock's navbar](Rewrite-1.2.5)).

Connect's API takes for a content item's name letters, digits, periods, hyphens and underscores ([Connect's API](https://docs.posit.co/connect/api/)), while pins creates a content item only for a name of letters, digits, hyphens and underscores, and refuses a slash in a pin's name on every board ([R/board_connect.R#L504-L519](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/board_connect.R#L504-L519)).
Today's drafts hash their keys for the same reason, since a workflow id may break Connect's rule on a folder board ([R/rack.R#L381-L384](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L381-L384)).
A record saved today under a key outside the rule, on a folder board, still opens, since the rule binds the key chooser and not the listing.

</details>
