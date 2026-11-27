# The controls and dialogs: opening, saving, New and the URL
Status: draft. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): the storage controls that every frontend draws for the plugin, with their rows and states, the dialogs of the plugin's own, opening a record as the page starts and later, saving, the key chooser, New, how the URL follows the open record, the controls where the plugin has no backend, the avatar and the plugin's notifications.
It shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that let a plugin open the board that R sent, rebuild session management with its controls and its dialogs, offer Save, Open and New where the plugin has no backend, and open the record that a URL names.
The operations behind the controls are [The storage API](Rewrite-1.6.1)'s, and the drafts button with its dialog is [Drafts in the browser](Rewrite-1.6.4)'s.

## What must hold

1. Every control and dialog of today's piece of the navbar has its place among the storage controls or in a dialog of the plugin's own, but for what [Session management as a storage plugin](Rewrite-1.6#today) drops with its reason, and every frontend draws the controls with its own components ([Plugins](Rewrite-1.1.12#storage)).
2. Opening a record, saving, "Save as new workflow…" and New reload no page ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 1).
3. The URL names the open record by its key, its owner and its version, in `id`, `user` and `version`, from the moment the record opens and after each save ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 3).
4. A board that no record holds asks for a key at its first save, and Save adds a version only to the record that the plugin opened ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 4).

## Proposal

### The controls

The plugin's storage controls are those of today's piece of the navbar, in today's order ([R/ui.R#L6-L184](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/ui.R#L6-L184)):

1. A menu named after the record's key, or "Untitled workflow" before the first save, with the ten most recent records, "All workflows…", "New workflow" and "New in a new tab".
2. A button that says how many drafts wait, such as "2 drafts", while any do ([Drafts in the browser](Rewrite-1.6.4)).
3. The save status, such as "Not saved", "Just now" or "5 mins ago", and "Saved as draft" or "Autosave failed" once the plugin writes drafts.
4. A menu named Save, with Save, which reads "Save…" before the first save, "Save as new workflow…", Download, "Version history" with the last three versions and "All versions…", and "Share…".

- Save and "Save as new workflow…" carry the shortcuts Mod+S and Mod+Shift+S, which every frontend binds ([Plugins](Rewrite-1.1.12#storage)).
- The controls call a record a workflow, as today's do, and the DAG's panel is named "Workflow", as today's extension is ([Client-drawn DAG](Rewrite-1.3#proposal)), since both name the user's board ([Glossary](Glossary)).
- The workflows menu names the record by its key rather than by the board's name, which no storage plugin keys a record on, and a dock app leaves the board's name out of its bar, so that the bar shows one name ([The dock's navbar](Rewrite-1.2.5#the-docks-own-parts)).
  Core's basic frontend heads its toolbar with the board's name, beside the workflows menu, so that it shows both, since the board's name and the record's key name different things ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
- A row of the workflows menu opens its record in place, since a control has no second action, while the dialog behind "All workflows…" keeps the link that opens a record in a new tab.
- The search over records lives in that dialog alone, as today's second search does, since core's three kinds of control hold no text field, and a menu holds a fixed set of rows, so the workflows menu loads no more rows as it scrolls ([Plugins](Rewrite-1.1.12#storage)).

### The avatar

- For the user whom the backend's `user` gives, a status with the user's initials follows those controls, in place of today's avatar, a navbar item of its own ([R/avatar.R#L23-L53](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/avatar.R#L23-L53)), while `avatar_navbar_item()` returns the navbar item that places that status apart.
- A dock app that appends that item to its `navbar`, as today's appends the avatar, keeps the status after the options button, where today's avatar sits ([The dock's navbar](Rewrite-1.2.5#what-the-bar-holds)).
- The plugin takes the initials from the backend, which gives in R's folder the user under whom R runs ([The storage API](Rewrite-1.6.1#who-the-user-is)).

### The dialogs

- The plugin draws what its controls cannot hold in dialogs of its own, with blockr.ui's components ([Plugins](Rewrite-1.1.12#storage)).
- "All workflows…" and "All versions…" open the records with their versions, as today's "Manage Workflows" does: the search, the table that loads more rows as it scrolls, a selection with select-all, Delete and Download of the selection, Upload, and for each record and each of its versions Load, a link to a new tab, Download and Delete.
- Download gives a record or a version as its JSON board, and several as a zip file, which the browser builds itself.
- Upload stores a JSON board once `core.store.check()` passes it, and a file of today's stack as it is, which converts as it opens ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today)).
- "Share…" opens the sharing settings ([Connect from the browser](Rewrite-1.6.2#sharing)).
- Save before the first save and "Save as new workflow…" ask for the record's key, as today's "Choose a workflow ID" does.
  At the first save, the field suggests a key made from the board's name, such as `sales-review` for "Sales review", where today's suggests the board's id, so that the two names start out alike.

### Opening

- A URL that names a record makes the plugin's `storage.load()` resolve with the text of that record's board.
  Core opens that board in place of the script's board, before anything is drawn or evaluated ([Drawing the board](Rewrite-1.1.8#starting-the-page)), so `rack_loader()` goes.
  Where the record does not load, core opens the script's board and tells the user why, where today's loader gives a cleared board without a word.
- A record that the user opens later, from a menu or a dialog, opens through `core.store.open()`, with no reload.
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
- "Save as new workflow…" creates a record under a key that the user picks, suggesting the key with `-copy`, as today, and moves the URL to it.
  It opens nothing, since the board on the page is the one that the new record holds.

### The URL

- As a record opens, and as a save adds a version, the plugin updates the URL in place, with the record's `id`, `user` and `version`, keeping the URL's other parameters as today.
- New drops the record from the URL (above).

### Without a backend

- Where the plugin has no backend, as on Connect for a visitor without a key, such as one who is not signed in, or where a service refuses with `unauthorized`, its controls are Save, which saves a download, Open, which opens an upload, and "New workflow", beside the drafts button.
- A status says why no records show, with a tooltip that names what is missing: a Connect sign-in, a sign-in to the service, which the status links where the service gives its `sign_in` ([The storage API](Rewrite-1.6.1#who-the-user-is)), or the blockr option `session_mgmt_backend`.
- Where the backend's capability `saving` is false, as on Connect for a visitor with the Viewer role, the controls list and open records as with a backend, while Save saves a download, "Save as new workflow…" and Delete are left out, and the status says that the user's role saves no records ([Connect from the browser](Rewrite-1.6.2#what-a-visitors-role-allows)).
- Open converts a file of today's stack through R, as an upload does ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today)).

### Notifications

- The plugin's notifications, such as "Saved workflow" with the key and every failure of the backend, go through `core.notifications.notify()`, which the frontend shows as toasts ([Plugins](Rewrite-1.1.12#storage)).

## Open questions

- Whether a record that opens adds an entry to the browser's history, so that Back returns to the record before, or replaces the URL in place, as today: it blocks the Work item on the URL, and the user's choice settles it.
- Which rules a key follows, such as its characters and its length, which the key chooser checks before a save: settled by what Connect and pins allow of a pin's name.
- Under which key an upload is stored, since the plugin keys no record on the board's id, which today's upload takes: the user's choice settles it, between a key made from the file's name and asking for one, as a first save does.

<details><summary>Notes for implementers</summary>

Today's avatar relies on the dock taking no room for a navbar item whose output renders nothing, which is among the coupling listed in [Client-drawn dock](Rewrite-1.2), while as one of the plugin's controls it is left out wherever the backend gives no user ([The dock's navbar](Rewrite-1.2.5)).

</details>
