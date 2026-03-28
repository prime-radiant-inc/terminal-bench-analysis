# terminal-bench-analysis

This repo fetches just the detailed JSON results from [harborframework/terminal-bench-2-leaderboard](https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard) and loads them into a SQLite database for further analysis.

Run SQL queries against the resulting database here:

https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench

<!--[[[cog
import cog
import os
import sqlite3
import textwrap

DB = "terminal-bench.db"
BLANK = os.environ.get("COG_BLANK")

def run_sql(sql):
    sql = textwrap.dedent(sql).strip()
    cog.outl("```sql")
    cog.outl(sql)
    cog.outl("```")
    cog.outl("")
    if BLANK:
        return
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql).fetchall()
    if not rows:
        cog.outl("No results.")
        conn.close()
        return
    cols = rows[0].keys()
    cog.outl("| " + " | ".join(cols) + " |")
    cog.outl("| " + " | ".join("---" for _ in cols) + " |")
    for row in rows:
        cog.outl("| " + " | ".join(str(v) for v in row) + " |")
    conn.close()
]]]-->
<!--[[[end]]]-->

## Overall Leaderboard

Which agent/model combination scores the highest across all tasks?

<!--[[[cog
run_sql("""
    select submission, n_trials, n_passed, n_failed, n_errored, avg_reward
    from submission_stats
    order by avg_reward desc
""")
]]]-->
```sql
select submission, n_trials, n_passed, n_failed, n_errored, avg_reward
from submission_stats
order by avg_reward desc
```

<!--[[[end]]]-->

## Best Model per Backbone

Multiple agents use the same underlying model. Which agent gets the most out of each model?

<!--[[[cog
run_sql("""
    select
        s.model_name,
        s.slug as best_submission,
        ss.avg_reward,
        ss.n_passed,
        ss.n_trials
    from submissions s
    join submission_stats ss on ss.submission = s.slug
    where ss.avg_reward = (
        select max(ss2.avg_reward)
        from submissions s2
        join submission_stats ss2 on ss2.submission = s2.slug
        where s2.model_name = s.model_name
    )
    order by ss.avg_reward desc
""")
]]]-->
```sql
select
    s.model_name,
    s.slug as best_submission,
    ss.avg_reward,
    ss.n_passed,
    ss.n_trials
from submissions s
join submission_stats ss on ss.submission = s.slug
where ss.avg_reward = (
    select max(ss2.avg_reward)
    from submissions s2
    join submission_stats ss2 on ss2.submission = s2.slug
    where s2.model_name = s.model_name
)
order by ss.avg_reward desc
```

<!--[[[end]]]-->

## The Hardest Tasks

Which tasks have the highest failure rates across all submissions?

<!--[[[cog
run_sql("""
    select task_name, n_trials, n_passed, n_failed, n_errored, failure_rate
    from task_stats
    order by failure_rate desc
    limit 15
""")
]]]-->
```sql
select task_name, n_trials, n_passed, n_failed, n_errored, failure_rate
from task_stats
order by failure_rate desc
limit 15
```

<!--[[[end]]]-->

## Tasks No One Has Solved

<!--[[[cog
run_sql("""
    select task_name, n_trials, n_failed, n_errored
    from task_stats
    where n_passed = 0
""")
]]]-->
```sql
select task_name, n_trials, n_failed, n_errored
from task_stats
where n_passed = 0
```

<!--[[[end]]]-->

## The Easiest Tasks

<!--[[[cog
run_sql("""
    select task_name, n_trials, n_passed, n_failed, n_errored, avg_reward
    from task_stats
    order by failure_rate asc
    limit 15
""")
]]]-->
```sql
select task_name, n_trials, n_passed, n_failed, n_errored, avg_reward
from task_stats
order by failure_rate asc
limit 15
```

<!--[[[end]]]-->

## Error Analysis

What kinds of errors do agents hit?

<!--[[[cog
run_sql("""
    select
        exception_type,
        count(*) as n,
        round(
            100.0 * count(*) / (
                select count(*) from trials where exception_type is not null
            ),
            1
        ) as pct
    from trials
    where exception_type is not null
    group by exception_type
    order by n desc
""")
]]]-->
```sql
select
    exception_type,
    count(*) as n,
    round(
        100.0 * count(*) / (
            select count(*) from trials where exception_type is not null
        ),
        1
    ) as pct
from trials
where exception_type is not null
group by exception_type
order by n desc
```

