# Connect from the browser: the visitor's key, pin bundles and sharing
Status: review. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): how the plugin reaches Connect from the browser, with the key that R exchanges for the visitor's session token, what the visitor's role on Connect allows, the calls to Connect's API behind each operation of the storage API, the pins that hold records, those that today's blockr.session saved included, the bundle that a save deploys, the Connect tag, sharing and the search of users, the recorded responses of Connect's API that its tests run against, and the spike that tries all of it on a Connect server first.
It shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that pass a plugin's request function the headers of the HTTP request that opened the session, run the spike, write the Connect backend and exchange the visitor's session token for a key.
The operations are [The storage API](Rewrite-1.6.1)'s, and the dialog in which a user shares a record is [The controls and dialogs](Rewrite-1.6.3#the-dialogs)'s.

## What must hold

1. On Connect, a visitor who is signed in lists, opens, saves, versions, shares and deletes their records with no storage call through R ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 2).
2. R takes part only to exchange the visitor's session token for a key, once for each R process that serves the page, and the browser keeps the key in the page's memory alone.
3. A visitor reaches only what their own key reaches, so that no visitor lists or opens the records of another, but those shared with them, as on the visitor's key today.
4. A record that the plugin saves on Connect is a pin that pins reads in R, as the records saved today are, and those records list and open ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 6).

## Today

