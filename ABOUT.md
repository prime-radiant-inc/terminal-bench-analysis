# terminal-bench-analysis

> Fetches Terminal Bench 2 leaderboard JSON results into SQLite and publishes queryable analysis via Datasette.

**Family:** eval-labs · **Type:** tool · **Lifecycle:** production · **Owner:** simonw

## What it does
Fetches detailed JSON results from the Terminal Bench 2 leaderboard (harborframework dataset on Hugging Face), loads them into a SQLite database, and publishes queryable analysis via Datasette. A scheduled GitHub Actions workflow refetches data and commits updated results, so commit history doubles as an Atom feed of newly reported runs. The README is generated with cog from live SQL queries.

## How it fits
- Depends on: — (no internal prime-radiant-inc code/service dependencies; see prose) — Pulls a public Hugging Face dataset and serves it through Datasette. No prime-radiant-inc code or service dependency.
- Used by: —
- External: Hugging Face datasets; Datasette; GitHub Actions; primeradiant.com hosting

## Runtime & data
- Runs: Python scripts + GitHub Actions cron; Datasette (datasette-lite) for queries
- Data in: Terminal Bench 2 leaderboard JSON (Hugging Face dataset)
- Data out: terminal-bench.db SQLite; published Datasette queries; cog-generated README

<!-- Maintained by the maintaining-project-map skill. Do not hand-edit; regenerated. -->
