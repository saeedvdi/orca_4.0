#!/usr/bin/env python3
"""
set_hpc_resources.py -- retarget SLURM job scripts onto a new rank/memory/time budget.

WHY THIS EXISTS
===============
The 97/98 batch was truncated by a resourcing bug that no one could see in the
generated file: scripts/make_hpc_nochk_jobs.py rewrote `#SBATCH --time` and
nothing else, so decks that were meant to run 32 ranks for 24 h inherited the
template's 16 ranks and 12 h. The scripts were internally consistent and looked
fine; they were simply resourced for a different job.

The lesson is not "remember to edit four lines". It is that rank count appears
TWICE in every one of these scripts -- once in `#SBATCH --ntasks` and once in
the `srun -n` argument -- and a script in which those two disagree is not a
resourcing mistake but a silently wrong job: SLURM allocates one number and MPI
launches the other. So this module changes all of them together and then reads
its own output back to prove they agree. There is no way to call it and get a
half-retargeted script.

WHAT IT DOES NOT DO
===================
It does not touch `--nodes`. Every script in this campaign asks for `--nodes=1`,
which keeps the MPI job inside one node's memory bus and has worked at 16, 32
and 64 ranks. At 128 that still fits a standard Rorqual node (192 cores), but it
is the one assumption here that depends on the cluster rather than on the file:
if a retargeted job sits in the queue indefinitely, drop the `--nodes` line and
let SLURM place the ranks.
"""
from __future__ import annotations

import re


class ResourceMismatch(RuntimeError):
    """Raised when a retargeted script does not agree with itself."""


def retarget(text: str, ntasks: int, mem_gb: int, walltime: str) -> str:
    """Return `text` with its rank count, memory and wall time replaced.

    `ntasks` is written to both `#SBATCH --ntasks` and the `srun -n` argument.
    The result is verified before it is returned, so a caller that gets a value
    back is holding a script whose two rank counts match.
    """
    out = re.sub(r"^#SBATCH --time=.*$", f"#SBATCH --time={walltime}", text, flags=re.M)
    out = re.sub(r"^#SBATCH --ntasks=\d+\s*$", f"#SBATCH --ntasks={ntasks}", out, flags=re.M)
    out = re.sub(r"^#SBATCH --mem=\d+G\s*$", f"#SBATCH --mem={mem_gb}G", out, flags=re.M)
    # The rank count on the srun line. Anchored on `srun` so a `-n` inside a
    # deck name or a path can never be caught by accident.
    out = re.sub(r"(^srun\b[^\n]*?\s-n\s+)\d+", rf"\g<1>{ntasks}", out, flags=re.M)
    verify(out, ntasks, mem_gb, walltime)
    return out


def verify(text: str, ntasks: int, mem_gb: int, walltime: str) -> None:
    """Read a script back and check it says what it was asked to say."""
    directive = re.findall(r"^#SBATCH --ntasks=(\d+)\s*$", text, flags=re.M)
    launched = re.findall(r"^srun\b[^\n]*?\s-n\s+(\d+)", text, flags=re.M)
    memory = re.findall(r"^#SBATCH --mem=(\d+)G\s*$", text, flags=re.M)
    time = re.findall(r"^#SBATCH --time=(\S+)\s*$", text, flags=re.M)

    for label, found, want in (
        ("#SBATCH --ntasks", directive, str(ntasks)),
        ("srun -n", launched, str(ntasks)),
        ("#SBATCH --mem", memory, str(mem_gb)),
        ("#SBATCH --time", time, walltime),
    ):
        if len(found) != 1:
            raise ResourceMismatch(
                f"expected exactly one {label} line, found {len(found)}: {found}")
        if found[0] != want:
            raise ResourceMismatch(f"{label} is {found[0]}, expected {want}")

    if directive[0] != launched[0]:
        raise ResourceMismatch(
            f"SLURM would allocate {directive[0]} ranks and srun would launch "
            f"{launched[0]}; this is the 97/98 truncation bug")
