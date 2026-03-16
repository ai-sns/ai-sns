"""
Blender headless script: Retarget Mixamo animation onto a Ready Player Me (RPM) GLB model.

Handles:
  - A-pose (RPM) vs T-pose (Mixamo) rest pose differences
  - mixamorig: bone name prefix stripping
  - FBX scale normalization (100x cm->m)
  - Quaternion-safe rotation transfer with rest-pose correction
  - Robust bone matching (case-insensitive fallback)
  - Root (Hips) translation retargeting
  - Clean GLB export with baked animation

Usage:
    blender --background --python rpm_mixamo_bind.py -- \
        --rpm  <path_to_rpm.glb> \
        --anim <path_to_mixamo.fbx> \
        --output <output_path.glb>

Example:
    blender --background --python rpm_mixamo_bind.py -- \
        --rpm  cankao2/man.glb \
        --anim cankao2/Idle.fbx \
        --output cankao2/man_idle.glb

Requirements:
    Blender 3.x or 4.x with import_scene.fbx and import_scene.gltf addons enabled.
"""

import bpy
import sys
import argparse
import os
import math
from mathutils import Matrix, Quaternion, Vector


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(
        description="Retarget Mixamo animation onto an RPM GLB model"
    )
    parser.add_argument("--rpm",    required=True, help="Path to Ready Player Me .glb file")
    parser.add_argument("--anim",   required=True, help="Path to Mixamo .fbx animation file")
    parser.add_argument("--output", required=True, help="Output .glb file path")
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Scene helpers
# ---------------------------------------------------------------------------

