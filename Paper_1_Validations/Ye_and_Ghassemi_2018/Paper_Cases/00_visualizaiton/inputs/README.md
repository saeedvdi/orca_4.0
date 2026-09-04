# inputs — every campaign deck, stored once

`mesh/` holds one copy of every mesh. Each deck folder carries a `mesh` symlink
into it, which satisfies both the `mesh/...` and `../mesh/...` conventions the
decks use, so a deck resolves its mesh from wherever it sits here.

`used_in_paper/` — a figure or table in the manuscript or SI depends on these.
`not_used_in_paper/` — run and archived, but nothing in the current manuscript
shows their results. They are kept because they document the campaign and
because 06 is still in progress.
