#!/usr/bin/env python3
"""Build the Kalantar 2025 Round-14 decks.

Round 13 settled the mechanical lever on OG-SH and refuted two hypotheses. This
round follows the surviving lever and adds one that the round-13 data exposed:
THE APERTURE LAW'S NORMAL-CLOSURE TERM IS SWITCHED OFF, AND THE GOUGE TERM HAS
BEEN ABSORBING ITS JOB.

=============================================================================
1. WHAT ROUND 13 ESTABLISHED
=============================================================================
110_38 reproduced 110_13 to every printed digit (tau 29 %, Q 9.3 %, mean 19), so
the ladder is readable against the 0.1 pp cross-machine floor.

  D_c (um)  d_s@st9   tau@st9   tau nRMSE   Q nRMSE   mean
    100       27.40    21.57       29 %      9.3 %     19
     50       60.72    16.59       24 %       13 %     19
     30       75.90    14.51       55 %       15 %     35
     15       77.79    14.26       68 %       16 %     42
  experiment  42.0     18.97

The response is linear in 1/D_c and the experiment is BRACKETED by the 100 and
50 um arms. Interpolating the two channels independently gives D_c = 69.5 um
from d_s and 65.7 um from tau. They agree, which is the reason to trust it.

REFUTED, do not re-propose:
  * Cohesion as a level knob. 110_43/110_44 raised OG-SC cohesion 0 -> 0.6 -> 1.0
    MPa and the specimen still burst at stage 6 (tau 9.11/9.16/9.20). 110_42 cut
    OG-SH cohesion to 0.6 and the joint failed during its own preload -- stage-1
    slip 31.4 um against 2.74. Under displacement control a stronger joint simply
    carries more shear stress, so cohesion moves tau and tau_limit together.
  * OG-T drainage geometry. Line-source ports (110_46) DID engage --
    inj_reaction_sum went -3.74e-9 -> -1.47e-8, a 3.9x flux increase -- and moved
    dp by +0.18 MPa. Drained platens (110_47) did nothing either. At
    k = 1.4e-20 m^2 no drainage boundary can drain this specimen on the ramp
    timescale: mid-height to platen is L^2/c = 1667 s against a 53 s ramp.

=============================================================================
2. THE NEW FINDING: THE CLOSURE TERM IS SATURATED TO ZERO
=============================================================================
Reconstructing the aperture budget stage by stage
(a_h = a_h0 + normal_stress_aperture - slip_damage, residual 0.005-0.076 um)
shows normal_stress_aperture_um_pp spans 0.0013 -> 0.0397 um across the ENTIRE
OG-SH experiment. Table 2 needs 0.61 um over the unloading branch alone.

The reason is in ADOrcaRoughnessDamageFracturePermeability::computeStressAperture:

    opening(N) = V_m * (g(ref) - g(N)),   g(s) = s^p / (sigma_0^p + s^p),
    sigma_0 = V_m * K_ni

With V_m = 1.2 um and K_ni = 1.25e13, sigma_0 = 15 MPa and p = 4. Over OG-SH's
working range of 33-43 MPa that puts g at 0.96-0.99 -- the joint sits on the flat
top of its own closure curve and cannot respond. The term is not disabled by a
flag; it is saturated by its parameters.

WHY THIS MATTERED AND WAS INVISIBLE. Table 2's aperture loss splits cleanly,
because the two branches separate the two mechanisms:

  loading   st1->st5: d_s +37 um, sigma'_n -9.64 MPa (FALLING), a_h -0.54 um
  unloading st5->st9: d_s + 3 um, sigma'_n +5.66 MPa (RISING),  a_h -0.61 um

On unloading the joint barely slips, so that 0.61 um is pure normal closure:
d(a_h)/d(sigma'_n) = -0.1078 um/MPa. On loading sigma'_n FALLS, so closure would
OPEN the joint by ~0.98 um; since a_h instead falls 0.54, gouge must supply
~1.52 um. The deck's slip_damage_scale is 1.15 um -- which is exactly Table 2's
END-TO-END loss, 4.87 -> 3.72. The calibration attributed the whole loss to gouge
because the closure term was contributing nothing, and got the ENDPOINT right
while getting the PATH wrong. A compensating error, and it is why the control
scores Q 9.3 % while every arm with more slip scores worse: raising slip exposes
the over-large gouge.

=============================================================================
3. THE FIT, AND WHAT IT CAN AND CANNOT DETERMINE
=============================================================================
Fitting the unloading branch (pure closure) and then the loading branch (gouge as
the residual):

  OG-SH   V_m = 8.0 um, sigma_0 = 24.0 MPa -> K_ni = 3.00e12   RMS 0.084 um
          gouge scale 2.85 um, characteristic slip 52.5 um     RMS 0.053 um
  OG-SC   V_m = 12.85 um, sigma_0 = 52.3 MPa -> K_ni = 4.07e12 RMS 0.067 um

HONEST LIMITS on that fit, which the arms below are built to respect:

  * V_m IS NOT WELL DETERMINED. The RMS is 0.113 at V_m = 4 um, 0.084 at 8, and
    0.078 at 30 -- essentially flat above 6 um, because g is near-linear over the
    working range and only the local slope is constrained. 8.0 um is chosen as
    the smallest value within 8 % of the asymptotic best that is also physically
    sane for a joint whose hydraulic aperture is 3.7-4.9 um. It is a CHOICE, not
    a measurement. Do not quote V_m as fitted.
  * OG-SC's GOUGE IS NOT IDENTIFIABLE and is deliberately left alone. That joint
    has d_s = 0-1 um through six stages and 20 um at one, so gouge-versus-slip has
    one usable point; a free fit runs to the grid edge (characteristic slip 1.0 um).
    The deck's own round-3 note said the same thing. Only OG-SC's closure moves.
  * The closure term can only OPEN, never close past a_h0: computeStressAperture
    clamps a negative result to zero. Both specimens work below their reference
    stress throughout, so the term is active -- but this is the third place a
    numerical guard does physical work, and it belongs in the paper's description
    of the law.

=============================================================================
4. THE ARMS
=============================================================================
OG-SH (parent 110_38, itself byte-identical to 110_13). The mechanical lever and
the aperture lever act on DIFFERENT channels -- D_c on tau and d_s, the aperture
pair on a_h and Q -- so they are given isolating arms before a combined one.
Round 13's lesson from 110_42 is that a two-parameter arm cannot be read when a
one-parameter arm has not been.

  110_48  D_c = 70 um only                    tests the round-13 interpolation
  110_49  aperture pair only, D_c = 100       tests the closure/gouge fit alone
  110_50  D_c = 70 um + aperture pair         the candidate
  110_51  D_c = 60 um + aperture pair         brackets D_c under the new gouge law,
                                              which saturates over 52.5 um instead
                                              of 15 and so changes how much slip
                                              the aperture can absorb

OG-SC (parent 110_45, the best arm of round 13 at mean 23). Its surviving lever is
slip_weakening_residual_friction_angle_degrees: 21.175 -> 22.200 moved mean 29 -> 23.
Extrapolating the unloading-branch tau needs 24.79 deg, but 22.660 is the deck's
residual_friction_angle_degrees -- the basic friction angle -- and a slip-weakening
FLOOR above the basic friction angle would mean slip strengthens the joint. So
22.660 is the physical ceiling and this round goes to it, not past it.

  110_52  slip-weakening residual -> 22.660   the ceiling; expected to fall short
  110_53  D_c 15.22 -> 40 um                  burst STABILITY, not strength level
  110_54  both

OG-SC gets no aperture arm. Its closure term was already fitted in an earlier round
(V_m = 2.6545e-6, sigma_0 = 36.36 MPa) and is live -- normal_stress_aperture spans
0.0432 -> 1.0512 um in 110_45 against OG-SH's 0.0013 -> 0.0238. THAT IS THE REAL SHAPE
OF THIS FINDING: the repair is not new, and OG-SH simply never received it.

OG-T (parent 110_36). Rounds 12 and 13 closed off ramp length and drainage
geometry. What is left is to STOP SIMULATING THE PRELOAD TRANSIENT: start from the
drained, preloaded equilibrium. Pore pressure is initialised at the production
value instead of 5 MPa, the axial stress is placed in initial_stress, and the axial
BC holds its final value from t = 0. Kalantar's specimen reached its preload
without failing, so its preload was itself drained -- this is the faithful
representation, not a shortcut.

  110_55  drained start at the deck's sigma_1 = 193.43 MPa
  110_56  drained start at sigma_1 = 185.49 MPa

WHY THE SECOND. Table 2 stage 1 gives OG-T tau = 63.21 and sigma'_n = 59.33, so
sigma_d = tau/(sin.cos) = 152.49 MPa at 28 deg and sigma_1 = 185.49 -- 7.94 MPa
below the deck's gated 193.43. That is +3.29 MPa of tau and +1.75 of sigma'_n,
which matters here because Table 2's own stage 1 already sits at
tau/sigma'_n = 1.0654, i.e. it needs a friction angle of 46.81 deg to stand up at
all. AND THAT IS THE POINT OF THIS PAIR: if the drained start still yields, the
question is whether the deck is overloaded (110_56 answers it) or whether
Kalantar's reduced stresses are themselves inconsistent -- which the reading notes
already suspect on independent grounds (the 26 deg angle that the geometry cannot
realise, and phi_r = 43.1 deg, which no granite has). A clean yield in BOTH arms
is a paper-level finding about the data, not a model failure.

Generated decks carry this builder's marker and are overwritten only if they do.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KAL = ROOT / "Examples/Kalantar2025"
SH_PARENT = KAL / "OGSH/110_38_og_sh_control_r13.i"
SC_PARENT = KAL / "OGSC/110_45_og_sc_coh0p6_swres22p2_r13.i"
OT_PARENT = KAL / "OGT/110_36_og_t_drained_preload_r12.i"
GENERATED = "GENERATED BY scripts/build_110_kalantar_round14_decks.py"
NOTE = "ROUND 14"

# ---- the fitted aperture pair -------------------------------------------------
SH_APERTURE = (
    ("bb_max_aperture_closure", "8.0e-06",
     "V_m 1.2 -> 8.0 um. sigma_0 = V_m*K_ni was 15 MPa, so g sat at 0.96-0.99 over "
     "OG-SH's 33-43 MPa range and the closure term returned 0.04 um where Table 2 "
     "needs 0.61. NOT a fitted value -- RMS is flat above V_m = 6 um; this is the "
     "smallest sane choice within 8 % of the best"),
    ("bb_initial_normal_stiffness", "3.00e+12",
     "K_ni 1.25e13 -> 3.00e12, which with V_m = 8 um puts sigma_0 at 24.0 MPa -- "
     "inside the working range instead of below it. Fitted on the unloading branch, "
     "where slip is frozen at +3 um so a_h change is pure closure. RMS 0.084 um"),
    ("slip_damage_scale", "2.85e-06",
     "1.15 -> 2.85 um. 1.15 was Table 2's END-TO-END loss 4.87 -> 3.72, assigned "
     "entirely to gouge because closure was contributing nothing. With closure "
     "restored, sigma'_n FALLS 9.64 MPa on the loading branch and would open the "
     "joint 0.98 um, so gouge must supply 1.52 um by stage 5"),
    ("slip_damage_characteristic_slip", "5.25e-05",
     "15 -> 52.5 um, fitted to the loading-branch gouge residual. RMS 0.053 um. "
     "At 15 um the gouge saturated before stage 4, which is why every round-13 arm "
     "with more slip scored WORSE on Q"),
)
# OG-SC gets NO aperture arm. Its closure was already fitted in an earlier round --
# bb_max_aperture_closure = 2.6545e-06 with sigma_0 = 36.36 MPa, RMS 25 nm over six
# slip-free stages -- and it is demonstrably live: normal_stress_aperture spans
# 0.0432 -> 1.0512 um in 110_45, against OG-SH's 0.0013 -> 0.0238. That earlier fit is
# BETTER than the one re-derived here (25 nm against 67 nm, and on stages where slip is
# genuinely zero rather than post-burst), and OG-SC's a_h channel already scores 11 %.
# Do not overwrite it. The finding of this round is that OG-SH NEVER RECEIVED THE SAME
# REPAIR, not that the repair is new.

@dataclass(frozen=True)
class Arm:
    stem: str
    parent: Path
    case_dir: str
    edits: tuple[tuple[str, str, str], ...] = ()
    rationale: str = ""
    drained_start: bool = False


DC = lambda um, why: ("characteristic_slip_distance", f"{um*1e-6:.2e}", why)

ARMS: tuple[Arm, ...] = (
    Arm("110_48_og_sh_dc70_r14", SH_PARENT, "OGSH",
        edits=(DC(70, "round 13 bracketed the answer between 100 and 50 um; d_s "
                      "interpolates to 69.5 and tau to 65.7, so 70 is the top of "
                      "the joint interval"),),
        rationale="ISOLATES the mechanical lever. Expect d_s@st9 ~ 42 um and "
                  "tau@st9 ~ 19.0. Q should stay near the control's 9.3 % or drift "
                  "slightly worse -- if it collapses, the gouge coupling is the "
                  "cause and 110_49 is the arm that says so."),
    Arm("110_49_og_sh_aperture_r14", SH_PARENT, "OGSH",
        edits=SH_APERTURE,
        rationale="ISOLATES the aperture lever at the control's D_c. tau and d_s "
                  "should barely move -- the aperture law does not feed the joint "
                  "strength -- while a_h on the unloading branch should fall 0.61 um "
                  "instead of the control's 0.029. If tau moves materially, the two "
                  "laws are coupled more than assumed and the combined arms below "
                  "cannot be read as a sum."),
    Arm("110_50_og_sh_dc70_aperture_r14", SH_PARENT, "OGSH",
        edits=(DC(70, "as 110_48"),) + SH_APERTURE,
        rationale="THE CANDIDATE. Only meaningful if 110_48 and 110_49 each behave "
                  "as predicted on their own channel."),
    Arm("110_51_og_sh_dc60_aperture_r14", SH_PARENT, "OGSH",
        edits=(DC(60, "lower bracket under the NEW gouge law"),) + SH_APERTURE,
        rationale="Brackets D_c under the restored aperture law. Gouge now saturates "
                  "over 52.5 um instead of 15, so the aperture absorbs slip "
                  "differently and the optimum D_c need not be the one interpolated "
                  "from round 13's runs."),

    Arm("110_52_og_sc_swres22p66_r14", SC_PARENT, "OGSC",
        edits=(("slip_weakening_residual_friction_angle_degrees", "22.660",
                "22.200 -> 22.660, which is this deck's own residual_friction_angle_degrees. "
                "A slip-weakening FLOOR above the basic friction angle would mean slip "
                "strengthens the joint, so this is the physical ceiling"),),
        rationale="Round 13 moved this 21.175 -> 22.200 and mean 29 -> 23. Linear "
                  "extrapolation of the unloading-branch tau asks for 24.79 deg, past the "
                  "ceiling, so this arm is EXPECTED TO FALL SHORT of the target. Its job is "
                  "to show the lever is exhausted."),
    Arm("110_53_og_sc_dc40_r14", SC_PARENT, "OGSC",
        edits=(("characteristic_slip_distance", "4.00e-05",
                "15.22 -> 40 um. The model still bursts at stage 6 (P_i = 21) where the "
                "experiment survives to stage 7 (P_i = 24). Cohesion cannot delay it "
                "(110_43/110_44 refuted). D_c sets the slip-weakening SLOPE, and a burst is "
                "the weakening slope exceeding the machine stiffness -- so raising D_c is "
                "the lever that acts on stability rather than on strength level"),),
        rationale="The OG-SH lesson applied to OG-SC. The deck's round-3 note says D_c "
                  "cannot be resolved here from the mu(s) path, and that is true -- but "
                  "burst TIMING and burst SIZE do constrain it, which is a different "
                  "argument and a legitimate one."),
    Arm("110_54_og_sc_dc40_swres22p66_r14", SC_PARENT, "OGSC",
        edits=(("characteristic_slip_distance", "4.00e-05", "as 110_53"),
               ("slip_weakening_residual_friction_angle_degrees", "22.660", "as 110_52")),
        rationale="Both. Read only after 110_52 and 110_53 have each been read alone -- "
                  "110_45 already conflated two changes and could not be attributed."),

    Arm("110_55_og_t_drained_start_r14", OT_PARENT, "OGT",
        drained_start=True,
        rationale="Drained preloaded equilibrium at the deck's gated sigma_1 = 193.43 "
                  "MPa. No ramp, so no undrained transient. Gate on dp <= 3 (it should "
                  "be ~0 by construction -- if it is not, the initial state is not an "
                  "equilibrium and the deck is wrong), then on yield and slip."),
    Arm("110_56_og_t_drained_start_t2stress_r14", OT_PARENT, "OGT",
        drained_start=True,
        edits=(("initial_stress", "'-3.3e+07 -3.3e+07 -1.8549e+08'",
                "axial component matched to the reduced sigma_1. The command and the "
                "initial stress MUST agree or step 1 is not an equilibrium and the probe "
                "measures a transient it was built to avoid"),
               ("axial_pres_final", "-4.101050e-04",
                "sigma_1 193.43 -> 185.49 MPa, recomputed through the deck's own series "
                "spring sigma_1/penalty + C_ax*(sigma_1-sigma_3) with penalty 9.6319e11 "
                "and C_ax 1.4265e-12. 185.49 is what Table 2 stage 1 implies: "
                "sigma_d = tau/(sin.cos) = 63.21/0.4145 = 152.49 at 28 deg"),),
        rationale="Separates 'the deck is overloaded by 7.94 MPa' from 'Kalantar's "
                  "reduced stresses do not stand up'. Table 2 stage 1 needs "
                  "tau/sigma'_n = 1.0654, i.e. a 46.81 deg friction angle. If BOTH "
                  "drained arms still yield, that is a finding about the data, and it "
                  "lands next to the reading notes' two existing doubts -- the 26 deg "
                  "angle the geometry cannot realise, and phi_r = 43.1 deg."),
)


def replace_assignment(text: str, key: str, value: str, why: str) -> str:
    # A deck declares a constant once at top level and then passes it into the
    # material block as "key = ${key}". Match only the declaration.
    pat = re.compile(rf"^(?P<i>[ \t]*){re.escape(key)}\s*=\s*(?P<v>[^\n#]*?)\s*(?:#.*)?$", re.M)
    hits = [m for m in pat.finditer(text) if m.group("v").strip() != "${" + key + "}"]
    if len(hits) != 1:
        raise RuntimeError(f"expected exactly one active {key!r}, found {len(hits)}")
    m = hits[0]
    return text[:m.start()] + f"{m.group('i')}{key} = {value}   # {NOTE}: {why}" + text[m.end():]


def output_bases(text: str, stem: str) -> str:
    for key, folder in (("exodus_file_base", "results_exodus_hpc"),
                        ("csv_file_base", "results_csv_hpc"),
                        ("checkpoint_file_base", "results_checkpoint_hpc")):
        text = replace_assignment(text, key, f"{folder}/{stem}_hpc", "self-named output")
    return text


def drained_start(text: str) -> str:
    """Start from the drained, preloaded equilibrium instead of ramping into it."""
    # 1. pore pressure starts at the production value, not 5 MPa
    pat = re.compile(r"(type = ConstantIC\s*\n\s*variable = pore_pressure\s*\n\s*)value = [^\n]*")
    if not pat.search(text):
        raise RuntimeError("cannot find the pore-pressure ConstantIC")
    text = pat.sub(rf"\g<1>value = ${{production_pressure}}   # {NOTE}: drained start -- "
                   f"the specimen begins in pore-pressure equilibrium at the production "
                   f"value, not 2 MPa above it", text, count=1)
    # 2. the axial stress is already there at t = 0
    text = replace_assignment(
        text, "initial_stress", "'-3.3e+07 -3.3e+07 -1.9343e+08'",
        "axial component set to the preloaded sigma_1 so the specimen STARTS loaded. "
        "Rounds 12 and 13 proved no ramp length and no drainage boundary can drain "
        "k = 1.4e-20 m^2 in the loading time; the remaining honest option is not to "
        "simulate the preload transient at all")
    # 3. no ramp: hold the final command from t = 0
    pat = re.compile(r"expression = 'if\(t<2\.0,[^']*'\s*(?:#[^\n]*)?")
    if not pat.search(text):
        raise RuntimeError("cannot find the axial_disp_ramp expression")
    text = pat.sub(f"expression = '${{axial_pres_final}}'   # {NOTE}: no ramp -- the axial "
                   f"command is held at its preloaded value from t = 0", text, count=1)
    # 4. axial_pres_initial is now orphaned -- the ramp that referenced it is gone, and
    #    MOOSE errors on an unused top-level parameter. Drop the declaration.
    pat = re.compile(r"^[ \t]*axial_pres_initial[ \t]*=[^\n]*\n", re.M)
    if len(pat.findall(text)) != 1:
        raise RuntimeError("expected exactly one axial_pres_initial declaration")
    text = pat.sub("", text, count=1)
    if "axial_pres_initial" in text:
        raise RuntimeError("axial_pres_initial is still referenced somewhere")

    # 5. short probe
    text = replace_assignment(text, "end_time", "600",
                              "600 s probe: long enough to show the state is an equilibrium "
                              "and that pore pressure stays at the production value")
    text = re.sub(r"time_t = '[^']*'[^\n]*",
                  f"time_t = '0.0 0.5 2.0 600.0'   # {NOTE}: drained-start probe", text)
    text = re.sub(r"time_dt = '[^']*'[^\n]*",
                  f"time_dt = '0.10 0.10 5.00 5.00'   # {NOTE}: fine first steps to settle "
                  f"the initial state, then coarse", text)
    text = replace_assignment(text, "dtmax", "5.0", "segment limits govern")
    text = re.sub(r"(\[injection_pressure\](?:(?!\[\]).)*?)x = '[^']*'[^\n]*",
                  rf"\g<1>x = '0.0 600.0'   # {NOTE}: preload probe, no injection schedule",
                  text, count=1, flags=re.S)
    text = re.sub(r"(\[injection_pressure\](?:(?!\[\]).)*?)y = '[^']*'[^\n]*",
                  rf"\g<1>y = '3000000.0 3000000.0'   # {NOTE}: held at production_pressure",
                  text, count=1, flags=re.S)
    text = re.sub(r"(\[event_dt_cap\](?:(?!\[\]).)*?)x = '[^']*'[^\n]*",
                  rf"\g<1>x = '0 2.0'   # {NOTE}: no event to resolve", text, count=1, flags=re.S)
    text = re.sub(r"(\[event_dt_cap\](?:(?!\[\]).)*?)y = '[^']*'[^\n]*",
                  rf"\g<1>y = '5.0 5.0'   # {NOTE}: see x", text, count=1, flags=re.S)
    return text


def banner(arm: Arm) -> str:
    L = ["#" * 78, f"# {arm.stem}", f"# {GENERATED}  -- do not hand-edit; regenerate instead.",
         f"# Parent: {arm.parent.relative_to(ROOT)}", "#"]
    if arm.drained_start:
        L += ["#   DRAINED START: pore pressure at production_pressure, axial stress in",
              "#   initial_stress, axial command held from t = 0. No preload ramp.", "#"]
    for k, v, why in arm.edits:
        L += [f"#   {k} = {v}", f"#       {why}"]
    L += ["#", f"# {arm.rationale}", "#" * 78, ""]
    return "\n".join(L)


def build(arm: Arm) -> Path:
    text = arm.parent.read_text()
    if arm.drained_start:
        text = drained_start(text)
    for k, v, why in arm.edits:
        text = replace_assignment(text, k, v, why)
    text = output_bases(text, arm.stem)
    out = KAL / arm.case_dir / f"{arm.stem}.i"
    if out.exists() and GENERATED not in out.read_text():
        raise RuntimeError(f"{out} exists and is not ours; refusing to overwrite")
    out.write_text(banner(arm) + text)
    return out


def main() -> int:
    for a in ARMS:
        print(f"wrote {build(a).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
