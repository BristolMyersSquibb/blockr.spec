# Documentation of the new stack
Status: review. Design for [Wrap-up](Rewrite-1.8).

One of the design pages of [Wrap-up](Rewrite-1.8): the R and TypeScript references and the long-form guides to the client internals of every package with client code.
It shapes the TypeScript-to-pkgdown build, the reusable CI and pkgdown workflows, core's reference and guides, and each later package's reference and guide, all items in Wrap-up's Work list.
The conversion and migration notes are [The conversion and the migration notes](Rewrite-1.8.3)'s, and the user guides that each implementation part already plans stay there.
The assistant's benchmark is [The assistant's benchmark](Rewrite-1.8.1)'s.

## What must hold

1. Every package with client code has one pkgdown site whose theme and navigation join its R documentation, its TypeScript reference and its guides, with no separately hosted TypeDoc site.
2. Roxygen2 remains the source of the R reference, TypeDoc generates the TypeScript reference from source entry points, and neither generator reads the bundles and declarations that a package's build writes into `inst/`.
3. TypeDoc documents the modules that core mounts and the declarations that other packages import, rather than every source file, while the guides explain the internal modules and how they work together.
4. Every package with client code has a long-form guide that names its own modules, follows its important end-to-end flows and links its source, tests and reference pages.
5. The generated TypeScript pages blend into pkgdown's articles and navigation, and their internal links survive the build.
6. A documentation change rebuilds the generated pages locally, in the pull request check and in the deployment workflow, without committing generated Markdown or requiring Node during `R CMD check`.
7. The comments that generate JSON Schemas keep their schema annotations when public TypeScript exports gain documentation comments.
8. The reference and client guide of each package with client code are complete before the switch, with a block package's following the port of its block classes.

## Today

The R packages use roxygen2 comments for their R reference and pkgdown for their sites, as blockr.core's [_pkgdown.yml](https://github.com/BristolMyersSquibb/blockr.core/blob/676b791e7ceebf1012d9f42b4e979addccbc87b9/_pkgdown.yml) shows.
The reusable pkgdown workflow installs R's dependencies and calls `pkgdown::build_site_github_pages()`, with no Node or TypeScript documentation step ([pkgdown.yaml](https://github.com/BristolMyersSquibb/blockr.ci/blob/main/.github/workflows/pkgdown.yaml)).

