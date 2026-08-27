#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
project_root_input="${RETENTION_PROJECT_ROOT:-$script_dir/../..}"
project_root="$(cd "$project_root_input" && pwd -P)"
config_input="${1:-$project_root/operations/release-retention.env}"
mode="${2:-dry-run}"

if [[ "$mode" != "dry-run" && "$mode" != "apply" ]]; then
  echo "Usage: $0 [config] [dry-run|apply]" >&2
  exit 2
fi
if [[ ! -f "$config_input" ]]; then
  echo "Missing retention config: $config_input" >&2
  exit 2
fi
config_dir="$(cd "$(dirname "$config_input")" && pwd -P)"
config="$config_dir/$(basename "$config_input")"
case "$config" in
  "$project_root"/*) ;;
  *) echo "Retention config must stay inside project root: $project_root" >&2; exit 2 ;;
esac
if [[ "$mode" == "apply" && "${RELEASE_CLOSEOUT_AUTHORIZED:-0}" != "1" ]]; then
  echo "Apply requires RELEASE_CLOSEOUT_AUTHORIZED=1 after target release validation." >&2
  exit 2
fi

ARTIFACT_CLEANUP_ENABLED=0
ARTIFACT_ROOT=
CURRENT_ARTIFACT=
PREVIOUS_ARTIFACT=
DOCKER_IMAGE_CLEANUP_ENABLED=0
MANAGED_IMAGE_REPOSITORIES=
CURRENT_IMAGES=
PREVIOUS_IMAGES=
PINNED_IMAGES=

load_config() {
  local line key value seen="|"
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ -z "$line" || "$line" == \#* ]] && continue
    [[ "$line" =~ ^([A-Z][A-Z0-9_]*)=([A-Za-z0-9._:/,@-]*)$ ]] || {
      echo "Invalid retention config assignment." >&2
      exit 2
    }
    key="${BASH_REMATCH[1]}"
    value="${BASH_REMATCH[2]}"
    case "$key" in
      ARTIFACT_CLEANUP_ENABLED|ARTIFACT_ROOT|CURRENT_ARTIFACT|PREVIOUS_ARTIFACT|DOCKER_IMAGE_CLEANUP_ENABLED|MANAGED_IMAGE_REPOSITORIES|CURRENT_IMAGES|PREVIOUS_IMAGES|PINNED_IMAGES) ;;
      *) echo "Unsupported retention config key: $key" >&2; exit 2 ;;
    esac
    case "$seen" in *"|$key|"*) echo "Duplicate retention config key: $key" >&2; exit 2 ;; esac
    seen="${seen}${key}|"
    printf -v "$key" '%s' "$value"
  done < "$config"
}
load_config

case "$ARTIFACT_CLEANUP_ENABLED:$DOCKER_IMAGE_CLEANUP_ENABLED" in
  0:0|0:1|1:0|1:1) ;;
  *) echo "Cleanup enable flags must be 0 or 1." >&2; exit 2 ;;
esac

# Apply is always preceded by a complete no-write pass so a missing rollback
# artifact or image cannot be discovered only after another object was removed.
if [[ "$mode" == "apply" && "${RETENTION_PREFLIGHT_COMPLETE:-0}" != "1" ]]; then
  RETENTION_PREFLIGHT_COMPLETE=1 RETENTION_PROJECT_ROOT="$project_root" \
    "$0" "$config" dry-run >/dev/null
fi

artifact_removed=0
artifact_kept=0
if [[ "$ARTIFACT_CLEANUP_ENABLED" == "1" ]]; then
  [[ -n "$ARTIFACT_ROOT" && "$ARTIFACT_ROOT" != /* && "$ARTIFACT_ROOT" != *".."* ]] || {
    echo "ARTIFACT_ROOT must be a project-relative path without '..'." >&2
    exit 2
  }
  [[ -n "$CURRENT_ARTIFACT" && "$CURRENT_ARTIFACT" != */* && "$CURRENT_ARTIFACT" != "." && "$CURRENT_ARTIFACT" != ".." ]] || {
    echo "CURRENT_ARTIFACT must be one direct child directory name." >&2
    exit 2
  }
  if [[ -n "$PREVIOUS_ARTIFACT" && ( "$PREVIOUS_ARTIFACT" == */* || "$PREVIOUS_ARTIFACT" == "." || "$PREVIOUS_ARTIFACT" == ".." ) ]]; then
    echo "PREVIOUS_ARTIFACT must be empty or one direct child directory name." >&2
    exit 2
  fi
  artifact_root_input="$project_root/$ARTIFACT_ROOT"
  [[ -d "$artifact_root_input" ]] || { echo "Missing artifact root: $artifact_root_input" >&2; exit 2; }
  artifact_root="$(cd "$artifact_root_input" && pwd -P)"
  case "$artifact_root" in "$project_root"/*) ;; *) echo "Artifact root escaped project root." >&2; exit 2 ;; esac
  [[ -d "$artifact_root/$CURRENT_ARTIFACT" ]] || { echo "Current artifact is missing." >&2; exit 1; }
  if [[ -n "$PREVIOUS_ARTIFACT" && ! -d "$artifact_root/$PREVIOUS_ARTIFACT" ]]; then
    echo "Previous artifact is missing." >&2
    exit 1
  fi
  while IFS= read -r -d '' candidate; do
    name="$(basename "$candidate")"
    if [[ "$name" == "$CURRENT_ARTIFACT" || ( -n "$PREVIOUS_ARTIFACT" && "$name" == "$PREVIOUS_ARTIFACT" ) ]]; then
      artifact_kept=$((artifact_kept + 1))
      echo "kept_artifact=$name"
      continue
    fi
    if [[ "$mode" == "dry-run" ]]; then
      echo "would_remove_artifact=$name"
    else
      find "$candidate" -depth -delete
      echo "removed_artifact=$name"
    fi
    artifact_removed=$((artifact_removed + 1))
  done < <(find "$artifact_root" -mindepth 1 -maxdepth 1 -type d -print0)
fi

image_removed=0
image_kept=0
if [[ "$DOCKER_IMAGE_CLEANUP_ENABLED" == "1" ]]; then
  command -v docker >/dev/null 2>&1 || { echo "Docker is required for image cleanup." >&2; exit 2; }
  managed_repositories=()
  current_images=()
  previous_images=()
  pinned_images=()
  [[ -z "$MANAGED_IMAGE_REPOSITORIES" ]] || IFS=',' read -r -a managed_repositories <<< "$MANAGED_IMAGE_REPOSITORIES"
  [[ -z "$CURRENT_IMAGES" ]] || IFS=',' read -r -a current_images <<< "$CURRENT_IMAGES"
  [[ -z "$PREVIOUS_IMAGES" ]] || IFS=',' read -r -a previous_images <<< "$PREVIOUS_IMAGES"
  [[ -z "$PINNED_IMAGES" ]] || IFS=',' read -r -a pinned_images <<< "$PINNED_IMAGES"
  (( ${#managed_repositories[@]} > 0 )) || { echo "At least one managed image repository is required." >&2; exit 2; }
  (( ${#current_images[@]} > 0 )) || { echo "At least one current image is required." >&2; exit 2; }

  keep_refs="$(mktemp)"
  keep_ids="$(mktemp)"
  container_refs="$(mktemp)"
  container_ids="$(mktemp)"
  trap 'rm -f "${keep_refs:-}" "${keep_ids:-}" "${container_refs:-}" "${container_ids:-}"' EXIT
  required_images=("${current_images[@]}")
  [[ -z "$PREVIOUS_IMAGES" ]] || required_images+=("${previous_images[@]}")
  [[ -z "$PINNED_IMAGES" ]] || required_images+=("${pinned_images[@]}")
  for image in "${required_images[@]}"; do
    [[ -n "$image" ]] || continue
    managed=0
    for repository in "${managed_repositories[@]}"; do
      [[ "$image" == "$repository":* || "$image" == "$repository"@* ]] && managed=1
    done
    [[ "$managed" == "1" ]] || { echo "Image is outside managed repositories: $image" >&2; exit 2; }
    image_id="$(docker image inspect --format '{{.Id}}' "$image")" || {
      echo "Required current, previous, or pinned image is missing: $image" >&2
      exit 1
    }
    printf '%s\n' "$image" >> "$keep_refs"
    printf '%s\n' "$image_id" >> "$keep_ids"
  done
  docker ps -a --format '{{.Image}}' > "$container_refs"
  while IFS= read -r container_id; do
    [[ -n "$container_id" ]] || continue
    docker inspect --format '{{.Image}}' "$container_id" >> "$container_ids"
  done < <(docker ps -aq)
  sort -u -o "$keep_refs" "$keep_refs"
  sort -u -o "$keep_ids" "$keep_ids"
  sort -u -o "$container_refs" "$container_refs"
  sort -u -o "$container_ids" "$container_ids"

  for repository in "${managed_repositories[@]}"; do
    [[ -n "$repository" ]] || continue
    while IFS='|' read -r ref image_id; do
      [[ -n "$ref" && -n "$image_id" && "$ref" != *":<none>" ]] || continue
      if grep -Fxq "$ref" "$keep_refs" || grep -Fxq "$image_id" "$keep_ids" || \
         grep -Fxq "$ref" "$container_refs" || grep -Fxq "$image_id" "$container_ids"; then
        image_kept=$((image_kept + 1))
        echo "kept_image=$ref"
        continue
      fi
      if [[ "$mode" == "dry-run" ]]; then
        echo "would_remove_image=$ref"
      else
        docker image rm "$ref" >/dev/null
        echo "removed_image=$ref"
      fi
      image_removed=$((image_removed + 1))
    done < <(docker image ls --no-trunc "$repository" --format '{{.Repository}}:{{.Tag}}|{{.ID}}')
  done
fi

echo "release_retention_status=completed mode=$mode artifacts_kept=$artifact_kept artifacts_removed=$artifact_removed images_kept=$image_kept images_removed=$image_removed"
