#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
cleanup="$script_dir/cleanup-release-assets.sh"
[[ -x "$cleanup" ]] || { echo "cleanup script is not executable" >&2; exit 1; }

fixture="$(mktemp -d)"
trap 'find "$fixture" -depth -delete' EXIT
mkdir -p "$fixture/bin" "$fixture/operations" "$fixture/delivery/artifacts/current" "$fixture/delivery/artifacts/previous" "$fixture/delivery/artifacts/old"
touch "$fixture/delivery/artifacts/current/manifest" "$fixture/delivery/artifacts/previous/manifest" "$fixture/delivery/artifacts/old/manifest"

cat > "$fixture/operations/release-retention.env" <<'EOF'
ARTIFACT_CLEANUP_ENABLED=1
ARTIFACT_ROOT=delivery/artifacts
CURRENT_ARTIFACT=current
PREVIOUS_ARTIFACT=previous
DOCKER_IMAGE_CLEANUP_ENABLED=1
MANAGED_IMAGE_REPOSITORIES=example/app
CURRENT_IMAGES=example/app@sha256:currentdigest
PREVIOUS_IMAGES=example/app:1.9.0
PINNED_IMAGES=
EOF

cat > "$fixture/bin/docker" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-} ${2:-} ${3:-}" == "image inspect --format" ]]; then
  case "$5" in
    example/app@sha256:currentdigest) echo sha256:current ;;
    example/app:1.9.0) echo sha256:previous ;;
    *) exit 1 ;;
  esac
elif [[ "${1:-} ${2:-} ${3:-}" == "ps -a --format" ]]; then
  echo example/app:1.9.0
elif [[ "${1:-} ${2:-}" == "ps -aq" ]]; then
  echo container-current
elif [[ "${1:-} ${2:-} ${3:-}" == "inspect --format {{.Image}}" && "${4:-}" == "container-current" ]]; then
  echo sha256:runtime
elif [[ "${1:-} ${2:-}" == "image ls" ]]; then
  printf '%s\n' 'example/app:2.0.0|sha256:current' 'example/app:old-alias|sha256:current' 'example/app:1.9.0|sha256:previous' 'example/app:runtime-old|sha256:runtime' 'example/app:1.8.0|sha256:old'
elif [[ "${1:-} ${2:-}" == "image rm" ]]; then
  echo "$3" >> "${FAKE_DOCKER_REMOVALS:?}"
else
  echo "unexpected fake docker invocation: $*" >&2
  exit 1
fi
EOF
chmod +x "$fixture/bin/docker"

export PATH="$fixture/bin:$PATH"
export FAKE_DOCKER_REMOVALS="$fixture/removals.log"

dry_run="$(RETENTION_PROJECT_ROOT="$fixture" "$cleanup" "$fixture/operations/release-retention.env" dry-run)"
grep -Fq 'would_remove_artifact=old' <<< "$dry_run"
grep -Fq 'would_remove_image=example/app:1.8.0' <<< "$dry_run"
grep -Fq 'kept_image=example/app:2.0.0' <<< "$dry_run"
grep -Fq 'kept_image=example/app:old-alias' <<< "$dry_run"
grep -Fq 'kept_image=example/app:runtime-old' <<< "$dry_run"
[[ -d "$fixture/delivery/artifacts/old" ]]
[[ ! -e "$fixture/removals.log" ]]

cp "$fixture/operations/release-retention.env" "$fixture/operations/invalid-retention.env"
sed 's#CURRENT_IMAGES=example/app@sha256:currentdigest#CURRENT_IMAGES=example/app:missing#' \
  "$fixture/operations/invalid-retention.env" > "$fixture/operations/invalid-retention.next"
mv "$fixture/operations/invalid-retention.next" "$fixture/operations/invalid-retention.env"
if RELEASE_CLOSEOUT_AUTHORIZED=1 RETENTION_PROJECT_ROOT="$fixture" \
  "$cleanup" "$fixture/operations/invalid-retention.env" apply >/dev/null 2>&1; then
  echo "apply unexpectedly succeeded with a missing current image" >&2
  exit 1
fi
[[ -d "$fixture/delivery/artifacts/old" ]]
[[ ! -e "$fixture/removals.log" ]]

RELEASE_CLOSEOUT_AUTHORIZED=1 RETENTION_PROJECT_ROOT="$fixture" \
  "$cleanup" "$fixture/operations/release-retention.env" apply >/dev/null
[[ -d "$fixture/delivery/artifacts/current" ]]
[[ -d "$fixture/delivery/artifacts/previous" ]]
[[ ! -e "$fixture/delivery/artifacts/old" ]]
grep -Fxq 'example/app:1.8.0' "$fixture/removals.log"
if grep -Eq '2\.0\.0|old-alias|runtime-old|1\.9\.0' "$fixture/removals.log"; then
  echo "current or previous image was selected for removal" >&2
  exit 1
fi

if RETENTION_PROJECT_ROOT="$fixture" "$cleanup" "$fixture/operations/release-retention.env" apply >/dev/null 2>&1; then
  echo "apply unexpectedly succeeded without closeout authorization" >&2
  exit 1
fi

echo "release_retention_contract=passed"
