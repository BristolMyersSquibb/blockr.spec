# The conversion and the migration notes
Status: review. Part of [State in JS](Rewrite-1).

This part covers blockr.convert, a package of its own that turns each file of today's stack into a JSON board once, and the migration notes that each package writes for the app scripts that call it, which the switch waits for.
It builds on [Serialization](Rewrite-1.1.4#files), which says what the conversion writes, and on every part whose package wrote today's files or exports what app scripts call, each of which gives its own methods and notes.

## Problem
No file that today's stack saved opens in the new one.
Such a file names the R class of every object and the constructor that rebuilds it, with its package and that package's version, and holds typedjson's tags where plain JSON cannot say a type, while the client opens JSON boards alone and R opens none ([Serialization](Rewrite-1.1.4#files)).
So each file needs one conversion, in R, by the `blockr_deser()` methods of the packages that wrote it, of which the workspace's packages register 35 on main: 11 in blockr.core, 16 in blockr.dplyr, 7 in blockr.dock and one in blockr.assistant.

What the conversion does is settled in pieces, by [Serialization](Rewrite-1.1.4#files) for core's objects, [Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today) for extensions and [Saved boards and app scripts across the switch](Rewrite-1.2.2) for the dock.
The package that runs it has four sentences in the Migration of [State in JS](Rewrite-1#migration) and no page, so none says what a user calls, how a package's methods reach blockr.convert, or what its tests hold.
Nor does any page say how the records that blockr.session stores today cross, while [Session management as a storage plugin](Rewrite-1.6) has the browser read the pin bundles of records saved today, which hold files that only R converts.

Every app script changes at the switch too, and 89 R scripts and 8 documents in 15 of the workspace's repos call `serve()`, in examples, vignettes, READMEs and dev scripts.
Each package's migration notes, a vignette, say what a script changes ([State in JS](Rewrite-1#migration)), but only blockr.core's ([blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445)) and blockr.dock's ([Client-drawn dock](Rewrite-1.2#work)) are planned.
Scripts also pass the extensions of blockr.dag, blockr.md and blockr.assistant, and of blockr.outline and blockr.viz outside the workspace, as the clinical data explorer's board does, and the plugins of blockr.session and blockr.code, whose packages plan no notes.
Only the dock checks its notes, by opening each example's script, changed as they say, beside the conversion of the file that the script saved ([Saved boards and app scripts across the switch](Rewrite-1.2.2#testing)), so for every other package a change that no note lists shows only when a script fails after the switch.

## What must hold

1. Every file that today's packages open converts once, through blockr.convert, into a JSON board, which opens with the same blocks, links, stacks, board option values and plugins' state, for the block classes and plugin classes that have been ported, as condition 4 of [State in JS](Rewrite-1#what-must-hold) asks.
2. Converting a file runs nothing that the file holds, so that a crafted file runs no code in the session that converts it ([Serialization](Rewrite-1.1.4#files)).
3. No package but blockr.convert holds code that reads today's files.
4. A record that blockr.session stored today opens in an app of the new stack for the user who stored it, and so does a file of today's stack that a user uploads to it.
5. A conversion leaves the file it reads as it was, so that the file converts again once the converting session has what it lacked.
6. Every package whose functions app scripts call, and which the switch changes, has migration notes, a vignette, that list each change a script needs, written so that an AI can apply them ([State in JS](Rewrite-1#migration)).
7. The examples of each such package and the clinical data explorer's board, with their scripts changed by an AI that is given nothing but the migration notes, open into the same board as the conversion of the files that their scripts saved before the change, as [Saved boards and app scripts across the switch](Rewrite-1.2.2#what-must-hold) asks of the dock's.

## Today

Today's blockr.core writes a file with `blockr_ser()` and reads one with `blockr_deser()`, a generic to which the packages that write files add their methods ([R/utils-serdes.R#L285-L559](https://github.com/BristolMyersSquibb/blockr.core/blob/5abaa52bc04bf202dab9c6e17772f2a170b10a38/R/utils-serdes.R#L285-L559)).
Its method for a list dispatches on the class vector that the file records for each object, and its method for a block calls the block's constructor with the args that the file holds ([#L291-L359](https://github.com/BristolMyersSquibb/blockr.core/blob/5abaa52bc04bf202dab9c6e17772f2a170b10a38/R/utils-serdes.R#L291-L359)).
The method for a constructor stops with `blockr_deser_missing_pkg` where the constructor's package is not installed, and unserializes a constructor that the file holds as a closure ([#L518-L538](https://github.com/BristolMyersSquibb/blockr.core/blob/5abaa52bc04bf202dab9c6e17772f2a170b10a38/R/utils-serdes.R#L518-L538)).
A block that cannot be rebuilt stops the whole read, unless the blockr option `deser_on_error` is `"drop"`, which drops the block and logs a warning ([#L363-L398](https://github.com/BristolMyersSquibb/blockr.core/blob/5abaa52bc04bf202dab9c6e17772f2a170b10a38/R/utils-serdes.R#L363-L398)).
On `js-state`, blockr.core has no `blockr_deser()` any more.

Today's files come from core's Export, the dock's Import and Export, and blockr.session, which stores each board as a pin, under the visitor's own account on Connect ([Session management as a storage plugin](Rewrite-1.6)).
Today's files are read with typedjson's `json_read()` and `json_read_str()`, whose `code` is `TRUE` by default, while `code = FALSE` came after its release 0.1.2 ([nbenn/typedjson#122](https://github.com/nbenn/typedjson/pull/122)).

## Proposal

### The package

The package blockr.convert depends on the new blockr.core, whose `blockr_ser()` writes a JSON board from the R board that `blockr_deser()` builds ([Serialization](Rewrite-1.1.4#files)), and on a release of typedjson after 0.1.2, whose readers take `code = FALSE`.
It holds the generic `blockr_deser()` with the methods of every package that wrote today's files, which leave those packages (condition 3), and one function:

```r
convert_file(path, out = NULL)   # converts the file of today's stack at `path` into a JSON board, which it writes to `out`, or returns as text where `out` is NULL
```

The function reads the file with typedjson in the mode that refuses code (condition 2), and loads the namespace of each package that the file's constructors name, whose classes the methods build (below).
Then `blockr_deser()` builds the R board, and `blockr_ser()` writes it as a JSON board, as [Serialization](Rewrite-1.1.4#files) has it: each block at the version of its class's state, and the state of each plugin at version 1, in the shape that its class starts the new stack with.
It refuses an `out` that names `path`, so that a file stays as it was (condition 5).
Core's method for a constructor leaves a closure unread, rather than unserialize it, so that a block whose class a script defined keeps the name that the file records as its registry id ([Board objects](Rewrite-1.1.1#block-classes-outside-a-package)).

### The methods of other packages

The methods of the other packages that wrote today's files move into blockr.convert as well, so that none of those packages keeps code for today's files (condition 3).
On main, those are blockr.dplyr's 16, blockr.assistant's one and blockr.dock's 7, which build the dock plugin's state and the plugins that take the place of today's extensions ([Saved boards and app scripts across the switch](Rewrite-1.2.2#the-dock-board)).
The method for each extension that a plugin takes the place of makes the plugin from the extension's state, with the constructor of the plugin's class: that of blockr.dag for the DAG, of blockr.assistant for the assistant, which takes none of the threads, as [The assistant's state](Rewrite-1.4.3#boards-saved-today) has it, and of blockr.md for its documents ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)).

### What a session cannot rebuild

Where the converting session cannot rebuild an object, since the package that the file names is not installed or blockr.convert has no method for it, the conversion leaves the object out, as [Saved boards and app scripts across the switch](Rewrite-1.2.2#extensions) has it for an extension.
It leaves out with a block the links that end at it and its place in a stack.
It names every object that it leaves out in one warning, with its class and its package, rather than stopping at the first, as today's `blockr_deser()` does, so that a user installs what the warning names and converts the file again (condition 5).

### Who converts

A user converts a file that they downloaded from an app of today's stack once, with `convert_file()`, and opens the JSON board in an app of the new stack, and so does a deployer with the file that `serve()` is given.
The client and `serve()` refuse a file without a `format` with an error that names `convert_file()`, since they tell such a file apart ([Serialization](Rewrite-1.1.4#files)), while core converts nothing (condition 3).

The storage plugin of blockr.session converts each record that blockr.session stored today as it opens the record, and each file of today's stack that a user uploads (condition 4), since the records sit under each visitor's own account on Connect, where no pass of a deployer's reaches them all ([Session management as a storage plugin](Rewrite-1.6)).
Where a record's board has no `format`, the plugin sends it to R in a request of its class, which R answers with `convert_file()` on the request's body ([Plugins](Rewrite-1.1.12#a-plugins-requests)), and opens the JSON board that comes back, while the record gains a version in the new format only when the user saves the board.
The warning of a conversion that leaves objects out reaches the user as a notification, as every warning that R raises does ([Notifications, logging and tracing](Rewrite-1.1.14)).
So blockr.session imports blockr.convert, and every app that may open a record saved today can convert it.

### The migration notes

Each package whose functions app scripts call, and which the switch changes, writes migration notes, a vignette, which list each change of a script, with what takes the place of each function that goes, written so that an AI can apply them ([State in JS](Rewrite-1#migration)).
They are Work on the part of each package: blockr.core's ([blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445)), blockr.dock's ([Client-drawn dock](Rewrite-1.2#work)), blockr.dag's ([Client-drawn DAG](Rewrite-1.3#work)), blockr.assistant's ([Assistant as a plugin](Rewrite-1.4#work)), blockr.code's ([Code export as a plugin](Rewrite-1.5#work)) and blockr.session's ([Session management as a storage plugin](Rewrite-1.6#work)), and each block package's as it is ported.
The package blockr.md has no part yet, so its notes wait for one, and the notes of blockr.outline and blockr.viz, outside the workspace, are their maintainers' to write.

### Testing

The tests of blockr.convert hold, for each package that wrote today's files, a file of each of its examples, written by main at the switch, and a file of the clinical data explorer's board, each beside the JSON board that the conversion writes for it, as [Saved boards and app scripts across the switch](Rewrite-1.2.2#testing) has them for the dock.
The script of each such example is changed for the new stack by an AI that is given nothing but the migration notes of the packages that it calls, and the tests open the board that the changed script builds and the conversion of the file that the unchanged script saved in the client, after the migrations of their classes, and check that they are the same board (condition 7).
A difference names a change that the notes lack, so the notes gain it and the AI changes the script again, rather than someone fixing the script by hand.
The tests also convert a crafted file whose tags would make a call under typedjson's default, which the conversion refuses (condition 2), and a file that names a package that the session lacks, whose objects the conversion leaves out and names (above).

### What does not cross

- A file of blockr.dock 0.1.0, which today's dock does not open either ([Saved boards and app scripts across the switch](Rewrite-1.2.2#which-files-cross)).
- An extension that an app script defined with `new_dock_extension()`, since a plugin class comes from a package ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)).
- A block of a class that a script defined, which opens only where a class of the name that it keeps is registered ([Board objects](Rewrite-1.1.1#block-classes-outside-a-package)).

## Open questions

None.

## Work

- Create blockr.convert, with `blockr_deser()` and the methods of blockr.core's main, and `convert_file()`, which reads a file of today's stack with typedjson in the mode that refuses code and writes its JSON board with `blockr_ser()`, with a README on converting a file, in blockr.convert
- Convert a dock board, with the methods of blockr.dock's main for the dock board, its stacks and the Edit board extension, which write the dock plugin's state at version 1 ([Saved boards and app scripts across the switch](Rewrite-1.2.2#the-dock-board)), in blockr.convert
- Refuse a file without a `format`, in the client and in `serve()`, with an error that names blockr.convert's `convert_file()`, in blockr.core
- Carry over the methods of `blockr_deser()` of blockr.dplyr's main, and write those that make the plugins of the DAG, the assistant and blockr.md from today's extensions, in blockr.convert
- Write the test files of every package that wrote today's files and of the clinical data explorer's board, from main at the switch, and the check that each example's script, changed by an AI from the migration notes alone, opens into the same board as the conversion of its file, in blockr.convert

<details><summary>Notes for implementers</summary>

Today's code, at `5abaa52`: the generic and core's methods are `R/utils-serdes.R`, with `deser_kind()`, which finds the kind of object that a class vector names, `deser_or_drop()` and `resolve_deser_on_error()`, while `blockr_ser.blockr_ctor()` writes each constructor's name, package and version ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/5abaa52bc04bf202dab9c6e17772f2a170b10a38/R/utils-serdes.R#L124-L142)), which give the packages whose namespaces the conversion loads.

Typedjson's readers on its main, at `b9d920a`, are `json_read(path, code = TRUE)` and `json_read_str(txt, code = TRUE)`, so blockr.convert pins typedjson's main in `Remotes` until the release after 0.1.2.

The tests can open the JSON boards in core's `CoreApi` for tests, where a test registers the block classes and plugin classes that it needs ([Plugins](Rewrite-1.1.12#testing)).
A request's body reaches R's function as a file, in `file`, which the request of blockr.session's plugin hands to `convert_file()` with `out = NULL` ([Plugins](Rewrite-1.1.12#a-plugins-requests)).

A deployment's skills change at the switch too, so blockr.assistant's migration notes list what a skill changes, beside what an app script changes ([The assistant's tools](Rewrite-1.4.2#the-requests-in-r)):

- The tools that its text names, where today's go, such as `commit`, `modify_block` and `list_views` ([The assistant's tools](Rewrite-1.4.2#today)).
- The block classes that it names in `blocks:`, by registry id in full, such as `blockr.dplyr-filter_block` in place of today's `filter_block`.
- The plugin classes that it names in `plugins:`, by their ids, in place of today's `extensions:`.

The clinical data explorer's skills are the case: seven of their files name today's tools, and two of its skills name block classes in `blocks:`.

</details>
