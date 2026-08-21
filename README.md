# Orca 4.0

Orca is a MOOSE-based application used here to reproduce the Ye and Ghassemi (2018)
hydraulic-shearing experiments.

## Current comparison and ranking

The analysis is current through 2026-08-20. The material-property comparison covers all 166
top-level sample decks, and the input coverage index also classifies the repository's eight
software-verification inputs (174 `.i` files total). Every one of the 111 available campaign result CSVs is indexed: 64 complete monotonic cases
are ranked, 15 incomplete monotonic cases are retained but excluded from ranking, and the remaining
32 files are discussion controls, superseded/retired runs, a duplicate, or derived summaries.
Sixty decks have no result CSV and therefore cannot be scored.

Authoritative outputs:

- `doc/independent_analysis/INPUT_DECK_MATERIAL_PROPERTY_COMPARISON_2026-08-18.md`
- `doc/independent_analysis/TABLE2_ERROR_ACCURACY_RANKING.csv`
- `doc/independent_analysis/INPUT_DECK_ANALYSIS_COVERAGE.csv`
- `doc/independent_analysis/RESULT_FILE_ANALYSIS_COVERAGE.csv`
- `doc/independent_analysis/CONSOLIDATED_ANALYSIS_2026-08-18.md`

Rebuild and verify them from the repository root:

```bash
PYTHONPATH=../moose/python /home/geomechanics/miniforge/envs/moose/bin/python3.14 \
  scripts/generate_input_deck_property_comparison.py
python scripts/update_table2_ranking.py --write
python scripts/analyze_101.py
python scripts/audit_analysis_coverage.py
```

The four completed SW-S4 101-series controls are deliberately marked qualified: their
preregistered check detected slip before injection, so they require redesigned reruns before they
can support an unqualified cyclic or shut-in conclusion.

For general MOOSE setup, see the
[MOOSE new-user guide](https://mooseframework.inl.gov/getting_started/new_users.html#create-an-app).

## HPC batch submission

From the YeGhasemmi2018 example directory, submit an explicitly selected series, for example:

```bash
cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018
for f in SW*/101_0*_hpc_nochk.sh; do
    echo "Submitting $f"
    sbatch "$f"
done
```
