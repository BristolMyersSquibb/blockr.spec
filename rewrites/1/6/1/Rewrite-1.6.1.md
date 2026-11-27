# The storage API: operations, the client and the folder backend
Status: review. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): the operations through which the plugin reaches every backend, with their args, their replies and their failures, what a record and a version are to them, who the user is, which each implementation of the API learns by its own sign-in, how the plugin chooses its backend and learns of it in its once-per-page request, a service of a deployment's own, which speaks the storage API in any language, and the folder backend, through which R serves the API on a pins folder of its own disk, for setting up and testing.
It shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that send the storage plugin's requests while its `storage.load()` runs, write the storage API's description and its client, document the API in a vignette, and serve it from R on a pins folder.
How the plugin calls Connect behind the same operations is [Connect from the browser](Rewrite-1.6.2)'s, and what the controls and the dialogs do with them is [The controls and dialogs](Rewrite-1.6.3)'s.

## What must hold

1. The plugin reaches every backend through one interface in the browser, which the Connect backend fills with calls to Connect's API and the client of the storage API with calls to a service or requests to the folder backend, so that the controls and the dialogs know no backend.
2. A service speaks the storage API from its description alone, in any language, and keeps a database, S3 or other storage behind it, with that storage's credentials out of the browser.
3. A service needs only the operations that every backend gives, since the controls leave out what a backend's capabilities do not give, such as sharing.
4. No storage call goes through R, but where R serves the API on a pins folder of its own disk, for setting up and testing ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 2).
5. Creating a record under a key that another record of its owner holds fails, so that a first save never adds a version to another record ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 4).
6. A service learns who the user is by its own sign-in, so that neither R nor the plugin holds a credential of it, while the API fixes only what the plugin needs to know: who the user is, or that nobody is signed in.

## Today

