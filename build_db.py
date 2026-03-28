# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "sqlite-utils"
# ]
# ///

import json
import pathlib
import sqlite_utils

ROOT = pathlib.Path("submissions")
DB_PATH = "terminal-bench.db"

db = sqlite_utils.Database(DB_PATH, recreate=True)

submissions = {}  # submission slug -> row
runs = {}  # (submission, run_id) -> row
tasks = {}  # task_name -> row
trials = []

for path in ROOT.rglob("result.json"):
    data = json.loads(path.read_text())

    if "task_name" not in data:
        continue

    # Extract submission and run_id from path:
    # .../submissions/terminal-bench/2.0/{submission}/{run_id}/{trial}/result.json
    parts = path.relative_to(ROOT).parts
    submission_slug = parts[2]  # e.g. "Ante__Gemini-3-Pro-Preview"
    run_date = parts[3]  # e.g. "2025-12-31__22-36-36"

    # --- submissions ---
    if submission_slug not in submissions:
        config_agent = (data.get("config") or {}).get("agent") or {}
        agent_info = data.get("agent_info") or {}
        model_info = agent_info.get("model_info") or {}
        submissions[submission_slug] = {
            "slug": submission_slug,
            "agent_name": agent_info.get("name"),
            "agent_version": agent_info.get("version"),
            "agent_import_path": config_agent.get("import_path"),
            "model_name": config_agent.get("model_name"),
            "model_provider": model_info.get("provider") if model_info else None,
        }

    # --- runs ---
    run_id = f"{submission_slug}-{run_date}"
    if run_id not in runs:
        config = data.get("config") or {}
        runs[run_id] = {
            "id": run_id,
            "submission": submission_slug,
            "run_date": run_date,
            "job_id": config.get("job_id"),
            "timeout_multiplier": config.get("timeout_multiplier"),
            "environment_type": (config.get("environment") or {}).get("type"),
        }

    # --- tasks ---
    task_name = data["task_name"]
    if task_name not in tasks:
        task_id = data.get("task_id") or {}
        tasks[task_name] = {
            "task_name": task_name,
            "source": data.get("source"),
            "git_url": task_id.get("git_url"),
            "git_commit_id": task_id.get("git_commit_id"),
            "task_checksum": data.get("task_checksum"),
        }

    # --- trial ---
    agent_result = data.get("agent_result") or {}
    exception_info = data.get("exception_info") or {}
    verifier_result = data.get("verifier_result") or {}
    rewards = verifier_result.get("rewards") or {}

    env_setup = data.get("environment_setup") or {}
    agent_setup = data.get("agent_setup") or {}
    agent_exec = data.get("agent_execution") or {}
    verifier = data.get("verifier") or {}

    # Determine status: passed / failed / errored
    reward = rewards.get("reward")
    has_exception = bool(exception_info.get("exception_type"))
    if reward == 1.0:
        status = "passed"
    elif has_exception:
        status = "errored"
    else:
        status = "failed"

    trials.append({
        "id": data["id"],
        "run_id": run_id,
        "submission": submission_slug,
        "task_name": task_name,
        "trial_name": data["trial_name"],
        # outcome
        "status": status,
        "reward": reward,
        # agent usage
        "n_input_tokens": agent_result.get("n_input_tokens"),
        "n_output_tokens": agent_result.get("n_output_tokens"),
        "n_cache_tokens": agent_result.get("n_cache_tokens"),
        "cost_usd": agent_result.get("cost_usd"),
        # exception
        "exception_type": exception_info.get("exception_type"),
        "exception_message": exception_info.get("exception_message"),
        "exception_occurred_at": exception_info.get("occurred_at"),
        # timestamps
        "started_at": data.get("started_at"),
        "finished_at": data.get("finished_at"),
        # phase timestamps
        "env_setup_started_at": env_setup.get("started_at"),
        "env_setup_finished_at": env_setup.get("finished_at"),
        "agent_setup_started_at": agent_setup.get("started_at"),
        "agent_setup_finished_at": agent_setup.get("finished_at"),
        "agent_exec_started_at": agent_exec.get("started_at"),
        "agent_exec_finished_at": agent_exec.get("finished_at"),
        "verifier_started_at": verifier.get("started_at"),
        "verifier_finished_at": verifier.get("finished_at"),
        # source file
        "file_path": str(path),
    })

# --- Write tables ---

db["submissions"].insert_all(submissions.values(), pk="slug")
print(f"  submissions: {len(submissions)}")

db["runs"].insert_all(runs.values(), pk="id")
db["runs"].add_foreign_key("submission", "submissions", "slug", ignore=True)
print(f"  runs: {len(runs)}")

db["tasks"].insert_all(tasks.values(), pk="task_name")
print(f"  tasks: {len(tasks)}")

db["trials"].insert_all(trials, pk="id")
db["trials"].add_foreign_key("run_id", "runs", "id", ignore=True)
db["trials"].add_foreign_key("submission", "submissions", "slug", ignore=True)
db["trials"].add_foreign_key("task_name", "tasks", "task_name", ignore=True)
print(f"  trials: {len(trials)}")

# --- Indexes ---
for col in ["submission", "task_name", "status", "reward", "run_id", "exception_type"]:
    db["trials"].create_index([col], if_not_exists=True)
db["trials"].create_index(["submission", "task_name"], if_not_exists=True)

# --- Views ---
db.execute("DROP VIEW IF EXISTS task_stats")
db.execute("""
CREATE VIEW task_stats AS
SELECT
    task_name,
    count(*) AS n_trials,
    sum(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) AS n_passed,
    sum(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS n_failed,
    sum(CASE WHEN status = 'errored' THEN 1 ELSE 0 END) AS n_errored,
    round(avg(reward), 4) AS avg_reward,
    round(1.0 - avg(reward), 4) AS failure_rate
FROM trials
GROUP BY task_name
""")

db.execute("DROP VIEW IF EXISTS submission_stats")
db.execute("""
CREATE VIEW submission_stats AS
SELECT
    submission,
    count(*) AS n_trials,
    sum(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) AS n_passed,
    sum(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS n_failed,
    sum(CASE WHEN status = 'errored' THEN 1 ELSE 0 END) AS n_errored,
    round(avg(reward), 4) AS avg_reward,
    round(sum(cost_usd), 2) AS total_cost_usd,
    round(avg(cost_usd), 4) AS avg_cost_usd,
    sum(n_input_tokens) AS total_input_tokens,
    sum(n_output_tokens) AS total_output_tokens
FROM trials
GROUP BY submission
""")

db.execute("DROP VIEW IF EXISTS submission_task_matrix")
db.execute("""
CREATE VIEW submission_task_matrix AS
SELECT
    submission,
    task_name,
    count(*) AS n_trials,
    round(avg(reward), 4) AS avg_reward,
    sum(CASE WHEN status = 'errored' THEN 1 ELSE 0 END) AS n_errored,
    group_concat(DISTINCT exception_type) AS exception_types
FROM trials
GROUP BY submission, task_name
""")

print(f"\nLoaded into {DB_PATH} with tables: submissions, runs, tasks, trials")
print(f"Views: task_stats, submission_stats, submission_task_matrix")
