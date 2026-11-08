# TODO

Items are grouped by the condition that opens them.

## Defects observed against the layout of project repositories

The assessment of 2026-11-08 checked Meandra against the common layout of the project repositories of Geonexus. Meandra fits that layout when the package of a project calls it from its own interface and passes it paths under `data/`. The following defects of Meandra itself would harm such a project.

- [ ] **Store the path of a checkpoint relative to its folder.** The metadata of a checkpoint, in `src/meandra/checkpoint/storage.py`, stores `data_path` as it was given, and loading reads that stored path. Resuming therefore breaks when the repository moves, for an absolute path, or when a run starts from another folder, for a relative path.
- [ ] **Resume from the checkpoint of the same run.** The latest checkpoint, in `src/meandra/checkpoint/manager.py`, is the most recent one of the workflow, from any run. Two runs of a sweep that share one folder can therefore resume from each other. Select the checkpoint by run, or give each run its own folder.
- [ ] **Pass the identifier of a run to the data catalog.** The orchestrator keeps its `run_id` local, so a template of the catalog that holds `{run_id}` needs the identifier by hand.
- [ ] **Let a project set the storage of a run.** `meandra run`, in `src/meandra/cli_app.py`, builds `SchedulingOrchestrator()` without checkpoints, run state or log. Offer a function such as `run_pipeline(...)` that takes those paths, for the interface of a project.
- [ ] **Implement or remove the snapshot of a configuration.** `ConfigProvider.snapshot`, in `src/meandra/configuration/mod.py`, is declared and never implemented or called, and `omegaconf` is declared as a dependency but never imported. `ParameterSet` of Tessara is no `ConfigProvider`, contrary to `docs/guide/configuration.md`.
- [ ] **Create the folder of a log file.** `configure_logging`, in `src/meandra/logging/config.py`, fails when the folder of `log_file` is missing.
- [ ] **Repair the failing test and the documented example.** One test fails with a `TypeError` in `src/meandra/integration/data.py`. The example `meandra run examples.configurable_pipeline:…` fails with "No module named 'examples'" unless run with `python -m meandra`. The README links to `docs/architecture/`, which no longer exists.