The rack layer is S3 generics over a backend, which a pins board fills, and which a database or another store fills by carrying the class `rack_backend` ([R/rack.R#L1-L95](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L1-L95)).
A `rack_id` names a record by its `id`, its `user` and its `version`, as the URL does, and `rack_list()` gives one row for each record, with its `id`, a display `name`, its `user` on Connect and the time it was `saved` ([R/connect.R#L130-L149](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/connect.R#L130-L149)).
The flags of `rack_capabilities()` turn on the generics that a minimal backend leaves out: `versioning`, `tags`, `metadata`, `sharing`, `visibility` and `user_discovery`.
A save writes the board as JSON with a content hash of the R list ([R/rack.R#L466-L480](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/rack.R#L466-L480)).
The dialog fetches every record at once and searches and pages them in R, matching the query against each record's display name ([R/server.R#L1317-L1329](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1317-L1329)).

## Proposal

### The interface

- The rack layer becomes a storage API of named operations, each with JSON args and a JSON reply (below), with what not every backend gives, such as saving and sharing, behind capabilities, as today's generics have it (notes).
- In the browser, one interface holds these operations, as a method for each, named in camelCase, such as `listRecords()` for `list_records`.
  A method takes the operation's args as one object and resolves with its reply, or rejects with a `StorageError` that carries the failure's code.
  The args and the replies keep the API's snake_case, as the JSON between the client and R does ([State in JS](Rewrite-1#principles)).
  The Connect backend fills it with calls to Connect's API, with the visitor's key ([Connect from the browser](Rewrite-1.6.2)).
  The client of the storage API fills it for any other backend, a service that speaks the API or the folder backend (below).
  It sends each operation to a service as a POST to the URL that the reply to the once-per-page request gives (below), with the operation's name appended to the URL's path and the args as a JSON body, `{}` for an operation that takes none.
  To the folder backend, it sends each operation as one of the plugin's requests, named after the operation (below).
- The controls and the dialogs call that interface alone, and leave out what the backend's capabilities do not give ([The controls and dialogs](Rewrite-1.6.3)).

### Records and versions

- A record is a board that the backend keeps under a key, with every version of it, each version being the JSON board that one save added ([Glossary](Glossary)).
- Its owner and its key name a record, so that two owners may each hold a record under the same key, as two accounts on Connect may each hold a pin of the same name.
  The owner is a string that the backend gives, such as the account's name on Connect, or the user under whom R runs in the folder backend (below).
  The URL's `user` names the owner where the owner is not the user whom the backend's `user` gives, as today ([R/utils.R#L158-L171](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/utils.R#L158-L171)).
- A record's key is fixed once the user picks it, as today, since a URL and every link to the record name it by its key, and since some backends cannot rename a key at all (notes).
  Every backend takes a key of 3 to 64 letters, digits, hyphens and underscores, the rule that the key chooser follows ([The controls and dialogs](Rewrite-1.6.3#the-key)), so that a record moves between backends under its key.
  The operation `create_record` refuses any other key with `invalid_key` (below).
  The key chooser also refuses a key that starts with `blockr-draft-`, the prefix of today's drafts, which the plugin leaves out of its listing ([Records, links and app scripts across the switch](Rewrite-1.6.5#todays-drafts)).
  That rule is the plugin's alone, so that no service has to know about today's drafts.
- The plugin keys a record on neither the board's name nor the board's id ([Plugins](Rewrite-1.1.12#storage)).
- A version is named by a string that the backend gives, such as the version of a pin, and holds the JSON board that a save stored and the time of the save.
- Whether a board changed is the plugin's to tell, and no backend's: the plugin keeps the text that `core.store.save()` writes for the version that it opened or saved last, and Save adds no version where `core.store.save()` writes the same text again ([The controls and dialogs](Rewrite-1.6.3#saving)).
  It compares the text itself, rather than a hash of it, since the browser's `crypto.subtle` exists only in a secure context, which a page served over plain HTTP lacks unless it comes from `localhost` (notes).
  The plugin keeps no text for a draft that the user restored, so that Save adds a version with the work that only the draft holds ([Drafts in the browser](Rewrite-1.6.4#offering-and-restoring)).
  So no backend stores or computes a hash, and listing a record's versions costs Connect one call ([Connect from the browser](Rewrite-1.6.2#records-as-pins)), where a hash for each version would cost a read of each.
- Where the backend keeps no versions, its capability `versioning` is false, a record holds one version, which `add_version` replaces, and the controls leave out the version history.

### The operations

Every backend gives the first nine, the four of them that change records where its capability `saving` says so, and the last five where its capabilities say so.

| Operation | Args | Reply | Fails with |
|---|---|---|---|
| `capabilities` | None | `{ api, saving, versioning, sharing, visibility, user_discovery }`, where `api` is the version of the storage API that the backend speaks, `1`, and the rest are flags | |
| `user` | None | `{ owner, name }` of the user whom the backend knows, where `owner` names the user as an owner of records | `unauthorized` |
| `list_records` | None | `{ records }`, each `{ owner, key, saved, writable }`, every record that the user may open, the user's own and those shared with them, the latest save first, where `writable` says whether the user may add versions to the record | |
| `record_versions` | `{ owner, key }` | `{ versions }`, each `{ version, saved }`, the latest first | `not_found` |
| `read_version` | `{ owner, key, version }`, where a missing `version` reads the latest | `{ version, saved, board }`, where `board` is the JSON that the save stored | `not_found` |
| `create_record` | `{ key, board }` | `{ owner, key, version, saved }`, the record created under the user whom the backend knows | `key_taken`, `invalid_key` |
| `add_version` | `{ owner, key, board }` | `{ version, saved }` | `not_found`, `forbidden` |
| `delete_version` | `{ owner, key, version }` | `{}` | `not_found`, `forbidden` |
| `delete_record` | `{ owner, key }` | `{}` | `not_found`, `forbidden` |
| `access` | `{ owner, key }` | `{ access, shares }`, where `access` is `acl`, `logged_in` or `all`, and each share is `{ principal, name }`, a user or a group that may open the record | `not_found` |
| `set_access` | `{ owner, key, access }` | `{}` | `not_found`, `forbidden` |
| `share` | `{ owner, key, principal }` | `{}` | `not_found`, `forbidden` |
| `unshare` | `{ owner, key, principal }` | `{}` | `not_found`, `forbidden` |
| `find_users` | `{ query }` | `{ users }`, each `{ principal, name, email, username }`, the users whose name starts with `query` | |

- The capability `saving` gives `create_record`, `add_version`, `delete_version` and `delete_record`, which a backend may withhold from a user who may only open records, as Connect withholds them from a viewer ([Connect from the browser](Rewrite-1.6.2#what-a-visitors-role-allows)), and where it is false, the controls save a download in place of a record ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
- The capability `visibility` gives `access` and `set_access`, `sharing` gives `share` and `unshare`, and `user_discovery` gives `find_users`, as today's flags give their generics.
  The flags `tags` and `metadata` go, since no operation needs them (notes).
- An access of `acl` lets only the owner and the users and groups that `shares` lists open the record, `logged_in` every user who is signed in, and `all` everyone, as Connect's access types do, while the dialog's Private is `acl` with no shares, as today's is ([R/server.R#L980-L1000](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L980-L1000)).
- A share's `principal` names a user or a group, and on Connect the shares hold every user and group of a content item's permissions, its collaborators included, so that the dialog never calls Private a record that others can open ([Connect from the browser](Rewrite-1.6.2#sharing)).
  So `unshare` takes either, while `share` takes a user that `find_users` gives, as the dialog's Share picks one.
- The operation `delete_version` refuses with `invalid` to delete the record's latest version, the one that `read_version` reads where the args name none, since Connect deletes no bundle while the content item serves it (notes).
  So a record always has a latest version, and `delete_record` deletes the record with every version.
- A record's `writable` holds where the user may add versions to it: on each of the user's own records, and, on Connect, on one whose owner made the user a collaborator in Connect's own settings, while a user whom the dialog's Share adds may only open the record ([Connect from the browser](Rewrite-1.6.2#sharing)).
  What Save does with it is [The controls and dialogs](Rewrite-1.6.3#saving)'s.
- A user that `find_users` gives carries `email` and `username` where the backend has them, so that the dialog tells two users of one name apart, as today's search shows the email, or else the username, under the name ([R/server.R#L1069-L1070](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L1069-L1070)).
- A time is a string in ISO 8601, with its time zone.
- A board in the args or a reply, as `board` is, is the JSON board itself, a JSON object, rather than a string that holds its text.
- The plugin uses a backend only where `api` names a version of the storage API that the plugin speaks, `1` for now, and otherwise has no backend, with a notification that names both versions ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
- The board of a version that today's stack saved is today's serialization, which holds no `format`, so the store refuses to open it ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today)).
  Running blockr.convert's `convert_file()` over a record worth keeping adds a version to it that opens.

### Failures

- Over HTTP, an operation that succeeds replies with status 200 and its reply as JSON, and one that fails replies with the status of its code and `{ "error": { "code", "message", "sign_in" } }`, where `message` is for the user to read, and `sign_in`, which only `unauthorized` carries and may leave out, is the URL of the service's sign-in (below).
  The folder backend replies with the same JSON, without a status (below).
- The codes are `not_found` (404), `key_taken` (409), `invalid_key` (422), `forbidden` (403), `unauthorized` (401), `unsupported` (501), for an operation that the backend's capabilities do not give, and `invalid` (400), for args that do not fit the operation.
- Any other status, a reply that is no such JSON, or a request that R fails to answer or drops, rejects with the code `failed`, and the plugin raises a notification for every failure that the user's action meets ([The controls and dialogs](Rewrite-1.6.3#notifications)).

### Who the user is

- The storage API leaves how a user signs in to each implementation of it, and fixes only what the plugin needs: who the user is, through `user`, and that nobody is signed in, through the failure `unauthorized`.
- The client of the storage API sends every call to a service with the browser's own credentials, through `credentials: "include"`, such as the cookie of a sign-in that guards both the app and the service, and adds none of its own, so that neither R nor the plugin holds a credential of the service.
  So a service shares the app's site, as a path on the app's server or another host of the app's domain does, since browsers withhold the cookies of a sign-in from calls to another site (notes).
- A service refuses an operation that needs a user with `unauthorized` while nobody is signed in, and may give `sign_in` with it, which the plugin's status links in place of the records ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
- On Connect, the visitor's key tells Connect who the user is ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)), and in the folder backend, where nobody signs in, the user is the one under whom R runs (below).
- A server of our own, which the Roadmap considers for leaving Shiny ([Roadmap](Roadmap#a-server-of-our-own)), may take signing in over, adding what it needs to each call without changing an operation.

### Listing and search

- The operation `list_records` gives every record that the user may open at once, as today's `rack_list()` does, and the plugin searches and pages them in the browser, as today's dialog does in R, so that a service needs no search and no paging of its own (Today).
- What the search matches and how the dialog loads more rows are [The controls and dialogs](Rewrite-1.6.3#the-dialogs)'s.

### Choosing the backend

- The blockr option `session_mgmt_backend` names a service that speaks the API by its URL, so that a database, S3 or other storage, such as the PocketBase that [blockr.session#27](https://github.com/BristolMyersSquibb/blockr.session/issues/27) asks for, sits behind a service of the deployment's own, in any language, which also keeps the credentials of that storage out of the browser.
- Without that blockr option, the plugin uses Connect where the visitor has a key ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)), the folder backend where R runs off Connect (below), and no backend otherwise ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
- R makes this choice in its reply to the once-per-page request (below), so that the plugin asks R once as the page starts.
  Reading `session_mgmt_backend` through `core.blockrOption()` would cost a request to R of its own, ahead of that one ([Board options and blockr options](Rewrite-1.1.13#blockr-options)).
- No storage call to Connect or to such a service goes through R, so that the app's own Connect key goes ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)).
- The browser's own storage holds no record, since it keeps a record in one browser alone, which may clear it.
- The plugin takes the initials of the user from the backend's `user`, from Connect's API with the visitor's key or from a service's `user` operation, so that R hands over the key alone.
  It gives no avatar in the folder backend, where nobody signs in, as the dock's navbar has the avatar only for a visitor who is signed in ([The dock's navbar](Rewrite-1.2.5#the-storage-plugins-controls)).

### The once-per-page request

- The plugin asks R through its request `session_backend` as its `storage.load()` runs, which core sends though no board is open yet ([Drawing the board](Rewrite-1.1.8#starting-the-page)).
- Its reply names the backend, by the first of these cases that holds:

| Reply | Where |
|---|---|
| `{ backend: "service", url }`, with the URL that `session_mgmt_backend` gives | That blockr option is set |
| `{ backend: "none", missing: "integration" }` | R runs on Connect, and no Visitor API Key integration is associated with the app, as on an app open to anyone without a login, with which Connect associates none |
| `{ backend: "none", missing: "sign_in" }` | R runs on Connect, and the visitor is not signed in |
| `{ backend: "connect", server, key }`, with Connect's address and the visitor's key | R runs on Connect, and it exchanged the visitor's session token for a key |
| `{ backend: "folder" }`, for the folder backend (below) | R runs off Connect |

- How R tells these cases apart on Connect is [Connect from the browser](Rewrite-1.6.2#the-visitors-key)'s.
- The plugin waits for the reply in its `storage.load()` only where the URL names a record, and otherwise resolves at once and draws its controls once the reply comes.
- Under the load lock, where core calls no `storage.load()`, the plugin asks as its `start` first runs.

### A deployment's own service

- The blockr.session package ships a description of the API as an OpenAPI 3.1 file in `inst/`, which a service is written against in any language, and from which the TypeScript types of the client of the storage API are generated, so that the two cannot drift.
- Its vignette documents the API, the operations, the failures and the capabilities, in place of today's on a backend of one's own ([vignettes/custom-storage-backend.qmd](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/vignettes/custom-storage-backend.qmd)).
- The tests of the client of the storage API run against the description's examples, and so do the tests of the folder backend, which answers the same operations (below).
- Where the service runs on another host of the app's site, it answers the browser's CORS preflight for the app's server and allows credentials, which the vignette shows ([CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)).
- A service refuses a call whose `Content-Type` is not `application/json` with `invalid`, so that a page of another site cannot send it an operation with the user's cookies (notes).

### The folder backend

- For setting up and testing, R serves the storage API itself, on a pins folder of its own disk, through today's methods of the rack generics for folder boards: `pins::board_local()`, unless the blockr option `session_folder` names another folder, as `session_mgmt_backend = pins::board_folder()` does today.
- The plugin uses it where R runs off Connect and `session_mgmt_backend` is unset, as today's `user_pins_board()` falls back to a local board.
- Each operation is one of the plugin's requests, named after the operation, which the plugin's method of `plugin_requests()` gives beside `session_backend` ([Plugins](Rewrite-1.1.12#a-plugins-requests)), so that the folder backend needs no URL of its own (notes).
  Its args are the operation's, but for `board`, which goes in the request's body, and its reply is the JSON that a service replies with, `{ error }` included, which the client of the storage API reads as it reads a service's (above).
  The reply of `read_version` goes in the reply's body, through `new_reply_body()`, since it holds a board.
  So no message on the websocket carries a board, as a message holds at most 4 MiB by default, while the transport carries a body over HTTP (notes).
- R answers requests one at a time, in the order they came, so a call to the folder backend waits for the evaluations queued before it, which setting up and testing can afford (notes).
  Opening a board drops the requests that R still holds for the board before ([Drawing the board](Rewrite-1.1.8#opening-a-board)), so the plugin opens a board only once its calls to the folder backend have come back.
- Every visitor of an app shares that one folder, as today's local board is shared, so that it suits setting up and testing, while a deployment for many visitors uses Connect or a service of its own.
- Nobody signs in to it, so its `user` gives the user under whom R runs, from `Sys.info()`, who owns every record in it, each `writable`, while its capabilities give `saving` and `versioning` alone.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The operations take what the controls and the dialogs use from today's generics: the records (`rack_list()`), a record's versions (`rack_info()`), reading a version (`rack_download()`), creating a record and adding a version (`rack_create()`, `rack_append()` and `rack_upload()`), deleting a version or a record (`rack_delete()` and `rack_purge()`), the capabilities (`rack_capabilities()`), and the access type, the shares and the search of users (`rack_acl()`, `rack_set_acl()`, `rack_share()`, `rack_unshare()`, `rack_shares()` and `rack_find_users()`).
Whether a key is taken (`rack_exists()`) becomes the failure `key_taken` of `create_record`, so that no other save can take the key between the check and the create.
Today's `rack_rename()`, `rack_name()`, `rack_tags()` and `rack_set_tags()` go, since no control uses them once the plugin sets no board's name, and so does the `draft` of `rack_create()` and `rack_records()`, since drafts leave the backend ([Drafts in the browser](Rewrite-1.6.4)).
So does `rack_content_hash()`, since the plugin tells a changed board itself.
With them go the flags `tags` and `metadata`, while the Connect tag stays the Connect backend's own ([Connect from the browser](Rewrite-1.6.2#records-as-pins)).
Connect's API takes a new `name` for a content item ([Connect's API](https://docs.posit.co/connect/api/)), but pins finds a pin by its owner and `name`, so a renamed key would leave every URL and link that names the record by its old key opening nothing.
The same API refuses to delete the bundle that a content item serves, which is a record's latest version: "Deletion is not allowed while the bundle is still active."

The text that `core.store.save()` writes is the same for the same board only where core writes the same board as the same text, its collections in the same order.
Where it does not, Save adds a version for a board that did not change, which costs a version and loses nothing.
A browser gives `crypto.subtle` only to a page in a secure context, one served over HTTPS or from `localhost` ([Secure contexts](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts)), so an app that a Shiny Server serves over plain HTTP on a company's network would have no hash.
Keeping the text costs the page one more copy of the board's JSON, and comparing it costs one pass over that text.

A form, or a `fetch()` whose `Content-Type` is `text/plain`, reaches another site without a CORS preflight ([Simple requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS#simple_requests)), and carries the cookies that the browser sends to that site.
A service that takes only `application/json` answers only the calls that a preflight let through.

Safari blocks the cookies of every call to another site by default ([Full Third-Party Cookie Blocking](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/)), and Firefox keeps a separate cookie jar for each site that the user visits ([Total Cookie Protection](https://blog.mozilla.org/en/mozilla/firefox-rolls-out-total-cookie-protection-by-default-to-all-users-worldwide/)), so the cookie of a sign-in on another site never reaches the calls that the app's page makes there.
A host of the app's own domain is the same site, whose cookies the browser sends with a call that sets `credentials: "include"`, once the service's reply to the CORS preflight allows the app's server with credentials.

On `js-state`, at `f139384`, `core.request()` refuses a plugin's request until a board is open, since `appPlugins()` gives no plugin while the store holds no board ([srcts/core/plugins.ts#L150-L152](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/srcts/core/plugins.ts#L150-L152), [srcts/core/requests.ts#L62-L64](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/srcts/core/requests.ts#L62-L64)).
R would answer such a request, since it checks the request's plugin against the app's plugins alone ([R/request-types.R#L184-L220](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/R/request-types.R#L184-L220)), and the scheduler holds back evaluations until the frontend's `render()` has returned, but not requests.
The first item of the [Work list](Rewrite-1.6#work) changes this, in blockr.core.

On `js-state`, at `cc9d457`, R answers every request from one queue, one at a time, in the order they came, evaluations included, and runs each from `later::later()`, outside the session's reactive domain ([R/evaluator-class.R#L481-L506](https://github.com/BristolMyersSquibb/blockr.core/blob/cc9d457bf6cd736fe551f6061d768c35b5aa5e83/R/evaluator-class.R#L481-L506)).
So a request finds no Shiny session through `shiny::getDefaultReactiveDomain()`, with which it could give the folder backend a URL of its own through Shiny's `session$registerDataObj()`.
Handing requests a way to register one would take a reserved argument in core that the folder backend alone would use, while the plugin's requests reach R already.
A message on the websocket holds at most the blockr option `max_message_size`, 4 MiB by default, while the transport posts a request's body over HTTP and serves a large body of a reply from a URL ([R/shiny-transport.R#L23-L34](https://github.com/BristolMyersSquibb/blockr.core/blob/cc9d457bf6cd736fe551f6061d768c35b5aa5e83/R/shiny-transport.R#L23-L34), [R/shiny-transport.R#L387-L399](https://github.com/BristolMyersSquibb/blockr.core/blob/cc9d457bf6cd736fe551f6061d768c35b5aa5e83/R/shiny-transport.R#L387-L399)).
Shiny refuses any HTTP request larger than `shiny.maxRequestSize`, 5 MiB by default, with status 413, so a board larger than that saves to the folder backend only where the app raises that option.
Leaving Shiny brings a server of our own ([Roadmap](Roadmap#a-server-of-our-own)), which can host or route the storage API itself, so that the folder backend may then speak it over HTTP, as a service does.

</details>
