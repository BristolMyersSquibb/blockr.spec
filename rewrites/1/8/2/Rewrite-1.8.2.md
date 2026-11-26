# Documentation of the new stack
Status: review. Design for [Wrap-up](Rewrite-1.8).

One of the design pages of [Wrap-up](Rewrite-1.8): the R and TypeScript references of every package with client code, and its client guides, the hand-written articles on how its client works inside.
It shapes the Work items of its section of that part's Work list.
The migration notes are [The conversion and the migration notes](Rewrite-1.8.3)'s, and the vignettes of the meta-package blockr are [The `blockr` meta-package](Rewrite-1.8.5)'s.
Each package's other user guides, such as core's vignette *Create a block class*, stay with the part that changes the package.

## What must hold

1. Every package with client code has one pkgdown site whose theme and navigation join its R documentation, its TypeScript reference and its client guides, with no separately hosted TypeDoc site.
2. Roxygen2 still writes the R reference, and TypeDoc writes the TypeScript reference from the entry points of the TypeScript source.
   Neither reads the bundles and declarations that the package's own build writes into `inst/`.
3. TypeDoc documents the package's modules that core mounts and the declarations that other packages import, not every source file.
   The client guides explain the internal modules and how they work together.
4. Every package with client code has a client guide.
   It names the package's modules, follows its main flows from start to end, and links their source, their tests and their reference pages.
5. The generated TypeScript pages are pkgdown articles in the site's navigation, and every link between the pages of the site works on the built site.
6. One command builds the generated pages, locally, in the check of a pull request and in the workflow that deploys the site.
   Git holds no generated page, and `R CMD check` needs no Node.
7. The comments from which the build writes JSON Schemas keep their annotations, such as `@minimum`, once the exports gain documentation comments.
8. The reference and client guide of each package with client code are complete before the switch, with a block package's following the port of its block classes.
   A reference is complete once every export of the package's entry points has a `/** ... */` comment, and the documentation build fails on an export without one.
9. Until the switch, each package's site shows the new stack under `dev/`, built from its `js-state` branch on each push.
   The root of the site keeps showing the released package.

## Today

The R packages use roxygen2 comments for their R reference and pkgdown for their sites, as blockr.core's [_pkgdown.yml](https://github.com/BristolMyersSquibb/blockr.core/blob/676b791e7ceebf1012d9f42b4e979addccbc87b9/_pkgdown.yml) shows.
The reusable pkgdown workflow of blockr.ci and the `pkgdown-dev` job of its reusable CI workflow install R's dependencies and build the site with pkgdown, with no Node and no step for TypeScript ([pkgdown.yaml](https://github.com/BristolMyersSquibb/blockr.ci/blob/51647f31367c4f5e3187141d1a2b3204e08a5216/.github/workflows/pkgdown.yaml), [ci.yaml](https://github.com/BristolMyersSquibb/blockr.ci/blob/51647f31367c4f5e3187141d1a2b3204e08a5216/.github/workflows/ci.yaml#L455-L516)).
The `pkgdown-dev` job checks the site on each pull request, those to `js-state` included.
Each package runs the pkgdown workflow, which deploys the site, only on a push to main.