Where the visitor carries a session token, `user_pins_board()` exchanges it for a key through `connectapi::connect(token = )` and opens a pins board on that key, else a board on the app's own key, else a local board ([R/backend.R#L40-L99](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/backend.R#L40-L99)).
The listing is one request, a search for the Connect tag where `session_connect_tag` names one and the content that the key sees otherwise, each with its owner, keeping the content items that are pins ([R/connect.R#L85-L149](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L85-L149)).
To save, pins finds or creates the content item, builds a bundle of the file, its `data.txt`, an `index.html` and a `manifest.json`, uploads it as a gzipped tar archive, deploys it and polls the task, and it reads a version from the path `_rev<bundle>/` of the content's URL ([R/board_connect.R#L215-L360](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/board_connect.R#L215-L360), [R/board_connect_bundle.R#L1-L52](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/board_connect_bundle.R#L1-L52)).
Sharing sets the content's access type and its permissions, and the search of users is Connect's ([R/connect.R#L433-L516](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L433-L516)).

## Proposal

### The visitor's key

- R's function for the request `session_backend` posts the visitor's session token to Connect's `/__api__/v1/oauth/integrations/credentials`, as a token exchange of [RFC 8693](https://datatracker.ietf.org/doc/html/rfc8693) that requests `urn:posit:connect:api-key`, authenticated with the content's own `CONNECT_API_KEY`, as connectapi's `get_oauth_credentials()` does ([R/get.R#L803-L828](https://github.com/posit-dev/connectapi/blob/7c4683625ef05b0f233a525195f1893608ed9636/R/get.R#L803-L828)).
  It replies `{ backend: "connect", server, key }` ([The storage API](Rewrite-1.6.1#the-once-per-page-request)), where `server` is Connect's address as the browser reaches it, which R takes from the `content_url` that Connect's API gives for the app itself, since `CONNECT_SERVER` may be an address that only R reaches (notes).
- R's function reads the token from the headers of the HTTP request that opened the session, which core passes it in the reserved argument `headers`, as the transport gives them, so that reading the token needs nothing of Shiny's session ([Plugins](Rewrite-1.1.12#a-plugins-requests)).
- The exchange needs a Visitor API Key integration, which an administrator sets up and the app's owner associates with the app ([Obtaining a visitor API key](https://docs.posit.co/connect/user/oauth-integrations/#obtaining-a-visitor-api-key)), on Connect 2025.01.0 or later, which connectapi requires for the exchange ([R/connect.R#L1034](https://github.com/posit-dev/connectapi/blob/7c4683625ef05b0f233a525195f1893608ed9636/R/connect.R#L1034)).
  Where the app is open to anyone without a login, Connect's viewer integrations give no key, and the plugin has no backend ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
- The key carries only the visitor's own rights, at the lesser of the visitor's role and the role that the integration caps it at ([Connect API integrations](https://docs.posit.co/connect/admin/integrations/oauth-integrations/connect/)).
- The browser keeps the key in the page's memory alone, as the assistant keeps a visitor's own key ([Model access](Rewrite-1.4.1#how-a-call-is-authenticated)).
- The key lives as long as the R process that asked for it, since Connect deletes it as that process exits (notes).
  So once Connect refuses the key with 401, as after R's process restarts, the Connect backend asks R again through `session_backend` and repeats the refused call once with the new key.
- The app's own Connect key, which today's `user_pins_board()` takes where the visitor has no key, goes, since it works for every visitor and so cannot go to the browser, and since every visitor saves under the publisher's account on it (notes).
  The Roadmap places calls on such a key with a server of our own ([Roadmap](Roadmap#a-server-of-our-own)).

### What a visitor's role allows

- Connect lets a publisher create, deploy and delete content and list users, and a viewer none of these ([Role permissions](https://docs.posit.co/connect/admin/user-management/role-permissions/)).
- So the Connect backend reads the visitor's role with `user`, and on a key with the Viewer role its capabilities give `saving`, `sharing`, `visibility` and `user_discovery` as false ([The storage API](Rewrite-1.6.1#the-operations)).
  The controls then list and open the records that others share with the visitor, and save a download in place of a record ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).

### Records as pins

- A record is a pin, a content item whose `content_category` is `pin`, as today, named by the record's key, which Connect keeps unique among its owner's content, so that a record's owner and key find its content item through `GET /v1/content?name=<key>&include=owner` ([Connect's API](https://docs.posit.co/connect/api/)).
- The Connect backend calls Connect's API on the server that serves the app, with the header `Authorization: Key <key>` and without the browser's cookies, so that the key alone authenticates each call.
- Each operation of the storage API becomes these calls, under `/__api__`:

| Operation | Calls to Connect's API |
|---|---|
| `capabilities` | None beyond those of `user`, whose role sets the flags (above) |
| `user` | `GET /v1/user`, whose `username` is the owner and whose first and last names, or else its `username`, are the name |
| `list_records` | `GET /v1/content?include=owner`, or `GET /v1/search/content?q=tag:"<tag>"&include=owner` where the Connect tag is set, keeping the pins, each with its owner's `username` and its `last_deployed_time` as the time it was saved |
| `record_versions` | `GET /v1/content/{guid}/bundles`, each bundle's `id` being a version and its `created_time` the time it was saved |
| `read_version` | The version's `data.txt` and then the file that it names, from the path `_rev<version>/` of the content's URL, the version being the content item's `bundle_id` where the args name none |
| `create_record` | `POST /v1/content` with the key as its `name` and `title` and the access type `acl`, then the calls of `add_version`, where a name that the owner holds fails with `key_taken`, and one outside `[-_A-Za-z0-9]` with `invalid_key` |
| `add_version` | `POST /v1/content/{guid}/bundles` with the bundle (below), `POST /v1/content/{guid}/deploy` with its `id`, then `GET /v1/tasks/{id}` until the task has finished, as pins does |
| `delete_version` | `DELETE /v1/content/{guid}/bundles/{version}` |
| `delete_record` | `DELETE /v1/content/{guid}` |
| `access` | The content item's `access_type`, and `GET /v1/content/{guid}/permissions`, with the name of each user from `GET /v1/users/{guid}` |
| `set_access` | `PATCH /v1/content/{guid}` with the `access_type` |
| `share` | `POST /v1/content/{guid}/permissions` with the user's `principal_guid`, `principal_type: "user"` and `role: "viewer"`, as today |
| `unshare` | The user's permission from `GET /v1/content/{guid}/permissions`, then `DELETE /v1/content/{guid}/permissions/{id}` |
| `find_users` | `GET /v1/users?prefix=<query>` |

- Without the Connect tag, the listing holds every pin that the visitor sees, as today's does, and a pin that holds no record shows only as it fails to open, since only its `data.txt` tells, which the listing does not read.
- A pin without the pin tag `blockr-session` in its `data.txt` holds no record, so `read_version` fails with `not_found`, as today's refuses to open it (notes).
- The Connect tag, the blockr option `session_connect_tag`, filters the listing on Connect's side, and `create_record` applies it with `POST /v1/content/{guid}/tags`, resolving its id from `GET /v1/tags`, as today, while the backend reads that blockr option with `core.blockrOption()`.
- Today's renaming of a record through a content's title goes, since no control uses it once the plugin sets no board's name ([The storage API](Rewrite-1.6.1#records-and-versions)).

### The bundle

- The bundle of a version holds four files, as pins writes them: the JSON board as `<key>.json`, `data.txt` with the pin's metadata, an `index.html` that links the board's file, and a `manifest.json` that names the content a static pin, with `index.html` as its page ([R/board_connect_bundle.R#L34-L52](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/board_connect_bundle.R#L34-L52)).
- Its `data.txt` holds `file`, `file_size`, `type: "file"`, `title`, `tags: ["blockr-session"]`, `created`, in pins' form `20261127T090000Z`, and `api_version: 1`, written as JSON, which is YAML too, so that pins in R reads it (notes).
- The backend writes the files as a tar archive of its own making, which a bundle of four files needs no library for, and gzips it with the browser's `CompressionStream`, which Chrome has since version 80, Firefox since 113 and Safari since 16.4 ([CompressionStream](https://developer.mozilla.org/en-US/docs/Web/API/CompressionStream)).
- It reads the `data.txt` of a version with a YAML parser, since pins in R writes it as YAML, and since a record saved today names its file at random, so that only `data.txt` tells which file holds the board (notes).

### Sharing

- The access type, the shares and the search of users go through Connect's API from the browser, on the visitor's key, since Connect gives them only on the visitor's own key (notes).
- Sharing makes a user a viewer of the record, as today, and the dialog's Private is the access type `acl` with no shares ([The storage API](Rewrite-1.6.1#the-operations)).

### Tests

- The responses of Connect's API that today's tests recorded carry over as fixtures of the Connect backend's tests, while the R helpers `mock_board_connect()` and `connect_fixture()` go ([R/tests.R](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/tests.R), [tests/testthat/_fixtures/connect](https://github.com/BristolMyersSquibb/blockr.session/tree/66d950549a905066a2860c1d39da1cf6cf320bc8/tests/testthat/_fixtures/connect)).

### The spike

- Before the Connect backend is written, a spike on a Connect server with a Visitor API Key integration tries what no one has run yet: from a page that Connect serves, on a visitor's key, it creates a pin, deploys a bundle that the browser built, reads it back, reads a record that today's blockr.session saved, and reads the new pin in R with `pins::pin_download()`.
- It passes where each of these works in Chrome, Firefox and Safari, and the backend is then written as above.
- Should Connect refuse a bundle that the browser built, R writes the pin through a request, as today's pins does, which puts R in every save on Connect, against condition 2 of [Session management as a storage plugin](Rewrite-1.6#what-must-hold), so that the page goes back to the user before that.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's records are pins written with `pins::pin_upload()` from the serialized board, with `format = "v1"` and a `content_hash` in their metadata, and with the pin tag `blockr-session` ([R/connect.R#L369-L412](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L369-L412)).
A pin without that tag refuses to open as a record ([R/pins.R#L324-L360](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/pins.R#L324-L360)).
On Connect, the Connect tag goes through Connect's tag API, and shares through its permissions API.
Connect gives sharing, visibility and the search of users only to a backend on the visitor's own key ([R/connect.R#L414-L431](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L414-L431)).
On the app's own key, today's second tier, every visitor saves under the publisher's account, so that each visitor lists, opens and overwrites the records of all the others ([R/backend.R#L60-L70](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/backend.R#L60-L70)).
Pins has clients for R and Python only, and npm has none, so the Connect backend writes and reads pin bundles itself, including those of records saved today.
Today's `connect_content_find()` takes the first content item of a name, whoever owns it ([R/connect.R#L586-L598](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L586-L598)), while the backend picks the item of the record's owner from the listing's `owner`.

Connect gives running content `CONNECT_SERVER` from its setting `Server.EnvAddress`, which an administrator may point at an internal address, so that it can differ from the address in the browser, and it gives the content's own GUID in `CONNECT_CONTENT_GUID` ([Content settings](https://docs.posit.co/connect/user/content-settings/)).
The `content_url` of `GET /v1/content/{guid}` for that GUID is computed from the GUID on the server's own address, so the part before `content/<guid>` is the address that the browser reaches.
Connect binds a visitor's key to the content process that requested it and deletes it as the process exits, so a key stops working across a restart, and a client takes a fresh key from the latest session token rather than caching one ([Connect API integrations](https://docs.posit.co/connect/admin/integrations/oauth-integrations/connect/)).
Viewer integrations support neither content open to anyone without a login nor share links ([OAuth integrations](https://docs.posit.co/connect/user/oauth-integrations/)).
The page could reach Connect's API with the visitor's own session cookie, as Connect's dashboard does, but Connect documents no such way for content, and the cookie gives the page every right of the visitor's session rather than those of a key that the integration caps.

In a check with pins 1.4.2 on a folder board, `pin_meta()` and `pin_download()` read a version whose `data.txt` was JSON and held no `pin_hash`, while the `data.txt` that `pin_upload()` wrote was YAML, naming a file such as `file745265fc9d34b.json`, the name of the temporary file that today's save uploads ([R/rack.R#L466-L474](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L466-L474)).

On `js-state`, at `f139384`, R calls a plugin's request function with its args, `reads` and `file` alone, so the function has no way to the headers of the request that opened the session, which carry the visitor's session token, but through Shiny's session.
The second item of the [Work list](Rewrite-1.6#work) changes this, in blockr.core.

</details>
