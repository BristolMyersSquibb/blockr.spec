# Connect from the browser: the visitor's key, pin bundles and sharing
Status: review. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): how the plugin reaches Connect from the browser, with the key that R exchanges for the visitor's session token, what the visitor's role on Connect allows, the calls to Connect's API behind each operation of the storage API, the pins that hold records, those that today's blockr.session saved included, the bundle that a save deploys, the Connect tag, sharing and the search of users, the recorded responses of Connect's API that its tests run against, and the spike that tries all of it on a Connect server first.
It shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that pass a plugin's request function the headers of the HTTP request that opened the session, run the spike, write the Connect backend and exchange the visitor's session token for a key.
The operations are [The storage API](Rewrite-1.6.1)'s, and the dialog in which a user shares a record is [The controls and dialogs](Rewrite-1.6.3#the-dialogs)'s.

## What must hold

1. On Connect, a visitor who is signed in lists, opens, saves, versions, shares and deletes their records with no storage call through R ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 2).
2. R takes part only to exchange the visitor's session token for a key, once for each R process that serves the page, and the browser keeps the key in the page's memory alone.
3. A visitor reaches only what their own key reaches, and lists only the records that the key may open, so that no visitor lists or opens the records of another but those shared with them, whatever role their key holds.
4. A record that the plugin saves on Connect is a pin that pins reads in R, as the records saved today are, which list, and open once blockr.convert's `convert_file()` has converted them ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today), [Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 6).
5. The capabilities follow what the visitor's key may do, as Connect reports it for that key, so that the controls offer no Save of a record on a key that may not create content, such as a viewer's, while they list and open the records shared with its visitor.

## Today

