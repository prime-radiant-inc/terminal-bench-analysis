# terminal-bench-analysis

This repo fetches just the detailed JSON results from [harborframework/terminal-bench-2-leaderboard](https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard) and loads them into a SQLite database for further analysis.

Run SQL queries against the resulting database here:

https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench

<!--[[[cog
import cog
import os
import sqlite3
import textwrap
from urllib.parse import quote

DB = "terminal-bench.db"
BLANK = os.environ.get("COG_BLANK")
DATASETTE_BASE = "https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench"

def run_sql(sql):
    sql = textwrap.dedent(sql).strip()
    cog.outl("```sql")
    cog.outl(sql)
    cog.outl("```")
    cog.outl("")
    encoded = quote(sql)
    cog.outl(f"[Run query]({DATASETTE_BASE}?sql={encoded})")
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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%20submission%2C%20n_trials%2C%20n_passed%2C%20n_failed%2C%20n_errored%2C%20avg_reward%0Afrom%20submission_stats%0Aorder%20by%20avg_reward%20desc)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20s.model_name%2C%0A%20%20%20%20s.slug%20as%20best_submission%2C%0A%20%20%20%20ss.avg_reward%2C%0A%20%20%20%20ss.n_passed%2C%0A%20%20%20%20ss.n_trials%0Afrom%20submissions%20s%0Ajoin%20submission_stats%20ss%20on%20ss.submission%20%3D%20s.slug%0Awhere%20ss.avg_reward%20%3D%20%28%0A%20%20%20%20select%20max%28ss2.avg_reward%29%0A%20%20%20%20from%20submissions%20s2%0A%20%20%20%20join%20submission_stats%20ss2%20on%20ss2.submission%20%3D%20s2.slug%0A%20%20%20%20where%20s2.model_name%20%3D%20s.model_name%0A%29%0Aorder%20by%20ss.avg_reward%20desc)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%20task_name%2C%20n_trials%2C%20n_passed%2C%20n_failed%2C%20n_errored%2C%20failure_rate%0Afrom%20task_stats%0Aorder%20by%20failure_rate%20desc%0Alimit%2015)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%20task_name%2C%20n_trials%2C%20n_failed%2C%20n_errored%0Afrom%20task_stats%0Awhere%20n_passed%20%3D%200)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%20task_name%2C%20n_trials%2C%20n_passed%2C%20n_failed%2C%20n_errored%2C%20avg_reward%0Afrom%20task_stats%0Aorder%20by%20failure_rate%20asc%0Alimit%2015)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20exception_type%2C%0A%20%20%20%20count%28%2A%29%20as%20n%2C%0A%20%20%20%20round%28%0A%20%20%20%20%20%20%20%20100.0%20%2A%20count%28%2A%29%20/%20%28%0A%20%20%20%20%20%20%20%20%20%20%20%20select%20count%28%2A%29%20from%20trials%20where%20exception_type%20is%20not%20null%0A%20%20%20%20%20%20%20%20%29%2C%0A%20%20%20%20%20%20%20%201%0A%20%20%20%20%29%20as%20pct%0Afrom%20trials%0Awhere%20exception_type%20is%20not%20null%0Agroup%20by%20exception_type%0Aorder%20by%20n%20desc)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20submission%2C%0A%20%20%20%20count%28%2A%29%20as%20n_trials%2C%0A%20%20%20%20sum%28case%20when%20exception_type%20is%20not%20null%20then%201%20else%200%20end%29%20as%20n_errors%2C%0A%20%20%20%20round%28%0A%20%20%20%20%20%20%20%20100.0%20%2A%20sum%28case%20when%20exception_type%20is%20not%20null%20then%201%20else%200%20end%29%0A%20%20%20%20%20%20%20%20/%20count%28%2A%29%2C%0A%20%20%20%20%20%20%20%201%0A%20%20%20%20%29%20as%20error_pct%2C%0A%20%20%20%20sum%28case%20when%20exception_type%20%3D%20%27AgentTimeoutError%27%20then%201%20else%200%20end%29%20as%20n_timeouts%0Afrom%20trials%0Agroup%20by%20submission%0Aorder%20by%20error_pct%20desc)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20task_name%2C%0A%20%20%20%20count%28%2A%29%20as%20n_timeouts%2C%0A%20%20%20%20round%28%0A%20%20%20%20%20%20%20%20100.0%20%2A%20count%28%2A%29%20/%20%28%0A%20%20%20%20%20%20%20%20%20%20%20%20select%20count%28%2A%29%20from%20trials%20t2%20where%20t2.task_name%20%3D%20t.task_name%0A%20%20%20%20%20%20%20%20%29%2C%0A%20%20%20%20%20%20%20%201%0A%20%20%20%20%29%20as%20timeout_pct%0Afrom%20trials%20t%0Awhere%20exception_type%20%3D%20%27AgentTimeoutError%27%0Agroup%20by%20task_name%0Aorder%20by%20timeout_pct%20desc%0Alimit%2015)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20status%2C%0A%20%20%20%20count%28%2A%29%20as%20n%2C%0A%20%20%20%20round%28avg%28%0A%20%20%20%20%20%20%20%20%28julianday%28agent_exec_finished_at%29%20-%20julianday%28agent_exec_started_at%29%29%20%2A%2086400%0A%20%20%20%20%29%2C%201%29%20as%20avg_agent_sec%2C%0A%20%20%20%20round%28min%28%0A%20%20%20%20%20%20%20%20%28julianday%28agent_exec_finished_at%29%20-%20julianday%28agent_exec_started_at%29%29%20%2A%2086400%0A%20%20%20%20%29%2C%201%29%20as%20min_sec%2C%0A%20%20%20%20round%28max%28%0A%20%20%20%20%20%20%20%20%28julianday%28agent_exec_finished_at%29%20-%20julianday%28agent_exec_started_at%29%29%20%2A%2086400%0A%20%20%20%20%29%2C%201%29%20as%20max_sec%0Afrom%20trials%0Awhere%20agent_exec_started_at%20is%20not%20null%0A%20%20and%20agent_exec_finished_at%20is%20not%20null%0Agroup%20by%20status)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20submission%2C%0A%20%20%20%20round%28avg%28%0A%20%20%20%20%20%20%20%20%28julianday%28env_setup_finished_at%29%20-%20julianday%28env_setup_started_at%29%29%20%2A%2086400%0A%20%20%20%20%29%2C%201%29%20as%20env_setup_sec%2C%0A%20%20%20%20round%28avg%28%0A%20%20%20%20%20%20%20%20%28julianday%28agent_setup_finished_at%29%20-%20julianday%28agent_setup_started_at%29%29%20%2A%2086400%0A%20%20%20%20%29%2C%201%29%20as%20agent_setup_sec%2C%0A%20%20%20%20round%28avg%28%0A%20%20%20%20%20%20%20%20%28julianday%28agent_exec_finished_at%29%20-%20julianday%28agent_exec_started_at%29%29%20%2A%2086400%0A%20%20%20%20%29%2C%201%29%20as%20exec_sec%2C%0A%20%20%20%20round%28avg%28%0A%20%20%20%20%20%20%20%20%28julianday%28verifier_finished_at%29%20-%20julianday%28verifier_started_at%29%29%20%2A%2086400%0A%20%20%20%20%29%2C%201%29%20as%20verify_sec%0Afrom%20trials%0Awhere%20env_setup_started_at%20is%20not%20null%0Agroup%20by%20submission%0Aorder%20by%20exec_sec%20desc%0Alimit%2015)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20submission%2C%0A%20%20%20%20sum%28case%20when%20status%20%3D%20%27passed%27%20then%201%20else%200%20end%29%20as%20n_passed%2C%0A%20%20%20%20round%28sum%28cost_usd%29%2C%202%29%20as%20total_cost%2C%0A%20%20%20%20round%28avg%28cost_usd%29%2C%202%29%20as%20avg_cost_per_trial%2C%0A%20%20%20%20round%28%0A%20%20%20%20%20%20%20%20sum%28cost_usd%29%0A%20%20%20%20%20%20%20%20/%20nullif%28sum%28case%20when%20status%20%3D%20%27passed%27%20then%201%20else%200%20end%29%2C%200%29%2C%0A%20%20%20%20%20%20%20%202%0A%20%20%20%20%29%20as%20cost_per_pass%0Afrom%20trials%0Awhere%20cost_usd%20is%20not%20null%20and%20cost_usd%20%3E%200%0Agroup%20by%20submission%0Ahaving%20n_passed%20%3E%200%0Aorder%20by%20cost_per_pass%20asc)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20m1.task_name%2C%0A%20%20%20%20round%28m1.avg_reward%2C%202%29%20as%20claude_opus%2C%0A%20%20%20%20round%28m2.avg_reward%2C%202%29%20as%20gpt_codex%2C%0A%20%20%20%20round%28m1.avg_reward%20-%20m2.avg_reward%2C%202%29%20as%20claude_advantage%0Afrom%20submission_task_matrix%20m1%0Ajoin%20submission_task_matrix%20m2%20using%20%28task_name%29%0Awhere%20m1.submission%20%3D%20%27Judy__Claude-Opus-4.6%27%0A%20%20and%20m2.submission%20%3D%20%27Droid__GPT-5.3-Codex%27%0A%20%20and%20abs%28m1.avg_reward%20-%20m2.avg_reward%29%20%3E%200.3%0Aorder%20by%20claude_advantage%20desc)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20m.task_name%2C%0A%20%20%20%20round%28avg%28case%20when%20ss.avg_reward%20%3E%200.65%20then%20m.avg_reward%20end%29%2C%203%29%20as%20top_half%2C%0A%20%20%20%20round%28avg%28case%20when%20ss.avg_reward%20%3C%3D%200.65%20then%20m.avg_reward%20end%29%2C%203%29%20as%20bottom_half%2C%0A%20%20%20%20round%28%0A%20%20%20%20%20%20%20%20avg%28case%20when%20ss.avg_reward%20%3E%200.65%20then%20m.avg_reward%20end%29%20-%0A%20%20%20%20%20%20%20%20avg%28case%20when%20ss.avg_reward%20%3C%3D%200.65%20then%20m.avg_reward%20end%29%2C%0A%20%20%20%20%20%20%20%203%0A%20%20%20%20%29%20as%20discrimination%0Afrom%20submission_task_matrix%20m%0Ajoin%20submission_stats%20ss%20on%20ss.submission%20%3D%20m.submission%0Awhere%20ss.n_trials%20%3E%20100%0Agroup%20by%20m.task_name%0Ahaving%20discrimination%20is%20not%20null%0Aorder%20by%20discrimination%20desc%0Alimit%2015)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20task_name%2C%0A%20%20%20%20round%28avg%28avg_reward%29%2C%203%29%20as%20mean_reward%2C%0A%20%20%20%20round%28min%28avg_reward%29%2C%203%29%20as%20worst%2C%0A%20%20%20%20round%28max%28avg_reward%29%2C%203%29%20as%20best%2C%0A%20%20%20%20round%28%0A%20%20%20%20%20%20%20%20avg%28avg_reward%20%2A%20avg_reward%29%20-%20avg%28avg_reward%29%20%2A%20avg%28avg_reward%29%2C%0A%20%20%20%20%20%20%20%204%0A%20%20%20%20%29%20as%20variance%2C%0A%20%20%20%20count%28%2A%29%20as%20n_submissions%0Afrom%20submission_task_matrix%0Agroup%20by%20task_name%0Ahaving%20n_submissions%20%3E%2010%0Aorder%20by%20variance%20desc%0Alimit%2015)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%0A%20%20%20%20r.submission%2C%0A%20%20%20%20r.run_date%2C%0A%20%20%20%20count%28%2A%29%20as%20n_trials%2C%0A%20%20%20%20sum%28case%20when%20t.status%20%3D%20%27passed%27%20then%201%20else%200%20end%29%20as%20n_passed%2C%0A%20%20%20%20round%28avg%28t.reward%29%2C%204%29%20as%20avg_reward%0Afrom%20trials%20t%0Ajoin%20runs%20r%20on%20t.run_id%20%3D%20r.id%0Agroup%20by%20r.submission%2C%20r.run_date%0Ahaving%20n_trials%20%3E%2040%0Aorder%20by%20r.submission%2C%20r.run_date)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%20submission%2C%20exception_type%2C%20count%28%2A%29%20as%20n%0Afrom%20trials%0Awhere%20exception_type%20in%20%28%0A%20%20%20%20%27DaytonaError%27%2C%0A%20%20%20%20%27EnvironmentStartTimeoutError%27%2C%0A%20%20%20%20%27DownloadVerifierDirError%27%2C%0A%20%20%20%20%27AddTestsDirError%27%2C%0A%20%20%20%20%27RewardFileNotFoundError%27%2C%0A%20%20%20%20%27VerifierTimeoutError%27%0A%29%0Agroup%20by%20submission%2C%20exception_type%0Aorder%20by%20n%20desc)

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

[Run query](https://primeradiant.com/terminal-bench-analysis/datasette-lite.html#/terminal-bench?sql=select%20task_name%2C%20round%28failure_rate%20%2A%20100%2C%201%29%20as%20failure_rate_pct%0Afrom%20task_stats%0Aorder%20by%20failure_rate%20desc)

<!--[[[end]]]-->
