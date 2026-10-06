# TTEA developer mode and TSDK platform plan

Status: local implementation available; redistribution, native CI, and physical acceptance remain release gates.

This file records the planning conversation and supersedes its earlier Raspberry Pi acceptance requirement.
No remote repository creation, pushes, or publication are authorized. Obtain explicit permission before those actions.

## Agreed decisions

| Decision | Contract |
| --- | --- |
| Repository layout | Four independent local repositories: TTEA, `../gingadivina`, `../TSDK`, and `../kartea`; remote creation/publication remains separate |
| Flagship | GingaDivina is the reference consumer of TTEA and TSDK |
| Cartridge | `.ttea` is a built ZIP container with portable Python source, assets, manifest, and license notices |
| Dependencies | Games use platform-provided runtime libraries only; no game-specific runtime dependency installation |
| Developer tools | Body, hands, and face simulation all belong to the initial release, not a feet-only subset |
| Participants | One participant per session: one body, two hands, or one face; one tracking profile active at a time |
| Initial platforms | Windows x86-64, macOS Apple Silicon, and Linux x86-64 |
| Deferred platforms | Linux ARM64/Raspberry Pi; hardware and OS selection do not block initial implementation |
| Version provenance | Every cartridge records the exact TSDK version automatically, similar to Unity build metadata |

## Source repository and history preservation

Source: <https://github.com/marcosoft47/exergamejam2025>.
Discovery: <https://github.com/larvattea/ttea/issues/5> identifies it as Ginga Divina, from ExergameJam 2025.
GitHub reports default branch `master`, a non-fork repository, and no detected license.
A recursive tree check found `requirements.txt`, but no standard LICENSE, COPYING, NOTICE, or README file.
This does not establish redistribution rights; inspect source headers and asset provenance and obtain permission where needed.

The eventual destination is `larvattea/gingadivina`, an independent copy, not a GitHub fork.
Preserve original commit identities, authorship, branches, tags, and any LFS objects.
Check submodules and historical assets before copying. Issues and release assets are not part of Git history.
Use a full-history clone/bare-copy workflow; do not squash, rebase, or rewrite the imported history.
Only push to a newly created destination after explicit permission. Never mirror-push over an existing populated repository.

Remove platform infrastructure in subsequent migration commits, not by deleting the game's history.
Preserve mechanics, scoring, assets, credits, and required license notices.
Establish a runnable behavioral baseline before migration.

## Responsibilities and dependency direction

| Repository | Owns | Does not own |
| --- | --- | --- |
| TTEA | Console UI, public game API, cartridge schema/loader, runtime, hardware, tracking, calibration, developer tools, installation, session storage | Individual game mechanics |
| GingaDivina | Gameplay, assets, game configuration, scoring, contract-conforming lifecycle callbacks | Camera/model initialization, calibration, platform lifecycle, dependency installation |
| KarTEA | Driving-game mechanics, assets, cartridge configuration, and lifecycle callbacks | Platform internals, camera ownership, registered-participant CSV implementation |
| TSDK | Project template, packaging CLI, contract validation, reusable CI workflow, development tooling | A second runtime or duplicate tracking implementation |

The runtime API and cartridge schema remain authoritative in TTEA.
TSDK consumes them; TTEA does not depend on its build tools.
Games depend on the `t-tea` distribution. TSDK is a development dependency.
Separate releases remain compatible through versioned contracts and cross-repository CI, not matching release numbers.

## Runtime ownership and injection

The Qt console starts a TTEA-controlled game process using the installed platform runtime.
The game process owns the Pygame loop, display, audio, camera, and selected detector.
Release calibration/preview camera ownership before starting gameplay.
Do not initialize unused detectors or open a camera in simulation mode.

Inject a context with drawing resources, input, timing, assets, configuration, and scoped session storage.
Games implement lifecycle callbacks rather than starting independent applications.
Allow ordinary Pygame drawing APIs; importing a drawing function does not duplicate Pygame.
Prohibit game-owned display initialization, event pumping, camera capture, and detector initialization.
Do not wrap every Pygame primitive in a second graphics API.

