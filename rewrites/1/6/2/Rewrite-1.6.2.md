# Connect from the browser: the visitor's key, pin bundles and sharing
Status: draft. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): how the plugin reaches Connect from the browser, with the key that R exchanges once per page for the visitor's session token, the calls to Connect's API behind each operation of the storage API, the pins that hold records, those that today's blockr.session saved included, the Connect tag, sharing and the search of users, and the recorded responses of Connect's API that its tests run against.
It shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that pass a plugin's request function the headers of the HTTP request that opened the session, write the Connect backend and exchange the visitor's session token for a key.
The operations are [The storage API](Rewrite-1.6.1)'s, and the dialog in which a user shares a record is [The controls and dialogs](Rewrite-1.6.3#the-dialogs)'s.

## What must hold

1. On Connect, a visitor who is signed in lists, opens, saves, versions, shares and deletes their records with no storage call through R ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 2).
2. R takes part once per page, to exchange the visitor's session token for a key, which the browser keeps in the page's memory alone.
3. A visitor reaches only what their own key reaches, so that no visitor lists or opens the records of another, but those shared with them, as on the visitor's key today.
4. The records that today's blockr.session saved on Connect list and open ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 6).

## Proposal

### The visitor's key

- Once per page, R exchanges the visitor's session token, which Connect attaches to the requests that reach the content's process, for a visitor-scoped API key through the Visitor API Key integration, and hands the key to the browser in the reply to the plugin's once-per-page request ([The storage API](Rewrite-1.6.1#the-once-per-page-request)).
  The key carries only the visitor's own rights, capped by the role an administrator sets ([Connect integrations](https://docs.posit.co/connect/user/oauth-integrations/)).
- R's function for that request reads the token from the headers of the HTTP request that opened the session, which core passes it in the reserved argument `headers`, as the transport gives them, so that reading the token needs nothing of Shiny's session ([Plugins](Rewrite-1.1.12#a-plugins-requests)).
- The browser keeps the key in the page's memory alone, as the assistant keeps a visitor's own key ([Model access](Rewrite-1.4.1#how-a-call-is-authenticated)).
- The app's own Connect key, which today's `user_pins_board()` takes where the visitor has no key, goes, since it works for every visitor and so cannot go to the browser, and since every visitor saves under the publisher's account on it (notes).
  The Roadmap places calls on such a key with a server of our own ([Roadmap](Roadmap#a-server-of-our-own)).

### Records as pins

- The Connect backend calls Connect's API directly, on the server that serves the app, with the visitor's key.
- A record is a pin, as today, and the backend writes and reads its bundles itself, those of records saved today included, since pins has no client for JS (notes).
- The Connect tag, the blockr option `session_connect_tag`, filters the listing on Connect's side, and each save applies it, as today, while the backend reads that blockr option with `core.blockrOption()`.
- Today's renaming of a record through a content's title goes, since no control uses it once the plugin sets no board's name ([The storage API](Rewrite-1.6.1#records-and-versions)).

### Sharing

- The access type, the shares and the search of users go through Connect's API from the browser, on the visitor's key, since Connect gives them only on the visitor's own key (notes).

### Tests

- The responses of Connect's API that today's tests recorded carry over as fixtures of the Connect backend's tests, while the R helpers `mock_board_connect()` and `connect_fixture()` go ([R/tests.R](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/tests.R), [tests/testthat/_fixtures/connect](https://github.com/BristolMyersSquibb/blockr.session/tree/66d950549a905066a2860c1d39da1cf6cf320bc8/tests/testthat/_fixtures/connect)).

## Open questions

- Which calls to Connect's API fill each operation, and how a save deploys a pin's bundle from the browser: it blocks the Connect backend's Work item, and a spike would settle it that saves a record from the browser on a visitor's key and reads one that today's blockr.session saved.
- How long the visitor's key lasts, and what the plugin does once Connect refuses it: settled by Connect's documentation of the Visitor API Key integration, and by the spike.

<details><summary>Notes for implementers</summary>

Today's records are pins written with `pins::pin_upload()` from the serialized board, with `format = "v1"` and a `content_hash` in their metadata, and with the pin tag `blockr-session` ([R/connect.R#L369-L412](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L369-L412)).
A pin without that tag refuses to open as a record ([R/pins.R#L324-L360](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/pins.R#L324-L360)).
On Connect, the Connect tag goes through Connect's tag API, and shares through its permissions API.
Connect gives sharing, visibility and the search of users only to a backend on the visitor's own key ([R/connect.R#L414-L431](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L414-L431)).
On the app's own key, today's second tier, every visitor saves under the publisher's account, so that each visitor lists, opens and overwrites the records of all the others ([R/backend.R#L60-L70](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/backend.R#L60-L70)).
Pins has clients for R and Python only, and npm has none, so the Connect backend writes and reads pin bundles itself, including those of records saved today.

On `js-state`, at `f139384`, R calls a plugin's request function with its args, `reads` and `file` alone, so the function has no way to the headers of the request that opened the session, which carry the visitor's session token, but through Shiny's session.
The second item of the [Work list](Rewrite-1.6#work) changes this, in blockr.core.

</details>
