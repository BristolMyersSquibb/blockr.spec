# The storage API: operations, the client and R's folder
Status: draft. Design for [Session management as a storage plugin](Rewrite-1.6).

One of the design pages of session management ([Session management as a storage plugin](Rewrite-1.6)): the operations through which the plugin reaches every backend, with what a record is to them, how the plugin chooses its backend and learns of it in its once-per-page request, a service of a deployment's own, which speaks the storage API in any language, and R serving the API on a pins folder of its own disk, for setting up and testing.
It shapes the Work items of [Session management as a storage plugin](Rewrite-1.6#work) that send the storage plugin's requests while its `storage.load()` runs, write the storage API's description and its client, document the API in a vignette, and serve it from R on a pins folder.
How the plugin calls Connect behind the same operations is [Connect from the browser](Rewrite-1.6.2)'s, and what the controls and the dialogs do with them is [The controls and dialogs](Rewrite-1.6.3)'s.

## What must hold

1. The plugin reaches every backend through one interface in the browser, which the Connect backend fills with calls to Connect's API and the client of the storage API with calls to a service, so that the controls and the dialogs know no backend.
2. A service speaks the storage API from its description alone, in any language, and keeps a database, S3 or other storage behind it, with that storage's credentials out of the browser.
3. No storage call goes through R, but where R serves the API on a pins folder of its own disk, for setting up and testing ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 2).
4. Creating a record under a key that another record holds fails, so that a first save never adds a version to another record ([Session management as a storage plugin](Rewrite-1.6#what-must-hold), condition 4).

## Proposal

### The operations

- The rack layer becomes a storage API of named operations, each with JSON args and a JSON reply, such as `list_records`, `record_versions`, `read_version`, `create_record`, `add_version`, `delete_version`, `delete_record`, `capabilities` and `user`, with sharing and the search of users behind capabilities, as today's generics have them (notes).
- In the browser, one interface holds these operations.
  The Connect backend fills it with calls to Connect's API, with the visitor's key ([Connect from the browser](Rewrite-1.6.2)).
  The client of the storage API fills it for any other backend, sending each operation as `POST <base>/<operation>` to a service that speaks the API.
- The blockr.session package ships a description of the API, such as an OpenAPI file, and its vignette documents the API in place of today's on a backend of one's own ([vignettes/custom-storage-backend.qmd](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/vignettes/custom-storage-backend.qmd)).

### Records

- A record is a board that the backend keeps under a key, with every version of it, each version being the JSON board that one save added ([Glossary](Glossary)).
- A record's key is fixed once the user picks it, as today, since a URL and every link to the record name it by its key, and since some backends cannot rename a key at all (notes).
- The plugin keys a record on neither the board's name nor the board's id ([Plugins](Rewrite-1.1.12#storage)).
- Each version holds the content hash of its JSON board, so that Save adds no version where the record's last version holds the same hash ([The controls and dialogs](Rewrite-1.6.3#saving)).

### Choosing the backend

- The blockr option `session_mgmt_backend` names a service that speaks the API by its URL, so that a database, S3 or other storage, such as the PocketBase that [blockr.session#27](https://github.com/BristolMyersSquibb/blockr.session/issues/27) asks for, sits behind a service of the deployment's own, in any language, which also keeps the credentials of that storage out of the browser.
- Without that blockr option, the plugin uses Connect where the visitor has a key ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)), R's folder where R runs off Connect (below), and no backend otherwise ([The controls and dialogs](Rewrite-1.6.3#without-a-backend)).
- No storage call to Connect or to such a service goes through R, so that the app's own Connect key goes ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)).
- The browser's own storage holds no record, since it keeps a record in one browser alone, which may clear it.
- The plugin takes the initials of the user who is signed in from the backend: from Connect's API with the visitor's key, or from the storage API's `user` operation where a service gives one, so that R hands over the key alone.

### The once-per-page request

- The plugin asks R through a request of its own as its `storage.load()` runs, which core sends though no board is open yet ([Drawing the board](Rewrite-1.1.8#starting-the-page)).
- The request's reply gives the visitor's key, where Connect sent a token ([Connect from the browser](Rewrite-1.6.2#the-visitors-key)), or the URL of R's folder, where R serves one (below), and the plugin waits for the reply there only where the URL names a record.
- Under the load lock, where core calls no `storage.load()`, the plugin asks as its `start` first runs.

### R's folder

- For setting up and testing, R serves the storage API itself, on a pins folder of its own disk, through today's methods of the rack generics for folder boards: `pins::board_local()`, unless the blockr option `session_folder` names another folder, as `session_mgmt_backend = pins::board_folder()` does today.
- The plugin uses it where R runs off Connect and `session_mgmt_backend` is unset, as today's `user_pins_board()` falls back to a local board.
- The blockr.session package registers the API's endpoint with Shiny's `session$registerDataObj()` as the plugin's once-per-page request runs, and that request's reply gives the endpoint's URL, so that the client sends R the operations over HTTP, as it sends them to any service (notes).
- Every visitor of an app shares that one folder, as today's local board is shared, so that it suits setting up and testing, while a deployment for many visitors uses Connect or a service of its own.

## Open questions

- What each operation takes and replies, and how it fails, which the client, the Connect backend and every service build against: writing them out from today's generics and from what the controls and the dialogs show settles it.
- How `list_records` searches, in which order it lists records, and how it gives the next rows as the dialog's table scrolls: settled with the operations.
- How a service of a deployment's own learns who the user is, which the visitor's key tells Connect: it blocks the API's description, and the user's choice settles it, between the service's own sign-in, which the browser sends with each call where the service shares the app's server, a token that R hands over in the once-per-page request, or both.
- Which hash a version holds, which the plugin computes from the JSON board in the browser: settled with the operations.

<details><summary>Notes for implementers</summary>

The storage API holds what the controls and the dialogs use, as today's generics give it: the records (`rack_list()`), a record's versions (`rack_info()`), reading a version (`rack_download()`), creating a record and adding a version (`rack_create()`, `rack_append()` and `rack_upload()`), whether a key is taken (`rack_exists()`), a version's content hash (`rack_content_hash()`), deleting a version or a record (`rack_delete()` and `rack_purge()`), the capabilities (`rack_capabilities()`), and the access type, the shares and the search of users (`rack_acl()`, `rack_set_acl()`, `rack_share()`, `rack_unshare()`, `rack_shares()` and `rack_find_users()`).
Today's `rack_rename()`, `rack_name()`, `rack_tags()` and `rack_set_tags()` go, since no control uses them once the plugin sets no board's name, and so does the `draft` of `rack_create()` and `rack_records()`, since drafts leave the backend ([Drafts in the browser](Rewrite-1.6.4)).
Connect's API takes a new `name` for a content item ([Connect's API](https://docs.posit.co/connect/api/)), but pins finds a pin by its owner and `name`, so a renamed key would leave every URL and link that names the record by its old key opening nothing.

On `js-state`, at `f139384`, `core.request()` refuses a plugin's request until a board is open, since `appPlugins()` gives no plugin while the store holds no board ([srcts/core/plugins.ts#L150-L152](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/srcts/core/plugins.ts#L150-L152), [srcts/core/requests.ts#L62-L64](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/srcts/core/requests.ts#L62-L64)).
R would answer such a request, since it checks the request's plugin against the app's plugins alone ([R/request-types.R#L184-L220](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/R/request-types.R#L184-L220)), and the scheduler holds back evaluations until the frontend's `render()` has returned, but not requests.
The first item of the [Work list](Rewrite-1.6#work) changes this, in blockr.core.

In Shiny 1.14.0, `sessionHandler()` routes `/session/<token>/…` to the session, whose `handleRequest()` hands the function that `registerDataObj()` registered the whole request, with its method, its headers and its body, inside the session's reactive domain, and checks no method.
Its route takes the name and one more path segment alone, `^([^/]+)(/[^/]+)?$`, which is room for an operation's name, while the operation's args go in the body of a POST, as DT's server-side tables send POST through the same route.
The endpoint's URL lives as long as the Shiny session.
The blockr.session package registers the endpoint from inside its once-per-page request, through `shiny::getDefaultReactiveDomain()`, which holds while R runs requests in the session's process, as it does for now ([Wire protocol](Rewrite-1.1.9#what-must-hold)), so that the registration moves where R comes to run requests in a worker.
Leaving Shiny brings a server of our own ([Roadmap](Roadmap#a-server-of-our-own)), which can host or route the storage API itself, so that R's folder is revisited then, rather than carried over through the transport.

</details>
