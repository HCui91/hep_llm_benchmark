#!/bin/bash
# Run Harbor with rootless podman on the development host. Usage: run_harbor.sh <harbor run args...>
#   e.g. run_harbor.sh -p track_a/harbor/tasks/atlas-2019-i1750330-resolved1d -a oracle
#
# Workarounds, local to this shell (plus a systemd drop-in for the podman API
# service, ~/.config/systemd/user/podman.service.d/hep_llm_benchmark.conf, that
# points it at the same two files):
# - storage.conf: podman images on local disk (the NFS home lacks xattrs) and
#   ignore_chown_errors (this account has no /etc/subuid or /etc/subgid range).
# - registries.conf: resolve unqualified image names (Harbor's sidecar uses one)
#   on Docker Hub without prompting.
# `podman compose` uses Docker Compose v2 (~/.docker/cli-plugins/docker-compose)
# through the user podman socket (`systemctl --user enable --now podman.socket`).
# podman-compose does not work here: Harbor passes `exec --no-TTY`, which
# podman-compose 1.6 rejects.
# The cgroup cpu controller is not delegated to users on that host, so pass
# `--cpus ignore`; memory limits still apply.
set -eo pipefail
HERE=$(dirname "$(readlink -f "$0")")
export CONTAINERS_STORAGE_CONF="$HERE/storage.conf"
export CONTAINERS_REGISTRIES_CONF="$HERE/registries.conf"
exec harbor run -e podman --cpus ignore -o "${HARBOR_JOBS_DIR:-${HEPBENCH_DATA:?set HEPBENCH_DATA or HARBOR_JOBS_DIR}/harbor_jobs}" "$@"