Process separation limits launcher crashes and global-state contamination; it is not a security sandbox.
The initial catalog uses reviewed publishers/releases. Compliance checks cannot make arbitrary Python safe.
Keep browsing and configuration metadata declarative rather than importing game code into the launcher.

## Shared tracking contract

Hardware, simulation, and replay providers produce the same public tracking semantics.
Games must not branch on developer mode.
Synthetic observations enter the same normalization and filtering pipeline as detected observations.

Document camera-normalized, projection-normalized, and model-relative 3D coordinate spaces separately.
Model-relative 3D coordinates are not room coordinates. A plane-projected point is not proof of floor contact.
Use anatomical left/right labels, explicit out-of-area state, timestamps, and missing/stale observation state.
Do not silently clamp out-of-area coordinates or turn tracking loss into valid coordinates at `(0, 0)`.
Preserve confidence/visibility where supplied; unsupported confidence remains unknown.

| Profile | Public data | Developer controls |
| --- | --- | --- |
| Body | Body landmarks, model-relative 3D landmarks, visibility, named heel/toe landmarks, derived projection-space feet | Full skeleton editing, whole-body movement, independent heel/toe controls, pose presets |
| Hands | 21 landmarks per hand, model-relative 3D landmarks, handedness | Independent positioning, joint editing, rotation, open/fist/pinch presets |
| Face | Face mesh, optional expression coefficients and facial transformation matrix | Mesh editing, position/orientation controls, expression sliders and presets |

Every profile includes disappearance/stale-input controls and timestamped recording/replay.
Record observations, calibration, and processing configuration so replay exercises the shared pipeline.
Face expression sliders create synthetic observations; coherent real-world fixtures remain necessary for realism checks.
Raw patient video must not be required or collected by default. Use synthetic development sessions and isolated data.

A profile is complete only when its real provider, simulator, replay, and runtime integration work.
Schema support alone does not count. Hands and face require runtime-owned models and providers beyond today's pose implementation.
Simulator success does not establish ChArUco detection, physical projection alignment, camera latency, or floor contact accuracy.

## Developer workflow

Implemented commands from a game checkout with sibling TTEA/TSDK development dependencies:

```text
uv run dev          # TTEA developer mode loads this game's checkout
uv run tsdk check   # Validate the game contract
uv run tsdk build   # Build the release cartridge
```

Default development UX: a full-screen window opens with no game loaded; Load game (browsing from the current checkout) runs it in the left two thirds with synthetic session data; the right third holds the developer panel.
Simulation requires neither player registration nor physical calibration.
TTEA already exports `dev`; adapt it to recognize the game project instead of installing competing `dev` entrypoints.
Commit `uv.lock`; use supported version ranges with deliberate upgrades, not unbounded automatic latest-version updates.
Test TTEA as an installed package outside its source checkout. Resource paths must not assume the repository layout.

## Cartridge format and version metadata

Package game source, assets, declarative metadata, and license notices in a versioned ZIP container.
Exclude Python interpreters, native extensions, platform library copies, model copies, virtual environments, and installation hooks.
TTEA may compile/cache source locally; bytecode-only and native-compiled cartridges are not the selected design.

The manifest identifies the game, its version, entrypoint, localized display metadata, tracking profile, and compatibility requirements.
Use one authored metadata source and generate release metadata rather than maintaining competing copies.

| Field | Meaning |
| --- | --- |
| `builder.version` | Exact installed TSDK version used for the build |
| `build.source_commit` | Source revision; distinguish dirty local builds |
| `format_version` | Cartridge container format version |
| `game_api` | Version of the game/runtime contract |
| `requires_ttea` | Supported TTEA runtime version range |

The game has its own independent version. Builder version alone must not determine runtime compatibility.
Release builds require clean source state and automatic provenance stamping.
These field names are the proposed schema; finalize its precise representation during implementation.

## Catalog and installation lifecycle

Maintain a curated repository list in TTEA with stable game identity, name, URL, and optional description/logo.
Preserve existing localized names and descriptions where applicable.
Catalog inclusion requires a compatible `.ttea` release and successful contract checks.