Where the visitor carries a session token, `user_pins_board()` exchanges it for a key through `connectapi::connect(token = )` and opens a pins board on that key, else a board on the app's own key, else a local board ([R/backend.R#L40-L99](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/backend.R#L40-L99)).
The listing searches for the Connect tag where `session_connect_tag` names one, 500 content items to a request, and otherwise takes the content that the key sees in one request, each item with its owner, keeping the items that are pins ([R/connect.R#L85-L149](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L85-L149), [#L550-L584](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L550-L584)).
Each save applies the Connect tag, which `session_connect_tag` names by a tag's name or by its path, as `Category/Name` ([R/connect.R#L236-L345](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L236-L345)).
To save, pins finds or creates the content item, and builds a bundle of the file, its `data.txt`, a preview page, `index.html`, with the scripts and styles that the page loads, and a `manifest.json` ([R/board_connect.R#L262-L313](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/board_connect.R#L262-L313), [R/board_connect_bundle.R#L1-L71](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/board_connect_bundle.R#L1-L71)).
It uploads the bundle as a gzipped tar archive, deploys it and polls the deploy's task ([R/board_connect.R#L315-L342](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/board_connect.R#L315-L342)).
It reads a version from the path `_rev<bundle>/` of the content's URL ([R/board_connect.R#L214-L259](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/board_connect.R#L214-L259)).
Sharing sets the content's access type and its permissions, and the search of users is Connect's ([R/connect.R#L433-L516](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L433-L516)).
Today's blockr.session offers all three only on the visitor's key, whatever role the key holds, and offers saving to every visitor ([R/connect.R#L411-L428](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L411-L428)).
Its shares are every user and group on the content item's permissions, collaborators included, and a group shows by its GUID, since each share is named through Connect's users ([R/connect.R#L486-L507](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L486-L507)).
Its README has the integration cap keys at Viewer, which it calls enough for reading and writing pins ([README.Rmd#L71-L79](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/README.Rmd#L71-L79)).

## Proposal

### The visitor's key

On Connect, where the blockr option `session_mgmt_backend` is unset, R's function for the request `session_backend` takes these steps, each call on the content's own key, `CONNECT_API_KEY`:

1. It lists the integrations that are associated with the app, through `GET /v1/content/{guid}/oauth/integrations/associations`.
   It replies `{ backend: "none", missing: "integration" }` where none of them has the template `connect`, the Visitor API Key integration, which gives keys to Connect's own API.
2. It replies `{ backend: "none", missing: "sign_in" }` where the headers name no user in `Shiny-Server-Credentials`, which Connect sets for a visitor who is signed in.
3. It posts the visitor's session token to Connect's `/__api__/v1/oauth/integrations/credentials`, as a token exchange of [RFC 8693](https://datatracker.ietf.org/doc/html/rfc8693) that requests `urn:posit:connect:api-key`, as connectapi's `get_oauth_credentials()` does ([R/get.R#L803-L828](https://github.com/posit-dev/connectapi/blob/7c4683625ef05b0f233a525195f1893608ed9636/R/get.R#L803-L828)).
   Where the app has more than one integration, as an app that also reaches a database through one has, it names the Visitor API Key integration in `audience`, which Connect then needs ([OAuth integrations](https://docs.posit.co/connect/user/oauth-integrations/)).
4. It replies `{ backend: "connect", server, key }`, where `server` is Connect's address as the browser reaches it, which R takes from the `content_url` that Connect's API gives for the app itself, since `CONNECT_SERVER` may be an address that only R reaches (notes).

The replies are those of [The storage API](Rewrite-1.6.1#the-once-per-page-request), and where the plugin gets no backend, its status says which of the two is missing ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).

- R's function reads the token and the user from the headers of the HTTP request that opened the session, which core passes it in the reserved argument `headers`, as the transport gives them, so that reading them needs nothing of Shiny's session ([Plugins](Rewrite-1.1.12#a-plugins-requests)).
- Connect has added a Visitor API Key integration by default since 2025.05.0, and the app's owner associates it with the app ([Obtaining a visitor API key](https://docs.posit.co/connect/user/oauth-integrations/#obtaining-a-visitor-api-key), [Posit Connect 2025.05.0](https://docs.posit.co/connect/news/#posit-connect-2025.05.0)).
  The exchange needs Connect 2025.01.0 or later, and `audience` needs 2025.07.0, as connectapi checks ([R/connect.R#L1034](https://github.com/posit-dev/connectapi/blob/7c4683625ef05b0f233a525195f1893608ed9636/R/connect.R#L1034), [R/get.R#L811-L813](https://github.com/posit-dev/connectapi/blob/7c4683625ef05b0f233a525195f1893608ed9636/R/get.R#L811-L813)).
  So R leaves `audience` out where the app has that integration alone.
- Connect associates no Visitor API Key integration with an app that is open to anyone without a login, so its visitors get no key, and the plugin has no backend there (notes).
- The key carries only the visitor's own rights, at the lesser of the visitor's role and the role that the integration caps it at ([Connect API integrations](https://docs.posit.co/connect/admin/integrations/oauth-integrations/connect/)).
- The browser keeps the key in the page's memory alone, as the assistant keeps a visitor's own key ([Model access](Rewrite-1.4.1#how-a-call-is-authenticated)).
- The key lives as long as the R process that asked for it, since Connect deletes it as that process exits (notes).
  So once Connect refuses the key with 401, as after R's process restarts, the Connect backend asks R again through `session_backend` and repeats the refused call once with the new key.
- The app's own Connect key, which today's `user_pins_board()` takes where the visitor has no key, goes, since it works for every visitor and so cannot go to the browser, and since every visitor saves under the publisher's account on it (notes).
  The Roadmap places calls on such a key with a server of our own ([Roadmap](Roadmap#a-server-of-our-own)).

### What a visitor's role allows

- By default, Connect lets a publisher create, deploy and delete content and list users, and a viewer none of these, while since Connect 2026.09.0 an administrator may change which permissions each of the two roles holds ([Role permissions](https://docs.posit.co/connect/admin/user-management/role-permissions/), [Posit Connect 2026.09.0](https://docs.posit.co/connect/news/#posit-connect-2026.09.0)).
- A key may hold a lower role than its visitor, where the app's integration caps keys below the visitor's role (above).
  So the Connect backend learns what the key may do from Connect, on the key itself ([Connect's API](https://docs.posit.co/connect/api/)).
  The call `GET /v1/roles` gives the key's own role alone, unless the key holds the permission `roles:read`, as only an administrator's key does, and then gives every role.
  The call `GET /v1/roles/{name}/permissions` gives what the key's role may do, while the Administrator role holds every permission.
- The capabilities follow those permissions ([The storage API](Rewrite-1.6.1#the-operations)): `saving` where the role holds `content:publish`, `content:update`, `bundles:upload` and `bundles:deploy`, `sharing` and `visibility` where it holds `content:update`, through which the owner or a collaborator of a content item changes who may open it, and `user_discovery` where it holds `users:read`.
- Where Connect answers `GET /v1/roles` with 404, as a server without its roles API does, the backend takes the key's role from the `user_role` of `GET /v1/user`, and Connect's default permissions for that role (notes).
  The spike checks which role that call gives on a key that the integration caps below its visitor's role (below), since where it gives the visitor's own, the capabilities offer what the key may not do, and those calls fail with `forbidden`.
- On a key with the Viewer role and Connect's default permissions, the capabilities give `saving`, `sharing`, `visibility` and `user_discovery` as false.
  The controls then list and open the records that others share with the visitor, and save a download in place of a record ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
- So the plugin works under any cap of the integration, while a cap at Publisher gives it all that it does and keeps an administrator's rights out of the page, which holds the key in its memory.
  Under a cap at Viewer, which today's README sets, no key may create content by Connect's default permissions, so the plugin saves no record for anyone, which the spike checks (below).
  Under a cap at Administrator, an administrator's key sees every content item on the server, of which `list_records` keeps those that the key may open (below).

### Records as pins

- A record is a pin, a content item whose `content_category` is `pin`, as today, named by the record's key, which Connect keeps unique among its owner's content, so that a record's owner and key find its content item through `GET /v1/content?name=<key>&include=owner` ([Connect's API](https://docs.posit.co/connect/api/)).
- The Connect backend calls Connect's API on the server that serves the app, with the header `Authorization: Key <key>` and without the browser's cookies, so that the key alone authenticates each call.
- Each operation of the storage API becomes these calls, under `/__api__`:

| Operation | Calls to Connect's API |
|---|---|
| `capabilities` | `GET /v1/roles` and `GET /v1/roles/{name}/permissions` for the key's role, or `GET /v1/user` where Connect has no roles API, which set the flags (above) |
| `user` | `GET /v1/user`, whose `username` is the owner and whose first and last names, or else its `username`, are the name |
| `list_records` | `GET /v1/content?include=owner`, or `GET /v1/search/content?q=tag:"<tag>"&include=owner` page by page where the Connect tag is set, keeping the pins whose `app_role` is not `none`, which Connect gives an item that the key sees but may not open, as an administrator's key sees every item, each with its owner's `username`, its `last_deployed_time` as the time it was saved, and `writable` where its `app_role` is `owner` or `editor` |
| `record_versions` | `GET /v1/content/{guid}/bundles` page by page, each bundle's `id` being a version and its `created_time` the time it was saved |
| `read_version` | The version's `data.txt` and then the file that it names, from the path `_rev<version>/` of the content's URL, the version being the content item's `bundle_id` where the args name none, and the `created` of the `data.txt` being the time it was saved |
| `create_record` | `POST /v1/content` with the key as its `name` and `title` and the access type `acl`, then the calls of `add_version`, and `DELETE /v1/content/{guid}` where those fail, so that the key is free again |
| `add_version` | `POST /v1/content/{guid}/bundles` with the bundle (below), `POST /v1/content/{guid}/deploy` with its `id` as the `bundle_id`, then `GET /v1/content/{guid}/bundles/{id}` until the bundle is `active` or its `deploy_failed_time` is set, and `DELETE /v1/content/{guid}/bundles/{id}` where the deploy failed |
| `delete_version` | `DELETE /v1/content/{guid}/bundles/{version}`, for a version other than the content item's `bundle_id`, which Connect refuses to delete while it serves it ([The storage API](Rewrite-1.6.1#the-operations)) |
| `delete_record` | `DELETE /v1/content/{guid}` |
| `access` | The content item's `access_type`, and every user and group of `GET /v1/content/{guid}/permissions`, collaborators included, each user named from `GET /v1/users/{guid}` and each group from `GET /v1/groups/{guid}` (below) |
| `set_access` | `PATCH /v1/content/{guid}` with the `access_type` |
| `share` | `POST /v1/content/{guid}/permissions` with the user's `principal_guid`, `principal_type: "user"` and `role: "viewer"`, as today |
| `unshare` | The permission of the user or group from `GET /v1/content/{guid}/permissions`, then `DELETE /v1/content/{guid}/permissions/{id}` |
| `find_users` | `GET /v1/users?prefix=<query>`, each user's `guid` being the principal, its first and last names, or else its `username`, the name, beside its `email`, where Connect gives one, and its `username` |

- The backend refuses a key outside the key's rule, 3 to 64 letters, digits, hyphens and underscores, with `invalid_key` before it calls Connect, since Connect takes periods too ([The controls and dialogs](Rewrite-1.6.3#the-key)).
- Connect's failures map to those of the storage API: a 404 to `not_found`, a 403 to `forbidden`, and a 409 with Connect's code 26, a name that the owner holds already, to `key_taken` ([Connect's API](https://docs.posit.co/connect/api/), [The storage API](Rewrite-1.6.1#failures)).
  A 401 asks R for a new key (above), and a second one rejects with `unauthorized`.
  Any other failure rejects with `failed`, with the `error` of Connect's reply as its message.
- The backend polls the bundle, where pins polls the deploy's task.
  On a cluster of Connect servers, only the node that runs a task answers for it, and the load balancer finds that node by the cookies of the deploy's reply, which the backend does not send (notes).
- Without the Connect tag, the listing holds every pin that the visitor sees, as today's does, and a pin that holds no record shows only as it fails to open, since only its `data.txt` tells, which the listing does not read.
- A pin without the pin tag `blockr-session` in its `data.txt` holds no record, so `read_version` fails with `not_found`, as today's refuses to open it (notes).
- The Connect tag, the blockr option `session_connect_tag`, filters the listing on Connect's side, and `create_record` applies it to the record's content item with `POST /v1/content/{guid}/tags`, resolving its id from `GET /v1/tags` (notes).
  The content item keeps the tag through every later version, so no other save applies it, where today's applies it at each save.
  The backend reads that blockr option with `core.blockrOption()`.
- Today's renaming of a record through a content's title goes, since no control uses it once the plugin sets no board's name ([The storage API](Rewrite-1.6.1#records-and-versions)).

### The bundle

- The bundle of a version holds four files: the JSON board as `<key>.json`, `data.txt` with the pin's metadata, an `index.html` that links the board's file, and a `manifest.json` that names the content a static pin, with `index.html` as its page ([R/board_connect_bundle.R#L34-L52](https://github.com/rstudio/pins-r/blob/335be1f83d889d3bd1ad9d149f3a06a1059ff4c9/R/board_connect_bundle.R#L34-L52)).
  Pins writes these four as well, and beside them the scripts and styles of its preview page, which the backend leaves out, since its `index.html` only links the board's file.
- Its `data.txt` holds `file`, `file_size`, `type: "file"`, `title`, `tags: ["blockr-session"]`, `created`, in pins' form `20261127T090000Z`, and `api_version: 1`, written as JSON, which is YAML too, so that pins in R reads it (notes).
- The backend writes the files as a tar archive of its own making, which a bundle of four files needs no library for, and gzips it with the browser's `CompressionStream`, which Chrome has since version 80, Firefox since 113 and Safari since 16.4 ([CompressionStream](https://developer.mozilla.org/en-US/docs/Web/API/CompressionStream)).
- It reads the `data.txt` of a version with a YAML parser, since pins in R writes it as YAML, for today's saves and for the version that a deployment writes back for each record that it converts with blockr.convert's `convert_file()`, and since a record saved today names its file at random, so that only `data.txt` tells which file holds the board (notes).

### Sharing

- Sharing makes a user a viewer of the record, as today, and the dialog's Private is the access type `acl` with no shares ([The storage API](Rewrite-1.6.1#the-operations)).
- The shares that `access` gives are every user and group on the content item's permissions, collaborators included, as today's are, since a share made in Connect's own settings may name a group or a collaborator, and the dialog would otherwise show Private for a record that others open (Today).
  The backend names a group from `GET /v1/groups/{guid}`, where today's shows its GUID.

### Tests

- The Connect backend's tests replay responses of Connect's API, each a call's request with its response, which a run of the tests against a Connect server records, as today's tests record theirs where `connect_test_recording` is set ([R/tests.R#L73-L132](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/tests.R#L73-L132)).
- Among them are the `data.txt` and the board of a record that today's blockr.session saved on Connect, which the spike records (below), so that the tests read today's pins as Connect serves them.
- Today's fixtures go, with the R helpers `mock_board_connect()` and `connect_fixture()`, since each holds what a call in R returned, as an R value that `jsonlite::serializeJSON()` wrote, rather than a response as Connect sent it ([tests/testthat/_fixtures/connect](https://github.com/BristolMyersSquibb/blockr.session/tree/66d950549a905066a2860c1d39da1cf6cf320bc8/tests/testthat/_fixtures/connect)).
  The board that they download is a stand-in, not one that blockr.session saved ([tests/testthat/helper-connect.R#L25-L32](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/tests/testthat/helper-connect.R#L25-L32)).

### The spike

- Before the Connect backend is written, a spike on a Connect server with a Visitor API Key integration tries what no one has run yet: from a page that Connect serves, on a visitor's key, it creates a pin, deploys a bundle that the browser built, reads it back, reads a record that today's blockr.session saved, and reads the new pin in R with `pins::pin_download()`.
- It records the responses of these calls as the first fixtures of the backend's tests (above).
- It checks which role `GET /v1/roles` and `GET /v1/user` give for a visitor with the Publisher role on a key that the integration caps at Viewer, and whether that key may create content, as today's README expects (Today), and which cap the integration that Connect adds by default has.
- It passes where each of these works in Chrome, Firefox and Safari, and the backend is then written as above.
- Should Connect refuse a bundle that the browser built, R writes the pin through a request, as today's pins does, which puts R in every save on Connect, against condition 2 of [Session management as a storage plugin](Rewrite-1.6#what-must-hold), so that the page goes back to the user before that.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's records are pins written with `pins::pin_upload()` from the serialized board, with `format = "v1"` and a `content_hash` in their metadata, and with the pin tag `blockr-session` ([R/connect.R#L369-L412](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L369-L412)).
A pin without that tag refuses to open as a record ([R/pins.R#L324-L360](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/pins.R#L324-L360)).
On Connect, the Connect tag goes through Connect's tag API, and shares through its permissions API.
On the app's own key, today's second tier, every visitor saves under the publisher's account, so that each visitor lists, opens and overwrites the records of all the others ([R/backend.R#L60-L70](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/backend.R#L60-L70)).
Pins has clients for R and Python only, and npm has none, so the Connect backend writes and reads pin bundles itself, including those of records saved today.
Today's `connect_content_find()` takes the first content item of a name, whoever owns it ([R/connect.R#L586-L598](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L586-L598)), while the backend picks the item of the record's owner from the listing's `owner`.
As today, the blockr option `session_connect_tag` takes a tag's name or its path, `Category/Name`, and a tag at the top of Connect's tree of tags, a category, filters the listing but cannot be applied, since Connect applies only the tags beneath one ([R/backend.R#L17-L21](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/backend.R#L17-L21)).

Connect gives running content `CONNECT_SERVER` from its setting `Server.EnvAddress`, which an administrator may point at an internal address, so that it can differ from the address in the browser, and it gives the content's own GUID in `CONNECT_CONTENT_GUID` ([Content settings](https://docs.posit.co/connect/user/content-settings/)).
The `content_url` of `GET /v1/content/{guid}` for that GUID is computed from the GUID on the server's own address, so the part before `content/<guid>` is the address that the browser reaches.
Connect binds a visitor's key to the content process that requested it and deletes it as the process exits, so a key stops working across a restart, and a client takes a fresh key from the latest session token rather than caching one ([Connect API integrations](https://docs.posit.co/connect/admin/integrations/oauth-integrations/connect/)).
Viewer integrations support neither content open to anyone without a login nor share links ([OAuth integrations](https://docs.posit.co/connect/user/oauth-integrations/)), and Connect refuses to associate a Visitor API Key integration with content that is open to anyone, with its error code 237 ([Connect's API](https://docs.posit.co/connect/api/)).
Connect's default permissions give the Publisher and Administrator roles every permission that the capabilities read, and the Viewer role none of them, but `users:read` where content runs as the visiting user through Connect's own nameservice ([Role permissions](https://docs.posit.co/connect/admin/user-management/role-permissions/)).
A role that holds what a save needs but not `content:delete`, which an administrator may revoke, saves records and fails to delete them with `forbidden`.
Connect gives a content item's `app_role` as `none` where the key may read the item's settings but not open it, as an administrator's key may for every item, and as `owner` or `editor` to the item's owner and its collaborators ([Connect's API](https://docs.posit.co/connect/api/)).
The page could reach Connect's API with the visitor's own session cookie, as Connect's dashboard does, but Connect documents no such way for content, and the cookie gives the page every right of the visitor's session rather than those of a key that the integration caps.

Connect's API reference says that on a cluster of Connect servers, a task's state comes only from the node that runs the task, which the load balancer finds by the cookies of the deploy's reply ([Connect's API](https://docs.posit.co/connect/api/)).
It names no such limit for a bundle, whose `active` turns true once its deploy worked, and whose `deploy_failed_time` is set once its deploy failed.
A content item keeps its name once `POST /v1/content` has created it, and a bundle that was uploaded but never deployed still lists among the bundles for its owner, so a save that fails halfway deletes what it made.
Connect gives its search of content, the bundles of a content item and its users in pages, 20 bundles to a page by default, so the backend follows the pages, as today's search does ([R/connect.R#L550-L584](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L550-L584)).

In a check with pins 1.4.2 on a folder board, `pin_meta()` and `pin_download()` read a version whose `data.txt` was JSON and held no `pin_hash`, while the `data.txt` that `pin_upload()` wrote was YAML, naming a file such as `file745265fc9d34b.json`, the name of the temporary file that today's save uploads ([R/rack.R#L466-L474](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L466-L474)).

On `js-state`, at `f139384`, R calls a plugin's request function with its args, `reads` and `file` alone, so the function has no way to the headers of the request that opened the session, which carry the visitor's session token, but through Shiny's session.
The second item of the [Work list](Rewrite-1.6#work) changes this, in blockr.core.

</details>
