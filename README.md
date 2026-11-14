# ghostty-copr

Fedora RPM builds of stable [Ghostty](https://ghostty.org) with an automatic software-GL
fallback, published to COPR as [`eleve/ghostty`](https://copr.fedorainfracloud.org/coprs/eleve/ghostty/).

Ghostty requires desktop OpenGL 4.3. Some GPUs expose less: Mali-G610 under Panfrost
reports OpenGL 3.1 (ES 3.1), so stock Ghostty fails with `Unable to create a GL context`.

| | |
|---|---|
| Chroots | `fedora-44` and `fedora-45`, `x86_64` and `aarch64` |
| Source | `release.files.ghostty.org` tarball, minisign-verified |
| Toolchain | official Zig release from `build.zig.zon`, minisign-verified (fetched in `%prep`) |
| Schedule | daily check of the highest `vX.Y.Z` tag; skips versions already published |

## How the fallback works

- `/usr/bin/ghostty` is a wrapper; the real binary lives in `/usr/libexec/ghostty/`.
- `ghostty-gl-probe` creates a surfaceless EGL context and requests desktop GL 4.3 core.
  Exit `0` = supported, `1` = only older desktop GL, `2` = undetermined (no change).
- On `1` the wrapper exports `LIBGL_ALWAYS_SOFTWARE=1` (Mesa llvmpipe, GL 4.5).
- The result is cached in `$XDG_RUNTIME_DIR/ghostty-gl-probe` (once per login, ~70 ms).
- A one-line patch removes `LIBGL_ALWAYS_SOFTWARE` from the shells Ghostty spawns,
  so GL apps started from the terminal still use the GPU.
- Every entry point goes through the wrapper: desktop file, D-Bus/systemd activation, CLI.

Override with `GHOSTTY_GL_FALLBACK=auto|force|off`. An explicit `LIBGL_ALWAYS_SOFTWARE` always wins.

## Install

```bash
sudo dnf copr enable eleve/ghostty
sudo dnf config-manager setopt copr:copr.fedorainfracloud.org:eleve:ghostty.priority=50
sudo dnf install ghostty            # or, replacing Terra: sudo dnf distro-sync 'ghostty*'
```

## Workflow

`.github/workflows/copr.yml` runs in a `fedora:latest` container: resolve version, skip if
published (unless `force`), set `Version`/`Release` in the spec, build the SRPM, `copr-cli build`.
Manual inputs: `version`, `release`, `force`.

The COPR project needs network access during builds (`copr-cli modify eleve/ghostty --enable-net on`).

## Secrets

`COPR_CONFIG`: contents of `~/.config/copr` from <https://copr.fedorainfracloud.org/api/>.
Tokens expire after 180 days:

```bash
gh secret set COPR_CONFIG -R ericklv/ghostty-copr < ~/.config/copr
```
