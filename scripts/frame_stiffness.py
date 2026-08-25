"""The 82.5 vs 150.5 MPa/mm gap: the joint sees the machine IN SERIES with the core.

k_eff = K_sys cos^2(theta) sin(theta) / A uses the MACHINE stiffness alone. But the
deck's axial BC is a penalty spring of K_sys/A backed by an elastic core, and the
two are in series, so the stiffness the joint actually unloads against is softer.
The axial gate already knows this -- it is the C_ax term in u_cmd -- but the
stability criterion and the tau/slip identity were both written with K_sys alone.
"""
import math, sys
sys.path.insert(0, "/media/geomechanics/Data4TB/projects/orca_4.0/scripts")
import build_110_kalantar_decks as B

for name in ("OGSH", "OGSC", "OGT"):
    spec = B.SPECIMENS[name]
    th = math.radians(spec["theta"])
    penalty = B.K_SYS / B.SAMPLE_AREA                       # Pa/m
    c_ax = B.C_AX_OVER_L_OVER_E * spec["core_height"] / B.YOUNGS_MODULUS  # m/Pa
    machine = 1.0 / penalty                                 # m/Pa, series compliance
    ratio = machine / (machine + c_ax)
    k_machine = B.K_SYS * math.cos(th)**2 * math.sin(th) / B.SAMPLE_AREA / 1e9
    print(f"{spec['label']:7} core {spec['core_height']*1e3:5.0f} mm | "
          f"machine {machine:.4e} + core {c_ax:.4e} m/Pa | series = {ratio:.3f} x machine")
    print(f"{'':7} k_eff  machine-only {k_machine:6.1f}  ->  SERIES {k_machine*ratio:6.1f} MPa/mm")

print("\nOG-SH, measured across the two completed runs (rounds 3 and 4, which differ")
print("in D_c alone): tau sheds 82.5 MPa per mm of slip.")
print("  machine-only prediction 150.5  -> off by 1.82x")
print("  series prediction        88.8  -> off by 1.08x   <-- this is the model's frame")
print("\nSo the model is right about its own mechanics and the CRITERION was wrong.")
print("Table 2's own dL_s/tau identity verifies with K_sys ALONE (0.4-4 % on all three")
print("specimens), so the paper's 'K_sys' is the whole loading system, core included.")
print("The deck then adds the core's compliance a SECOND time, on top of a penalty")
print("spring already set to K_sys/A -- and the joint unloads against 0.59 of the")
print("stiffness the experiment had.")
