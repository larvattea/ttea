# TSDK platform: remaining work and release gates

Date: 2026-10-02  
Scope: TTEA plus local `../gingadivina`, `../TSDK`, and `../kartea`.

**TL;DR:** The local implementation gaps from the previous report are closed and pass synthetic checks in all four repositories.
The release is still not accepted. The remaining gates are real-camera tracking, physical calibration, native CI, rights clearance, and publication permission.
Nothing was committed, pushed, or published.

This report supplements [the implementation plan](sdk-platform-plan.md). It separates observed results from checks that have not run.

## 1. Contract gaps closed in this round

| Gap | Resolution | Evidence |
| --- | --- | --- |
| Handedness had two shapes | Every provider emits per-side `{label, score}`. Synthetic scores are `null`. `Observation.confidence_source` records `authored`, `measured`, or unknown. | Replay round-trip test. Real hand model on MediaPipe test images: raw frames give anatomical labels (`right_hands.jpg` → Right, flipped → Left). |
| Synthetic world landmarks followed image position | Body world landmarks are centered on the hips (2 m per image unit); hand world landmarks are centered on the hand centroid (0.5 m per unit). Translation leaves them unchanged; rotation rotates them rigidly. Face world landmarks are absent, as on hardware. | `test_model_coordinates_ignore_translation_and_rotate_rigidly` |
| Face simulator was a spiral point cloud | Pinned Apache-2.0 MediaPipe canonical 468-vertex mesh plus authored iris rings. Presets deform indexed eyes and lips. | Index-geometry, expression, and orientation tests; panel screenshot inspected |
| KarTEA was a bundled consumer | Independent local repository `../kartea` (`main:KarTEA`, bounded `t-tea>=2.0,<3`). TTEA no longer ships gameplay. Registered-player CSV access goes through the platform-owned `context.records`. | `tsdk check` passes; loopback install of the built `.ttea`; two registered runs wrote two synthetic CSV sessions |
| Calibration mirroring provenance was unknown | New captures store method, frame size, coordinate space, and corner order. Mirror conversion uses `width - 1 - x`. Legacy files stay readable but block launch until recalibration. | 5 calibration provenance tests; synthetic migration refuses an existing target |

> **Gotcha:** The scales of synthetic world landmarks are authored fixtures, not measurements. Synthetic face expressions are not a validated physiological model.

## 2. Acceptance completed locally

All runs used SDL/Qt dummy drivers, temporary data roots, and no camera or participant data.

| Area | Observed result |
| --- | --- |
| TTEA suite | 38 tests pass: tracking, runtime lifecycle across profiles, cartridge/library boundaries, calibration, KarTEA records |
| Installed wheel | Built and installed non-editably in a fresh venv. 38 tests pass from outside the checkout. The fixture license, models, catalog, and locales ship in the wheel. |
| GingaDivina | The late-input scoring from preserved commit `a2c9c67` is restored. Zero initial speed is documented as lifecycle state. 3 mechanics tests pass. All four modes, misses, speed limits, the results-to-menu transition, repeated rounds, and pause/termination ran synthetically. |
| KarTEA | 6 gameplay tests pass: lane changes, leaving the play area, target/barrier collision and avoidance, level-end feedback, menu progression, pause/resume speed restoration, and one event log per level |
| Records boundary | Cartridges see only five record methods. Foreign `player_id` and unknown or other-run `session_id` values are rejected. Records attach only when `player_id > 0`. |
| Developer panels | For body, hands, and face: edits reached gameplay, recordings replayed, live restart resumed, cooperative close exited 0 |
| Cartridge lifecycle | Covered: successful updates with ordered receipt history, failed activation, interrupted download and extraction, incompatible or non-newer updates, conflicting operations, a corrupt receipt skipped and preserved, uninstall keeping results |
| Archive protections | Covered: size, count, and ratio limits, file/directory and case collisions, CRC corruption, unsupported compression and special files, Windows device names |
| Release provenance | A clean committed fixture stamped the exact Git HEAD and builder `0.1.0`. Dirty trees and ignored, uncommitted packaged content were rejected. |
| Consumer CI gates | Both games pass `mypy --check-untyped-defs` and ruff `E9,F63,F7,F82` with no ignores. Both built cartridges pass `installed_consumer.py`. |

## 3. Remaining work that can be done locally

| Priority | Gap | Next step |
| --- | --- | --- |
| High | Real body and face models have not detected anything positive. Hands detected only on MediaPipe test images. | Run the body and face models on licensed still images or recordings. Check that two hands are assigned to the correct sides, and that loss and reacquisition work, without collecting patient video. |
| High | Neither game's real release has been built. `../kartea` has no commits; GingaDivina's migration is uncommitted. | After review, commit locally, then run `tsdk build --release` for each game. |
| Medium | Long-play acceptance | Play a full 120 s KarTEA level, phases 2–3, through `run_game`. Play a full-length GingaDivina song with audible output. |
| Medium | Records binding is keyed on the manifest id `kartea` | Before a second records consumer appears, generalize the binding to a manifest capability. |
| Medium | Real legacy KarTEA data | Only synthetic legacy data was tested. Test with a de-identified copy of real records, then decide whether guided migration is needed. |
| Low | Library housekeeping | Superseded version directories stay on disk with receipt history. Launch does not take the operation lock. A hard kill can leave staging directories behind. |

## 4. External release gates

| Gate | Status | Required evidence or authorization |
| --- | --- | --- |
| GingaDivina rights | No license grant in the 32-commit history | Rights-holder permission for code, graphics, effects, music, and historical assets |
| KarTEA rights | Package text asserts `MIT License`, but no grant text or asset inventory was found (`../kartea/RIGHTS.md`, `NOTICE`) | Confirm the code grant and each asset's origin with the rights holders |
| Model and dependency notices | Face fixture license shipped; no release-level inventory yet | License and provenance inventory for models, dependencies, and assets |
| Native desktop CI | Workflows authored for Windows x86-64, macOS ARM64, Linux x86-64; only macOS ARM64 ran locally | Run the matrix and keep the results |
| Physical acceptance | No hardware session on the migrated code | Calibration, projector alignment, mirroring, raised-hand handedness, capture handoff, audio, latency, tracking recovery |
| Compatibility range | CI accepts one `ttea-ref` per run | Define supported TTEA versions; test the lowest supported version and the upgrade version |
| Publication | Not authorized | Explicit permission before each remote creation, push, or publication. Never mirror-push over a populated repository. |

Process separation is not a security sandbox. A cartridge runs in the same Python process and can import TTEA internals.
Per-player isolation therefore holds only for reviewed catalog cartridges.
Projection is not proof of floor contact, and simulation proves no physical accuracy.

## 5. Order for the remaining work

1. Run positive-detection checks for body and face using licensed media.
2. Commit the reviewed local changes and run real `--release` builds for both games.
3. Run native and cross-repository CI, then the physical acceptance session.
4. Clear rights and confirm distribution names.
5. Request authorization for remote creation, pushes, and publication.

Linux ARM64/Raspberry Pi remains deferred and does not block the initial release.

**Next action:** run body and face model detections on licensed media, then commit locally for release builds.