<!--[[[end]]]-->

### Which submissions error the most?

<!--[[[cog
run_sql("""
    select
        submission,
        count(*) as n_trials,
        sum(case when exception_type is not null then 1 else 0 end) as n_errors,
        round(
            100.0 * sum(case when exception_type is not null then 1 else 0 end)
            / count(*),
            1
        ) as error_pct,
        sum(case when exception_type = 'AgentTimeoutError' then 1 else 0 end) as n_timeouts
    from trials
    group by submission
    order by error_pct desc
""")
]]]-->
```sql
select
    submission,
    count(*) as n_trials,
    sum(case when exception_type is not null then 1 else 0 end) as n_errors,
    round(
        100.0 * sum(case when exception_type is not null then 1 else 0 end)
        / count(*),
        1
    ) as error_pct,
    sum(case when exception_type = 'AgentTimeoutError' then 1 else 0 end) as n_timeouts
from trials
group by submission
order by error_pct desc
```

<!--[[[end]]]-->

### Tasks that cause the most timeouts

<!--[[[cog
run_sql("""
    select
        task_name,
        count(*) as n_timeouts,
        round(
            100.0 * count(*) / (
                select count(*) from trials t2 where t2.task_name = t.task_name
            ),
            1
        ) as timeout_pct
    from trials t
    where exception_type = 'AgentTimeoutError'
    group by task_name
    order by timeout_pct desc
    limit 15
""")
]]]-->
```sql
select
    task_name,
    count(*) as n_timeouts,
    round(
        100.0 * count(*) / (
            select count(*) from trials t2 where t2.task_name = t.task_name
        ),
        1
    ) as timeout_pct
from trials t
where exception_type = 'AgentTimeoutError'
group by task_name
order by timeout_pct desc
limit 15
```

<!--[[[end]]]-->

## Timing Analysis

How long do agents actually spend on tasks, and does spending more time correlate with success?

<!--[[[cog
run_sql("""
    select
        status,
        count(*) as n,
        round(avg(
            (julianday(agent_exec_finished_at) - julianday(agent_exec_started_at)) * 86400
        ), 1) as avg_agent_sec,
        round(min(
            (julianday(agent_exec_finished_at) - julianday(agent_exec_started_at)) * 86400
        ), 1) as min_sec,
        round(max(
            (julianday(agent_exec_finished_at) - julianday(agent_exec_started_at)) * 86400
        ), 1) as max_sec
    from trials
    where agent_exec_started_at is not null
      and agent_exec_finished_at is not null
    group by status
""")
]]]-->
```sql
select
    status,
    count(*) as n,
    round(avg(
        (julianday(agent_exec_finished_at) - julianday(agent_exec_started_at)) * 86400
    ), 1) as avg_agent_sec,
    round(min(
        (julianday(agent_exec_finished_at) - julianday(agent_exec_started_at)) * 86400
    ), 1) as min_sec,
    round(max(
        (julianday(agent_exec_finished_at) - julianday(agent_exec_started_at)) * 86400
    ), 1) as max_sec
from trials
where agent_exec_started_at is not null
  and agent_exec_finished_at is not null
group by status
```

<!--[[[end]]]-->

### Time breakdown: setup vs execution vs verification

