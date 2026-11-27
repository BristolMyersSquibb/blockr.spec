# Records, links and app scripts across the switch
Status: review. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): how what users made with today's blockr.session crosses the switch.
It covers the records that today's blockr.session saved, which open once `convert_file()` has converted them, today's drafts, the files of today's stack that a visitor uploads, the links made today, and the app scripts and deployments that call blockr.session's functions or set its blockr options, with its migration notes.
It builds on [The conversion and the migration notes](Rewrite-1.8.3), which settles the conversion as a whole, and shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that open the record that a URL names, rebuild session management as a storage plugin and write the migration notes.

## What must hold

1. The plugin converts nothing that today's stack saved, and refuses a record or a file of today's stack with core's error ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 6).
   A record that blockr.session stored today opens once blockr.convert's `convert_file()` has converted it.
2. A link made today opens the record that it names, through `board_name` too, once that record has been converted ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 3).
3. An app script that uses blockr.session today runs on the new stack once it makes the changes that the migration notes list.

## Today

Today's blockr.session exports the plugin `manage_project()` with its server and UI, the loader `rack_loader()`, the backend `user_pins_board()`, `avatar_navbar_item()`, and the rack layer's constructors, generics and entry points ([NAMESPACE](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/NAMESPACE)).
The blockr option `session_mgmt_backend` takes a backend, a pins board or an object of class `rack_backend`, or a function that returns one, `user_pins_board()` by default ([R/utils.R#L1-L25](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/utils.R#L1-L25)).
On Connect, that default exchanges the visitor's session token for a key on the visitor's own account.
Connect sends the token only where a Visitor API Key integration is associated with the app and the visitor is signed in.
Without a token, the default takes a board on the app's own key instead, under the publisher's account, which every such visitor shares ([R/backend.R#L1-L58](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/backend.R#L1-L58)).
The README sets the integration's maximum role to Viewer ([README.Rmd#L73-L79](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/README.Rmd#L73-L79)).

The URL names a record in `id`, or `board_name` where `id` is missing, `user` and `version` ([R/utils.R#L131-L139](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/utils.R#L131-L139)).
New puts `new` in the URL, and a draft's link puts `recover` there with the draft's key.
A bare `recover` opens the list of drafts ([R/draft.R#L242-L261](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/draft.R#L242-L261)).
As a record opens, the board takes the record's title as its name, and Save gives a new record its key as its title ([R/server.R#L68-L82](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L68-L82), [#L199](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L199)).

Today's drafts are records at keys that start with `blockr-draft-`, which `rack_records()` leaves out of the listing ([R/rack.R#L359-L366](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L359-L366)).
For a record that a user saves, `rack_create()` refuses such a key ([R/rack.R#L399-L415](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L399-L415)).
An upload stores a file only once `blockr_deser()` reads it, and skips any other file with a message that names it ([R/transfer.R#L33-L76](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/transfer.R#L33-L76)).

## Proposal

### Records and files saved today

- The plugin converts nothing that today's stack saved.
  A deployment converts on purpose, in R, only the records that it keeps, so that whoever converts them sees the warning that names what each conversion left out ([The conversion and the migration notes](Rewrite-1.8.3#what-a-session-cannot-rebuild)).
  So R converts nothing as a record opens.
- The board of a record that blockr.session stored today has no `format`, unlike every JSON board ([Serialization](Rewrite-1.1.4#files)).
  So the store refuses it as the plugin opens it, with an error that names blockr.convert's `convert_file()`, and core tells the user why ([The conversion and the migration notes](Rewrite-1.8.3#who-converts), [The controls and dialogs](Rewrite-1.6.3#opening)).
- An upload skips a file of today's stack, as it skips every file that `core.store.check()` refuses, and Open refuses one where the plugin has no backend ([The controls and dialogs](Rewrite-1.6.3#the-dialogs), [The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
  So the plugin saves no board of today's stack to a backend.
- A deployment that keeps records saved today runs `convert_file()` over them in R, and the migration notes say how.
  It writes each JSON board back as a new version of its record, so that the record keeps its key and its title, and the links made today open it (Links made today).
  The versions that today's stack saved stay as they were, and the store refuses each of them, whether or not their record was converted.
- The Connect backend reads the pins of records saved today as it reads its own, their `data.txt` in YAML included ([Connect from the browser](Rewrite-1.6.2#the-bundle)), and R's folder reads those of today's local board through today's methods ([The storage API](Rewrite-1.6.1#rs-folder)).
  So the plugin lists every record saved today, and opens each that was converted.
  A deployment that saved its records today through a backend of its own may serve them through a service of its own, and converts those that it keeps in the same way.
- A converted record opens under the name that its board held when it was saved, since the conversion takes the board's name from today's `board_name` board option ([Defining a board in R](Rewrite-1.1.3#the-script)).
  Today's open names the board after the record's title instead, which Save sets to the record's key (Today).
  This follows from the plugin setting no board's name as a record opens ([The controls and dialogs](Rewrite-1.6.3#opening)).

### Today's drafts

- The plugin leaves out of the listing every record whose key starts with `blockr-draft-`, as today's `rack_records()` does, since such a record is one of today's drafts, which the new stack keeps in the browser instead ([Drafts in the browser](Rewrite-1.6.4)).
- So a key that a user picks may not start with `blockr-draft-`, since the listing would hide its record.
  Today's `rack_create()` refuses such a key too (Today), and the key chooser says so as the user types ([The controls and dialogs](Rewrite-1.6.3#the-key)).
- Today's drafts are not offered again, since each holds a board of today's stack, which the plugin does not convert.
  Unsaved work that one holds is the user's to restore before the switch.
- A deployment may delete them with pins in R, and the migration notes say how.

### Links made today

- A URL names a record in `id`, `user` and `version`, as today, and the plugin reads `board_name` where `id` is missing, as today's stack does ([R/server.R#L1246](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1246)).
  The record that such a link names opens once it has been converted (Records and files saved today).
- A version names the same thing as today: a bundle's id on Connect, and a pin's version on a folder board.
  So a link made today that names a version names one that today's stack saved, which the store refuses, since converting a record adds a version rather than changing one in place.
- A link with `new` names no record.
  So it opens what such a URL opens, the board that R sent, as today's New does in an app that passes no loader ([The controls and dialogs](Rewrite-1.6.3#new)).
- A link with `recover` and a draft's key opens the record that its `id` names, if any, since drafts leave the URL ([Drafts in the browser](Rewrite-1.6.4#offering-and-restoring)).
- A link with a bare `recover` opens the page as if the link held no `recover`.
  Today that link opens the list of drafts.
  Now the plugin's drafts button shows whenever a draft waits, and one click on it opens the drafts, so the link needs no list of its own ([The controls and dialogs](Rewrite-1.6.3#the-controls)).
- As the page starts, the plugin replaces `board_name` in the URL with `id`, and drops `new` and `recover`, keeping the URL's other parameters ([The controls and dialogs](Rewrite-1.6.3#the-url)).

### App scripts

What changes for an app script, each change argued on the page that it links:

- The `manage_project()` plugin goes, with `manage_project_server()` and `manage_project_ui()`, since session management runs by default wherever blockr.session is installed ([Session management as a storage plugin](Rewrite-1.6#proposal)).
  A script drops it from the plugins that it passes to `serve()` ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)).
- The loader `rack_loader()` goes, since the plugin's `storage.load()` opens the record that a URL names ([The controls and dialogs](Rewrite-1.6.3#opening)).
  A script drops the `loader` that it passes to `serve()`, which takes none any more ([Defining a board in R](Rewrite-1.1.3#the-opening-board)).
  That holds as well for a loader of the script's own that wraps `rack_loader()`, such as one that keeps the script's board where the URL names no record, since that board is what such a URL opens now.
- The blockr option `session_mgmt_backend` names a service by its URL, where today it holds a backend or a function that returns one ([The storage API](Rewrite-1.6.1#choosing-the-backend)).
  A script drops it where its value is `user_pins_board()`, `pins::board_local()`, or a function of the script's own that does what `user_pins_board()` does: a board on the visitor's key on Connect, and a local board elsewhere.
  A script that sets it to `pins::board_folder()` sets the blockr option `session_folder` to that folder instead, which R serves only where it runs off Connect ([The storage API](Rewrite-1.6.1#rs-folder)).
  A script may set it to a board on the app's own Connect key, such as `pins::board_connect`, which today's README gives for one store that every visitor shares.
  Such a script drops it, and its deployment changes as Deployments says (below).
  A script that sets it to a backend of its own, of class `rack_backend`, names a service that speaks the storage API instead ([The storage API](Rewrite-1.6.1#a-deployments-own-service)).
- As the app starts, blockr.session refuses a value of `session_mgmt_backend` that is not a string, with an error that names `session_folder`.
  Without that error, a script that the notes missed would save to another backend without a word, since R leaves out of what the browser reads every blockr option that it cannot write as JSON ([Board options and blockr options](Rewrite-1.1.13#blockr-options)).
- The function `user_pins_board()` goes, since R opens no pins board for the browser but R's folder ([The storage API](Rewrite-1.6.1#rs-folder)).
- The function `avatar_navbar_item()` stays, and returns the navbar item that places the plugin's avatar status apart ([The controls and dialogs](Rewrite-1.6.3#the-avatar)).
- A dock app passes `drop = "name"` to `custom_navbar()`, so that its bar shows the record's key alone rather than beside the board's name ([The dock's navbar](Rewrite-1.2.5#app-scripts-from-today)).
- The rack layer's exports go, since the storage API takes their place ([The storage API](Rewrite-1.6.1#the-operations)): `as_rack_id()`, `new_rack_id()`, `new_rack_record()`, and every function whose name starts with `rack_` but `rack_loader()` (above).
  A backend of a deployment's own that fills the rack generics becomes a service that speaks the storage API.
- The blockr option `session_connect_tag` stays.
- The blockr options `session_autosave` and `session_draft_ttl` go, since the plugin writes drafts in every app and every draft expires after 7 days ([Drafts in the browser](Rewrite-1.6.4#writing-a-draft)).
  A script drops them, and one that still sets them runs all the same, since nothing reads them any more.

### Deployments

- On Connect, a deployment that saves for its visitors associates a Visitor API Key integration with the app, and sets the integration's maximum role to Publisher.
  Its visitors need the Publisher role too ([Connect from the browser](Rewrite-1.6.2#what-a-visitors-role-allows)).
  On Connect's default roles, a key at the Viewer role creates no content ([Role permissions](https://docs.posit.co/connect/admin/user-management/role-permissions/)), so a visitor whose key is capped at Viewer saves downloads alone.
  A cap at Publisher gives the plugin all that it does, while a higher cap would put an administrator's rights in the page, which holds the key in its memory ([Connect from the browser](Rewrite-1.6.2#what-a-visitors-role-allows)).
  So the migration notes raise the maximum role that today's README sets to Viewer (Today), to Publisher and no higher.
- A deployment on Connect without that integration saves today under the publisher's account, through the app's own key (Today).
  After the switch, its visitors have no backend until the integration is associated ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
  An app that is open to anyone without a login gets no visitor's key at all ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)), so its visitors save downloads alone, unless it runs a service of its own.
  Its records stay under the publisher's account, for the deployment to sort out by hand.
  A deployment that needs one store that every visitor shares, as such an app's visitors share one today, runs a service of its own ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)).
- A deployment that keeps the records that its visitors saved today converts them with `convert_file()`, after which they open (Records and files saved today).

### The migration notes

- The migration notes of blockr.session are a vignette that lists each change above that an app script or a deployment needs, written for an AI to apply ([The conversion and the migration notes](Rewrite-1.8.3#the-migration-notes)).
- They are checked as [The conversion and the migration notes](Rewrite-1.8.3#testing) checks every package's notes.
  Among the examples that an AI changes there, with nothing but the notes of the packages that a script calls, are those that pass `manage_project()`, such as blockr.dplyr's `duckdb-lazy` ([inst/examples/duckdb-lazy.R#L155](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/58f232f5baebfab329e54255feca3ef9341d97e1/inst/examples/duckdb-lazy.R#L155)).
- The tests of the plugin open a record that today's blockr.session saved in a pins folder, through R's folder, before and after converting it as the migration notes say.
  Before the conversion, the store refuses the record.
  After it, the record opens under its key and its title, while the store still refuses the version that today's stack saved.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's content hash is `rlang::hash()` of the R list that a save writes ([R/rack.R#L478-L480](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L478-L480)), which the new stack neither reads nor writes, since the plugin tells a changed board itself.

Today's drafts take the key `blockr-draft-record-<hash>` for the draft of a record, and `blockr-draft-session-<epoch>-<hash>` for the draft of a board that no record holds, where the hash is the first eight characters of `rlang::hash()` of the record's key or of the session's own key ([R/rack.R#L393-L430](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L393-L430)).
So nothing but the prefix tells a draft from a record, and only R can tell which record a draft belongs to.

R calls the method of `plugin_requests()` for the plugin's class as `serve()` builds the app ([Plugins](Rewrite-1.1.12#plugin-classes)), so that method is where blockr.session can refuse a `session_mgmt_backend` that is not a string.

</details>