def clear_scene():
    """Remove everything from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for col in (bpy.data.meshes, bpy.data.armatures, bpy.data.actions,
                bpy.data.materials, bpy.data.images):
        for block in list(col):
            if block.users == 0:
                col.remove(block)


def snapshot_objects():
    return set(bpy.data.objects.keys())


def new_objects(before):
    after = set(bpy.data.objects.keys())
    return [bpy.data.objects[n] for n in (after - before)]


def find_armature(objects):
    for obj in objects:
        if obj.type == 'ARMATURE':
            return obj
    return None


def deselect_all():
    bpy.ops.object.select_all(action='DESELECT')


def set_active(obj):
    bpy.context.view_layer.objects.active = obj


def enter_mode(mode):
    bpy.ops.object.mode_set(mode=mode)


# ---------------------------------------------------------------------------
# Bone / action helpers
# ---------------------------------------------------------------------------

MIXAMO_PREFIX = "mixamorig:"

def strip_prefix(name):
    return name[len(MIXAMO_PREFIX):] if name.startswith(MIXAMO_PREFIX) else name


def rename_mixamo_bones(armature):
    """Strip 'mixamorig:' prefix from bone names in edit mode."""
    set_active(armature)
    enter_mode('EDIT')
    count = 0
    for eb in armature.data.edit_bones:
        if eb.name.startswith(MIXAMO_PREFIX):
            eb.name = strip_prefix(eb.name)
            count += 1
    enter_mode('OBJECT')
    print(f"  Renamed {count} bones (stripped '{MIXAMO_PREFIX}' prefix)")


def fix_action_fcurve_paths(action):
    """Update F-curve data_paths after renaming bones."""
    if not action:
        return
    count = 0
    for fc in action.fcurves:
        if MIXAMO_PREFIX in fc.data_path:
            fc.data_path = fc.data_path.replace(MIXAMO_PREFIX, "")
            count += 1
    if count:
        print(f"  Fixed {count} F-curve paths in action '{action.name}'")


def apply_scale(obj):
    """Apply scale transform only."""
    deselect_all()
    set_active(obj)
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    deselect_all()


def normalize_mixamo_armature(armature):
    """
    Mixamo FBX imports at 100x scale (cm vs m).
    Apply ONLY the scale — never apply rotation, which can distort hand/finger axes.
    """
    scale = armature.scale
    if any(abs(s - 1.0) > 0.001 for s in scale):
        print(f"  Applying Mixamo armature scale: {tuple(round(s,3) for s in scale)}")
        apply_scale(armature)
    else:
        print(f"  Mixamo armature scale is already ~1.0, skipping apply")


# ---------------------------------------------------------------------------
# Rest-pose matrix helpers
# ---------------------------------------------------------------------------

def bone_rest_local(armature_obj, bone_name):
    """
    Return the rest-pose local matrix of 'bone_name' relative to its parent.
    This is the bone's own contribution to the armature-space matrix.
    """
    dbone = armature_obj.data.bones.get(bone_name)
    if dbone is None:
        return Matrix.Identity(4)
    if dbone.parent:
        return dbone.parent.matrix_local.inverted_safe() @ dbone.matrix_local
    return dbone.matrix_local.copy()


# ---------------------------------------------------------------------------
# Core retargeting
# ---------------------------------------------------------------------------

def retarget_animation(rpm_arm, mix_arm, shared_bones, frame_start, frame_end):
    """
    Per-frame rotation retargeting with rest-pose correction.

    For each bone B shared by both rigs, the correction quaternion C is:
        C = inv(rpm_rest_B) @ mix_rest_B

    At each frame the Mixamo pose rotation delta_m is transformed into the
    RPM bone's local space:
        delta_r = C @ delta_m @ inv(C)

    This properly accounts for A-pose vs T-pose (and any other rest-pose) differences.
    """
    print(f"  Setting all shared bones to QUATERNION rotation mode...")
    for name in shared_bones:
        for arm in (rpm_arm, mix_arm):
            pb = arm.pose.bones.get(name)
            if pb:
                pb.rotation_mode = 'QUATERNION'

    # Also ensure Hips (root) uses quaternion
    for arm in (rpm_arm, mix_arm):
        hips = arm.pose.bones.get("Hips")
        if hips:
            hips.rotation_mode = 'QUATERNION'

    # ---- Precompute per-bone correction quaternions ----
    corrections = {}
    for name in shared_bones:
        rpm_rest_q = bone_rest_local(rpm_arm, name).to_quaternion()
        mix_rest_q = bone_rest_local(mix_arm, name).to_quaternion()
        if rpm_rest_q.magnitude < 1e-6 or mix_rest_q.magnitude < 1e-6:
            print(f"    WARNING: Skipping bone '{name}' — zero-length rest quaternion")
            continue
        rpm_rest_q.normalize()
        mix_rest_q.normalize()
        # C maps RPM rest -> Mixamo rest
        corrections[name] = rpm_rest_q.inverted() @ mix_rest_q

    print(f"  Computed corrections for {len(corrections)}/{len(shared_bones)} bones")

    # ---- Ensure RPM has an action ----
    if not rpm_arm.animation_data:
        rpm_arm.animation_data_create()
    if not rpm_arm.animation_data.action:
        rpm_arm.animation_data.action = bpy.data.actions.new("RPM_Retargeted")
    rpm_action = rpm_arm.animation_data.action

    # ---- Per-frame bake ----
    set_active(rpm_arm)
    enter_mode('POSE')

    total_frames = frame_end - frame_start + 1
    report_every = max(1, total_frames // 10)

    for i, frame in enumerate(range(frame_start, frame_end + 1)):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()

        if i % report_every == 0:
            print(f"    Frame {frame}/{frame_end} ({100*i//total_frames}%)")

        # --- Root (Hips) translation ---
        rpm_hips = rpm_arm.pose.bones.get("Hips")
        mix_hips = mix_arm.pose.bones.get("Hips")
        if rpm_hips and mix_hips:
            rpm_hips.location = mix_hips.location.copy()
            rpm_hips.keyframe_insert(data_path="location", frame=frame)

        # --- Rotations ---
        for name, C in corrections.items():
            rpm_pb = rpm_arm.pose.bones.get(name)
            mix_pb = mix_arm.pose.bones.get(name)
            if rpm_pb is None or mix_pb is None:
                continue

            delta_m = mix_pb.rotation_quaternion.normalized()
            # Transform Mixamo rotation into RPM bone space
            C_inv = C.inverted()
            delta_r = C @ delta_m @ C_inv
            delta_r.normalize()

            rpm_pb.rotation_quaternion = delta_r
            rpm_pb.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    enter_mode('OBJECT')
    print(f"  Retargeting complete — {total_frames} frames baked")


# ---------------------------------------------------------------------------
# Build bone mapping (case-insensitive fallback)
# ---------------------------------------------------------------------------

def build_bone_map(rpm_arm, mix_arm):
    """
    Find bones present in both armatures.
    First try exact match, then case-insensitive fallback.
    Returns a list of canonical (RPM) bone names to retarget.
    """
    rpm_bones  = {b.name for b in rpm_arm.data.bones}
    mix_bones  = {b.name for b in mix_arm.data.bones}

    exact      = rpm_bones & mix_bones

    # Case-insensitive fallback for anything not matched exactly
    mix_lower  = {b.lower(): b for b in mix_bones}
    rpm_lower  = {b.lower(): b for b in rpm_bones}
    ci_pairs   = []   # (rpm_name, mix_name)
    for rname in rpm_bones - exact:
        mname = mix_lower.get(rname.lower())
        if mname:
            ci_pairs.append((rname, mname))

    if ci_pairs:
        print(f"  Case-insensitive extra matches: {len(ci_pairs)}")

    return list(exact), ci_pairs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    rpm_path    = os.path.abspath(args.rpm)
    anim_path   = os.path.abspath(args.anim)
    output_path = os.path.abspath(args.output)

    print("=" * 64)
    print("  RPM × Mixamo Animation Retargeter")
    print("=" * 64)
    print(f"  RPM model : {rpm_path}")
    print(f"  Animation : {anim_path}")
    print(f"  Output    : {output_path}")
    print()

    # ---- Validate inputs ----
    if not os.path.isfile(rpm_path):
        sys.exit(f"ERROR: RPM file not found: {rpm_path}")
    if not os.path.isfile(anim_path):
        sys.exit(f"ERROR: Animation file not found: {anim_path}")

    # ================================================================
    # STEP 1 — Clear scene
    # ================================================================
    print("[1/8] Clearing scene...")
    clear_scene()

    # ================================================================
    # STEP 2 — Import RPM GLB
    # ================================================================
    print("[2/8] Importing RPM GLB...")
    before = snapshot_objects()
    bpy.ops.import_scene.gltf(filepath=rpm_path)
    rpm_objects  = new_objects(before)
    rpm_armature = find_armature(rpm_objects)

    if not rpm_armature:
        sys.exit("ERROR: No armature found in RPM GLB")

    print(f"  RPM armature: '{rpm_armature.name}'  —  {len(rpm_armature.data.bones)} bones")

    # ================================================================
    # STEP 3 — Import Mixamo FBX
    # ================================================================
    print("[3/8] Importing Mixamo FBX...")
    before = snapshot_objects()
    bpy.ops.import_scene.fbx(
        filepath=anim_path,
        use_manual_orientation=False,
        global_scale=1.0,
        bake_space_transform=False,
        use_custom_normals=True,
        use_image_search=False,
        use_alpha_decals=False,
        decal_offset=0.0,
        use_anim=True,
        anim_offset=1.0,
        use_subsurf=False,
        use_custom_props=True,
        use_custom_props_enum_as_string=True,
        ignore_leaf_bones=False,
        force_connect_children=False,
        automatic_bone_orientation=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        use_prepost_rot=True,
    )
    mix_objects  = new_objects(before)
    mix_armature = find_armature(mix_objects)

    if not mix_armature:
        sys.exit("ERROR: No armature found in Mixamo FBX")

    print(f"  Mixamo armature: '{mix_armature.name}'  —  {len(mix_armature.data.bones)} bones")

    # ================================================================
    # STEP 4 — Normalize Mixamo, rename bones
    # ================================================================
    print("[4/8] Normalizing Mixamo armature & renaming bones...")

    normalize_mixamo_armature(mix_armature)

    # Grab the action BEFORE renaming so we can fix its fcurve paths
    mix_action = None
    if mix_armature.animation_data and mix_armature.animation_data.action:
        mix_action = mix_armature.animation_data.action

    rename_mixamo_bones(mix_armature)
    fix_action_fcurve_paths(mix_action)

    # Re-fetch action in case it was just assigned
    if mix_action is None:
        if mix_armature.animation_data and mix_armature.animation_data.action:
            mix_action = mix_armature.animation_data.action

    # Last resort: pick any action with fcurves
    if mix_action is None:
        for act in bpy.data.actions:
            if act.fcurves:
                mix_action = act
                break

    if mix_action is None:
        sys.exit("ERROR: No animation action found in Mixamo file")

    # Assign action to Mixamo rig
    if not mix_armature.animation_data:
        mix_armature.animation_data_create()
    mix_armature.animation_data.action = mix_action

    frame_start = int(mix_action.frame_range[0])
    frame_end   = int(mix_action.frame_range[1])
    print(f"  Action: '{mix_action.name}'  —  frames {frame_start}–{frame_end}")

    # ================================================================
    # STEP 5 — Build bone map
    # ================================================================
    print("[5/8] Building bone map...")
    exact_matches, ci_pairs = build_bone_map(rpm_armature, mix_armature)
    print(f"  Exact matches: {len(exact_matches)}")

    # For case-insensitive matches, temporarily rename Mixamo bones so the
    # retargeter can find them by the RPM canonical name.
    if ci_pairs:
        set_active(mix_armature)
        enter_mode('EDIT')
        for rpm_name, mix_name in ci_pairs:
            eb = mix_armature.data.edit_bones.get(mix_name)
            if eb:
                eb.name = rpm_name   # rename to match RPM
                exact_matches.append(rpm_name)
                # Fix fcurve paths for this bone
                for fc in mix_action.fcurves:
                    old_seg = f'bones["{mix_name}"]'
                    new_seg = f'bones["{rpm_name}"]'
                    if old_seg in fc.data_path:
                        fc.data_path = fc.data_path.replace(old_seg, new_seg)
        enter_mode('OBJECT')

    shared_bones = sorted(set(exact_matches))
    print(f"  Total bones to retarget: {len(shared_bones)}")

    if len(shared_bones) == 0:
        print("  RPM bones:", sorted(b.name for b in rpm_armature.data.bones)[:20])
        print("  Mixamo bones:", sorted(b.name for b in mix_armature.data.bones)[:20])
        sys.exit("ERROR: No matching bones found between RPM and Mixamo rigs")

    # ================================================================
    # STEP 6 — Retarget animation
    # ================================================================
    print("[6/8] Retargeting animation (per-frame sampling)...")
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end   = frame_end
    bpy.context.scene.frame_set(frame_start)
    bpy.context.view_layer.update()

    retarget_animation(rpm_armature, mix_armature, shared_bones, frame_start, frame_end)

    # ================================================================
    # STEP 7 — Clean up Mixamo objects
    # ================================================================
    print("[7/8] Removing Mixamo objects...")
    deselect_all()
    still_alive = [o for o in mix_objects if o and o.name in bpy.data.objects]
    for obj in still_alive:
        obj.select_set(True)
    if still_alive:
        bpy.ops.object.delete(use_global=False)
    print(f"  Removed {len(still_alive)} Mixamo object(s)")

    # ================================================================
    # STEP 8 — Export GLB
    # ================================================================
    print("[8/8] Exporting GLB...")

    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    bpy.ops.object.select_all(action='SELECT')

    export_kwargs = dict(
        filepath=output_path,
        export_format='GLB',
        use_selection=False,
        export_animations=True,
        export_frame_range=True,
        export_frame_step=1,
        export_force_sampling=True,   # force sampling for baked keyframes
        export_nla_strips=False,
        export_current_frame=False,
    )

    # Blender 4.x renamed some export params — try gracefully
    try:
        bpy.ops.export_scene.gltf(**export_kwargs)
    except TypeError:
        # Older Blender might not support export_force_sampling
        export_kwargs.pop("export_force_sampling", None)
        bpy.ops.export_scene.gltf(**export_kwargs)

    # ================================================================
    # Result
    # ================================================================
    if os.path.isfile(output_path):
        size_mb = os.path.getsize(output_path) / (1024 ** 2)
        print(f"\n✓ SUCCESS — {output_path}  ({size_mb:.1f} MB)")
    else:
        sys.exit("\n✗ ERROR: Output file was not created")

    print("=" * 64)
    print("Done!")
    print("=" * 64)


if __name__ == "__main__":
    main()