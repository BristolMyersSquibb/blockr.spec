# Principles
Revised on 2026-11-02.

These principles hold for every blockr package, whichever rewrite, spec or issue changes it. A rewrite's root page holds the principles of that rewrite alone and links here for these, as it links the [glossary](Glossary) for its terms.

## Core gives a basic implementation and ways to extend it

Core implements what every board needs in a basic form, and offers ways to extend it. It does not build one solution for every case, least of all where such a solution would be expensive or cannot work in general. A case that needs more uses a way to extend core, such as a renderer of its own, a method of a coercion, a request or a block class of its own. So core's default stays simple and sensible, and core keeps no special case for what a package can do itself.

Core's table output is an example ([blockr.core#422](https://github.com/BristolMyersSquibb/blockr.core/issues/422)). It holds the names and classes of a table's columns, one page of its rows and its total row count, which may be unknown. A cell that is not a single value shows its summary, so that the table stays flat, and every other value goes to the JSON writer as it is. Core shows no column labels, no groups and no row names. A renderer that shows them asks R for them through requests of its own ([blockr.core#425](https://github.com/BristolMyersSquibb/blockr.core/issues/425#issuecomment-6579784904)), and a deployment picks that renderer for table outputs. A package whose results need another kind of table output adds a method of `as_table_output()` for their class.
