# Session management as a client extension
Status: draft. Part of [State in JS](Rewrite-1).

This part covers blockr.session, whose session management becomes a dock extension that makes its storage calls from the browser. It builds on [Client-drawn dock and extensions](Rewrite-1.2) and on core's command that replaces the board ([Client-owned board state](Rewrite-1.1)).

## Problem

The blockr.session package opens, saves, versions and shares boards from `manage_project()`, a replacement for core's `preserve_board()` plugin, with storage behind the rack layer, S3 generics over pins ([`rack.R#L154-L540`](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/rack.R#L154-L540)), on Connect under each visitor's own account ([`backend.R#L1-L15`](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/backend.R#L1-L15)). A Shiny board cannot be replaced in place, so opening another board or a new one is a `session$reload()` ([`server.R#L236-L246`](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/server.R#L236-L246)), and `rack_loader()`, a `board_loader()` for `serve()`, picks the board to build from the URL at the request ([`server.R#L1182-L1207`](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/server.R#L1182-L1207)). With the board held by the client ([Client-owned board state](Rewrite-1.1)), and only what must run in R running there, none of this needs R: storage is calls to an API.

## What must hold

1. Opening, saving, versioning, sharing and tagging boards work as today, from a dock extension ([Client-drawn dock and extensions](Rewrite-1.2)) and without a session reload.
2. The browser makes every storage call. R takes part once per session, to exchange the visitor's credential, which only the content's process receives.
3. A URL still names a board by `board_name`, `user` and `version`, and a new board gets a fresh id, so saving it forks a record instead of overwriting the one served.
4. Unsaved work survives a crash, as the drafts of `session_autosave` do today.
5. Records saved today open ([blockr.core#402](https://github.com/BristolMyersSquibb/blockr.core/issues/402)).

## Proposal

- Session management is a dock extension, with navbar items for new, open, save and share and a panel or dialog for the board list and versions. Opening a board or a version runs core's command that replaces the board, and the extension updates the URL in place.
- The rack layer becomes a TypeScript interface in the extension, with a backend for pins on Connect, whose API the browser reaches on the content's own origin, and one for the browser's own storage when there is no Connect.
- At the start of a session, R exchanges the visitor's session token, which Connect attaches to the requests that reach the content's process, for a visitor-scoped API key through the Visitor API Key integration, and hands the key to the browser. The key carries only the visitor's own rights, capped by the role an administrator sets ([Connect integrations](https://docs.posit.co/connect/user/oauth-integrations/)).
- The app's opening board still comes from R ([blockr.core#394](https://github.com/BristolMyersSquibb/blockr.core/issues/394)), and a URL that names a record makes the extension load that record and open it in place of the opening board from its startup module, before anything is drawn or evaluated ([Front-ends and extension points](Rewrite-1.1.8#starting-the-page)), so `rack_loader()` goes.
- The extension provides the dock's storage service, in place of the default download and upload.

## Open questions

- Whether the tier on the app's own Connect key survives: that key works for every visitor and cannot go to the browser, so its calls would stay in R.
- Whether drafts go to the backend, recoverable from any device as today, or to the browser's own storage.

## Work

- Write the storage interface, with a backend for pins on Connect and one for the browser's own storage, in blockr.session
- Exchange the visitor's session token for a visitor-scoped API key at session start, in blockr.session
- Rebuild session management as a client extension on the storage interface, in blockr.session

<details><summary>Notes for implementers</summary>

The rack generics to carry over: `rack_list()`, `rack_info()`, `rack_load()`, `rack_create()` (with `draft`), `rack_append()`, `rack_records()`, `rack_download()`, `rack_upload()`, `rack_rename()`, `rack_delete()`, `rack_purge()`, `rack_capabilities()`, `rack_tags()`, `rack_set_tags()`, `rack_acl()`, `rack_set_acl()`, `rack_share()`, `rack_unshare()`, `rack_shares()` and `rack_find_users()`.

A record is a pin written with `pins::pin_upload()` from the serialized board, with `format = "v1"` and a `content_hash` in its metadata ([`connect.R#L380-L400`](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/connect.R#L380-L400)). On Connect a renamed record changes its content title through the API, tags go through Connect's tag API, and shares through its permissions API. Pins has clients for R and Python only, and npm has none, so the Connect backend writes and reads pin bundles itself, including those of records saved today.

Drafts are rack records with `draft = TRUE`, written every `session_autosave` seconds when that option is set and kept for `session_draft_ttl` days, 7 by default ([`draft.R#L1-L30`](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/draft.R#L1-L30)). The navbar button's styling through `.blockr-navbar-icon-btn` is among the coupling listed in [Client-drawn dock and extensions](Rewrite-1.2).

</details>
