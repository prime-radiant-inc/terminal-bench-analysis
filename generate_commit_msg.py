# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "sqlite-utils"
# ]
# ///
"""
Generate a descriptive commit message for a terminal-bench-analysis commit.

Usage:
    uv run generate_commit_msg.py <commit-hash>

Builds the database from both the commit and its parent, then compares
to produce a message highlighting new submissions, rank changes, and
new task-level records.
"""

import json
import pathlib
import sqlite3
import subprocess
import sys
import tempfile

import sqlite_utils


def extract_submissions(commit_hash, dest_dir):
    """Extract submissions/ tree from a commit into dest_dir using git archive."""
    archive = subprocess.run(
        ["git", "archive", commit_hash, "--", "submissions/"],
        capture_output=True,
    )
    if archive.returncode != 0:
        # Might be no submissions dir at this commit (e.g. initial commit)
        return
    subprocess.run(
        ["tar", "xf", "-", "-C", dest_dir],
        input=archive.stdout,
        check=True,
    )


def build_db(submissions_root, db_path):
    """Build the terminal-bench database from a submissions directory.

    Mirrors the logic in build_db.py but parameterized.
    """
    root = pathlib.Path(submissions_root) / "submissions"
    db = sqlite_utils.Database(db_path, recreate=True)

    submissions = {}
    runs = {}
    tasks = {}
    trials = []

    if not root.exists():
        # Empty state — write empty tables and return
        db["submissions"].create({"slug": str}, pk="slug")
        db["runs"].create({"id": str, "submission": str}, pk="id")
        db["tasks"].create({"task_name": str}, pk="task_name")
        db["trials"].create(
            {"id": str, "submission": str, "task_name": str, "reward": float, "status": str, "run_id": str},
            pk="id",
        )
        return db

    for path in root.rglob("result.json"):
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        if "task_name" not in data:
            continue

        parts = path.relative_to(root).parts
        submission_slug = parts[2]
        run_date = parts[3]

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

        run_id = f"{submission_slug}-{run_date}"
        if run_id not in runs:
            config = data.get("config") or {}
            runs[run_id] = {
                "id": run_id,
                "submission": submission_slug,
                "run_date": run_date,
            }

        task_name = data["task_name"]
        if task_name not in tasks:
            tasks[task_name] = {"task_name": task_name}

        agent_result = data.get("agent_result") or {}
        exception_info = data.get("exception_info") or {}
        verifier_result = data.get("verifier_result") or {}
        rewards = verifier_result.get("rewards") or {}

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
            "status": status,
            "reward": reward,
            "n_input_tokens": agent_result.get("n_input_tokens"),
            "n_output_tokens": agent_result.get("n_output_tokens"),
            "cost_usd": agent_result.get("cost_usd"),
            "exception_type": exception_info.get("exception_type"),
            "started_at": data.get("started_at"),
            "finished_at": data.get("finished_at"),
        })

    db["submissions"].insert_all(submissions.values(), pk="slug")
    db["runs"].insert_all(runs.values(), pk="id")
    db["tasks"].insert_all(tasks.values(), pk="task_name")
    db["trials"].insert_all(trials, pk="id")
    for col in ["submission", "task_name", "status", "reward", "run_id"]:
        db["trials"].create_index([col], if_not_exists=True)
    db["trials"].create_index(["submission", "task_name"], if_not_exists=True)

    return db