1. Browse catalog metadata without executing game code; resolve compatible stable releases rather than blindly using latest.
2. Download the selected artifact and verify its digest and manifest compatibility before activation.
3. Extract into staging with traversal, link, collision, and size protections; never run installation hooks.
4. Activate atomically. Failures preserve the working installation; retain version/install receipts and keep updates explicit.
5. Support offline launches and uninstall without deleting session results or saves stored separately from installed game code.

A checksum detects corruption, not malicious publisher behavior. The reviewed catalog remains a trust boundary.
Exercise the real downloader with locally served built cartridges before authorized remote publication.

## CI and flagship acceptance

TSDK provides reusable checks for game repositories. Enforce concrete rules, not a claim of general clean-code certification.

- Validate metadata, API compatibility, runtime dependency declarations, imports, and cartridge contents.
- Enforce ownership boundaries: no independent camera, detector, display initialization, event pump, or dependency installation.
- Exercise meaningful tracking loss/recovery, pause/resume, termination, and session-result behavior.
- Install and execute the built cartridge outside its source checkout, including replay-driven behavior.
- Check supported TTEA versions, cross-repository compatibility, linting, and types at public boundaries.

Use GingaDivina as the primary independent consumer and KarTEA as a second consumer before freezing the API.
Changes to platform dependencies must account for existing calibration and KarTEA callsites; do not break them by merely changing a pin.
Native CI initially covers Windows x86-64, macOS ARM64, and Linux x86-64.
Camera/projector alignment, capture behavior, audio, and latency still require physical-device acceptance.

## Implementation sequence

| Stage | Deliverable | Acceptance gate |
| --- | --- | --- |
| 1. Audit and copy | Inspect GingaDivina, rights, assets, dependencies, and history; prepare a local full-history copy | Original behavior recorded; attribution and redistribution requirements understood |
| 2. Runtime contract | Installable TTEA package, source-independent resources, injected services, and shared tracking contracts | A game runs outside TTEA's checkout without owning platform resources |
| 3. Flagship and SDK | Port GingaDivina while developing TSDK; complete developer tools for all three profiles | Local developer workflow, real/simulated providers, replay, and lifecycle behavior work end to end |
| 4. Cartridges and library | Build/validate `.ttea`; implement browsing, downloading, install/update/uninstall | Installed cartridge works independently; failed installation preserves working game and saves |
| 5. Validation and release | Native CI, second-consumer compatibility, and physical validation | Initial desktop targets pass; remote creation/push/publication occur only after explicit permission |

## Evidence collected during planning

Current TTEA launches scripts/executables with player, professional, and language arguments.
Its metadata loader scans local game folders; it does not download games.
KarTEA constructs its own camera/detector. Ginga metadata points to a missing `Gingada.Divina.exe`.
Source-layout assumptions in resource/data paths need attention before normal wheel-based consumption.
Public PyPI JSON requests for `t-tea` and `tsdk` returned 404 during planning; publication/naming must be established before registry-based usage.

Local catalog and homography smoke probes ran successfully without exercising physical hardware.
The homography probe mapped camera points to `(0,0)`, `(400,300)`, and `(800,600)`.
Installed MediaPipe result-type inspection confirmed pose, hand, and face result APIs.
No actual game, camera, or projector was exercised in these probes.

Binary-only dependency resolution of current project pins with Python 3.10 succeeded for the three initial desktop targets.
It failed for Linux ARM64 because MediaPipe 0.10.21 has no matching wheel.
An in-memory override to MediaPipe 1.0.1 with Python 3.12 resolved for desktop targets and ARM64/glibc 2.39.
ARM64/glibc 2.36 still failed on PySide6 6.11.1. No dependency files were changed.
These are resolver checks, not cross-platform runtime validation or approval to upgrade.

Raspberry Pi is explicitly deferred. Its findings are retained for later planning, not initial-release blockers.
The initial release need not adopt the candidate MediaPipe/Python upgrade merely to satisfy deferred ARM64 support.

## Local implementation and operation

The independent local repositories are `../gingadivina`, `../TSDK`, and `../kartea`.
GingaDivina retains upstream history; migration changes are separate working-tree changes.
No remote repository was created, pushed, or published.

TTEA owns `ttea.sdk.api`, `runtime`, `tracking`, `providers`, `simulator`,
`developer`, `cartridge`, and `library`. TSDK imports the authoritative
TTEA schema rather than maintaining a second runtime.

