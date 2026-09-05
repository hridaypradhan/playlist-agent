# Playlist Agent

A goal-driven playlist curation system for creating and editing playlists under explicit user constraints and objectives.

Playlist Agent treats playlist curation as a state-changing decision problem rather than a one-shot recommendation task. Given a music catalog, an existing playlist, a set of hard constraints, and an optimization objective, the system selects and executes playlist edits, validates the resulting state, and records an auditable execution trace.

The current implementation is a deterministic baseline designed to establish reproducible behavior and evaluation criteria for a future agentic system.

## Overview

Playlist editing often involves multiple requirements at the same time. A user might want to preserve particular tracks, exclude explicit content, enforce tempo requirements, control playlist duration, avoid repeated artists, and shape the energy progression of the playlist.

Rather than returning a textual list of recommendations, Playlist Agent operates on an explicit playlist state. The current baseline can:

- load a local music catalog and existing playlist;
- evaluate the playlist against hard constraints;
- remove tracks that violate supported per-track constraints;
- search feasible combinations of replacement tracks;
- optimize candidate selections according to a configurable objective;
- reorder tracks according to a supported energy-order constraint;
- detect basic contradictory constraints and catalog-limited failure cases;
- save the resulting playlist; and
- record structured JSONL events describing validations, decisions, actions, and failures.

### Current baseline vs. project direction

The current system uses a deterministic, rule-based policy with a fixed repair workflow. It does **not** yet use an LLM or dynamically choose arbitrary next actions.

The longer-term project is to replace this fixed policy with an agent that can interpret natural-language playlist goals, choose tools based on the current state and feedback, resolve or negotiate conflicting constraints, and iteratively act until the user's goal is satisfied or the task is determined to be infeasible.

## Baseline Architecture

The baseline separates the playlist environment, state, actions, evaluation, objectives, and orchestration:

```text
Test case
   |
   +---- hard constraints
   |
   +---- optimization objective
   |
   v
Playlist state <---- Music catalog
   |
   v
Validate
   |
   v
Deterministic baseline policy
   |
   +---- remove track
   +---- select/add tracks
   +---- reorder tracks
   |
   v
Validate resulting state
   |
   +---- success
   |
   +---- explicit failure
   |
   v
Playlist JSON + execution trace
```

For the current baseline, the repair workflow is fixed. The execution trace makes each state-changing decision inspectable rather than treating the result as a black box.

## Project Structure

```text
playlist-agent/
├── data/
│   ├── songs.json
│   └── playlists/
│       └── demo.json
├── examples/
│   ├── test1.json
│   ├── test_impossible.json
│   └── test_catalog_impossible.json
├── outputs/
├── scripts/
│   └── check_environment.py
├── src/
│   └── playlist_agent/
│       ├── __init__.py
│       ├── actions.py
│       ├── baseline.py
│       ├── catalog.py
│       ├── environment.py
│       ├── evaluation.py
│       ├── feasibility.py
│       ├── objectives.py
│       ├── selection.py
│       ├── state.py
│       ├── trace.py
│       └── validator.py
├── tests/
├── pyproject.toml
├── run_baseline.py
└── README.md
```

`data/` contains the local playlist environment and music catalog used by the baseline. `examples/` contains reproducible task specifications. `src/playlist_agent/` contains the implementation, while `tests/` contains development and scenario tests. `outputs/` is used for generated playlist artifacts and execution traces.

## Requirements

- Python 3.10 or newer
- Git

The current baseline uses only Python's standard library at runtime. No GPU, local language model, Spotify account, Spotify Premium subscription, or external API credentials are required.

## Quick Start

Clone the repository and create a virtual environment:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd playlist-agent

python -m venv .venv
.venv\Scripts\Activate.ps1
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

Install the project in editable mode:

```powershell
python -m pip install -e .
```

Run the reproducible baseline example:

```powershell
python run_baseline.py --input examples/test1.json
```

The baseline should report a successful result with all seven hard constraints satisfied.

The run produces:

```text
outputs/test1_playlist.json
outputs/test1_trace.jsonl
```

The first file contains the resulting playlist. The second contains the structured execution trace.

### Running the Failure Examples

A contradictory-constraint example is available at:

```powershell
python run_baseline.py --input examples/test_impossible.json
```

A catalog-limited infeasibility example is available at:

```powershell
python run_baseline.py --input examples/test_catalog_impossible.json
```

These cases demonstrate that the baseline distinguishes successful execution from explicit failure.

## Input Format

A run is defined by a JSON task specification containing three components:

