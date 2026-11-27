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

Today's piece of the navbar is the workflows menu, which is named after the record's key, then the drafts notice, the save status and the Save menu ([R/ui.R#L6-L184](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/ui.R#L6-L184)).
A row of the workflows menu shows a record's display name and how long ago it was saved, with an icon that opens it in a new tab ([R/server.R#L1331-L1355](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1331-L1355)).
The Save menu holds "Save…" before the first save, and Save, "Save as new workflow…" and Download after it, beside the last three versions, each with how long ago it was saved ([R/server.R#L742-L839](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L742-L839)).
The open version is marked "(Current)", and it opens nothing, there and in the dialog "Manage Workflows", which gives it no Load and no Delete ([R/server.R#L1859-L1946](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1859-L1946)).
The Save menu's Download gives the record's latest version as the backend stores it ([R/server.R#L357-L382](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L357-L382)).
The dialog "Choose a workflow ID" asks for the key in a field "Workflow ID" with the hint "Must be unique.", and "Save as new workflow…" suggests the key with `-copy`, then `-copy-2` and on, where one is taken ([R/server.R#L1439-L1481](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1439-L1481)).
Today's sharing settings set the visibility to Private, Restricted, Logged-in or Public, list every user and group that a record is shared with, collaborators included and a group by its GUID, each with Remove, and search users to share with ([R/server.R#L871-L1161](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L871-L1161), [R/connect.R#L486-L507](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L486-L507)).
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
  { kind: "button", id: "drafts", label: "2 drafts", tooltip: "Unsaved work from an earlier session", run },
  { kind: "status", id: "status", text: "5 mins ago", tooltip: "Saved at 09:24" },
  { kind: "menu", id: "save-menu", label: "Save", items: [
    { kind: "button", id: "save", label: "Save", shortcut: "Mod+S", run },
    { kind: "button", id: "save-as", label: "Save as new workflow…", shortcut: "Mod+Shift+S", run },
    { kind: "button", id: "download", label: "Download", run },
    { kind: "menu", id: "versions", label: "Version history", items: [
      { kind: "button", id: "version-1", label: "5 mins ago (Current)", tooltip: "Saved at 09:24", disabled: true, run },   // the last three versions
      { kind: "button", id: "all-versions", label: "All versions…", run },
    ] },
    { kind: "button", id: "share", label: "Share…", run },
  ] },
  { kind: "status", id: "avatar", text: "JD", tooltip: "Jane Doe" },
]
```

- The workflows menu is named after the open record's key, or "Untitled workflow" while no record is open, as before the first save.
  Where another user owns the open record, the name has the owner before the key, as the rows have it (below), where today's shows the key alone.
  Its rows are the ten records of the latest saves among those that `list_records` gives, each labeled with its key, and with its owner before it, as `jane/q3-cohorts`, where another user owns it, as pins names a pin, with how long ago it was saved as its tooltip.
  Until the listing comes, and where it fails, the menu holds its last three rows alone.
  The plugin lists the records as it starts, after each save, upload or delete of its own, and as a dialog of records opens.
- The drafts button shows while any draft waits, as "1 draft" or "2 drafts", with today's tooltip, and opens the drafts ([Drafts in the browser](Rewrite-1.6.4)).
- The save status reads "Not saved" before the first save, "Just now" after a save, and then how long ago the open version was saved, such as "5 mins ago", with the time of the save as its tooltip, and "Saved as draft" or "Autosave failed" as the plugin writes a draft, which it does in every app except under the load lock ([Drafts in the browser](Rewrite-1.6.4#writing-a-draft)).
  The plugin's `subscribe()` calls back each minute, so that the frontend draws the status again.
- The Save menu holds "Save…" alone before the first save, and Save, "Save as new workflow…", Download, "Version history" and "Share…" after it, as today's does.
  Its Download gives the open version as the backend stores it, where today's gives the latest version even after the user opened an older one.
  "Version history" is a menu of its own, with the last three versions, each labeled with how long ago it was saved, with the time of the save as its tooltip, and "All versions…".
  The open version is marked "(Current)" and greyed out, since it opens nothing, as today's is.
  "Share…" shows where the backend's capabilities give `sharing` or `visibility` and the user owns the record.
- Save and "Save as new workflow…" carry the shortcuts Mod+S and Mod+Shift+S, which every frontend binds ([Plugins](Rewrite-1.1.12#storage)).
- The controls call a record a workflow, as today's do, and the DAG's panel is named "Workflow", as today's extension is ([Client-drawn DAG](Rewrite-1.3#proposal)), since both name the user's board ([Glossary](Glossary)).
- The workflows menu names the record by its key rather than by the board's name, which no storage plugin keys a record on.
  So an app script with this plugin passes `drop = "name"` to the dock's `custom_navbar()`, which leaves the board's name off the dock's bar, so that the bar shows one name ([The dock's navbar](Rewrite-1.2.5#the-docks-own-parts)).
  Core's basic frontend heads its toolbar with the board's name and draws the workflows menu at the toolbar's end, so that it shows both, since the board's name and the record's key name different things ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
- A row of the workflows menu opens its record in place, since a control has no second action, while the dialog behind "All workflows…" keeps the link that opens a record in a new tab.
- The search over records lives in that dialog alone, as today's second search does, since core's three kinds of control hold no text field, and a menu holds a fixed set of rows, so the workflows menu loads no more rows as it scrolls ([Plugins](Rewrite-1.1.12#storage)).
- Under the load lock, which fixes the app to its opening board, the controls and the dialogs leave out what opens a board ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
  So the workflows menu gives way to a status with the record's key, and the version history holds "All versions…" alone, which opens the same dialog as "All workflows…".
  The dialogs leave out Load, and the links that open a record in a new tab, since a page under that lock opens its opening board whatever its URL names.
  Saving, downloads, uploads, deletes and sharing stay.

### The avatar

- For a user who is signed in, on Connect or to a service, a status with the user's initials follows those controls, in place of today's avatar, a navbar item of its own ([R/avatar.R#L23-L53](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/avatar.R#L23-L53)), while `avatar_navbar_item()` returns the navbar item that places that status apart.
  Its tooltip is the user's name.
- In the folder backend, where nobody signs in, the plugin gives no avatar, as [The dock's navbar](Rewrite-1.2.5#the-storage-plugins-controls) has it.
  Today's avatar draws nothing there either, since `session$user` is unset off Connect ([R/avatar.R#L42-L53](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/avatar.R#L42-L53)).
- A dock app that appends that item to its `navbar`, as today's appends the avatar, keeps the status after the options button, where today's avatar sits ([The dock's navbar](Rewrite-1.2.5#what-the-bar-holds)).
- The plugin makes the initials from the `name` that the backend's `user` gives ([The storage API](Rewrite-1.6.1#who-the-user-is)), by the rule of today's `get_initials()`: the first letters of the name's first two words, or else its first two letters ([R/avatar.R#L55-L68](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/avatar.R#L55-L68)).

### The dialogs

- The plugin draws what its controls cannot hold in dialogs of its own, with blockr.ui's components ([Plugins](Rewrite-1.1.12#storage)).
- "All workflows…" opens the records, and "All versions…" opens them with the open record's versions shown, as today's "Manage Workflows" does.
  A search field filters the records by their key and their owner, ignoring case, and the table shows ten rows, and ten more as it scrolls to its end, from the listing that the plugin holds ([The storage API](Rewrite-1.6.1#listing-and-search)).
  Each row shows the record's key, its owner where another user owns it, and how long ago it was saved, with Load, which closes the dialog and opens the record in place, a link that opens it in a new tab, Download, and Delete.
  It expands to its versions, each showing how long ago it was saved and its version, with the same four.
  The open version has no Load and no Delete, as today's has none, and the latest version has no Delete, since the storage API refuses to delete it, as Connect refuses to delete the bundle that a pin serves ([The storage API](Rewrite-1.6.1#the-operations)).
  Delete shows only on the records that the user owns and on their versions, as "Share…" does, since sharing makes other users viewers of a record, who may open it but not change it ([Connect from the browser](Rewrite-1.6.2#sharing)).
  A collaborator, whom Connect's own settings add, may add versions to another user's record ([Saving](#saving)), but sees no Delete on it, since `writable` says only that the user may add versions.
  A selection with select-all, which takes every record that the search leaves, downloads the records that it holds and deletes those of them that the user owns, and Upload adds records from files.
- Delete asks first, in a dialog of blockr.ui's that names the record, the version or how many records the selection holds, since a deleted record or version does not come back, where today's asks through the browser's `confirm()`.
  Deleting the open record leaves its board on the page, which then no record holds, and the plugin drops the record from the URL, so that the next save asks for a key (condition 4).
- Download gives the text that a version stores: a JSON board, or today's serialization for a version that today's stack saved, which the store refuses ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today)).
  It names a record's file after its key, as `sales-review.json`, and a version's after the key and the version, as `sales-review_v<version>.json`, as today's names a version's file ([R/server.R#L591-L701](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L591-L701)).
  It gives several as a zip file, which the browser builds itself.
- Upload takes one or several files, and stores each as a record under the file's name without `.json` where that name follows the rule of a key (below), and otherwise under a key made from it, as the key chooser makes one from the board's name.
  Where the user holds that key already, Upload adds `-copy`, then `-copy-2` and on, as "Save as new workflow…" does, so that an upload never adds a version to another record (condition 4).
  So a record that a download carries to another backend keeps its key there (condition 5).
  It stores a file once `core.store.check()` passes it, and skips any other, a file of today's stack among them, with a notification that names the file and why the check refused it ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today)).
- "Share…" opens the sharing settings ([Connect from the browser](Rewrite-1.6.2#sharing)): the access, as Private, Restricted, Logged-in or Public, as today's settings set it, where Private is `acl` with no shares, and for Restricted the users and groups whom the record is shared with, collaborators included, each with Remove, and a search of users that shares the record with the user picked.
  The search shows each user's email, or else their username, under their name, as today's does ([R/server.R#L1053-L1080](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1053-L1080)).
  Picking Private removes every share, as today's does ([R/server.R#L1094-L1121](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1094-L1121)).
  The dialog leaves out what the backend's capabilities do not give: the access without `visibility`, the shares without `sharing`, and the search without `user_discovery` ([The storage API](Rewrite-1.6.1#the-operations)).
- Save before the first save, Save on a record that the user may only open ([Saving](#saving)), and "Save as new workflow…" open the key chooser, as today's "Choose a workflow ID" does, with its field "Workflow ID".
  At the first save, the field suggests a key made from the board's name, such as `sales-review` for "Sales review", where today's suggests the board's id, so that the two names start out alike, and "Save as new workflow…" suggests the open record's key with `-copy`, then `-copy-2` and on, as today.
  Where a key with its suffix would pass 64 characters, the chooser cuts the key before the suffix.

### The key

- A key is 3 to 64 letters, digits, hyphens and underscores, `[-_A-Za-z0-9]{3,64}`, which is what Connect takes through pins, the strictest of the backends, so that a key that one backend takes, every backend takes (notes).
- A key may not start with `blockr-draft-`, since the listing leaves out such records as today's drafts ([Records, links and app scripts across the switch](Rewrite-1.6.5#todays-drafts)).
  Today's saves and uploads refuse that prefix as well ([R/rack.R#L403-L415](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L403-L415)).
  This rule is the plugin's own, which the key chooser and Upload keep, while the storage API's rule is the first alone, so that no service has to know of today's drafts ([The storage API](Rewrite-1.6.1#records-and-versions)).
- The key chooser makes a key from a name, in this order:
  1. It turns the name to lower case and drops its accents.
  2. It turns every run of characters other than letters, digits and underscores into one hyphen.
  3. It drops a leading `blockr-draft-`.
  4. It cuts the key to 64 characters and trims hyphens from its ends.
  5. It falls back to `workflow` where fewer than three characters are left.
- As the user types, the key chooser says where a key breaks the rule, and where the user holds a record of that key among the listing, so that Save stays greyed out until the key fits.
  Since another page may take the key in the meantime, the failure `key_taken` of `create_record` has the last word, and the chooser then stays open and says so, as it does for any other failure of `create_record` ([The storage API](Rewrite-1.6.1#failures)).

### Opening

- A URL that names a record makes the plugin's `storage.load()` resolve with the text of that record's board.
  Core opens that board in place of the script's board, before anything is drawn or evaluated ([Drawing the board](Rewrite-1.1.8#starting-the-page)), so `rack_loader()` goes.
  Where the record does not load, core opens the script's board and tells the user why, where today's loader gives a cleared board without a word.
  The plugin then holds no record open, so that the next save asks for a key rather than adding the script's board to that record (condition 4).
  The URL keeps naming the record, so that a reload tries it again.
- A record that the user opens later, from a menu or a dialog, opens through `core.store.open()`, with no reload.
  A record that does not open leaves the open board as it was.
  Where the backend fails, the plugin tells the user why, with an error of the code `board_open_failed`.
  Where the store refuses the board, as it refuses one that today's stack saved until blockr.convert's `convert_file()` has converted it ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today)), core tells the user why, as it does for core's Open ([Plugins](Rewrite-1.1.12#storage)).
- Opening a record, or New (below), drops the board that was open, unsaved work included, as today's reload does, while a draft keeps that work ([Drafts in the browser](Rewrite-1.6.4#writing-a-draft)).
- A page whose URL names no record opens the script's board as R sent it ([Defining a board in R](Rewrite-1.1.3#the-opening-board)), where today's loader clears its blocks, so a deployment that wants an empty start serves an empty board.
- The plugin sets no board's name as a record opens, where today's sets it from the record's title, since the record holds the board with the name it was saved with.
- Under the load lock, core calls no `storage.load()`, and the controls leave out what opens a board ([Plugins](Rewrite-1.1.12#storage)).

### New

- "New workflow" opens the board that R sent again, through what `CoreApi` gives plugins to open it ([Drawing the board](Rewrite-1.1.8#opening-a-board)), with no reload, and drops the record from the URL, so that it gives what a page whose URL names no record gives, blocks included, as today's New does in an app that passes no loader to `serve()`, while today's `rack_loader()` clears them ([Backlog](Backlog#an-empty-new-and-new-in-cores-storage-plugin)).
- "New in a new tab" opens the app's URL without a record in a new tab.

### Saving

- The controls save the JSON board that `core.store.save()` writes ([Serialization](Rewrite-1.1.4#files)).
- Save adds a version to the record that the plugin opened, unless the board is the one that the plugin opened or saved last, which it tells by the board's text ([The storage API](Rewrite-1.6.1#records-and-versions)), and which it reports as "No changes to save", as today.
- Save adds a version to a record that another user owns only where the user may add versions to it, as a collaborator may on Connect, which today's Save allows too, since it saves under the open record's owner ([R/connect.R#L38-L40](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L38-L40)).
- Where the user may only open the record, as a user whom its owner shared it with, Save opens the key chooser as "Save as new workflow…" does, with the key that it suggests, such as `q3-cohorts-copy`, and a line saying that the user may open `jane/q3-cohorts` but not save to it.
  The plugin tells which from the listing, where each record's `writable` says whether the user may add versions to it ([The storage API](Rewrite-1.6.1#the-operations)).
  Until the listing comes, and where it fails, Save tries to add the version, and a save that `add_version` refuses with `forbidden`, there or where the owner took the user's rights away after the listing, opens the key chooser the same way.
- A board that no record holds asks for a key at its first save, which creates the record and fails where the key is taken ([The storage API](Rewrite-1.6.1#records-and-versions)).
- "Save as new workflow…" creates a record under a key that the user picks, and moves the URL to it.
  It opens nothing, since the board on the page is the one that the new record holds.
- The plugin saves or opens one board at a time.
  While it saves or opens one, Save, "Save as new workflow…" and every control that opens a board grey out, so that a save that ends after another board opened never moves the URL to that board.
  The save status says "Saving…" until the save ends.
  A save that fails leaves the record as it was, and the plugin tells the user why through a notification, while the status keeps the time of the last save that worked.

### The URL

- As a record opens, and as a save adds a version, the plugin replaces the URL in place, through `history.replaceState()`, with the record's `id`, `user` and `version`, keeping the rest of the URL's query string, as today's `updateQueryString()` replaces it before its reload ([R/utils.R#L141-L144](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/utils.R#L141-L144)).
  So Back leaves the app, as it does today, rather than opening the record before, which could drop unsaved work.
- The URL names `user` only where another user owns the record, and `version` only where the user picked a version, in the version history, a dialog or a link, until the next save drops it, as today's does ([R/utils.R#L158-L171](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/utils.R#L158-L171)).
- New drops the record from the URL (above), and so does deleting the open record ([The dialogs](#the-dialogs)).
- As the page starts, the plugin also updates a link made today, as [Records, links and app scripts across the switch](Rewrite-1.6.5#links-made-today) has it.

### Without a backend

- The plugin has no backend on Connect for a visitor without a key, such as one who is not signed in, where a service refuses with `unauthorized`, and where a service speaks a version of the storage API that the plugin does not, which a notification names ([The storage API](Rewrite-1.6.1#the-operations)).
  Its controls are then Save, which saves a download as core's Save does, Open, which opens an upload, and "New workflow", beside the drafts button.
- A status says why no records show.
  Its tooltip names what is missing, as the reply to the once-per-page request names it ([The storage API](Rewrite-1.6.1#the-once-per-page-request)): a Connect sign-in, the app's Visitor API Key integration on Connect, which the app's owner can add only where the app requires a login, or a sign-in to the service.
  Where the service gives its `sign_in`, a button "Sign in" beside the status opens it in a new tab, since a status runs nothing ([The storage API](Rewrite-1.6.1#who-the-user-is)).
  As the user comes back to the page after signing in there, the plugin asks the backend's `user` again, so that the records and the controls come back without a reload.
- Where the backend's capability `saving` is false, as on Connect for a key with the Viewer role, whether the visitor's role or the cap of the app's integration gives it ([Connect from the browser](Rewrite-1.6.2#what-a-visitors-role-allows)), the controls list and open records as with a backend, while Save saves a download, whichever record is open.
  They leave out "Save as new workflow…", Upload and Delete, and the status says that the user may open records here but not save them.

### Notifications

- The plugin's notifications, such as "Saved workflow" with the key, "No changes to save", "Deleted version" and every failure of the backend, with the message that the failure carries, go through `core.notifications.notify()`, which the frontend shows as toasts ([Plugins](Rewrite-1.1.12#storage)).
- Each carries a code.
  A failure of the backend carries the failure's code, such as `forbidden`, and a record that does not open carries `board_open_failed`, as core's Open gives it.
  A message carries what it reports, such as `saved` or `no_changes`.
- Each holds until the plugin next does the same, such as the next save for a save's, so that a save that works takes back why the save before it failed.
  Core withdraws all of them as the next board opens ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
- A failure that the plugin shows itself, such as `key_taken` in the key chooser, or the `forbidden` of a save that opens the chooser ([Saving](#saving)), raises no notification ([Notifications, logging and tracing](Rewrite-1.1.14#taking-a-calls-notifications)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's avatar relies on the dock taking no room for a navbar item that renders nothing, which is among the coupling listed in [Client-drawn dock](Rewrite-1.2), while as one of the plugin's controls it is left out wherever no user is signed in ([The dock's navbar](Rewrite-1.2.5)).

Connect's API takes for a content item's name letters, digits, periods, hyphens and underscores ([Connect's API](https://docs.posit.co/connect/api/)).
Its error code 5 says that the name must be 3 to 64 of them, though the API's description of the property gives no length.
Pins creates a content item only for a name of letters, digits, hyphens and underscores ([R/board_connect.R#L504-L519](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/board_connect.R#L504-L519)), and it refuses a slash in a pin's name on every board ([R/pin-read-write.R#L344-L352](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/pin-read-write.R#L344-L352)).
Today's drafts hash their keys for the same reason, since a workflow id may break Connect's rule on a folder board ([R/rack.R#L381-L384](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L381-L384)).
A record saved today under a key outside the rule, on a folder board, still lists, since the rule binds the key chooser and not the listing, and opens once it has been converted, as any record that today's stack saved does ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today)).

Opening a board starts core again, the plugin's `start` and its storage included ([Drawing the board](Rewrite-1.1.8#opening-a-board)).
So the plugin keeps what has to outlive an opening in its module, which loads once per page: the open record, the text of its board as the plugin opened or saved it, the listing, and the backend with its key.
A board that opens without the plugin's call, as where another plugin calls `core.store.open()`, holds no record, so the plugin then drops the record from the URL, as New does.

A browser opens a new tab or a file picker only within the user's click or key press.
So "New in a new tab" and "Sign in" open their tab, and Open and Upload their picker, before they await anything, as core's Open asks for its file.

Save adds a version whatever another page, a collaborator's included, saved to the record since it opened, as today's does, so the later of two saves becomes the latest version.
Collaboration between people is not built ([State in JS](Rewrite-1#proposal)).

</details>
