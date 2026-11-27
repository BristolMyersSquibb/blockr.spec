# The storage API: operations, the client and R's folder
Status: review. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): the operations through which the plugin reaches every backend, with their args, their replies and their failures, what a record and a version are to them, who the user is, which each implementation of the API learns by its own sign-in, how the plugin chooses its backend and learns of it in its once-per-page request, a service of a deployment's own, which speaks the storage API in any language, and R serving the API on a pins folder of its own disk, for setting up and testing.
It shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that send the storage plugin's requests while its `storage.load()` runs, write the storage API's description and its client, document the API in a vignette, and serve it from R on a pins folder.
How the plugin calls Connect behind the same operations is [Connect from the browser](Rewrite-1.6.2)'s, and what the controls and the dialogs do with them is [The controls and dialogs](Rewrite-1.6.3)'s.

## What must hold

1. The plugin reaches every backend through one interface in the browser, which the Connect backend fills with calls to Connect's API and the client of the storage API with calls to a service, so that the controls and the dialogs know no backend.
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

- The rack layer becomes a storage API of named operations, each with JSON args and a JSON reply (below), with sharing and the search of users behind capabilities, as today's generics have them (notes).
- In the browser, one interface holds these operations, as a method for each, which takes the operation's args as one object and resolves with its reply, or rejects with a `StorageError` that carries the failure's code.
  The Connect backend fills it with calls to Connect's API, with the visitor's key ([Connect from the browser](Rewrite-1.6.2)).
  The client of the storage API fills it for any other backend, sending each operation as `POST <base>/<operation>` with its args as the body, to a service that speaks the API or to R's folder (below).
- The controls and the dialogs call that interface alone, and leave out what the backend's capabilities do not give ([The controls and dialogs](Rewrite-1.6.3)).

### Records and versions