```sh
# From ../gingadivina:
uv run dev
uv run tsdk check
uv run tsdk build
# A clean, committed source tree is required for release builds:
uv run tsdk build --release
```

Author metadata in `ttea.toml` under `[game]`: `id`, `version`, `entrypoint`,
`tracking_profile`, `game_api = 1`, `requires_ttea`, `assets`, and `licenses`, plus
optional `resolution = [width, height]`: the runtime surface size when the session
config sets none (default 1280×720), and the suggested developer camera region.
Localized strings live in `[game.name]` and optional `[game.description]`.
The builder generates `manifest.json` with `format_version = 1`, exact installed
`builder.version`, and `build.source_commit`/`build.dirty`. Local non-Git builds
use `source_commit = "unversioned"` and `dirty = true`; release builds reject them.

Games implement `start`, `update`, `draw`, `pause`, `resume`, and `stop`, optionally
inheriting defaults from `ttea.sdk.api.Game`. Context assets resolve from the
project root. `context.request_stop(result)` terminates cleanly; `stop` may return
a result dictionary. P toggles pause; Escape terminates. Tracking loss pauses
updates, retains drawing, and resumes after recovery unless the user paused.

The developer window renders the game in its left two thirds: the runtime draws
with SDL's dummy video driver, publishes RGBX frames through a shared file, and
receives mouse and keyboard input as JSON lines on stdin, so games must read
input from `context.events`. The right third holds the tracking controls, the
camera/skeleton preview below them, and, at the bottom, Load game (project
folder or `.ttea` cartridge, extracted to temporary storage), Restart game, and
Stop game while a game runs, or Exit once it stops. Synthetic edits all
body/hand/face landmarks, presets, translation, rotation, disappearance, stale
timestamps, and recordings. Face sliders and mesh geometry are synthetic, not
validated physiological fixtures. Developer sessions use temporary storage and
do not register participants. Mouse + keyboard is the default tracking source:
the cursor over the skeleton preview is a position in game-normalized
coordinates. With no key held it moves the whole subject (body feet midpoint,
hand pair, or face); holding A or D plants the left or right foot (or moves
that hand) at the cursor. A planted foot stays between `MIN_STANCE` and
`MAX_STRIDE` from the other one, the torso follows the feet midpoint, and the
knees stay between hip and ankle. Hovering the preview gives it the keyboard;
keys other than A/D still reach the game, and leaving the preview returns the
keyboard to the game. The game area always receives its own mouse and keys.
Selecting Camera opens the chosen device by name (system default first). For a
hands or face game, it runs that profile's detector, previews the frame with the
detected skeleton (low-visibility joints faded), and feeds those observations to
the game. For a body game, Camera control picks the MediaPipe model (body, hand,
and face are separate models) that drives the body skeleton: Body feeds the
detected body directly; Hands (index fingers down) plants the left and right
feet at the two index fingertips when each hand points its index
finger down with the other fingers folded (one such hand moves the nearer foot;
other hand shapes hold the pose); Whole hands does the same with each palm centre
(wrist and knuckle mean) in any hand shape; Face (nose) moves the
midpoint of both feet to the nose tip. Hands and Face use a mirrored (selfie)
camera view, so moving right moves the body right. The preview poses the body in camera
coordinates, so the feet sit under the fingertips or nose. The game receives the
same pose translated so the feet midpoint maps from the dashed camera region to
the whole game, clamped. Camera region sets that region's width × height in
camera pixels; it is suggested from the game `resolution` (scaled down to fit the
camera frame) and centred per control: frame centre for the nose, 67.5% down for
fingertips (keeping the fists above them), 55% down for palm centres, shifted to
stay inside the frame. Camera sensitivity scales the
mapping about the region centre per control (defaults: hands 1, nose 2.5). The preview draws the detected hand or
face in violet under the driven body. Frames are previewed only; recordings
still contain observations, never video.

### Tracking and installation contracts

