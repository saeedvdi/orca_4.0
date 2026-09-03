# Ye-Ghassemi protocol-consistency HPC package

This directory contains eleven generated Orca input files, one Slurm preload-gate script, and one Slurm full-run script. The adopted source decks are not modified.

## Important scientific status

The generated inputs use one common provisional machine stiffness:

`K_sys = 796 kN/mm = 7.96e8 N/m`.

This value is reported by Kalantar et al. (2025) for an MTS 815. It is **not** a measured stiffness for the MTS 816 used by Ye and Ghassemi (2018). The case names therefore include `commonK796`, and these runs must be described as a common-stiffness sensitivity until an MTS 816 calibration or a globally fitted value is adopted.

The generator converts the common physical stiffness to each specimen's areal penalty using `k_p=K_sys/A`. It also transforms the prescribed preload command to preserve the adopted parent's specimen displacement and spring stress at approximately 55 s. The transformed preload must still pass the supplied gate before full execution.

## Corrections represented

- All specimens use one physical `K_sys`, with only the area conversion differing.
- The piston command is constant after 55 s.
- Confinement is constant at 30 MPa.
- Figure 7 pressure histories remain the primary histories.
- SW-T2 uses the physical 31-degree Table 1 mesh. The paper's Table 2 stresses imply 30 degrees, so the existing 30-degree result remains the published-stress-reduction reference.
- All inputs request the reported 6 mm port offset. `ExtraNodesetGenerator` selects the closest existing node, so the realized offset should be checked, especially on a size-5 mesh.
- SW-S4 BB case 116_07 uses measured JRC 1.19. Case 116_09 retains effective JRC 5 under the same corrected loading and isolates the JRC effect.
- SW-T2 cases 116_10 and 116_11 retain the measured transition order but give each unloading plateau 400 s for the numerical equilibrium control.
- Selected MC values are baked into the inputs: `pb04` for SW-T1 and SW-T2, `pb06` for SW-S3, and `center` for SW-S4.

No constitutive parameters were refitted after the boundary corrections.

## Static validation

On 2026-09-02, all eleven generated decks completed `orca-opt --check-input`
with exit code 0 and `Syntax OK`.  This was a one-process parser/setup check;
no simulation timesteps were run.  The inherited `OrcaTHMaterial` deprecation
warnings do not prevent execution and are unrelated to the protocol changes.

## Files and execution order

1. Review `case_manifest.tsv`.
2. Upload this whole directory to the HPC system.
3. Run the eight short preload gates:

   ```bash
   sbatch submit_preload_gates_hpc.sh
   ```

4. Check every gate CSV before launching full simulations. At the end of the gate, confirm:

   - zero or negligible plastic slip;
   - the intended near-critical differential stress;
   - agreement between reaction stress and machine-spring stress;
   - source and outlet nodes lie on the split fracture interface.

5. If the gates pass, submit the eleven full cases:

   ```bash
   sbatch submit_protocol_consistency_11_hpc.sh
   ```

Both scripts use eight MPI ranks per case and limit the array to three simultaneous jobs.

## Regenerating with a different common stiffness

The package is reproducible. On the HPC system, regenerate the inputs from the live project decks with, for example:

```bash
python3 build_protocol_consistency_inputs.py \
  --project-root /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0 \
  --ksys-kn-per-mm 796
```

Replace `796` when an MTS 816 stiffness is selected. Regeneration overwrites only the eleven generated files in the specimen subdirectories of this package.

## Output locations

Each submit script copies the selected generated deck into the live specimen's `proposed_inputs` directory and runs it there. This keeps its `../mesh/...` reference valid. The copied filename is unique and does not replace an adopted source deck. Outputs are written below that specimen directory:

- `proposed_inputs/protocol_consistency_20260902/csv/`
- `proposed_inputs/protocol_consistency_20260902/exodus/`
- `proposed_inputs/protocol_consistency_20260902/checkpoint/`
- `proposed_inputs/protocol_consistency_20260902/logs/`

The full Slurm script disables checkpoints by default to reduce I/O, matching the recent project workflow. Remove `Outputs/chk/enable=false` if checkpoints are required.
