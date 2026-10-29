# Pages of the blockr wiki

The pages of the [blockr wiki](https://github.com/BristolMyersSquibb/blockr/wiki) live in [BristolMyersSquibb/blockr.spec](https://github.com/BristolMyersSquibb/blockr.spec): plans for changes to blockr too big for one spec, each a tree of pages from a root page through parts to the design pages that set out an API in full. The wiki is where they are read, and the repo is where they change.

## Changing a page

Every change is a pull request into `main`, which only moves through the merge queue. The queue's one required check pushes a change to the wiki before the queue merges it, so the wiki always mirrors `main`. An edit made on the wiki itself is fine too: it comes into `main` within the hour, or as soon as a queued pull request lacks it, and that pull request then goes through the queue again. The script [wiki-sync.sh](https://github.com/BristolMyersSquibb/blockr.spec/blob/main/.github/wiki-sync.sh) says how the two stay on one line of history.

Because the wiki mirrors the repo, every file in the repo also lands in the wiki's git repository, and every one in a format the wiki renders becomes a page there, this README included. So keep files other than pages in formats the wiki ignores, as the license and the scripts are.

## License

Everything here, the scripts included, is licensed under [CC BY-SA 4.0](https://github.com/BristolMyersSquibb/blockr.spec/blob/main/LICENSE): it may be shared and adapted, with credit, as long as what is adapted is shared under the same license. The license is one-way compatible with the GPL-3 of the blockr packages, so text from these pages can move into them.
