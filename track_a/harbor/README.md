# Harbor task: atlas-2019-i1750330-resolved1d

Wraps `track_a/grader/closure.py`. The agent writes Rivet routine `BENCH_0001`.

## Regenerate assets
    python3 track_a/harbor/make_task_assets.py   # yoda.gz rename, solution copies, tests/ files, smoke file
    python3 track_a/harbor/make_instruction.py   # instruction.md from the summary JSON

## Run (Harbor 0.24.0, `uv tool install harbor`; `uv tool install podman-compose`)
    track_a/harbor/run_harbor.sh -p track_a/harbor/tasks/atlas-2019-i1750330-resolved1d -a oracle -n 1 --cpus ignore
    track_a/harbor/run_harbor.sh -p track_a/harbor/tasks/atlas-2019-i1750330-resolved1d -a nop -n 1 --cpus ignore

`run_harbor.sh` sets the local podman workarounds below. Job output goes to
`$HARBOR_JOBS_DIR`, by default `$HEPBENCH_DATA/harbor_jobs`. The smoke file
is the first 80 events of the Herwig 7 tt̄ sample (`track_a/samples/`), at
`$HEPBENCH_DATA/samples/smoke/herwig7_ttbar_80ev.hepmc.gz`.

## Status on the development host (2026-10-09): blocked on two admin-level limits

Rootless podman 5.8.2 on a shared Linux host (NFS home), step by step:

| # | Problem | Fix | State |
|---|---|---|---|
| 1 | Image layers cannot unpack on the NFS home (no xattrs) | `storage.conf`: graphroot on /var/tmp (local xfs) | fixed |
| 2 | No /etc/subuid, /etc/subgid range for the account: `lchown /etc/gshadow` on pull | `storage.conf`: `ignore_chown_errors` | worked around for pulls only (see 7) |
| 3 | No compose provider | Docker Compose v2 in ~/.docker/cli-plugins + `systemctl --user enable --now podman.socket` (drop-in in ~/.config/systemd/user/podman.service.d/ points the service at storage.conf and registries.conf) | fixed |
| 4 | Harbor's egress sidecar image has an unqualified name | `registries.conf`: short names from docker.io | fixed |
| 5 | cgroup `cpu` controller not delegated to users (only memory, pids) | `--cpus ignore` (in run_harbor.sh) | worked around |
| 6 | podman-compose rejects Harbor's `exec --no-TTY` | use Docker Compose v2 instead (row 3) | fixed |
| 7 | `compose cp` fails: `lchown ... invalid argument` (single UID mapping, same cause as 2); oracle files never reach the container, no reward file | none without a subuid range | **blocked** |
| 8 | Any network mode except `public` uses Harbor's egress sidecar, whose nftables `redirect` rule fails ("Could not process rule") | none without kernel/admin support | **blocked** for scored runs |

Admin requests that would unblock it:
- a subordinate UID/GID range for the account in /etc/subuid and /etc/subgid (e.g. `<user>:100000:65536`), then `podman system migrate`;
- nftables NAT redirect support for rootless containers (the `nft_redir` / `nft_nat` modules), for allow-list networking;
- optionally cgroup v2 `cpu` delegation for user sessions.

Alternatives: a machine with rootful Docker, or a cloud sandbox Harbor supports
with network control (Daytona, Modal, E2B), or Harbor's `singularity` backend
on Slurm nodes for development runs (no network control).

The grader itself does not depend on Harbor: `track_a/grader/run_closure.sh`
runs anywhere with the LCG view.
