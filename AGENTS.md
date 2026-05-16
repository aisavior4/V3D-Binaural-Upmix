# V3D Agent Rules

## Project Goal

V3D is a mobile video spatial audio engine.

Target:
Smartphone video audio -> headphone-friendly spatial / binaural output.

## Current Product Direction

V5.x = Stereo Enhancement
V6.x = Spatial Reconstruction for mobile video

Current focus:

* Camera perspective
* Front / Rear distance
* Body preservation
* Width support
* Elevation is postponed

## Core Rules

* Preserve dry signal.
* Do not destroy center voice.
* Do not use source separation in this phase.
* Do not optimize only for analyzer metrics.
* Listening perception is the final judge.
* GitHub is the source of truth.

## Roles

### Aru / ChatGPT / Codex

Lead developer and technical director.
Owns DSP structure and final implementation decisions.

### Muse / Gemini

Planning and UX reviewer.
Does not write core DSP code.
Checks roadmap, user perception, demo strategy, and scope creep.

### Puzz / Perplexity

Research and QA reviewer.
Checks claims, references, measurements, and risk signals.
Does not decide final product direction.

## Pull Request Rules

Every PR must include:

* What changed
* Why it changed
* Expected listening effect
* Affected presets
* Safety checks


## Product Priority

The priority is not perfect Dolby Atmos reproduction.
The priority is perceptible spatial improvement for ordinary users.

## Merge Policy

Do not merge automatically.
Human approval is required.