def compare_databases(before_db_path, after_db_path, commit_hash):
    """Compare before/after databases and generate a commit message."""
    conn = sqlite3.connect(after_db_path)
    conn.execute(f"ATTACH DATABASE '{before_db_path}' AS before_db")
    conn.row_factory = sqlite3.Row

    # --- What submissions are new? ---
    new_submissions = conn.execute("""
        SELECT slug FROM main.submissions
        WHERE slug NOT IN (SELECT slug FROM before_db.submissions)
    """).fetchall()
    new_slugs = [r["slug"] for r in new_submissions]

    # --- What submissions were removed? ---
    removed_submissions = conn.execute("""
        SELECT slug FROM before_db.submissions
        WHERE slug NOT IN (SELECT slug FROM main.submissions)
    """).fetchall()
    removed_slugs = [r["slug"] for r in removed_submissions]

    # --- Did the README change? ---
    readme_changed = False
    diff_files = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", commit_hash],
        capture_output=True, text=True,
    )
    changed_files = diff_files.stdout.strip().split("\n")
    readme_changed = "README.md" in changed_files
    submission_files_changed = any(f.startswith("submissions/") for f in changed_files)

    # --- New submission stats ---
    new_sub_stats = []
    for slug in new_slugs:
        row = conn.execute("""
            SELECT
                submission,
                count(*) as n_trials,
                sum(case when status = 'passed' then 1 else 0 end) as n_passed,
                round(avg(reward), 4) as avg_reward
            FROM main.trials
            WHERE submission = ?
            GROUP BY submission
        """, (slug,)).fetchone()
        if row:
            new_sub_stats.append(dict(row))

    # --- Leaderboard: before and after rankings ---
    before_ranking = conn.execute("""
        SELECT
            submission,
            round(avg(reward), 4) as avg_reward,
            count(*) as n_trials
        FROM before_db.trials
        GROUP BY submission
        ORDER BY avg_reward DESC
    """).fetchall()
    before_ranks = {r["submission"]: (i + 1, r["avg_reward"]) for i, r in enumerate(before_ranking)}

    after_ranking = conn.execute("""
        SELECT
            submission,
            round(avg(reward), 4) as avg_reward,
            count(*) as n_trials
        FROM main.trials
        GROUP BY submission
        ORDER BY avg_reward DESC
    """).fetchall()
    after_ranks = {r["submission"]: (i + 1, r["avg_reward"]) for i, r in enumerate(after_ranking)}

    total_submissions_after = len(after_ranks)

    # --- New task-level records ---
    # Tasks where a new submission now holds the best avg_reward
    new_task_records = []
    if new_slugs:
        placeholders = ",".join("?" for _ in new_slugs)
        new_task_records = conn.execute(f"""
            WITH after_task_scores AS (
                SELECT
                    task_name,
                    submission,
                    round(avg(reward), 4) as avg_reward
                FROM main.trials
                GROUP BY task_name, submission
            ),
            best_per_task AS (
                SELECT
                    task_name,
                    submission,
                    avg_reward,
                    ROW_NUMBER() OVER (PARTITION BY task_name ORDER BY avg_reward DESC) as rn
                FROM after_task_scores
            ),
            before_best AS (
                SELECT
                    task_name,
                    max(avg_reward) as best_reward
                FROM (
                    SELECT task_name, submission, round(avg(reward), 4) as avg_reward
                    FROM before_db.trials
                    GROUP BY task_name, submission
                )
                GROUP BY task_name
            )
            SELECT
                b.task_name,
                b.submission,
                round(b.avg_reward, 4) as new_score,
                round(bb.best_reward, 4) as prev_best
            FROM best_per_task b
            LEFT JOIN before_best bb ON b.task_name = bb.task_name
            WHERE b.rn = 1
              AND b.submission IN ({placeholders})
              AND (bb.best_reward IS NULL OR b.avg_reward > bb.best_reward)
            ORDER BY b.task_name
        """, new_slugs).fetchall()

    # --- Existing submissions with new runs (more trials than before) ---
    updated_submissions = conn.execute("""
        SELECT
            a.submission,
            a.cnt as after_count,
            b.cnt as before_count
        FROM (SELECT submission, count(*) as cnt FROM main.trials GROUP BY submission) a
        JOIN (SELECT submission, count(*) as cnt FROM before_db.trials GROUP BY submission) b
            ON a.submission = b.submission
        WHERE a.cnt > b.cnt
    """).fetchall()

    conn.close()

    # --- Build the message ---
    lines = []

    # Title line
    if not submission_files_changed and readme_changed:
        lines.append("Regenerate README (no new data)")
        return "\n".join(lines)

    if not new_slugs and not removed_slugs and not updated_submissions:
        if readme_changed:
            lines.append("Regenerate README")
        else:
            lines.append("Update metadata (no submission changes)")
        return "\n".join(lines)

    # Build title from new submissions
    if new_slugs:
        total_new_trials = sum(s["n_trials"] for s in new_sub_stats)
        if len(new_slugs) == 1:
            stat = new_sub_stats[0]
            slug = stat["submission"]
            rank = after_ranks.get(slug, (None, None))[0]
            pct = round(stat["avg_reward"] * 100, 1)
            title = f"Add {slug} ({stat['n_trials']} trials, {pct}% pass"
            if rank:
                title += f" — ranks #{rank}/{total_submissions_after}"
            title += ")"
            lines.append(title)
        else:
            slugs_str = ", ".join(new_slugs[:3])
            if len(new_slugs) > 3:
                slugs_str += f" +{len(new_slugs) - 3} more"
            lines.append(f"Add {total_new_trials} trials for {len(new_slugs)} submissions: {slugs_str}")
    elif updated_submissions:
        updated_slugs = [r["submission"] for r in updated_submissions]
        total_new = sum(r["after_count"] - r["before_count"] for r in updated_submissions)
        lines.append(f"Add {total_new} new trials for {', '.join(updated_slugs[:3])}")

    if removed_slugs:
        lines.append(f"Remove: {', '.join(removed_slugs[:5])}")

    # Body details
    details = []

    # Where do the new submissions land on the leaderboard?
    for stat in sorted(new_sub_stats, key=lambda s: s["avg_reward"], reverse=True):
        slug = stat["submission"]
        rank_after = after_ranks.get(slug, (None, None))[0]
        pct = round(stat["avg_reward"] * 100, 1)

        # Find the neighbors
        sorted_after = sorted(after_ranks.items(), key=lambda x: x[1][0])
        if rank_after and rank_after <= 10:
            if rank_after == 1:
                details.append(f"  NEW #1! {slug} at {pct}%")
                if len(sorted_after) > 1:
                    runner_up = sorted_after[1]
                    details[-1] += f" (prev leader: {runner_up[0]} at {round(runner_up[1][1] * 100, 1)}%)"
            else:
                prev_entry = sorted_after[rank_after - 2]  # one rank above
                details.append(
                    f"  {slug} enters top 10 at #{rank_after} ({pct}%), "
                    f"behind {prev_entry[0]} ({round(prev_entry[1][1] * 100, 1)}%)"
                )
        elif rank_after:
            details.append(f"  {slug}: {pct}% pass, #{rank_after}/{total_submissions_after}")

    # Top 5 status
    top5_after = sorted(after_ranks.items(), key=lambda x: x[1][0])[:5]
    top5_changed = False
    for slug, (rank, score) in top5_after:
        before = before_ranks.get(slug)
        if before is None or before[0] != rank:
            top5_changed = True
            break
    if not top5_changed and new_slugs:
        leader = top5_after[0]
        details.append(f"  Top 5 unchanged ({leader[0]} leads at {round(leader[1][1] * 100, 1)}%)")

    # New task-level records
    if new_task_records:
        if len(new_task_records) <= 5:
            task_list = ", ".join(r["task_name"] for r in new_task_records)
            details.append(f"  New task-level bests: {task_list}")
        else:
            details.append(f"  {len(new_task_records)} new task-level bests")

    if readme_changed:
        details.append("  README regenerated")

    if details:
        lines.append("")
        lines.extend(details)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run generate_commit_msg.py <commit-hash>", file=sys.stderr)
        sys.exit(1)

    commit_hash = sys.argv[1]

    # Resolve to full hash
    full_hash = subprocess.run(
        ["git", "rev-parse", commit_hash],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    parent_hash = subprocess.run(
        ["git", "rev-parse", f"{full_hash}~1"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    print(f"Comparing {parent_hash[:8]} (before) → {full_hash[:8]} (after)", file=sys.stderr)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        before_dir = tmpdir / "before"
        after_dir = tmpdir / "after"
        before_dir.mkdir()
        after_dir.mkdir()

        print("Extracting before state...", file=sys.stderr)
        extract_submissions(parent_hash, str(before_dir))

        print("Extracting after state...", file=sys.stderr)
        extract_submissions(full_hash, str(after_dir))

        before_db_path = str(tmpdir / "before.db")
        after_db_path = str(tmpdir / "after.db")

        print("Building before database...", file=sys.stderr)
        build_db(str(before_dir), before_db_path)

        print("Building after database...", file=sys.stderr)
        build_db(str(after_dir), after_db_path)

        print("Comparing...", file=sys.stderr)
        msg = compare_databases(before_db_path, after_db_path, full_hash)

    print(msg)


if __name__ == "__main__":
    main()
