# Records, links and app scripts across the switch
Status: draft. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): how what users made with today's blockr.session crosses the switch.
It covers the records that today's blockr.session saved, which convert as the plugin opens them, the files of today's stack that a visitor uploads, the links made today, and the app scripts that call blockr.session's functions or set its blockr options, with its migration notes.
It builds on [The conversion and the migration notes](Rewrite-1.8.3), which settles the conversion as a whole, and shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that convert what today's stack saved and write the migration notes.

## What must hold

1. Records that blockr.session stored today open, and so do files of today's stack that a visitor uploads ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 6).
2. A link made today opens the record that it names, through `board_name` too ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 3).
3. An app script that uses blockr.session today runs on the new stack once it makes the changes that the migration notes list.

## Proposal

### Records and files saved today

- A record that blockr.session stored today, or a file of today's stack that a visitor uploads, converts as the plugin opens it, through a request that R answers with blockr.convert's `convert_file()` ([The conversion and the migration notes](Rewrite-1.8.3#who-converts)).
- An upload of a file of today's stack is stored as it is, and converts as it opens, as a record saved today does.
- The Connect backend reads the pins of records saved today as it reads its own ([Connect from the browser](Rewrite-1.6.2#records-as-pins)), and R's folder reads those of today's local board ([The storage API](Rewrite-1.6.1#rs-folder)).
- The first save after a record saved today opens always adds a version, the record's first in the new format, since no hash of a JSON board matches today's content hash (notes).

### Links made today

- A URL names a record in `id`, `user` and `version`, as today, and `board_name`, which today's stack reads where `id` is missing, still names the record's key ([R/server.R#L1246](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1246)).
- The URL's `recover` goes, since a draft opens from the drafts button, with no reload ([Drafts in the browser](Rewrite-1.6.4)).

### App scripts

What changes for an app script, each change argued on the page that it links:

- The `manage_project()` plugin goes, since session management runs by default wherever blockr.session is installed ([Session management as a storage plugin](Rewrite-1.6#proposal)).
- The loader `rack_loader()` goes, since the plugin's `storage.load()` opens the record that a URL names ([The controls and dialogs](Rewrite-1.6.3#opening)).
- The blockr option `session_mgmt_backend` names a service by its URL, where today it holds a backend or a function that returns one, and the blockr option `session_folder` names the folder that a folder board names there today ([The storage API](Rewrite-1.6.1#choosing-the-backend)).
- The function `avatar_navbar_item()` returns the navbar item that places the plugin's avatar status apart ([The controls and dialogs](Rewrite-1.6.3#the-avatar)).
- The exported `rack_create()`, `rack_append()`, `rack_load()` and `rack_records()` go, with the rack generics, since the storage API takes their place ([The storage API](Rewrite-1.6.1#the-operations)).
- The test helpers `mock_board_connect()` and `connect_fixture()` go ([Connect from the browser](Rewrite-1.6.2#tests)).
- The blockr options `session_connect_tag`, `session_autosave` and `session_draft_ttl` stay.

### The migration notes

- The migration notes of blockr.session are a vignette that lists each change above that an app script needs, written for an AI to apply ([The conversion and the migration notes](Rewrite-1.8.3#the-migration-notes)).

## Open questions

- What becomes of today's drafts, records at reserved keys that `draft = TRUE` marks, which the new stack's drafts no longer read: the user's choice settles it, between leaving them out of every listing and offering them once.
- What a link made today with `new` opens, which today's New puts in the URL: settled with how the URL follows the open record ([The controls and dialogs](Rewrite-1.6.3#the-url)).

<details><summary>Notes for implementers</summary>

Today's content hash is `rlang::hash()` of the R list that a save writes ([R/rack.R#L478-L480](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L478-L480)), which no hash of a JSON board matches.
So the first save after a record saved today opens always adds a version, the record's first in the new format, as [The conversion and the migration notes](Rewrite-1.8.3#who-converts) has it.

</details>
