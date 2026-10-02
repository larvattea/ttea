# TSDK platform progress

Date: 2026-10-02

**TL;DR:** TTEA now runs games as independent cartridges with simulated and real tracking. GingaDivina and KarTEA are separate consumer repositories, and every local check passes.
Release still waits on real-camera tracking, physical calibration, native CI, rights clearance, and publication permission.
All work is committed locally; nothing is pushed.

## The platform is split into four local repositories

| Repository | Role | State |
| --- | --- | --- |
| `ttea` | Console, runtime, tracking, calibration, cartridge library | 38 tests pass, also from an installed wheel |
| `../TSDK` | `tsdk check`, `tsdk build`, reusable game CI | 5 release tests pass |
| `../gingadivina` | Flagship dance game; upstream history preserved | 3 mechanics tests pass |
| `../kartea` | Driving game extracted from TTEA | 6 gameplay tests pass |

## Closed gaps since the previous report

| Gap | Result |
| --- | --- |
| Handedness had two shapes | Every provider emits `{label, score}`. Real hand-model runs confirmed that raw frames give anatomical labels. |
| Simulated 3D followed screen position | Body and hand world coordinates ignore translation and rotate rigidly. Face world data is absent, as on hardware. |
| Face simulator was a point cloud | Uses MediaPipe's Apache-2.0 canonical mesh |
| KarTEA was bundled | Independent cartridge. Player CSV access goes through a five-method `context.records` that rejects other players' data. |
| Calibration mirroring was unknown | Each capture stores its provenance. Legacy calibrations require recalibration. |
| Update failures were unproven | Interrupted, failed, conflicting, and corrupt cases all keep the working install |

## Everything verified ran without camera or participant data

```text
ttea          38 tests OK (source and installed wheel)
TSDK    5 tests OK; clean release stamps exact Git HEAD
gingadivina    3 tests OK; mypy + ruff clean; cartridge runs installed
kartea         6 tests OK; mypy + ruff clean; 2 registered sessions -> 2 CSV records
panels         body/hands/face: edit -> game, record -> replay, clean exit
```

> **Gotcha:** Simulation and blank-frame inference prove wiring, not tracking accuracy or floor contact.

## Gates that remain

| Gate | Owner action |
| --- | --- |
| Body and face positive detections | Run both models on licensed media |
| Release builds | Run `tsdk build --release` on the committed games |
| Native CI | Run the Windows, macOS, and Linux matrix |
| Physical acceptance | Calibrate, align the projector, check raised-hand sides, latency, recovery |
| Rights | Clear GingaDivina and KarTEA code and assets with the rights holders |
| Publication | Explicit permission before any remote, push, or release |

Details: [gap report](docs/sdk-platform-gap-report.md) · [plan](docs/sdk-platform-plan.md).

**Next:** run body and face detection on licensed media.