1. a playlist and music catalog describing the environment;
2. hard constraints that every successful output must satisfy; and
3. an objective used to choose among feasible outputs.

The primary reproducible example is `examples/test1.json`:

```json
{
  "playlist": "data/playlists/demo.json",
  "catalog": "data/songs.json",
  "constraints": {
    "min_bpm": 110,
    "allow_explicit": false,
    "unique_artist": true,
    "energy_order": "ascending",
    "must_keep": [
      "track_002"
    ],
    "min_duration_sec": 780,
    "max_duration_sec": 900
  },
  "objective": {
    "type": "maximize_duration"
  }
}
```

### Hard Constraints

The current baseline supports the following constraint fields:

| Constraint | Meaning |
| --- | --- |
| `min_bpm` | Every selected track must meet or exceed the specified BPM. |
| `allow_explicit` | When `false`, explicit tracks are not permitted. |
| `unique_artist` | When `true`, an artist may appear at most once. |
| `energy_order` | Requires track energy to be ordered `"ascending"` or `"descending"`. |
| `must_keep` | Track IDs that must remain in the resulting playlist. |
| `min_duration_sec` | Minimum total playlist duration in seconds. |
| `max_duration_sec` | Maximum total playlist duration in seconds. |

For the current baseline, these are **hard constraints**: a run is successful only when every specified constraint is satisfied.

Constraint processing order does not imply priority. If the requirements cannot all be satisfied, the baseline reports failure rather than intentionally relaxing one of them.

### Objectives

Constraints determine whether a playlist is feasible. The objective determines which feasible playlist is preferred.

The current objective implementations are:

| Objective | Behavior |
| --- | --- |
| `maximize_duration` | Prefer the feasible playlist with the greatest total duration. |
| `maximize_track_count` | Prefer the feasible playlist containing the greatest number of tracks. |

For example:

```json
{
  "objective": {
    "type": "maximize_duration"
  }
}
```

The separation between hard constraints and objectives is intentional. A future agent may infer from natural-language requests whether a playlist property is mandatory or merely preferred, and may need to reason about tradeoffs when multiple preferences compete.

## Music Data

The current baseline operates on local JSON metadata rather than a streaming-service API. This keeps the baseline deterministic, lightweight, and reproducible without requiring user accounts or external credentials.

Each catalog entry contains metadata such as:

```json
{
  "id": "track_005",
  "title": "Redline",
  "artist": "Signal Fire",
  "genre": "electronic",
  "duration_sec": 205,
  "bpm": 136,
  "energy": 0.91,
  "explicit": false
}
```

The music catalog included in the current baseline is a small synthetic development dataset. It is intended to exercise playlist-editing behavior and is not presented as a production recommendation dataset.

The architecture is designed so that the local catalog can later be replaced or expanded with a larger music metadata source without coupling the core playlist logic to Spotify or another streaming platform.

## Example Baseline Run

Running:

```powershell
python run_baseline.py --input examples/test1.json
```

starts with the five-track `Demo Workout Mix`.

The initial playlist violates several requested constraints. The deterministic baseline:

1. evaluates the initial playlist;
2. removes tracks that violate supported per-track constraints;
3. searches feasible combinations of catalog tracks;
4. selects additions according to the requested objective;
5. reorders the playlist when necessary to satisfy the requested energy ordering; and
6. validates the resulting playlist.

For the included example, the final playlist is:

| Order | Track | Artist | BPM | Energy | Duration |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | Open Road | Paper Satellites | 114 | 0.57 | 231 s |
| 2 | Forward Motion | Luna Vale | 118 | 0.62 | 198 s |
| 3 | Static Rush | Northbound | 126 | 0.78 | 224 s |
| 4 | Redline | Signal Fire | 136 | 0.91 | 205 s |

Total duration:

```text
858 seconds (14 minutes 18 seconds)
```

Final constraint result:

```text
7/7 constraints satisfied
```

The generated playlist is written to:

```text
outputs/test1_playlist.json
```

## Execution Trace

Each run also produces a JSONL execution trace. Rather than exposing only the final playlist, the trace records structured events describing what the baseline evaluated and changed.

The current event types include:

- `validation` — records the number of satisfied constraints and the constraints that remain violated;
- `decision` — records a structured policy decision, such as selecting additions according to an objective;
- `action` — records an executed state-changing operation and the evidence relevant to that operation; and
- `failure` — records why the system terminated without a feasible solution.

For example, an action event may look like:

```json
{
  "step": 2,
  "event": "action",
  "action": "remove_track",
  "track_id": "track_001",
  "reason": "violates_min_bpm",
  "evidence": {
    "track_bpm": 105,
    "required_min_bpm": 110
  }
}
```

A later reordering event records both the state before and after the operation:

```json
{
  "event": "action",
  "action": "reorder_playlist",
  "reason": "violates_energy_order",
  "evidence": {
    "requested_order": "ascending",
    "energies_before": [0.62, 0.78, 0.91, 0.57],
    "energies_after": [0.57, 0.62, 0.78, 0.91]
  }
}
```

The trace is intended to make the baseline's externally observable decision process auditable and to provide a common trajectory format that future agentic implementations can extend.

## Success and Failure

A run succeeds when all specified hard constraints are satisfied:

```text
success = all hard constraints satisfied
```

The baseline currently distinguishes between multiple failure conditions, including:

- directly contradictory constraints, such as a minimum duration greater than the maximum duration;
- failure to find a feasible set of catalog additions within the baseline's fixed repair workflow; and
- termination with one or more constraints still unsatisfied.

This distinction is important because an infeasible request should not be presented as a successful playlist simply because the system produced an output.

## Current Limitations

The current implementation is intentionally a deterministic baseline rather than the final agentic system.

Its main limitations are:

- **Structured input only.** User goals must currently be expressed through predefined JSON constraints and objectives rather than natural language.
- **Fixed orchestration.** The baseline follows a predefined repair workflow instead of dynamically choosing the next action from the current state and feedback.
- **Limited constraint vocabulary.** Only the currently implemented constraint types can be represented and validated.
- **Limited objective vocabulary.** Objective selection is explicit and currently limited to the implemented scoring functions.
- **Hard constraints only.** The baseline does not yet distinguish between mandatory requirements and softer preferences expressed by a user.
- **Limited conflict handling.** Some infeasible requests can be detected, but the system does not negotiate which constraint or preference should be relaxed.
- **Stage-based optimization.** Removal, addition, and reordering are handled in separate stages rather than through global planning over arbitrary edit sequences.
- **Exhaustive candidate search.** Addition selection enumerates candidate subsets, which is suitable for the small development catalog but does not scale to large music collections.
- **Simple ordering model.** Energy ordering currently uses deterministic numerical sorting rather than reasoning about richer playlist flow or transitions.
- **No user memory.** Feedback and preferences are not retained across sessions.
- **Synthetic development data.** The included catalog is intentionally small and does not represent the diversity or scale of a production music dataset.
- **No streaming-service integration.** The current environment operates entirely on local metadata and does not modify playlists on Spotify or another external platform.

These limitations establish the baseline against which later agentic capabilities can be evaluated.

## Roadmap

The longer-term goal is a natural-language playlist curation agent that can reason over user goals, choose and execute playlist-editing tools, observe the consequences of those actions, and continue until the task succeeds, fails, or requires user input.

### 1. Natural-Language Goal Interpretation

Replace manually authored JSON task specifications with natural-language requests such as:

> "Turn this into a 45-minute workout playlist. Keep these two songs, avoid explicit tracks, don't repeat artists, and gradually build the energy toward the end."

The system would translate the request into structured constraints, preferences, and objectives that can be validated against the playlist environment.

### 2. Dynamic Agent Loop

Replace the baseline's fixed repair sequence with a feedback-driven loop:

```text
observe current playlist and goal
            |
            v
     decide next action
            |
            v
       execute tool
            |
            v
      observe result
            |
            v
        re-evaluate
            |
       +----+----+
       |         |
   continue    finish/fail
```

Instead of always executing removal, addition, and reordering in a predetermined sequence, the agent would choose its next action based on the current state and previous tool results.

Potential tools include:

```text
inspect_playlist()
search_catalog()
add_track()
remove_track()
replace_track()
move_track()
reorder_playlist()
compute_playlist_stats()
validate_constraints()
save_playlist()
```

### 3. Hard Constraints and Soft Preferences

Natural-language requests do not always assign equal importance to every desired property.

For example:

> "Do not include explicit tracks."

is naturally interpreted as a hard constraint, while:

> "Try to keep the energy building toward the end."

may be a softer preference.

A future system should distinguish:

```text
hard constraints
    -> must be satisfied

soft preferences
    -> optimize when possible
```

The same playlist property may be hard or soft depending on how the user expresses it.

### 4. Constraint Conflict Detection and Negotiation

Some user requests may be impossible to satisfy simultaneously.

Rather than silently violating a requirement, the future agent should identify the conflict and, when appropriate, return control to the user.