Core's `package.json` has scripts that type-check, lint, test and build, but none that documents ([package.json](https://github.com/BristolMyersSquibb/blockr.core/blob/676b791e7ceebf1012d9f42b4e979addccbc87b9/package.json)).
Its build writes `inst/js/` and `inst/types/` from `srcts/` ([build.ts](https://github.com/BristolMyersSquibb/blockr.core/blob/676b791e7ceebf1012d9f42b4e979addccbc87b9/srcts/build/build.ts)).
The vignette *Create a block class* shows how a package writes a block class and its UI module, and `inst/protocol/README.md` specifies the wire protocol.
No guide maps core's client or follows a piece of work across its modules.

Core's client documents its exports in `//` comments, such as the 110 lines of them in [hosts.ts](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/srcts/types/hosts.ts), on `BlockHost` and the other hosts.
TypeDoc does not read such comments by default.
The declarations that core ships in `inst/types/`, which other packages build against, keep none of them.
Of the client's 17 `/** ... */` comments, 15 describe the state of core's block classes.
Some of them carry annotations, such as `@asType`, `@minimum` and `@pattern`, that `ts-json-schema-generator` reads for the JSON Schemas.

## Proposal

### One site per package

Each package keeps pkgdown as the only website generator, and pkgdown builds the TypeScript pages into the package's one site:

1. The package's npm script `docs` runs TypeDoc with `typedoc-plugin-markdown`, through the package's own configuration of TypeDoc, which names its entry points.
2. TypeDoc writes the TypeScript reference as Markdown pages, into a folder under `vignettes/articles/`.
3. Each page is an `.Rmd` or `.qmd` file whose YAML header gives its title, since pkgdown builds an article from no other file.
4. Then pkgdown's `build_site()` builds those pages as articles of the site, in its theme, beside the R reference that roxygen2 writes and the hand-written client guides.

On every page, pkgdown already rewrites a relative link to an `.md` file into a link to the `.html` file.
No TypeDoc HTML theme or standalone TypeScript website enters the deployment.

The first issue, in blockr.core, proves that route for `@blockr/core` before another package takes it up.
It succeeds when a local build of the site shows the R and TypeScript pages under one theme and navigation, and when a check of the built site finds that every link among the TypeScript pages, and between them and an article, works.
The issue finds out whether TypeDoc's options alone write such files, as the option `fileExtension` of `typedoc-plugin-markdown` and the plugin `typedoc-plugin-frontmatter` may, and puts whatever else it takes into core's `docs` script.
It records how the pages are named and kept out of the R package.
If TypeDoc's Markdown cannot keep those links through pkgdown, the issue tries TypeDoc's JSON output as the source of the pages, rather than shipping a separate site.

Git and `.Rbuildignore` ignore the generated pages, and CI builds them afresh.
A package runs its `docs` script locally for a preview, and the `pkgdown-dev` job and the pkgdown workflow run it in CI.
The two jobs run it just before their pkgdown build, and build the site as today for a package that has no such script.
R's build and check still need no Node, since the documentation build has no part in them.

The package's `_pkgdown.yml` gives the TypeScript reference and the client guides places of their own in the navbar, beside the R reference, the other articles and the migration notes.
The TypeScript reference cannot go into pkgdown's Reference section, which lists only R help topics.
The first issue sets their labels and paths, and every package uses the same ones.
A reader moves from a guide to the signatures that it discusses, and from a signature to its source and its guide.
TypeDoc links each declaration to its line in the source, and the comment of each entry point links the guide that explains it.

Until the switch, each package also deploys the site that its `js-state` branch builds, under `dev/` on its site.
The authors who move their packages to the new stack before the switch read the new stack's documentation there.
The package adds `js-state` to the branches that its pkgdown workflow runs on.
On a push to `js-state`, the pkgdown workflow of blockr.ci sets pkgdown's development mode through the variable `PKGDOWN_DEV_MODE`, so that pkgdown writes the site into `docs/dev/`.
The root of the site keeps showing the released package, which main deploys.
At the switch, the root shows the new stack, and the package removes `dev/` from its site.

### The TypeScript reference

Each package lists two kinds of entry point of its TypeScript source for TypeDoc.
The first kind are its modules that core mounts: the UI modules of its block classes and board options, and the modules of its plugin classes and renderers.
The second kind are the entries whose declarations other packages import, such as `@blockr/core/react`.
TypeDoc follows their re-exports, so it documents what those entries export without making every internal file an entry point.

The TypeScript source, not `inst/js/` or `inst/types/`, carries the `/** ... */` comments that explain an export's purpose, arguments, result, errors and examples where readers need them.
The `//` comments that document an export today, such as those on the members of `BlockHost`, become such comments.
So the declarations in `inst/types/` carry them too, and an editor shows them to the author of another package's module.
The `//` comments that explain how a file works, such as the steps at the head of `srcts/core/start.ts`, stay as they are, since the client guides explain how the modules work together.

Core's entry points are its modules in `srcts/modules/`, such as `head-block` and `dark-mode-option`, and the six entries that `inst/types/package.json` exposes, from `@blockr/core` to `@blockr/core/build`.
The entry `@blockr/core/components` joins them once [blockr.core#869](https://github.com/BristolMyersSquibb/blockr.core/issues/869) splits core's React SDK.
The root entry, `@blockr/core`, holds types alone.
So the guides show how a module reaches core's runtime through its host or `CoreApi`, rather than through an import of core's store.
Other packages name their own entry points in their configuration of TypeDoc.

New documentation comments keep the annotations from which the build writes JSON Schemas.
TypeDoc's configuration accepts those annotations, or leaves them out of the pages, without removing them from the source.
TypeDoc's warnings fail the documentation build.
With its option `validation.notDocumented` on, TypeDoc warns about each export without a `/** ... */` comment, as `R CMD check` warns about an R export without a help page.
Each package turns that option on in the issue that writes its reference, so that it holds in every package by the switch.
TypeDoc documents only what the entry points export, so no internal declaration needs a comment.

### The client guides

The client guides are hand-written Quarto articles.
They sit in `vignettes/articles/`, so that pkgdown builds them into the site and `.Rbuildignore` keeps them out of the package, as it keeps blockr.ui's article on its design system.
A vignette would not do: the guides link the generated pages, which only the site holds, and explain TypeScript that the package's tarball leaves out.

A guide organizes its package by the directories of its TypeScript source.
In core, a lint rule makes each directory a module, which other modules import through its `index.ts`.
A guide describes its own package, and links core's guides rather than repeating them.

Each guide starts with the package's source directories, each with what it holds, and names the files that the build generates from them.
It then follows the flows that explain the package best, with a sequence diagram where it helps to see who acts in what order.
For each module, it names the entry point, the data that the module holds, the modules that it calls and the tests that show how it behaves.
The generated reference holds the signatures, so the guide links them rather than repeating them.

Core's overview names three flows, and one of core's guides follows each in full:

1. Starting the page, from `startPage()` until the plugins have started ([Drawing the board](Rewrite-1.1.8#starting-the-page)).
2. An edit, from a control's `submit()` or a board action until the store has applied the step and the scheduler has raised the revision of each block whose recipe changed ([Board updates](Rewrite-1.1.2#applying-a-delta), [Evaluation in the client](Rewrite-1.1.10#revisions)).
3. An evaluation, from a frontend's demand until core mounts the block's output ([Evaluation in the client](Rewrite-1.1.10#demand), [Drawing the board](Rewrite-1.1.8#renderers)).

Core's other guides cover `CoreApi` and the hosts, mounting modules, the store with its deltas and steps, the command registry and board actions, the scheduler with the wire protocol and the Shiny transport, core's frontend and plugins, the UI modules of its block classes and board options, storage, logging and tracing, its React SDK with the binding and the controls, and its build and tests.
The guides link the design pages whose behavior they explain, but take the code and the tests as their source for what the implementation does.

The client guides of the other packages have the same shape, with areas and flows of their own:

- The guide of blockr.ui covers how its source makes its components, its stylesheet with the theme variables, and its build preset, and links its article on the design system for how to use them ([blockr.ui#116](https://github.com/BristolMyersSquibb/blockr.ui/issues/116)).
- The guide of blockr.dock covers its frontend, its views and grids, its panels and the places that it offers plugins.
- The guide of blockr.graph covers how it draws the DAG, its commands and its plugin state.
- The guide of blockr.assistant covers its agent loop in the browser, its tools and its chat.
- The guides of blockr.code and blockr.session cover their plugins and their requests to R.
- The guide of each block package covers the UI modules of its block classes, the schemas of their state and the requests of its block classes, once those have moved to the new stack.

### Ownership and checks

Wrap-up owns the documentation builds, the new steps of blockr.ci's workflows and the client guides.
The implementation parts keep the user guides and migration notes that they already list.
The reference and client guide of a package whose part starts later join the Work list of this page's spec once that part starts, as blockr.md's will.
Once a package's guide and documentation comments exist, a pull request that changes its client updates them too, as the Conventions of [State in JS](Rewrite-1#conventions) say.

The `pkgdown-dev` job and the pkgdown workflow each build the whole site and check the links of the TypeScript reference and the client guides.
TypeDoc's warnings and a broken link fail both.
The first issue chooses the link checker and the paths that it checks, and the two workflows run that check in every package that has a `docs` script.

## Open questions

None.

<details><summary>Notes for implementers</summary>

TypeDoc 0.28.20, its latest release, supports TypeScript 6.0.x, which core builds with, and `typedoc-plugin-markdown` 4.14.1 targets TypeDoc 0.28.
TypeDoc reads `/** ... */` comments by default and follows re-exports from explicit entry points, so no `entryPointStrategy: expand` over `srcts/` is needed.

The `pkgdown-dev` job of the reusable CI workflow and the reusable pkgdown workflow remove `vignettes/_metadata.yml` before building, because of Mermaid.
They then call `pkgdown::build_site(devel = TRUE, new_process = FALSE, install = FALSE)` and `pkgdown::build_site_github_pages(new_process = FALSE, install = FALSE)`, respectively.
The documentation build belongs just before each call.

Both jobs give `GITHUB_PAT` to every step.
Their checkout also leaves the job's token in the clone, and the pkgdown workflow's token may push to the repo, as it must to deploy the site.
The documentation build runs the code of npm packages, TypeDoc and its plugins among them.
So its npm steps run with neither token.
The typescript job of the CI workflow keeps `GITHUB_PAT` for the steps that install R's dependencies alone, and audits the lockfile before `npm ci --ignore-scripts`, for the same reason.

Every package deploys in the pkgdown workflow's default mode, which pushes `docs/` to the branch `gh-pages` without removing what is there.
So a deployment of `dev/` leaves the root of the site alone, and a deployment of the root leaves `dev/` alone.
In the mode `deploy: actions`, each deployment replaces the whole site, so the workflow deploys `dev/` only in the default mode.

The `js-state` branch of blockr.assistant calls the pkgdown workflow at `v0.1.1`, which lacks the documentation build.
The main branches of blockr.session, blockr.ggplot and blockr.io, from which their `js-state` branches will start, call it at `v0.1.1` too.
So the item of such a package moves its call to `main`, where core's call points already.
The package blockr.ai has no pkgdown site yet.

Core's `inst/types/package.json` exposes `.`, `./binding`, `./build`, `./react`, `./stubs` and `./controls`, from `srcts/index.ts` and the `index.ts` of the directory of each name.
The root `tsconfig.json` is a solution file that references `tsconfig.client.json` and `tsconfig.node.json`, and `srcts/build/` belongs to the second.
So the first issue chooses the TypeScript configuration that TypeDoc needs, rather than assuming that the root file compiles the source.
The rule `no-restricted-imports` in `eslint.config.ts` makes each directory of `srcts/` a module that other modules import through its `index.ts`, all but `types` and `testing`.
The tests in `srcts/build/build.test.ts` and `srcts/build/types.test.ts` already check the generated schemas and the type package that the builds of other packages consume.

The option `validation.notDocumented` is off by default in TypeDoc 0.28.
Once it is on, TypeDoc warns about a declaration without a comment if its option `requiredToBeDocumented` lists the declaration's kind.
By default, those kinds are enums and their members, variables, functions, classes, interfaces and type aliases, and the properties, methods and accessors of each, much as `R CMD check` asks for a description of every argument.

The JSDoc annotations on the state of block classes feed `ts-json-schema-generator`.
A tag that TypeDoc reads must not change the declarations or the schemas that `npm run build` writes.
The documentation build writes nothing into `inst/`, so the typescript job's check that a rebuild leaves `inst/` unchanged still holds.

</details>