<!--[[[cog
run_sql("""
    select
        submission,
        round(avg(
            (julianday(env_setup_finished_at) - julianday(env_setup_started_at)) * 86400
        ), 1) as env_setup_sec,
        round(avg(
            (julianday(agent_setup_finished_at) - julianday(agent_setup_started_at)) * 86400
        ), 1) as agent_setup_sec,
        round(avg(
            (julianday(agent_exec_finished_at) - julianday(agent_exec_started_at)) * 86400
        ), 1) as exec_sec,
        round(avg(
            (julianday(verifier_finished_at) - julianday(verifier_started_at)) * 86400
        ), 1) as verify_sec
    from trials
    where env_setup_started_at is not null
    group by submission
    order by exec_sec desc
    limit 15
""")
]]]-->
```sql
select
    submission,
    round(avg(
        (julianday(env_setup_finished_at) - julianday(env_setup_started_at)) * 86400
    ), 1) as env_setup_sec,
    round(avg(
        (julianday(agent_setup_finished_at) - julianday(agent_setup_started_at)) * 86400
    ), 1) as agent_setup_sec,
    round(avg(
        (julianday(agent_exec_finished_at) - julianday(agent_exec_started_at)) * 86400
    ), 1) as exec_sec,
    round(avg(
        (julianday(verifier_finished_at) - julianday(verifier_started_at)) * 86400
    ), 1) as verify_sec
from trials
where env_setup_started_at is not null
group by submission
order by exec_sec desc
limit 15
```

<!--[[[end]]]-->

## Cost Analysis

Only some submissions report token usage and costs.

<!--[[[cog
run_sql("""
    select
        submission,
        sum(case when status = 'passed' then 1 else 0 end) as n_passed,
        round(sum(cost_usd), 2) as total_cost,
        round(avg(cost_usd), 2) as avg_cost_per_trial,
        round(
            sum(cost_usd)
            / nullif(sum(case when status = 'passed' then 1 else 0 end), 0),
            2
        ) as cost_per_pass
    from trials
    where cost_usd is not null and cost_usd > 0
    group by submission
    having n_passed > 0
    order by cost_per_pass asc
""")
]]]-->
```sql
select
    submission,
    sum(case when status = 'passed' then 1 else 0 end) as n_passed,
    round(sum(cost_usd), 2) as total_cost,
    round(avg(cost_usd), 2) as avg_cost_per_trial,
    round(
        sum(cost_usd)
        / nullif(sum(case when status = 'passed' then 1 else 0 end), 0),
        2
    ) as cost_per_pass
from trials
where cost_usd is not null and cost_usd > 0
group by submission
having n_passed > 0
order by cost_per_pass asc
```

<!--[[[end]]]-->

## Head-to-Head: Claude vs GPT on Individual Tasks

Where does Claude Opus 4.6 (via Judy) beat GPT-5.3-Codex (via Droid), and vice versa?

<!--[[[cog
run_sql("""
    select
        m1.task_name,
        round(m1.avg_reward, 2) as claude_opus,
        round(m2.avg_reward, 2) as gpt_codex,
        round(m1.avg_reward - m2.avg_reward, 2) as claude_advantage
    from submission_task_matrix m1
    join submission_task_matrix m2 using (task_name)
    where m1.submission = 'Judy__Claude-Opus-4.6'
      and m2.submission = 'Droid__GPT-5.3-Codex'
      and abs(m1.avg_reward - m2.avg_reward) > 0.3
    order by claude_advantage desc
""")
]]]-->
```sql
select
    m1.task_name,
    round(m1.avg_reward, 2) as claude_opus,
    round(m2.avg_reward, 2) as gpt_codex,
    round(m1.avg_reward - m2.avg_reward, 2) as claude_advantage
from submission_task_matrix m1
join submission_task_matrix m2 using (task_name)
where m1.submission = 'Judy__Claude-Opus-4.6'
  and m2.submission = 'Droid__GPT-5.3-Codex'
  and abs(m1.avg_reward - m2.avg_reward) > 0.3
order by claude_advantage desc
```

<!--[[[end]]]-->

## Consistency: Which Tasks Discriminate Strong from Weak Models?

Some tasks are too easy (everyone passes) or too hard (everyone fails) to be useful discriminators. Which tasks best separate the top models from the bottom?