Core's `package.json` has type-check, lint, test and build scripts but no documentation generator ([package.json](https://github.com/BristolMyersSquibb/blockr.core/blob/676b791e7ceebf1012d9f42b4e979addccbc87b9/package.json)).
Its build writes `inst/js/` and `inst/types/` from `srcts/`, so the generated files do not provide another source to document ([build.ts](https://github.com/BristolMyersSquibb/blockr.core/blob/676b791e7ceebf1012d9f42b4e979addccbc87b9/srcts/build/build.ts)).
The block class author guide covers writing an extension, and `inst/protocol/README.md` specifies the wire protocol, but no guide maps the client or follows its work across module boundaries.

The client already holds useful explanations in `//` comments, which TypeDoc does not read by default, and JSDoc annotations such as `@asType`, `@minimum` and `@pattern`, which `ts-json-schema-generator` reads for JSON Schemas.
Generated declarations preserve the JSDoc comments but not the surrounding `//` explanations.
A blanket conversion of those explanations into public API comments would duplicate the guides instead of explaining the architecture.

## Proposal

### One site per package

Each package keeps pkgdown as the only website generator.
Roxygen2 continues to write the R help topics that pkgdown's Reference section renders.
A package with client code generates Markdown through TypeDoc and `typedoc-plugin-markdown`, and a small build step turns that output into pkgdown articles with the YAML metadata and relative links that pkgdown needs.
No TypeDoc HTML theme or standalone TypeScript website enters the deployment.

Blockr.core's first documentation issue proves that route for `@blockr/core` before another package adopts it.
The issue succeeds when a local site build shows the R and TypeScript pages under one theme and navigation, the TypeScript pages link to one another and back to their guides, and a check of the built site finds no broken internal link in the new pages.
The issue records how the generated Markdown is wrapped, named and excluded from the R package source.
If TypeDoc's Markdown cannot preserve those links through pkgdown, the issue evaluates TypeDoc's JSON output as the input to the same pkgdown build step rather than shipping a separate site.

The generated pkgdown input is ignored by git and `.Rbuildignore`, and CI creates it afresh.
A package runs the same command for a local preview, in the reusable CI workflow's `pkgdown-dev` job and in the reusable pkgdown workflow, each of which calls it immediately before its pkgdown build.
The reusable workflows leave a package with no TypeScript entry points unchanged.
R's build and check continue to need no Node because the TypeScript build has no part in them.

The site's navigation gives the TypeScript reference and the client guide their own places beside the existing R reference, articles and migration notes.
The spike establishes their exact labels and paths once, and the shared build keeps them stable across packages.
A reader can move from a guide to the signatures it discusses and from a signature back to its source and guide.

### The TypeScript reference

Each package lists two kinds of TypeScript source entry point: the modules that core mounts, including its block, board option, plugin and output modules, and the entries whose declarations other packages import.
TypeDoc follows their re-exports, so it documents what those entries export without making every internal file an entry point.
The source entry points, not `inst/js/` or `inst/types/`, carry the `/** ... */` comments that explain an export's purpose, arguments, result, errors and examples where readers need them.

Core's current public entries are `srcts/index.ts`, `srcts/react/index.ts`, `srcts/binding/index.ts`, `srcts/controls/index.ts`, `srcts/stubs/index.ts` and `srcts/build/index.ts`.
The planned `@blockr/core/components` entry joins them when core splits its React SDK ([UI kit and design system for the client](Rewrite-1.7#work)).
The source entry points of core's mounted block, board option, plugin and output modules join them under the same rule.
The root `@blockr/core` entry is type-only, and the guides explain how a module reaches runtime behavior through `CoreApi` or its host rather than implying that an extension imports core's runtime store.
Other packages name their own entry points in their documentation build.

New documentation comments preserve the annotations from which the build generates JSON Schemas.
TypeDoc configuration recognizes or excludes those generator-specific annotations without removing them from the source.
Documentation warnings fail the documentation build, but an initial completeness gate does not require comments on every internal declaration.

### The client guides

The guides are hand-written Quarto articles under `vignettes/`, built by pkgdown beside the R and TypeScript references.
They organize a package by the directories of its TypeScript source and each directory's public entry point, which core's import rules already establish as its module boundaries.
A guide describes only the package in front of it rather than repeating core's design across every package.

Each package's guide starts with a source map that distinguishes its TypeScript source from its generated files.
It then follows the flows that best explain the package, using a sequence diagram where seeing who acts in what order helps.
Each area names its source entry points, the data it owns, its calls to other modules and the tests that show the intended behavior.
The generated reference holds signatures, so the guide links them rather than reproducing them.

Core's overview first follows three flows:

1. The page's `startPage()` sends `hello`, loads and registers the modules, opens the board, renders the frontend, starts the scheduler and starts the plugins.
2. A control or board action submits an edit, the command registry plans a batch, the store applies one step, and the scheduler revises what changed.
3. A frontend demands a block, the scheduler requests an evaluation, R replies, and core mounts the output when its readiness and on-screen rules allow one.

Later core guides cover `CoreApi` and the hosts, the store with deltas and steps, the command registry and board actions, the scheduler with the wire protocol and Shiny transport, mounting modules, core's frontend and plugins, its block and option modules, its React SDK with binding and controls, storage with logging and tracing, and its build and tests.
The guides link the design pages whose behavior they explain but take the code and tests as their source for what the implementation does.

The later package guides follow the same shape without forcing the same areas.
Blockr.dock explains its frontend, panels, views, grids and plugin mounts; blockr.graph its DAG drawing, commands and plugin state; and blockr.assistant its browser agent loop, tools and chat.
Blockr.ui explains its components, theme variables and build preset, while blockr.code and blockr.session explain their plugins and requests to R.
Each block package explains its block modules, state schemas, hosts and any requests after its block classes have moved to the new stack.

### Ownership and checks

Wrap-up owns the shared build and the new client guides.
The implementation parts keep the user guides and migration notes they already list.
The reference and client guide of a package whose implementation part starts later join Wrap-up's Work when that part starts.
An implementation change updates the affected guide and public comments in the same pull request once those pages exist.

The pull request check and the deployment workflow each build the complete site and check the internal links of the new TypeScript reference and client guides.
TypeDoc warnings and link-check failures stop both.
The first issue chooses the link checker and the paths it checks, and the reusable workflows run the same command for every package.

## Open questions

None.

<details><summary>Notes for implementers</summary>

TypeDoc supports TypeScript 6.0.x in its current 0.28 release, and `typedoc-plugin-markdown` 4.x targets TypeDoc 0.28.
TypeDoc reads `/** ... */` comments by default and follows re-exports from explicit entry points, so no `entryPointStrategy: expand` over `srcts/` is needed.
The reusable CI workflow's `pkgdown-dev` job and the reusable pkgdown workflow currently remove `vignettes/_metadata.yml` before building because of Mermaid.
They then call `pkgdown::build_site(devel = TRUE, new_process = FALSE, install = FALSE)` and `pkgdown::build_site_github_pages(new_process = FALSE, install = FALSE)`, respectively.
The TypeScript build belongs immediately before each call.

Core's `srcts/index.ts` exports the public types, and `inst/types/package.json` exposes `.`, `./binding`, `./build`, `./react`, `./stubs` and `./controls`.
The root `tsconfig.json` is a solution file that references the browser and Node projects, so the first issue chooses the TypeScript configuration that TypeDoc needs instead of assuming the root file compiles sources directly.
Each directory of `srcts/` is a module whose other callers import through its `index.ts`; the `types` and `testing` directories are exempt.
The tests in `srcts/build/build.test.ts` and `srcts/build/types.test.ts` already check generated schemas and the type package that extension builds consume.

Existing JSDoc annotations on block state feed `ts-json-schema-generator`; documentation-specific TypeDoc tags must not change the declarations or schemas that `npm run build` writes.
The documentation build never changes the generated `inst/` check that CI already runs.

</details>
