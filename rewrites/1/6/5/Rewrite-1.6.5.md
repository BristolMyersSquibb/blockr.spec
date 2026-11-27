# Records, links and app scripts across the switch
Status: review. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): how what users made with today's blockr.session crosses the switch.
It covers the records that today's blockr.session saved, which convert as the plugin opens them, today's drafts, the files of today's stack that a visitor uploads, the links made today, and the app scripts and deployments that call blockr.session's functions or set its blockr options, with its migration notes.
It builds on [The conversion and the migration notes](Rewrite-1.8.3), which settles the conversion as a whole, and shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that convert what today's stack saved and write the migration notes.

## What must hold

1. Records that blockr.session stored today open, and so do files of today's stack that a visitor uploads ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 6).
2. A link made today opens the record that it names, through `board_name` too ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 3).
3. An app script that uses blockr.session today runs on the new stack once it makes the changes that the migration notes list.

## Today

Today's blockr.session exports the plugin `manage_project()` with its server and UI, the loader `rack_loader()`, the backend `user_pins_board()`, `avatar_navbar_item()`, and the rack layer's constructors, generics and entry points ([NAMESPACE](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/NAMESPACE)).
The blockr option `session_mgmt_backend` takes a backend, a pins board or an object of class `rack_backend`, or a function that returns one, `user_pins_board()` by default ([R/utils.R#L1-L25](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/utils.R#L1-L25)).
The URL names a record in `id`, or `board_name` where `id` is missing, `user` and `version`, while New puts `new` there and a draft's link `recover` ([R/utils.R#L131-L139](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/utils.R#L131-L139)).
Today's drafts are records at keys that start with `blockr-draft-`, which `rack_records()` leaves out of the listing ([R/rack.R#L359-L366](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L359-L366)).

## Proposal

### Records and files saved today

- A record that blockr.session stored today, or a file of today's stack that a visitor uploads, converts as the plugin opens it, through a request that R answers with blockr.convert's `convert_file()` ([The conversion and the migration notes](Rewrite-1.8.3#who-converts)).
- The plugin tells such a board by its lack of a `format`, which `core.store.check()` refuses, so that it sends R only what needs converting ([Serialization](Rewrite-1.1.4#files)).
- An upload of a file of today's stack is stored as it is, and converts as it opens, as a record saved today does.
- The Connect backend reads the pins of records saved today as it reads its own, their `data.txt` in YAML included ([Connect from the browser](Rewrite-1.6.2#the-bundle)), and R's folder reads those of today's local board through today's methods ([The storage API](Rewrite-1.6.1#rs-folder)).
- The first save after a record saved today opens adds a version in the new format, since the plugin holds no hash for a board that it converted ([The storage API](Rewrite-1.6.1#records-and-versions)), while the record's versions of today stay, and open as they convert.

### Today's drafts

- The listing leaves out every record whose key starts with `blockr-draft-`, as today's `rack_records()` does, since such a record is one of today's drafts, which the new stack keeps in the browser instead ([Drafts in the browser](Rewrite-1.6.4)).
- So today's drafts are not offered again: unsaved work that a draft of today's holds is the user's to restore before the switch, while the record that it shadowed opens as it was last saved.
- A deployment may delete them with pins in R, and the migration notes say how.

### Links made today

- A URL names a record in `id`, `user` and `version`, as today, and the plugin reads `board_name` where `id` is missing, as today's stack does ([R/server.R#L1246](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1246)).
- A version names the same thing as today, a bundle's id on Connect and a pin's version on a folder board, so that a link to a version made today opens that version.
- A link with `new` names no record, so it opens what such a URL opens, the board that R sent, as today's New does in an app that passes no loader ([The controls and dialogs](Rewrite-1.6.3#new)), and a link with `recover` opens the record that it names, if any, since drafts leave the URL ([Drafts in the browser](Rewrite-1.6.4#offering-and-restoring)).
- As the page starts, the plugin replaces `board_name` in the URL with `id`, and drops `new` and `recover`, keeping the URL's other parameters ([The controls and dialogs](Rewrite-1.6.3#the-url)).

### App scripts and deployments

What changes for an app script, each change argued on the page that it links:

- The `manage_project()` plugin goes, with `manage_project_server()` and `manage_project_ui()`, since session management runs by default wherever blockr.session is installed ([Session management as a storage plugin](Rewrite-1.6#proposal)).
- The loader `rack_loader()` goes, since the plugin's `storage.load()` opens the record that a URL names ([The controls and dialogs](Rewrite-1.6.3#opening)).
- The blockr option `session_mgmt_backend` names a service by its URL, where today it holds a backend or a function that returns one ([The storage API](Rewrite-1.6.1#choosing-the-backend)).
  A script that sets it to `pins::board_folder()` sets the blockr option `session_folder` to that folder instead, one that sets it to `pins::board_local()` or to `user_pins_board()` sets nothing, and one that sets it to a board on the app's own Connect key loses that key's shared records, which a service of its own can keep ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)).
  As the app starts, blockr.session refuses a value of `session_mgmt_backend` that is no URL, with an error that names `session_folder`, so that a script that the notes missed fails at once rather than at its first save.
- The function `user_pins_board()` goes, since R opens no pins board for the browser but R's folder ([The storage API](Rewrite-1.6.1#rs-folder)).
- The function `avatar_navbar_item()` returns the navbar item that places the plugin's avatar status apart ([The controls and dialogs](Rewrite-1.6.3#the-avatar)).
- The exported constructors, generics and entry points of the rack layer go, from `new_rack_id()` to `rack_records()`, since the storage API takes their place ([The storage API](Rewrite-1.6.1#the-operations)), and so does a backend of a deployment's own that fills them, which becomes a service that speaks the API.
- The test helpers `mock_board_connect()` and `connect_fixture()` go ([Connect from the browser](Rewrite-1.6.2#tests)).
- The blockr options `session_connect_tag`, `session_autosave` and `session_draft_ttl` stay.
- On Connect, a deployment that saves for its visitors needs a Visitor API Key integration associated with the app, as today's first tier needs, and visitors with the Publisher role, while one that relied on the app's own key for viewers needs a service of its own ([Connect from the browser](Rewrite-1.6.2#what-a-visitors-role-allows)).

### The migration notes

- The migration notes of blockr.session are a vignette that lists each change above that an app script or a deployment needs, written for an AI to apply ([The conversion and the migration notes](Rewrite-1.8.3#the-migration-notes)).
- The tests that check them run the examples of today's blockr.session against the new stack, as [The conversion and the migration notes](Rewrite-1.8.3) has every package's checked, and the Connect backend's tests read today's pins from the fixtures that today's tests recorded ([Connect from the browser](Rewrite-1.6.2#tests)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's content hash is `rlang::hash()` of the R list that a save writes ([R/rack.R#L478-L480](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L478-L480)), which the new stack neither reads nor writes, since the plugin tells a changed board itself.
The first save after a record saved today opens adds a version in the new format, as [The conversion and the migration notes](Rewrite-1.8.3#who-converts) has it.

Today's drafts take the keys `blockr-draft-<state>-<epoch>-<hash>`, where the hash stands for the record or the session that a draft belongs to, so that nothing but the prefix tells a draft from a record ([R/rack.R#L368-L401](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L368-L401)).

</details>