For example:

```text
Requested:
- maximum duration: 30 minutes
- at least 10 tracks

Available catalog:
- no feasible 10-track combination fits within 30 minutes
```

A future agent could explain the conflict and ask whether to relax the duration or track-count requirement.

### 5. User-Specified and Multi-Objective Optimization

Different users may want different definitions of a "best" feasible playlist.

Examples include:

- maximize playlist duration;
- maximize number of tracks;
- preserve as much of the original playlist as possible;
- maximize artist or genre diversity;
- minimize unnecessary edits;
- prefer smoother transitions; or
- balance several objectives simultaneously.

Future versions can support weighted or context-dependent objectives inferred from natural-language requests.

### 6. Richer Playlist Ordering and Flow

The current baseline interprets energy ordering as numerical sorting.

Future ordering strategies could support requests such as:

- gradually build energy;
- peak near the middle;
- build toward a finale;
- alternate intensity;
- begin energetic and end with a cooldown;
- avoid abrupt genre or tempo transitions; or
- preserve selected tracks at specific positions.

This turns playlist ordering from a simple sorting operation into a planning problem over the playlist as a whole.

### 7. Memory and Personalization

The agent could retain useful preference feedback across interactions.

For example:

```text
User feedback:
"I don't like long intros in running playlists."
```

could later influence another request such as:

```text
"Make me another running playlist."
```

Memory would allow the system to move from one-shot constraint satisfaction toward personalized curation.

### 8. Playlist Diagnosis and Repair

Creation and editing can be extended with diagnostic behavior.

For a request such as:

> "Why does this playlist lose momentum in the middle?"

the agent could inspect playlist statistics and transitions, identify likely outliers or structural problems, propose changes, execute approved edits, and validate the resulting playlist.

Diagnosis therefore becomes another path into the same underlying playlist-editing environment rather than a separate system.

### 9. Scalable Search and Real Music Data

The exhaustive subset search used by the current baseline is intentionally simple and transparent, but it will not scale to realistic catalogs.

Future work can explore:

- heuristic and constrained search;
- optimization algorithms;
- retrieval and ranking;
- embeddings and semantic metadata;
- larger public music datasets; and
- more efficient candidate generation.

The local environment can remain useful for reproducible evaluation even if external music sources are added.

### 10. External Integrations

The core playlist reasoning system is intentionally decoupled from Spotify or another streaming platform.

A future integration layer could optionally synchronize the resulting playlist with an external service while keeping the underlying agent, evaluation, and test environment service-independent.

This separation allows the system to remain reproducible for development and evaluation without requiring every user or evaluator to have the same streaming account or subscription.

## Evaluation Direction

The current baseline provides deterministic behavior that future implementations can be compared against.

Potential evaluation metrics include:

- **hard-constraint satisfaction rate** — proportion of requested hard constraints satisfied;
- **task success rate** — proportion of tasks for which all hard constraints are satisfied;
- **objective score** — performance on the user-selected optimization objective;
- **playlist preservation** — proportion of original tracks retained when preservation is desired;
- **edit efficiency** — number of additions, removals, replacements, and moves required to reach the final state;
- **trajectory efficiency** — number of decisions or tool calls required to complete a task;
- **failure recognition** — ability to identify infeasible requests rather than returning invalid results;
- **recovery rate** — ability to recover from invalid actions or tool failures;
- **preference satisfaction** — degree to which soft user preferences are met; and
- **human evaluation** — stakeholder judgment of playlist quality, usefulness, and faithfulness to the request.

The execution trace provides a basis for evaluating both the final outcome and the process used to reach it.

## Development and AI Assistance

This project was developed with assistance from **OpenAI ChatGPT**.

ChatGPT was used for project ideation, architecture discussion, implementation guidance, debugging, test design, and documentation support. The repository owner reviewed and tested the implementation, made design decisions throughout development, and validated the behavior of the runnable baseline.

This disclosure describes AI assistance used during development; it does not imply that the current baseline itself uses an LLM at runtime. The current baseline is deterministic and rule-based.

For academic submissions associated with this project, course-specific generative AI disclosure and interaction-record requirements are handled separately in accordance with the applicable course policy.

## Project Context

Playlist Agent began as a baseline implementation for an Agentic AI capstone project and is being developed as a broader exploration of goal-directed, tool-using playlist curation.

The initial baseline intentionally emphasizes reproducibility, explicit state transitions, deterministic evaluation, and inspectable execution traces. These components provide a controlled environment for comparing future agentic implementations against a known starting point.