<!--[[[cog
run_sql("""
    select
        m.task_name,
        round(avg(case when ss.avg_reward > 0.65 then m.avg_reward end), 3) as top_half,
        round(avg(case when ss.avg_reward <= 0.65 then m.avg_reward end), 3) as bottom_half,
        round(
            avg(case when ss.avg_reward > 0.65 then m.avg_reward end) -
            avg(case when ss.avg_reward <= 0.65 then m.avg_reward end),
            3
        ) as discrimination
    from submission_task_matrix m
    join submission_stats ss on ss.submission = m.submission
    where ss.n_trials > 100
    group by m.task_name
    having discrimination is not null
    order by discrimination desc
    limit 15
""")
]]]-->
```sql
select
    m.task_name,
    round(avg(case when ss.avg_reward > 0.65 then m.avg_reward end), 3) as top_half,
    round(avg(case when ss.avg_reward <= 0.65 then m.avg_reward end), 3) as bottom_half,
    round(
        avg(case when ss.avg_reward > 0.65 then m.avg_reward end) -
        avg(case when ss.avg_reward <= 0.65 then m.avg_reward end),
        3
    ) as discrimination
from submission_task_matrix m
join submission_stats ss on ss.submission = m.submission
where ss.n_trials > 100
group by m.task_name
having discrimination is not null
order by discrimination desc
limit 15
```

<!--[[[end]]]-->

## The Most Inconsistent Tasks

Which tasks have the highest variance in performance across submissions? These are tasks where the agent scaffold matters more than the model.

<!--[[[cog
run_sql("""
    select
        task_name,
        round(avg(avg_reward), 3) as mean_reward,
        round(min(avg_reward), 3) as worst,
        round(max(avg_reward), 3) as best,
        round(
            avg(avg_reward * avg_reward) - avg(avg_reward) * avg(avg_reward),
            4
        ) as variance,
        count(*) as n_submissions
    from submission_task_matrix
    group by task_name
    having n_submissions > 10
    order by variance desc
    limit 15
""")
]]]-->
```sql
select
    task_name,
    round(avg(avg_reward), 3) as mean_reward,
    round(min(avg_reward), 3) as worst,
    round(max(avg_reward), 3) as best,
    round(
        avg(avg_reward * avg_reward) - avg(avg_reward) * avg(avg_reward),
        4
    ) as variance,
    count(*) as n_submissions
from submission_task_matrix
group by task_name
having n_submissions > 10
order by variance desc
limit 15
```

<!--[[[end]]]-->

## Submissions That Improved Across Runs

Some submissions ran the benchmark multiple times. Did they get better?

<!--[[[cog
run_sql("""
    select
        r.submission,
        r.run_date,
        count(*) as n_trials,
        sum(case when t.status = 'passed' then 1 else 0 end) as n_passed,
        round(avg(t.reward), 4) as avg_reward
    from trials t
    join runs r on t.run_id = r.id
    group by r.submission, r.run_date
    having n_trials > 40
    order by r.submission, r.run_date
""")
]]]-->
```sql
select
    r.submission,
    r.run_date,
    count(*) as n_trials,
    sum(case when t.status = 'passed' then 1 else 0 end) as n_passed,
    round(avg(t.reward), 4) as avg_reward
from trials t
join runs r on t.run_id = r.id
group by r.submission, r.run_date
having n_trials > 40
order by r.submission, r.run_date
```

<!--[[[end]]]-->

## Infrastructure Errors

Some errors aren't the agent's fault — they're infrastructure issues.

<!--[[[cog
run_sql("""
    select submission, exception_type, count(*) as n
    from trials
    where exception_type in (
        'DaytonaError',
        'EnvironmentStartTimeoutError',
        'DownloadVerifierDirError',
        'AddTestsDirError',
        'RewardFileNotFoundError',
        'VerifierTimeoutError'
    )
    group by submission, exception_type
    order by n desc
""")
]]]-->
```sql
select submission, exception_type, count(*) as n
from trials
where exception_type in (
    'DaytonaError',
    'EnvironmentStartTimeoutError',
    'DownloadVerifierDirError',
    'AddTestsDirError',
    'RewardFileNotFoundError',
    'VerifierTimeoutError'
)
group by submission, exception_type
order by n desc
```

<!--[[[end]]]-->

## All 89 Tasks by Failure Rate

<!--[[[cog
run_sql("""
    select task_name, round(failure_rate * 100, 1) as failure_rate_pct
    from task_stats
    order by failure_rate desc
""")
]]]-->
```sql
select task_name, round(failure_rate * 100, 1) as failure_rate_pct
from task_stats
order by failure_rate desc
```

<!--[[[end]]]-->
