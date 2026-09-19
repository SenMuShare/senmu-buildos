#!/usr/bin/env bash
# Governed, reproducible release assets only; not a general file/container prune.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
project_root="$(cd "${RETENTION_PROJECT_ROOT:-$script_dir/../..}" && pwd -P)"
config_input="${1:-$project_root/operations/release-retention.env}"
mode="${2:-dry-run}"
status=blocked
artifact_planned=0; artifact_removed=0; artifact_kept=0
image_planned=0; image_removed=0; image_kept=0; image_unowned=0; attempted=0
scratch=
finish() {
  code=$?
  trap - EXIT
  if [[ "$code" != 0 ]]; then
    status=blocked
    if (( attempted > 0 )); then status=failed; fi
  fi
  printf 'release_retention_status=%s mode=%s artifacts_kept=%s artifacts_planned=%s artifacts_removed=%s images_kept=%s images_planned=%s images_removed=%s images_unowned=%s space_reclaimed=not_measured image_count_unit=references\n' \
    "$status" "$mode" "$artifact_kept" "$artifact_planned" "$artifact_removed" "$image_kept" "$image_planned" "$image_removed" "$image_unowned"
  # Only this invocation's disposable inventory files, never user resources.
  if [[ -n "$scratch" ]]; then
    rm -f "$scratch"/*
    rmdir "$scratch"
  fi
  exit "$code"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
fail() { echo "$*" >&2; exit 2; }
[[ "$mode" == dry-run || "$mode" == apply ]] || fail "Usage: $0 [config] [dry-run|apply]"
[[ -f "$config_input" && ! -L "$config_input" ]] || fail "Missing or linked retention config."
config_dir="$(cd "$(dirname "$config_input")" && pwd -P)"
config="$config_dir/$(basename "$config_input")"
case "$config" in "$project_root"/*) ;; *) fail "Retention config must stay inside project root." ;; esac

ARTIFACT_CLEANUP_ENABLED=0; ARTIFACT_ROOT=; CURRENT_ARTIFACT=; PREVIOUS_ARTIFACT=; PINNED_ARTIFACTS=
DOCKER_IMAGE_CLEANUP_ENABLED=0; MANAGED_IMAGE_REPOSITORIES=; CURRENT_IMAGES=; PREVIOUS_IMAGES=; PINNED_IMAGES=
DOCKER_CONTEXT=; RESOURCE_SURFACE=unspecified
seen='|'
while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line%$'\r'}"
  [[ -z "$line" || "$line" == \#* ]] && continue
  [[ "$line" =~ ^([A-Z][A-Z0-9_]*)=(.*)$ ]] || fail "Invalid retention config assignment."
  key="${BASH_REMATCH[1]}"; value="${BASH_REMATCH[2]}"
  case "$key" in
    ARTIFACT_CLEANUP_ENABLED|ARTIFACT_ROOT|CURRENT_ARTIFACT|PREVIOUS_ARTIFACT|PINNED_ARTIFACTS|DOCKER_IMAGE_CLEANUP_ENABLED|MANAGED_IMAGE_REPOSITORIES|CURRENT_IMAGES|PREVIOUS_IMAGES|PINNED_IMAGES|DOCKER_CONTEXT|RESOURCE_SURFACE) ;;
    *) fail "Unsupported retention config key: $key" ;;
  esac
  case "$seen" in *"|$key|"*) fail "Duplicate retention config key: $key" ;; esac
  seen="${seen}${key}|"
  # Data assignment, never source/eval: spaces and non-ASCII paths are allowed.
  printf -v "$key" '%s' "$value"
done < "$config"
case "$ARTIFACT_CLEANUP_ENABLED:$DOCKER_IMAGE_CLEANUP_ENABLED" in 0:0|0:1|1:0|1:1) ;; *) fail "Cleanup enable flags must be 0 or 1." ;; esac
printf 'resource_surface=%s\n' "$RESOURCE_SURFACE"
if [[ "$ARTIFACT_CLEANUP_ENABLED:$DOCKER_IMAGE_CLEANUP_ENABLED" == 0:0 ]]; then
  status=disabled
  echo 'reason=cleanup_not_configured_or_enabled'
  exit 0
fi
[[ "$mode" != apply || "${RELEASE_CLOSEOUT_AUTHORIZED:-0}" == 1 ]] || fail "Apply requires RELEASE_CLOSEOUT_AUTHORIZED=1 after target release validation."
scratch="$(mktemp -d)"
: > "$scratch/artifacts"; : > "$scratch/images"

if [[ "$ARTIFACT_CLEANUP_ENABLED" == 1 ]]; then
  command -v python3 >/dev/null || fail "Python 3 is required for artifact boundary checks."
  # Inspect all descendants before any delete. The reusable generated template
  # cannot assume that a directory name proves ownership or excludes a nested repo.
  cat > "$scratch/check_artifacts.py" <<'PY'
import hashlib, json, os, stat, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
relative, current, previous, pins = sys.argv[2:6]
parts = Path(relative).parts
if not relative or Path(relative).is_absolute() or '..' in parts or relative in ('.', ''):
    raise SystemExit('Artifact root must be a strict project-relative directory.')
base = root / relative
for p in (base, *base.parents):
    if p == root: break
    if p.is_symlink(): raise SystemExit('Linked artifact root is not eligible.')
    if p.name == '.git' or ((p / 'HEAD').is_file() and (p / 'objects').is_dir() and (p / 'refs').is_dir()):
        raise SystemExit('Artifact root is inside Git metadata; retain all resources.')
if not base.is_dir() or not base.resolve().is_relative_to(root) or base.resolve() == root:
    raise SystemExit('Artifact root is missing or outside project scope.')
keep = [current] + ([previous] if previous else []) + ([p for p in pins.split(',') if p] if pins else [])
if not current or any(not x or '/' in x or '\\' in x or x in ('.', '..') for x in keep):
    raise SystemExit('Current, rollback and pinned artifacts must be direct child names.')
if any(not (base / x).is_dir() or (base / x).is_symlink() for x in keep):
    raise SystemExit('Required current, rollback or pinned artifact is missing or linked.')
seen = 0
identity = hashlib.sha256()
candidates = []
for child in sorted(base.iterdir()):
    if child.is_symlink(): raise SystemExit('Linked artifact entry requires separate review.')
    if not child.is_dir(): continue
    if child.name in keep:
        print('kept_artifact=' + child.name, file=sys.stderr)
        continue
    device = base.stat().st_dev
    for directory, dirs, files in os.walk(child, followlinks=False, onerror=lambda e: (_ for _ in ()).throw(e)):
        dirs.sort(); files.sort()
        d = Path(directory)
        names = set(dirs + files)
        if '.git' in names or d.name == '.git' or {'HEAD', 'objects', 'refs'}.issubset(names):
            raise SystemExit('Repository metadata inside artifact; retain the entire candidate.')
        for p in (d, *(d / name for name in dirs + files)):
            seen += 1
            if seen > 100000: raise SystemExit('Artifact inspection incomplete: entry budget exceeded.')
            st = p.lstat()
            identity.update(json.dumps([str(p.relative_to(root)), st.st_dev, st.st_ino, st.st_mode, st.st_size, st.st_mtime_ns, st.st_ctime_ns]).encode())
            if stat.S_ISLNK(st.st_mode) or st.st_dev != device or os.path.ismount(p):
                raise SystemExit('Link or mount boundary inside artifact; retain the entire candidate.')
            if not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):
                raise SystemExit('Special resource inside artifact; retain the entire candidate.')
    candidates.append(str(child))
Path(sys.argv[6]).write_bytes(b''.join(os.fsencode(p) + b'\0' for p in candidates))
Path(sys.argv[6] + '.identity').write_text(identity.hexdigest())
print(len(set(keep)))
PY
  artifact_kept="$(python3 "$scratch/check_artifacts.py" "$project_root" "$ARTIFACT_ROOT" "$CURRENT_ARTIFACT" "$PREVIOUS_ARTIFACT" "$PINNED_ARTIFACTS" "$scratch/artifacts")" || fail "Artifact inspection failed; nothing was deleted."
  while IFS= read -r -d '' candidate; do
    artifact_planned=$((artifact_planned + 1))
    printf 'would_remove_artifact=%s\n' "$(basename "$candidate")"
  done < "$scratch/artifacts"
fi

if [[ "$DOCKER_IMAGE_CLEANUP_ENABLED" == 1 ]]; then
  command -v docker >/dev/null || fail "Docker is required for image cleanup."
  docker_cmd=(docker)
  if [[ -n "$DOCKER_CONTEXT" ]]; then docker_cmd+=(--context "$DOCKER_CONTEXT"); fi
  # Record the actual engine; a receipt from this target never closes another host.
  actual_context="$("${docker_cmd[@]}" context show)" || fail "Cannot inspect Docker context."
  daemon_id="$("${docker_cmd[@]}" info --format '{{.ID}}')" || fail "Cannot inspect Docker engine identity."
  [[ -n "$daemon_id" ]] || fail "Docker engine identity is empty."
  printf 'docker_context=%s docker_engine_id=%s\n' "$actual_context" "$daemon_id"
  managed_repositories=(); current_images=(); previous_images=(); pinned_images=()
  [[ -z "$MANAGED_IMAGE_REPOSITORIES" ]] || IFS=',' read -r -a managed_repositories <<< "$MANAGED_IMAGE_REPOSITORIES"
  [[ -z "$CURRENT_IMAGES" ]] || IFS=',' read -r -a current_images <<< "$CURRENT_IMAGES"
  [[ -z "$PREVIOUS_IMAGES" ]] || IFS=',' read -r -a previous_images <<< "$PREVIOUS_IMAGES"
  [[ -z "$PINNED_IMAGES" ]] || IFS=',' read -r -a pinned_images <<< "$PINNED_IMAGES"
  (( ${#managed_repositories[@]} > 0 && ${#current_images[@]} > 0 )) || fail "Managed repositories and current images are required."
  : > "$scratch/keep_refs"; : > "$scratch/keep_ids"; : > "$scratch/container_ids"
  required_images=("${current_images[@]}")
  [[ -z "$PREVIOUS_IMAGES" ]] || required_images+=("${previous_images[@]}")
  [[ -z "$PINNED_IMAGES" ]] || required_images+=("${pinned_images[@]}")
  for image in "${required_images[@]}"; do
    managed=0
    for repository in "${managed_repositories[@]}"; do
      [[ -n "$repository" && "$repository" != -* && "$repository" != *[[:space:]]* ]] || fail "Invalid managed repository."
      [[ "$image" == "$repository":* || "$image" == "$repository"@* ]] && managed=1
    done
    [[ "$managed" == 1 ]] || fail "Required image is outside managed repositories."
    image_id="$("${docker_cmd[@]}" image inspect --format '{{.Id}}' "$image")" || fail "Required current, rollback or pinned image is missing: $image"
    [[ -n "$image_id" ]] || fail "Required image has no identity."
    printf '%s\n' "$image" >> "$scratch/keep_refs"
    printf '%s\n' "$image_id" >> "$scratch/keep_ids"
  done
  "${docker_cmd[@]}" ps -a --format '{{.Image}}' > "$scratch/container_refs" || fail "Cannot enumerate container image references."
  "${docker_cmd[@]}" ps -aq > "$scratch/containers" || fail "Cannot enumerate containers."
  while IFS= read -r container_id; do
    [[ -n "$container_id" ]] || continue
    "${docker_cmd[@]}" inspect --format '{{.Image}}' "$container_id" >> "$scratch/container_ids" || fail "Cannot inspect a container reference."
  done < "$scratch/containers"
  for repository in "${managed_repositories[@]}"; do
    # Do not hide producer failures in process substitution: failed is not empty.
    "${docker_cmd[@]}" image ls --no-trunc "$repository" --format '{{.Repository}}:{{.Tag}}|{{.ID}}' > "$scratch/listing" || fail "Cannot enumerate managed images."
    while IFS='|' read -r ref image_id; do
      [[ -n "$ref" ]] || continue
      [[ -n "$image_id" ]] || fail "Image listing is missing an identity."
      if [[ "$ref" == *":<none>" ]]; then image_unowned=$((image_unowned + 1)); continue; fi
      [[ "$ref" == "$repository":* ]] || fail "Image listing escaped the selected repository."
      if grep -Fxq "$ref" "$scratch/keep_refs" || grep -Fxq "$image_id" "$scratch/keep_ids" || \
         grep -Fxq "$ref" "$scratch/container_refs" || grep -Fxq "$image_id" "$scratch/container_ids"; then
        image_kept=$((image_kept + 1))
        printf 'kept_image=%s reason=retention_or_container_reference\n' "$ref"
      elif ! grep -Fxq "$ref|$image_id" "$scratch/images"; then
        printf '%s|%s\n' "$ref" "$image_id" >> "$scratch/images"
        image_planned=$((image_planned + 1))
        printf 'would_remove_image=%s\n' "$ref"
      fi
    done < "$scratch/listing"
  done
  echo 'coverage=selected_engine_tagged_images_only excluded=containers,volumes,build_cache,remote_registry,unowned_images'
fi

if [[ "$mode" == dry-run ]]; then status=planned; exit 0; fi
# All required inventories succeeded. Only now can an apply perform side effects.
if [[ "$ARTIFACT_CLEANUP_ENABLED" == 1 ]]; then
  python3 "$scratch/check_artifacts.py" "$project_root" "$ARTIFACT_ROOT" "$CURRENT_ARTIFACT" "$PREVIOUS_ARTIFACT" "$PINNED_ARTIFACTS" "$scratch/revalidated" >/dev/null || fail "Artifact revalidation failed."
  cmp -s "$scratch/artifacts" "$scratch/revalidated" || fail "Artifact candidates changed; re-plan."
  cmp -s "$scratch/artifacts.identity" "$scratch/revalidated.identity" || fail "Artifact identities or contents changed; re-plan."
  while IFS= read -r -d '' candidate; do
    attempted=$((attempted + 1))
    find "$candidate" -xdev -depth -delete || fail "Artifact removal failed; inspect partial state."
    [[ ! -e "$candidate" ]] || fail "Artifact still exists after removal."
    artifact_removed=$((artifact_removed + 1))
    printf 'removed_artifact=%s\n' "$(basename "$candidate")"
  done < "$scratch/artifacts"
fi
if [[ "$DOCKER_IMAGE_CLEANUP_ENABLED" == 1 ]]; then
  current_daemon="$("${docker_cmd[@]}" info --format '{{.ID}}')" || fail "Docker identity revalidation failed."
  [[ "$current_daemon" == "$daemon_id" ]] || fail "Docker engine changed; re-plan."
  while IFS='|' read -r ref image_id; do
    [[ -n "$ref" ]] || continue
    current_id="$("${docker_cmd[@]}" image inspect --format '{{.Id}}' "$ref")" || fail "Image changed; re-plan."
    [[ "$current_id" == "$image_id" ]] || fail "Image reference changed; re-plan."
    attempted=$((attempted + 1))
    "${docker_cmd[@]}" image rm "$ref" || fail "Image removal failed; inspect native state."
    "${docker_cmd[@]}" image ls --no-trunc "${ref%:*}" --format '{{.Repository}}:{{.Tag}}|{{.ID}}' > "$scratch/after_remove" || fail "Image removal result is unverified."
    if grep -Fq "$ref|" "$scratch/after_remove"; then fail "Image reference still exists after removal."; fi
    image_removed=$((image_removed + 1))
    printf 'removed_image=%s\n' "$ref"
  done < "$scratch/images"
fi
if (( artifact_planned + image_planned == 0 )); then status=no_candidates; else status=completed; fi