- A record is a board that the backend keeps under a key, with every version of it, each version being the JSON board that one save added ([Glossary](Glossary)).
- Its owner and its key name a record, so that two owners may each hold a record under the same key, as two accounts on Connect may each hold a pin of the same name.
  The owner is a string that the backend gives, such as the account's name on Connect, or the user under whom R runs in R's folder (below).
  The URL's `user` names the owner where the owner is not the user whom the backend's `user` gives, as today ([R/utils.R#L158-L171](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/utils.R#L158-L171)).
- A record's key is fixed once the user picks it, as today, since a URL and every link to the record name it by its key, and since some backends cannot rename a key at all (notes).
  Its rules are the backend's, and a key that the backend refuses fails with `invalid_key` (below).
- The plugin keys a record on neither the board's name nor the board's id ([Plugins](Rewrite-1.1.12#storage)).
- A version is named by a string that the backend gives, such as the version of a pin, and holds the JSON board that a save stored, the time of the save and the board's content hash.
  The content hash is the SHA-256 of the text that `core.store.save()` wrote, in hex, which the plugin computes with the browser's `crypto.subtle` and sends with the board, and which the backend stores and gives back.
  So Save adds no version where the record's last version holds the same hash ([The controls and dialogs](Rewrite-1.6.3#saving)), and no service computes a hash.
- Where the backend keeps no versions, its capability `versioning` is false, a record holds one version, which `add_version` replaces, and the controls leave out the version history.

### The operations

Every backend gives the first nine, and a backend gives the last five where its capabilities say so.

| Operation | Args | Reply | Fails with |
|---|---|---|---|
| `capabilities` | None | `{ api, versioning, sharing, visibility, user_discovery }`, where `api` is the version of the storage API that the backend speaks, `1`, and the rest are flags | |
| `user` | None | `{ owner, name }` of the user whom the backend knows, where `owner` names the user as an owner of records | `unauthorized` |
| `list_records` | None | `{ records }`, each `{ owner, key, saved }`, every record that the user may open, the user's own and those shared with them, the latest save first | |
| `record_versions` | `{ owner, key }` | `{ versions }`, each `{ version, saved, hash }`, the latest first | `not_found` |
| `read_version` | `{ owner, key, version }`, where a missing `version` reads the latest | `{ version, saved, hash, board }`, where `board` is the JSON that the save stored | `not_found` |
| `create_record` | `{ key, board, hash }` | `{ owner, key, version, saved }`, the record created under the user whom the backend knows | `key_taken`, `invalid_key` |
| `add_version` | `{ owner, key, board, hash }` | `{ version, saved }` | `not_found`, `forbidden` |
| `delete_version` | `{ owner, key, version }` | `{}` | `not_found`, `forbidden` |
| `delete_record` | `{ owner, key }` | `{}` | `not_found`, `forbidden` |
| `access` | `{ owner, key }` | `{ access, shares }`, where `access` is `acl`, `logged_in` or `all`, and each share is `{ principal, name }`, a user who may open the record | `not_found` |
| `set_access` | `{ owner, key, access }` | `{}` | `not_found`, `forbidden` |
| `share` | `{ owner, key, principal }` | `{}` | `not_found`, `forbidden` |
| `unshare` | `{ owner, key, principal }` | `{}` | `not_found`, `forbidden` |
| `find_users` | `{ query }` | `{ users }`, each `{ principal, name }`, the users whose name starts with `query` | |

- The capability `visibility` gives `access` and `set_access`, `sharing` gives `share` and `unshare`, and `user_discovery` gives `find_users`, as today's flags give their generics.
  The flags `tags` and `metadata` go, since no operation needs them (notes).
- An access of `acl` lets only the owner and the users that `shares` lists open the record, `logged_in` every user who is signed in, and `all` everyone, as Connect's access types do, while the dialog's Private is `acl` with no shares, as today's is ([R/server.R#L980-L1000](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/server.R#L980-L1000)).
- A time is a string in ISO 8601, with its time zone.
- The board of a version that today's stack saved is today's serialization, which holds no `format`, and converts as the plugin opens it ([Records, links and app scripts across the switch](Rewrite-1.6.5#records-and-files-saved-today)).

### Failures

- Over HTTP, an operation that succeeds replies with status 200 and its reply as JSON, and one that fails replies with the status of its code and `{ "error": { "code", "message", "sign_in" } }`, where `message` is for the user to read, and `sign_in`, which only `unauthorized` carries and may leave out, is the URL of the service's sign-in (below).
- The codes are `not_found` (404), `key_taken` (409), `invalid_key` (422), `forbidden` (403), `unauthorized` (401), `unsupported` (501), for an operation that the backend's capabilities do not give, and `invalid` (400), for args that do not fit the operation.
- Any other status, or a reply that is no such JSON, rejects with the code `failed`, and the plugin raises a notification for every failure that the user's action meets ([The controls and dialogs](Rewrite-1.6.3#notifications)).

### Who the user is

- The storage API leaves how a user signs in to each implementation of it, and fixes only what the plugin needs: who the user is, through `user`, and that nobody is signed in, through the failure `unauthorized`.
- The client of the storage API sends every call with the browser's own credentials, through `credentials: "include"`, such as the cookie of a sign-in that guards both the app and the service, and adds none of its own, so that neither R nor the plugin holds a credential of the service.
  So a service shares the app's site, as a path on the app's server or another host of the app's domain does, since browsers withhold the cookies of a sign-in from calls to another site (notes).
- A service refuses an operation that needs a user with `unauthorized` while nobody is signed in, and may give `sign_in` with it, which the plugin's status links in place of the records ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
- On Connect, the visitor's key tells Connect who the user is ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)), and in R's folder, where nobody signs in, the user is the one under whom R runs (below).
- A server of our own, which the Roadmap considers for leaving Shiny ([Roadmap](Roadmap#a-server-of-our-own)), may take signing in over, adding what it needs to each call without changing an operation.

### Listing and search

- The operation `list_records` gives every record that the user may open at once, as today's `rack_list()` does, and the plugin searches and pages them in the browser, as today's dialog does in R, so that a service needs no search and no paging of its own (Today).
- What the search matches and how the dialog loads more rows are [The controls and dialogs](Rewrite-1.6.3#the-dialogs)'s.

### Choosing the backend

- The blockr option `session_mgmt_backend` names a service that speaks the API by its URL, so that a database, S3 or other storage, such as the PocketBase that [blockr.session#27](https://github.com/BristolMyersSquibb/blockr.session/issues/27) asks for, sits behind a service of the deployment's own, in any language, which also keeps the credentials of that storage out of the browser.
  The plugin reads it with `core.blockrOption()`, so that it reaches such a service without waiting on R.
- Without that blockr option, the plugin uses Connect where the visitor has a key ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)), R's folder where R runs off Connect (below), and no backend otherwise ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
- No storage call to Connect or to such a service goes through R, so that the app's own Connect key goes ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)).
- The browser's own storage holds no record, since it keeps a record in one browser alone, which may clear it.
- The plugin takes the initials of the user from the backend's `user`: from Connect's API with the visitor's key, from a service's `user` operation, or from R's folder, so that R hands over the key alone.

### The once-per-page request

- Where the blockr option `session_mgmt_backend` is unset, the plugin asks R through its request `session_backend` as its `storage.load()` runs, which core sends though no board is open yet ([Drawing the board](Rewrite-1.1.8#starting-the-page)).
- Its reply names the backend: `{ backend: "connect", key }` with the visitor's key, where Connect sent a token ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)), `{ backend: "folder", url }` with the URL of R's folder, where R serves one (below), or `{ backend: "none", missing }`, where `missing` is `"sign_in"` on Connect for a visitor without a token.
- The plugin waits for the reply in its `storage.load()` only where the URL names a record, and otherwise resolves at once and draws its controls once the reply comes.
- Under the load lock, where core calls no `storage.load()`, the plugin asks as its `start` first runs.

### A deployment's own service

- The blockr.session package ships a description of the API as an OpenAPI 3.1 file in `inst/`, which a service is written against in any language, and from which the client's TypeScript types are generated, so that the two cannot drift.
- Its vignette documents the API, the operations, the failures and the capabilities, in place of today's on a backend of one's own ([vignettes/custom-storage-backend.qmd](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/vignettes/custom-storage-backend.qmd)).
- The tests of the client run against the description's examples, and against R's folder, which speaks the same API (below).
- Where the service runs on another host of the app's site, it answers the browser's CORS preflight for the app's server and allows credentials, which the vignette shows ([CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)).

### R's folder

- For setting up and testing, R serves the storage API itself, on a pins folder of its own disk, through today's methods of the rack generics for folder boards: `pins::board_local()`, unless the blockr option `session_folder` names another folder, as `session_mgmt_backend = pins::board_folder()` does today.
- The plugin uses it where R runs off Connect and `session_mgmt_backend` is unset, as today's `user_pins_board()` falls back to a local board.
- The blockr.session package registers the API's endpoint with Shiny's `session$registerDataObj()` as the request `session_backend` runs, and the request's reply gives the endpoint's URL, so that the client sends R the operations over HTTP, as it sends them to any service (notes).
  The client appends the operation to the path of the URL that it was given and keeps the URL's query, which that URL needs.
- Every visitor of an app shares that one folder, as today's local board is shared, so that it suits setting up and testing, while a deployment for many visitors uses Connect or a service of its own.
- Nobody signs in to it, so its `user` gives the user under whom R runs, from `Sys.info()`, who owns every record in it, while its capabilities give `versioning` alone.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The operations take what the controls and the dialogs use from today's generics: the records (`rack_list()`), a record's versions (`rack_info()`), reading a version (`rack_download()`), creating a record and adding a version (`rack_create()`, `rack_append()` and `rack_upload()`), a version's content hash (`rack_content_hash()`), deleting a version or a record (`rack_delete()` and `rack_purge()`), the capabilities (`rack_capabilities()`), and the access type, the shares and the search of users (`rack_acl()`, `rack_set_acl()`, `rack_share()`, `rack_unshare()`, `rack_shares()` and `rack_find_users()`).
Whether a key is taken (`rack_exists()`) becomes the failure `key_taken` of `create_record`, so that no other save can take the key between the check and the create.
Today's `rack_rename()`, `rack_name()`, `rack_tags()` and `rack_set_tags()` go, since no control uses them once the plugin sets no board's name, and so does the `draft` of `rack_create()` and `rack_records()`, since drafts leave the backend ([Drafts in the browser](Rewrite-1.6.4)).
With them go the flags `tags` and `metadata`, while the Connect tag stays the Connect backend's own ([Connect from the browser](Rewrite-1.6.2#records-as-pins)).
Connect's API takes a new `name` for a content item ([Connect's API](https://docs.posit.co/connect/api/)), but pins finds a pin by its owner and `name`, so a renamed key would leave every URL and link that names the record by its old key opening nothing.

The text that `core.store.save()` writes hashes alike for the same board only where core writes the same board as the same text, its collections in the same order.
Where it does not, Save adds a version for a board that did not change, which costs a version and loses nothing.

Safari blocks the cookies of every call to another site by default ([Full Third-Party Cookie Blocking](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/)), and Firefox keeps a separate cookie jar for each site that the user visits ([Total Cookie Protection](https://blog.mozilla.org/en/mozilla/firefox-rolls-out-total-cookie-protection-by-default-to-all-users-worldwide/)), so the cookie of a sign-in on another site never reaches the calls that the app's page makes there.
A host of the app's own domain is the same site, whose cookies the browser sends with a call that sets `credentials: "include"`, once the service's reply to the CORS preflight allows the app's server with credentials.

On `js-state`, at `f139384`, `core.request()` refuses a plugin's request until a board is open, since `appPlugins()` gives no plugin while the store holds no board ([srcts/core/plugins.ts#L150-L152](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/srcts/core/plugins.ts#L150-L152), [srcts/core/requests.ts#L62-L64](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/srcts/core/requests.ts#L62-L64)).
R would answer such a request, since it checks the request's plugin against the app's plugins alone ([R/request-types.R#L184-L220](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/R/request-types.R#L184-L220)), and the scheduler holds back evaluations until the frontend's `render()` has returned, but not requests.
The first item of the [Work list](Rewrite-1.6#work) changes this, in blockr.core.

In Shiny 1.14.0, `sessionHandler()` routes `/session/<token>/…` to the session, whose `handleRequest()` hands the function that `registerDataObj()` registered the whole request, with its method, its headers and its body, inside the session's reactive domain, and checks no method.
Its route takes the name and one more path segment alone, `^([^/]+)(/[^/]+)?$`, which is room for an operation's name, while the operation's args go in the body of a POST, as DT's server-side tables send POST through the same route.
The URL that `registerDataObj()` returns, `session/<token>/dataobj/<name>?w=&nonce=`, carries its query, so the operation goes before it: `session/<token>/dataobj/<name>/<operation>?w=&nonce=`.
The endpoint's URL lives as long as the Shiny session.
The blockr.session package registers the endpoint from inside the request `session_backend`, through `shiny::getDefaultReactiveDomain()`, which holds while R runs requests in the session's process, as it does for now ([Wire protocol](Rewrite-1.1.9#what-must-hold)), so that the registration moves where R comes to run requests in a worker.
Leaving Shiny brings a server of our own ([Roadmap](Roadmap#a-server-of-our-own)), which can host or route the storage API itself, so that R's folder is revisited then, rather than carried over through the transport.

</details>