Camera landmarks are normalized image coordinates. A 3x3 homography maps them to
normalized projection coordinates; values outside `[0,1]` remain outside.
Projected points have no meaningful depth. World landmarks remain model-relative
3D; face world landmarks and unsupported visibility remain absent/unknown.
`TrackingFrame` distinguishes missing and stale observations and exposes anatomical
heel/toe landmarks and midpoint feet. Neither projection nor simulation proves
floor contact. JSONL recordings retain observations, calibration, processing
configuration, and processing time; replay uses the recorded processing clock.
No patient video is recorded.

Calibration captures persist method, frame dimensions, mirror coordinate space, and TL/TR/BL/BR projection-corner order.
ChArUco stores raw camera pixels. Manual calibration records the snapshot's mirror setting.
Conversion undoes horizontal pixel mirroring with `width - 1 - x`; anatomical labels do not change.
The homography consumes normalized unmirrored camera points and produces normalized top-left-origin projection points.
Legacy eight-column calibration files remain readable and unchanged, but require recalibration before launching.
Current settings cannot establish how historical points were captured.

Catalog release descriptors contain `version`, `url`, `sha256`, `game_api`,
`format_version`, and `requires_ttea`. Selection skips incompatible or prerelease
versions. The checked-in catalog has no published compatible releases yet.
The library accepts HTTPS or loopback HTTP, verifies digests and manifests, stages
protected extraction, and atomically switches version receipts. Updates are
explicit. Offline launch needs no network; uninstall leaves session storage intact.
Checksums and AST contract checks do not sandbox Python or establish publisher trust.

### Existing data needs explicit migration

Writable application data now uses `platformdirs.user_data_dir("ttea", "udesc")`,
not the checkout. Bundled models and Qt resources remain inside the installed
package. Before first launch, explicitly copy old console data to an absent target:

```sh
python -c 'from pathlib import Path; from shutil import copytree; from platformdirs import user_data_dir; copytree(Path("/absolute/path/to/old/ttea/data"), Path(user_data_dir("ttea", "udesc")))'
```

This preserves originals and refuses an existing destination. Do not enable
overwrite merging; resolve existing records manually. Legacy KarTEA `players`,
`log`, and `kartea.ini` belong under the new root's `exergames/kartea`; TTEA
still reads them through its KarTEA records adapter. The game code itself now
ships as the separate `../kartea` cartridge; never copy it into the data root.
A synthetic copy test confirmed readable configuration, preserved sources, and refusal of an existing target.
No existing patient data was inspected or migrated during implementation.

### KarTEA records boundary

KarTEA receives `context.records` only when TTEA launches it for a registered player.
The adapter binds the launching player and professional; the cartridge never sees DAOs, paths, or other players.
One CSV session spans a run and accumulates across levels, matching the original game.
Developer and anonymous sessions get no records and write only to scoped session storage.

### Release gates

GingaDivina's 32-commit history contains no discovered license grant. Code, music,
graphics, and historical assets require rights clearance; its `RIGHTS.md` records
the audit and grants no redistribution permission. The original application
launched and initialized its camera; that does not prove full-song physical play.
Native desktop CI is configured but must run on each target. Camera/projector
alignment, calibration mirroring, audio, and latency still need physical acceptance.
Remote repository creation, pushes, and publication still require explicit permission.

### Local verification

These checks ran against source checkouts with SDL/Qt dummy drivers. No camera, projector, or participant data was used.

| Area | Observed result |
| --- | --- |
| TTEA suite | 38 tests passed, also from a non-editable wheel outside the checkout: tracking, runtime lifecycle, cartridge/library, calibration provenance, KarTEA records |
| TSDK | 5 release tests passed; clean release stamped the exact Git HEAD; dirty and ignored-uncommitted trees were rejected |
| GingaDivina | 3 mechanics tests passed; preserved `a2c9c67` late-input scoring restored; all four modes ran synthetically |
| KarTEA | `tsdk check`, mypy, and ruff passed; 6 gameplay tests passed; built `.ttea` installed over loopback HTTP and ran two registered sessions into synthetic CSV records |
| Developer panels | All three profiles: edits reached gameplay, recordings replayed, live restart resumed, cooperative close exited 0 |

Real MediaPipe inference on blank synthetic video previously returned explicit missing observations.
That proves model loading, not physical tracking accuracy.
