# Input decks restored

The `.i` decks are back in this folder, beside the outputs and submit scripts
they belong with. The `00_visualizaiton/inputs/` consolidation was undone on
2026-09-04.

Two groups deliberately stayed in `00_visualizaiton/inputs/`:

  * every SW-T1 deck, because a local SW-T1 run was in progress;
  * the analytical benchmark decks, which came from
    `Examples/Validaitons/benchmarks/` rather than from here.

Each folder carries a `mesh/` link so every deck resolves its mesh in place.
The single-specimen submit scripts were repointed back. Two orchestrators,
`run_all_main_validation_hpc.sh` and `run_rerun_failed_meshcases.sh`, still
point at the consolidated path because they drive SW-T1 as well as the others.
