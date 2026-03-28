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

| submission | n_trials | n_passed | n_failed | n_errored | avg_reward |
| --- | --- | --- | --- | --- | --- |
| OB-1_GPT-5.4-GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 445 | 367 | 77 | 1 | 0.8266 |
| Forge__GPT-5.4 | 445 | 364 | 49 | 32 | 0.818 |
| Forge__Opus-4.6 | 445 | 364 | 49 | 32 | 0.818 |
| Judy__Gemini-3.1-Pro-Preview | 445 | 357 | 29 | 59 | 0.8132 |
| OpenSage__GPT-5.3-Codex | 445 | 349 | 53 | 43 | 0.795 |
| Forge__Gemini-3.1-Pro-Preview | 445 | 349 | 60 | 36 | 0.786 |
| Droid__GPT-5.3-Codex | 445 | 344 | 73 | 28 | 0.773 |
| Capy__Claude-Opus-4.6 | 445 | 335 | 58 | 52 | 0.7579 |
| Simple-Codex__GPT-5.3-Codex | 445 | 332 | 46 | 67 | 0.7563 |
| Terminus-KIRA__Gemini-3.1-Pro-Preview | 445 | 333 | 76 | 36 | 0.7517 |
| Terminus-KIRA__Claude-Opus-4.6 | 445 | 331 | 54 | 60 | 0.7489 |
| Mux__GPT-5.3-Codex | 445 | 332 | 83 | 30 | 0.7461 |
| Ante__Gemini-3.1-Pro-Preview | 445 | 328 | 60 | 57 | 0.7455 |
| MAYA__Claude-4.6-opus | 445 | 320 | 114 | 11 | 0.7373 |
| OB-1_GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 445 | 322 | 121 | 2 | 0.7269 |
| Judy__Claude-Opus-4.6 | 445 | 320 | 65 | 60 | 0.7256 |
| Junie_CLI__Gemini-3-Flash-Preview-Gemini-3.1-Pro-Preview-Claude-Opus-4.6-GPT-5.3-Codex | 445 | 316 | 98 | 31 | 0.7117 |
| Droid__Claude-Opus-4.6 | 445 | 311 | 108 | 26 | 0.7052 |
| CodeBrain-1__GPT-5.3-Codex | 445 | 313 | 98 | 34 | 0.705 |
| IndusAGICodingAgent__gpt-5.3-codex | 445 | 261 | 84 | 100 | 0.685 |
| Deep-Agents__GPT-5.2-Codex | 445 | 293 | 77 | 75 | 0.6798 |
| Crux__Claude-Opus-4.6 | 445 | 272 | 99 | 74 | 0.67 |
| Mux__Claude-Opus-4.6 | 445 | 296 | 113 | 36 | 0.6652 |
| OpenSage__Gemini-3-Pro-Preview | 445 | 290 | 131 | 24 | 0.6576 |
| Terminus2__GPT-5.3-Codex | 445 | 288 | 70 | 87 | 0.6545 |
| Ante__Gemini-3-Pro-Preview | 445 | 288 | 129 | 28 | 0.6501 |
| Terminus2__Claude-Opus-4.6 | 445 | 280 | 92 | 73 | 0.6349 |
| CodeBrain-1__Gemini-3-Pro-Preview | 445 | 277 | 136 | 32 | 0.6225 |
| Mux__GPT-5.2 | 89 | 54 | 25 | 10 | 0.6207 |
| Mux__Claude-Opus-4.5 | 89 | 52 | 29 | 8 | 0.5843 |
| Terminus2__GLM-5 | 445 | 231 | 113 | 101 | 0.5397 |
| OpenCode__Claude-Opus-4.5 | 89 | 46 | 38 | 5 | 0.5227 |
| Gemini_CLI__Gemini-3-Flash-Preview | 445 | 211 | 178 | 56 | 0.4806 |
| MAYA__Claude-4.5-sonnet | 445 | 190 | 241 | 14 | 0.4408 |
| Terminus2__Kimi-k2.5 | 445 | 189 | 161 | 95 | 0.4385 |
| Terminus2__Minimax-m2.5 | 445 | 188 | 92 | 165 | 0.4292 |
| Terminus2__DeepSeek-V3.2 | 445 | 176 | 183 | 86 | 0.3982 |
| Terminus2__GLM-4.7 | 445 | 147 | 139 | 159 | 0.3475 |
| ClaudeCode__GLM-4.7 | 445 | 148 | 250 | 47 | 0.3348 |
| dakou__qwen3-coder-480b | 445 | 121 | 232 | 92 | 0.275 |
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

| model_name | best_submission | avg_reward | n_passed | n_trials |
| --- | --- | --- | --- | --- |
| auto | OB-1_GPT-5.4-GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 0.8266 | 367 | 445 |
| litellm_proxy/sage-gpt-5.3-codex | OpenSage__GPT-5.3-Codex | 0.795 | 349 | 445 |
| gpt-5.3-codex | Droid__GPT-5.3-Codex | 0.773 | 344 | 445 |
| anthropic/claude-opus-4-6 | Capy__Claude-Opus-4.6 | 0.7579 | 335 | 445 |
| openai/gpt-5.3-codex | Simple-Codex__GPT-5.3-Codex | 0.7563 | 332 | 445 |
| vertex_ai/gemini-3.1-pro-preview | Terminus-KIRA__Gemini-3.1-Pro-Preview | 0.7517 | 333 | 445 |
| vertex_ai/claude-opus-4-6 | Terminus-KIRA__Claude-Opus-4.6 | 0.7489 | 331 | 445 |
| gemini-3.1-pro-preview | Ante__Gemini-3.1-Pro-Preview | 0.7455 | 328 | 445 |
| aurora-01-21 | Droid__Claude-Opus-4.6 | 0.7052 | 311 | 445 |
| openai-codex/gpt-5.3-codex | IndusAGICodingAgent__gpt-5.3-codex | 0.685 | 261 | 445 |
| openai:gpt-5.2-codex | Deep-Agents__GPT-5.2-Codex | 0.6798 | 293 | 445 |
| claude-opus-4-6 | Crux__Claude-Opus-4.6 | 0.67 | 272 | 445 |
| litellm_proxy/gemini-3-pro-preview | OpenSage__Gemini-3-Pro-Preview | 0.6576 | 290 | 445 |
| gemini-3-pro-preview | Ante__Gemini-3-Pro-Preview | 0.6501 | 288 | 445 |
| vertex_ai/gemini-3-pro-preview | CodeBrain-1__Gemini-3-Pro-Preview | 0.6225 | 277 | 445 |
| openai/gpt-5.2 | Mux__GPT-5.2 | 0.6207 | 54 | 89 |
| anthropic/claude-opus-4-5 | Mux__Claude-Opus-4.5 | 0.5843 | 52 | 89 |
| openai/glm-5 | Terminus2__GLM-5 | 0.5397 | 231 | 445 |
| google/gemini-3-flash-preview | Gemini_CLI__Gemini-3-Flash-Preview | 0.4806 | 211 | 445 |
| openai/kimi-k2.5:cloud | Terminus2__Kimi-k2.5 | 0.4385 | 189 | 445 |
| openai/minimax-m2.5:cloud | Terminus2__Minimax-m2.5 | 0.4292 | 188 | 445 |
| deepseek/deepseek-chat | Terminus2__DeepSeek-V3.2 | 0.3982 | 176 | 445 |
| openai/glm-4.7:cloud | Terminus2__GLM-4.7 | 0.3475 | 147 | 445 |
| GLM-4.7 | ClaudeCode__GLM-4.7 | 0.3348 | 148 | 445 |
| qwen3-coder-modelscope | dakou__qwen3-coder-480b | 0.275 | 121 | 445 |
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

| task_name | n_trials | n_passed | n_failed | n_errored | failure_rate |
| --- | --- | --- | --- | --- | --- |
| make-doom-for-mips | 188 | 0 | 38 | 150 | 1.0 |
| filter-js-from-html | 188 | 6 | 160 | 22 | 0.9639 |
| caffe-cifar-10 | 188 | 7 | 61 | 120 | 0.9598 |
| install-windows-3.11 | 188 | 12 | 160 | 16 | 0.9358 |
| sam-cell-seg | 188 | 12 | 173 | 3 | 0.9351 |
| train-fasttext | 188 | 13 | 41 | 134 | 0.9253 |
| raman-fitting | 188 | 16 | 119 | 53 | 0.914 |
| extract-moves-from-video | 188 | 17 | 74 | 97 | 0.9086 |
| gpt2-codegolf | 188 | 22 | 47 | 119 | 0.883 |
| video-processing | 188 | 38 | 146 | 4 | 0.7957 |
| torch-pipeline-parallelism | 188 | 39 | 106 | 43 | 0.7869 |
| dna-assembly | 188 | 44 | 118 | 26 | 0.7634 |
| make-mips-interpreter | 188 | 47 | 63 | 78 | 0.7418 |
| model-extraction-relu-logits | 188 | 50 | 109 | 29 | 0.7283 |
| mteb-retrieve | 188 | 52 | 128 | 8 | 0.7111 |
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

| task_name | n_trials | n_failed | n_errored |
| --- | --- | --- | --- |
| make-doom-for-mips | 188 | 38 | 150 |
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

| task_name | n_trials | n_passed | n_failed | n_errored | avg_reward |
| --- | --- | --- | --- | --- | --- |
| git-leak-recovery | 188 | 185 | 2 | 1 | 0.9893 |
| fix-git | 188 | 183 | 5 | 0 | 0.9734 |
| constraints-scheduling | 188 | 181 | 5 | 2 | 0.9731 |
| nginx-request-logging | 188 | 181 | 6 | 1 | 0.9679 |
| multi-source-data-merger | 188 | 180 | 7 | 1 | 0.9626 |
| vulnerable-secret | 188 | 180 | 7 | 1 | 0.9626 |
| modernize-scientific-stack | 188 | 177 | 6 | 5 | 0.962 |
| custom-memory-heap-crash | 188 | 180 | 3 | 5 | 0.9574 |
| prove-plus-comm | 188 | 179 | 8 | 1 | 0.9572 |
| code-from-image | 188 | 178 | 3 | 7 | 0.957 |
| cobol-modernization | 188 | 179 | 9 | 0 | 0.9521 |
| distribution-search | 188 | 177 | 6 | 5 | 0.9465 |
| log-summary-date-ranges | 188 | 177 | 10 | 1 | 0.9465 |
| portfolio-optimization | 188 | 172 | 11 | 5 | 0.9399 |
| git-multibranch | 188 | 174 | 11 | 3 | 0.9355 |
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

| exception_type | n | pct |
| --- | --- | --- |
| AgentTimeoutError | 2175 | 90.7 |
| VerifierTimeoutError | 44 | 1.8 |
| AgentSetupTimeoutError | 42 | 1.8 |
| RuntimeError | 41 | 1.7 |
| DaytonaError | 31 | 1.3 |
| EnvironmentStartTimeoutError | 19 | 0.8 |
| BadRequestError | 9 | 0.4 |
| RewardFileNotFoundError | 9 | 0.4 |
| NameError | 8 | 0.3 |
| OSError | 8 | 0.3 |
| AddTestsDirError | 4 | 0.2 |
| AttributeError | 4 | 0.2 |
| DownloadVerifierDirError | 4 | 0.2 |
| KeyError | 1 | 0.0 |
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

| submission | n_trials | n_errors | error_pct | n_timeouts |
| --- | --- | --- | --- | --- |
| Terminus2__Minimax-m2.5 | 445 | 181 | 40.7 | 179 |
| Terminus2__GLM-4.7 | 445 | 161 | 36.2 | 143 |
| Terminus2__GLM-5 | 445 | 111 | 24.9 | 108 |
| IndusAGICodingAgent__gpt-5.3-codex | 445 | 106 | 23.8 | 42 |
| Terminus2__Kimi-k2.5 | 445 | 101 | 22.7 | 91 |
| dakou__qwen3-coder-480b | 445 | 95 | 21.3 | 92 |
| Judy__Gemini-3.1-Pro-Preview | 445 | 94 | 21.1 | 90 |
| Simple-Codex__GPT-5.3-Codex | 445 | 92 | 20.7 | 90 |
| Terminus2__GPT-5.3-Codex | 445 | 92 | 20.7 | 92 |
| Terminus2__DeepSeek-V3.2 | 445 | 91 | 20.4 | 90 |
| Judy__Claude-Opus-4.6 | 445 | 86 | 19.3 | 83 |
| Ante__Gemini-3.1-Pro-Preview | 445 | 83 | 18.7 | 78 |
| Deep-Agents__GPT-5.2-Codex | 445 | 82 | 18.4 | 70 |
| Terminus-KIRA__Claude-Opus-4.6 | 445 | 81 | 18.2 | 78 |
| Terminus2__Claude-Opus-4.6 | 445 | 81 | 18.2 | 81 |
| Crux__Claude-Opus-4.6 | 445 | 78 | 17.5 | 40 |
| Capy__Claude-Opus-4.6 | 445 | 70 | 15.7 | 67 |
| Forge__Gemini-3.1-Pro-Preview | 445 | 63 | 14.2 | 62 |
| Mux__GPT-5.2 | 89 | 12 | 13.5 | 11 |
| Gemini_CLI__Gemini-3-Flash-Preview | 445 | 57 | 12.8 | 51 |
| OpenSage__GPT-5.3-Codex | 445 | 54 | 12.1 | 49 |
| Forge__Opus-4.6 | 445 | 53 | 11.9 | 53 |
| ClaudeCode__GLM-4.7 | 445 | 48 | 10.8 | 46 |
| Mux__Claude-Opus-4.6 | 445 | 46 | 10.3 | 46 |
| Forge__GPT-5.4 | 445 | 45 | 10.1 | 45 |
| Terminus-KIRA__Gemini-3.1-Pro-Preview | 445 | 43 | 9.7 | 43 |
| Mux__Claude-Opus-4.5 | 89 | 8 | 9.0 | 8 |
| CodeBrain-1__GPT-5.3-Codex | 445 | 36 | 8.1 | 35 |
| Mux__GPT-5.3-Codex | 445 | 36 | 8.1 | 36 |
| CodeBrain-1__Gemini-3-Pro-Preview | 445 | 35 | 7.9 | 35 |
| Junie_CLI__Gemini-3-Flash-Preview-Gemini-3.1-Pro-Preview-Claude-Opus-4.6-GPT-5.3-Codex | 445 | 35 | 7.9 | 35 |
| Ante__Gemini-3-Pro-Preview | 445 | 30 | 6.7 | 29 |
| Droid__GPT-5.3-Codex | 445 | 29 | 6.5 | 29 |
| Droid__Claude-Opus-4.6 | 445 | 26 | 5.8 | 22 |
| OpenCode__Claude-Opus-4.5 | 89 | 5 | 5.6 | 5 |
| OpenSage__Gemini-3-Pro-Preview | 445 | 25 | 5.6 | 21 |
| MAYA__Claude-4.5-sonnet | 445 | 14 | 3.1 | 0 |
| MAYA__Claude-4.6-opus | 445 | 11 | 2.5 | 0 |
| OB-1_GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 445 | 2 | 0.4 | 0 |
| OB-1_GPT-5.4-GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 445 | 1 | 0.2 | 0 |
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

| task_name | n_timeouts | timeout_pct |
| --- | --- | --- |
| make-doom-for-mips | 148 | 78.7 |
| train-fasttext | 130 | 69.1 |
| gpt2-codegolf | 120 | 63.8 |
| caffe-cifar-10 | 118 | 62.8 |
| extract-moves-from-video | 99 | 52.7 |
| make-mips-interpreter | 75 | 39.9 |
| db-wal-recovery | 73 | 38.8 |
| qemu-alpine-ssh | 70 | 37.2 |
| path-tracing | 69 | 36.7 |
| tune-mjcf | 64 | 34.0 |
| write-compressor | 56 | 29.8 |
| torch-pipeline-parallelism | 53 | 28.2 |
| raman-fitting | 53 | 28.2 |
| query-optimize | 49 | 26.1 |
| path-tracing-reverse | 45 | 23.9 |
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

| status | n | avg_agent_sec | min_sec | max_sec |
| --- | --- | --- | --- | --- |
| errored | 1950 | 1517.5 | 0.0 | 12000.1 |
| failed | 3983 | 543.7 | 0.1 | 9338.2 |
| passed | 10667 | 440.2 | 1.3 | 6250.0 |
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

| submission | env_setup_sec | agent_setup_sec | exec_sec | verify_sec |
| --- | --- | --- | --- | --- |
| Terminus2__Minimax-m2.5 | 17.5 | 18.3 | 965.5 | 93.5 |
| Terminus2__GLM-4.7 | 14.0 | 20.6 | 886.2 | 90.8 |
| Terminus2__GLM-5 | 10.5 | 17.2 | 822.9 | 63.2 |
| Judy__Gemini-3.1-Pro-Preview | 9.0 | 46.5 | 793.8 | 73.4 |
| Judy__Claude-Opus-4.6 | 11.2 | 47.1 | 760.5 | 72.0 |
| Terminus-KIRA__Claude-Opus-4.6 | 39.2 | 17.8 | 753.8 | 46.2 |
| Ante__Gemini-3.1-Pro-Preview | 9.8 | 6.9 | 748.5 | 70.1 |
| Simple-Codex__GPT-5.3-Codex | 2.7 | 13.2 | 742.4 | 66.1 |
| dakou__qwen3-coder-480b | 52.1 | 109.7 | 737.2 | 122.6 |
| Terminus2__GPT-5.3-Codex | 2.9 | 12.7 | 734.7 | 48.0 |
| Terminus2__Kimi-k2.5 | 15.1 | 12.4 | 711.6 | 74.5 |
| Deep-Agents__GPT-5.2-Codex | 3.4 | 0.0 | 704.5 | 45.8 |
| Terminus2__DeepSeek-V3.2 | 9.5 | 8.7 | 703.4 | 31.1 |
| Capy__Claude-Opus-4.6 | 1.2 | 7.5 | 674.8 | 65.4 |
| Terminus2__Claude-Opus-4.6 | 3.6 | 12.9 | 656.2 | 49.6 |
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

| submission | n_passed | total_cost | avg_cost_per_trial | cost_per_pass |
| --- | --- | --- | --- | --- |
| Mux__GPT-5.3-Codex | 148 | 0.0 | 0.0 | 0.0 |
| Terminus2__DeepSeek-V3.2 | 176 | 13.67 | 0.03 | 0.08 |
| Mux__Claude-Opus-4.6 | 101 | 37.22 | 0.32 | 0.37 |
| IndusAGICodingAgent__gpt-5.3-codex | 261 | 134.43 | 0.36 | 0.52 |
| Terminus2__Claude-Opus-4.6 | 280 | 293.61 | 0.66 | 1.05 |
| Capy__Claude-Opus-4.6 | 316 | 366.66 | 0.99 | 1.16 |
| Terminus-KIRA__Gemini-3.1-Pro-Preview | 333 | 406.63 | 0.91 | 1.22 |
| Terminus-KIRA__Claude-Opus-4.6 | 331 | 713.67 | 1.61 | 2.16 |
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

| task_name | claude_opus | gpt_codex | claude_advantage |
| --- | --- | --- | --- |
| qemu-alpine-ssh | 1.0 | 0.0 | 1.0 |
| mcmc-sampling-stan | 0.8 | 0.0 | 0.8 |
| torch-pipeline-parallelism | 0.8 | 0.0 | 0.8 |
| db-wal-recovery | 1.0 | 0.4 | 0.6 |
| overfull-hbox | 1.0 | 0.4 | 0.6 |
| query-optimize | 0.75 | 0.4 | 0.35 |
| extract-moves-from-video | 0.0 | 0.4 | -0.4 |
| git-multibranch | 0.6 | 1.0 | -0.4 |
| mteb-leaderboard | 0.2 | 0.6 | -0.4 |
| path-tracing | 0.6 | 1.0 | -0.4 |
| schemelike-metacircular-eval | 0.6 | 1.0 | -0.4 |
| tune-mjcf | 0.4 | 0.8 | -0.4 |
| write-compressor | 0.6 | 1.0 | -0.4 |
| financial-document-processor | 0.4 | 1.0 | -0.6 |
| adaptive-rejection-sampler | 0.2 | 1.0 | -0.8 |
| build-pmars | 0.2 | 1.0 | -0.8 |
| make-mips-interpreter | 0.0 | 0.8 | -0.8 |
| openssl-selfsigned-cert | 0.2 | 1.0 | -0.8 |
| regex-chess | 0.0 | 1.0 | -1.0 |
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

| task_name | top_half | bottom_half | discrimination |
| --- | --- | --- | --- |
| sanitize-git-repo | 0.931 | 0.127 | 0.803 |
| protein-assembly | 0.846 | 0.127 | 0.719 |
| chess-best-move | 0.792 | 0.109 | 0.683 |
| break-filter-js-from-html | 0.915 | 0.236 | 0.679 |
| circuit-fibsqrt | 0.938 | 0.309 | 0.629 |
| overfull-hbox | 0.846 | 0.218 | 0.628 |
| write-compressor | 0.804 | 0.182 | 0.622 |
| feal-linear-cryptanalysis | 0.912 | 0.291 | 0.621 |
| path-tracing | 0.682 | 0.073 | 0.609 |
| path-tracing-reverse | 0.692 | 0.091 | 0.601 |
| polyglot-rust-c | 0.677 | 0.091 | 0.586 |
| bn-fit-modify | 0.977 | 0.418 | 0.559 |
| winning-avg-corewars | 0.788 | 0.255 | 0.534 |
| polyglot-c-py | 0.623 | 0.091 | 0.532 |
| financial-document-processor | 0.823 | 0.291 | 0.532 |
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

| task_name | mean_reward | worst | best | variance | n_submissions |
| --- | --- | --- | --- | --- | --- |
| polyglot-rust-c | 0.465 | 0.0 | 1.0 | 0.2108 | 40 |
| chess-best-move | 0.57 | 0.0 | 1.0 | 0.1951 | 40 |
| path-tracing-reverse | 0.525 | 0.0 | 1.0 | 0.1934 | 40 |
| polyglot-c-py | 0.43 | 0.0 | 1.0 | 0.1851 | 40 |
| write-compressor | 0.573 | 0.0 | 1.0 | 0.1814 | 40 |
| protein-assembly | 0.585 | 0.0 | 1.0 | 0.1808 | 40 |
| db-wal-recovery | 0.325 | 0.0 | 1.0 | 0.1734 | 40 |
| break-filter-js-from-html | 0.703 | 0.0 | 1.0 | 0.17 | 40 |
| path-tracing | 0.463 | 0.0 | 1.0 | 0.1686 | 40 |
| feal-linear-cryptanalysis | 0.698 | 0.0 | 1.0 | 0.1667 | 40 |
| qemu-alpine-ssh | 0.552 | 0.0 | 1.0 | 0.165 | 40 |
| regex-chess | 0.371 | 0.0 | 1.0 | 0.1607 | 40 |
| configure-git-webserver | 0.525 | 0.0 | 1.0 | 0.1594 | 40 |
| overfull-hbox | 0.66 | 0.0 | 1.0 | 0.1584 | 40 |
| sanitize-git-repo | 0.69 | 0.0 | 1.0 | 0.1579 | 40 |
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

| submission | run_date | n_trials | n_passed | avg_reward |
| --- | --- | --- | --- | --- |
| Ante__Gemini-3-Pro-Preview | 2025-12-31__22-36-36 | 445 | 288 | 0.6501 |
| Ante__Gemini-3.1-Pro-Preview | 2026-02-20__19-31-44 | 445 | 328 | 0.7455 |
| Capy__Claude-Opus-4.6 | eval-terminal-bench-2-0-anthropic-claude-opus-4-6-2550be0a-1773212093281 | 89 | 66 | 0.75 |
| Capy__Claude-Opus-4.6 | eval-terminal-bench-2-0-anthropic-claude-opus-4-6-ae1eef84-1773189792834 | 89 | 68 | 0.7727 |
| Capy__Claude-Opus-4.6 | eval-terminal-bench-2-0-anthropic-claude-opus-4-6-b5a5edf0-1773245492872 | 89 | 67 | 0.7614 |
| Capy__Claude-Opus-4.6 | eval-terminal-bench-2-0-anthropic-claude-opus-4-6-e4c20869-1773208202009 | 89 | 68 | 0.764 |
| Capy__Claude-Opus-4.6 | eval-terminal-bench-2-0-anthropic-claude-opus-4-6-f67d7dea-1773208226179 | 89 | 66 | 0.7416 |
| ClaudeCode__GLM-4.7 | 2026-02-06__13-08-08 | 445 | 148 | 0.3348 |
| CodeBrain-1__GPT-5.3-Codex | 2026-02-08__11-01-20 | 89 | 60 | 0.6742 |
| CodeBrain-1__GPT-5.3-Codex | 2026-02-08__20-43-33 | 89 | 66 | 0.7416 |
| CodeBrain-1__GPT-5.3-Codex | 2026-02-09__01-09-07 | 89 | 65 | 0.7303 |
| CodeBrain-1__GPT-5.3-Codex | 2026-02-09__10-03-38 | 89 | 60 | 0.6818 |
| CodeBrain-1__GPT-5.3-Codex | 2026-02-09__14-06-10 | 89 | 62 | 0.6966 |
| CodeBrain-1__Gemini-3-Pro-Preview | 2026-01-31__22-50-53 | 89 | 56 | 0.6292 |
| CodeBrain-1__Gemini-3-Pro-Preview | 2026-02-01__11-30-31 | 89 | 56 | 0.6292 |
| CodeBrain-1__Gemini-3-Pro-Preview | 2026-02-01__16-43-15 | 89 | 54 | 0.6067 |
| CodeBrain-1__Gemini-3-Pro-Preview | 2026-02-05__00-52-21 | 89 | 56 | 0.6292 |
| CodeBrain-1__Gemini-3-Pro-Preview | 2026-02-05__11-19-55 | 89 | 55 | 0.618 |
| Crux__Claude-Opus-4.6 | submission-run | 445 | 272 | 0.67 |
| Deep-Agents__GPT-5.2-Codex | 2026-02-10__12-43-13 | 445 | 293 | 0.6798 |
| Droid__Claude-Opus-4.6 | fudge_2026-01-29__03-21-39 | 89 | 61 | 0.6932 |
| Droid__Claude-Opus-4.6 | fudge_2026-01-29__06-23-59 | 89 | 64 | 0.7273 |
| Droid__Claude-Opus-4.6 | fudge_2026-01-29__07-55-11 | 89 | 61 | 0.6932 |
| Droid__Claude-Opus-4.6 | fudge_2026-01-29__23-21-40 | 89 | 63 | 0.7079 |
| Droid__Claude-Opus-4.6 | fudge_2026-01-30__02-21-25 | 89 | 62 | 0.7045 |
| Droid__GPT-5.3-Codex | 53codex_2026-02-16__17-43-12 | 89 | 69 | 0.7753 |
| Droid__GPT-5.3-Codex | 53codex_2026-02-21__21-58-56 | 89 | 68 | 0.764 |
| Droid__GPT-5.3-Codex | 53codex_2026-02-22__06-09-07 | 89 | 68 | 0.764 |
| Droid__GPT-5.3-Codex | 53codex_2026-02-22__09-59-36 | 89 | 69 | 0.7753 |
| Droid__GPT-5.3-Codex | 53codex_2026-02-22__10-19-01 | 89 | 70 | 0.7865 |
| Forge__GPT-5.4 | 2026-03-07__04-54-03 | 445 | 364 | 0.818 |
| Forge__Gemini-3.1-Pro-Preview | 2026-02-26__14-28-30 | 445 | 349 | 0.786 |
| Forge__Opus-4.6 | 2026-03-11__06-58-11 | 445 | 364 | 0.818 |
| Gemini_CLI__Gemini-3-Flash-Preview | 2026-03-05__16-55-44 | 445 | 211 | 0.4806 |
| IndusAGICodingAgent__gpt-5.3-codex | 2026-03-17__07-15-58 | 445 | 261 | 0.685 |
| Judy__Claude-Opus-4.6 | 2026-02-10__18-07-36 | 89 | 64 | 0.7273 |
| Judy__Claude-Opus-4.6 | 2026-02-11__11-58-19 | 89 | 63 | 0.7079 |
| Judy__Claude-Opus-4.6 | 2026-02-12__11-31-57 | 89 | 62 | 0.7045 |
| Judy__Claude-Opus-4.6 | 2026-02-12__18-19-55 | 89 | 64 | 0.7273 |
| Judy__Claude-Opus-4.6 | 2026-02-13__00-57-16 | 89 | 67 | 0.7614 |
| Judy__Gemini-3.1-Pro-Preview | 2026-03-07__01-45-03 | 89 | 69 | 0.7753 |
| Judy__Gemini-3.1-Pro-Preview | 2026-03-07__14-20-34 | 89 | 69 | 0.7841 |
| Judy__Gemini-3.1-Pro-Preview | 2026-03-08__06-54-22 | 89 | 79 | 0.8977 |
| Judy__Gemini-3.1-Pro-Preview | 2026-03-08__16-45-59 | 89 | 69 | 0.7931 |
| Judy__Gemini-3.1-Pro-Preview | 2026-03-08__16-47-12 | 89 | 71 | 0.8161 |
| Junie_CLI__Gemini-3-Flash-Preview-Gemini-3.1-Pro-Preview-Claude-Opus-4.6-GPT-5.3-Codex | 2026-03-06__12-25-19 | 445 | 316 | 0.7117 |
| MAYA__Claude-4.5-sonnet | 2025-11-13__09-25-32 | 89 | 38 | 0.4419 |
| MAYA__Claude-4.5-sonnet | 2025-12-05__06-20-00 | 89 | 38 | 0.4419 |
| MAYA__Claude-4.5-sonnet | 2025-12-05__16-42-55 | 89 | 38 | 0.4368 |
| MAYA__Claude-4.5-sonnet | 2025-12-06__16-31-45 | 89 | 38 | 0.4524 |
| MAYA__Claude-4.5-sonnet | 2025-12-09__13-26-21 | 89 | 38 | 0.4318 |
| MAYA__Claude-4.6-opus | 2026-02-27__16-48-59 | 89 | 65 | 0.7386 |
| MAYA__Claude-4.6-opus | 2026-03-02__08-17-24 | 89 | 66 | 0.7765 |
| MAYA__Claude-4.6-opus | 2026-03-04__07-44-02 | 89 | 63 | 0.7326 |
| MAYA__Claude-4.6-opus | 2026-03-05__07-04-22 | 89 | 61 | 0.7011 |
| MAYA__Claude-4.6-opus | 2026-03-09__08-44-46 | 89 | 65 | 0.7386 |
| Mux__Claude-Opus-4.5 | 2026-01-16__00-15-05 | 89 | 52 | 0.5843 |
| Mux__Claude-Opus-4.6 | 2026-02-09__01-47-04 | 89 | 59 | 0.6629 |
| Mux__Claude-Opus-4.6 | 2026-02-09__01-47-09 | 89 | 62 | 0.6966 |
| Mux__Claude-Opus-4.6 | 2026-02-10__00-43-32 | 89 | 57 | 0.6404 |
| Mux__Claude-Opus-4.6 | 2026-02-10__02-03-21 | 89 | 60 | 0.6742 |
| Mux__Claude-Opus-4.6 | 2026-02-10__02-43-25 | 89 | 58 | 0.6517 |
| Mux__GPT-5.2 | 2026-01-16__00-55-00 | 89 | 54 | 0.6207 |
| Mux__GPT-5.3-Codex | 2026-02-11__13-01-28 | 89 | 68 | 0.764 |
| Mux__GPT-5.3-Codex | 2026-02-11__15-49-49 | 89 | 65 | 0.7303 |
| Mux__GPT-5.3-Codex | 2026-02-11__17-02-37 | 89 | 66 | 0.7416 |
| Mux__GPT-5.3-Codex | 2026-02-12__09-49-12 | 89 | 67 | 0.7528 |
| Mux__GPT-5.3-Codex | 2026-02-12__13-28-42 | 89 | 66 | 0.7416 |
| OB-1_GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 2026-02-21__12-03-27 | 89 | 65 | 0.7386 |
| OB-1_GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 2026-02-22__10-25-31 | 89 | 65 | 0.7303 |
| OB-1_GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 2026-02-24__01-21-30 | 89 | 65 | 0.7303 |
| OB-1_GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 2026-02-25__10-05-26 | 89 | 63 | 0.7079 |
| OB-1_GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 2026-02-25__17-36-00 | 89 | 64 | 0.7273 |
| OB-1_GPT-5.4-GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 2026-03-06__15-35-05 | 89 | 71 | 0.8068 |
| OB-1_GPT-5.4-GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 2026-03-06__18-04-12 | 89 | 73 | 0.8202 |
| OB-1_GPT-5.4-GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 2026-03-06__22-10-12 | 89 | 75 | 0.8427 |
| OB-1_GPT-5.4-GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 2026-03-07__00-42-23 | 89 | 73 | 0.8202 |
| OB-1_GPT-5.4-GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | 2026-03-10__12-20-19 | 89 | 75 | 0.8427 |
| OpenCode__Claude-Opus-4.5 | 2026-01-11__01-42-13 | 89 | 46 | 0.5227 |
| OpenSage__GPT-5.3-Codex | 2026-03-04__17-15-16 | 89 | 69 | 0.7841 |
| OpenSage__GPT-5.3-Codex | 2026-03-06__14-31-56 | 89 | 70 | 0.7955 |
| OpenSage__GPT-5.3-Codex | 2026-03-06__23-35-01 | 89 | 70 | 0.7955 |
| OpenSage__GPT-5.3-Codex | 2026-03-07__02-36-36 | 89 | 70 | 0.8046 |
| OpenSage__GPT-5.3-Codex | 2026-03-08__01-10-22 | 89 | 70 | 0.7955 |
| OpenSage__Gemini-3-Pro-Preview | 2026-01-23__08-25-43 | 89 | 57 | 0.6477 |
| OpenSage__Gemini-3-Pro-Preview | 2026-01-23__22-00-30 | 89 | 59 | 0.6705 |
| OpenSage__Gemini-3-Pro-Preview | 2026-01-25__05-43-22 | 89 | 60 | 0.6742 |
| OpenSage__Gemini-3-Pro-Preview | 2026-01-25__20-11-02 | 89 | 57 | 0.6477 |
| OpenSage__Gemini-3-Pro-Preview | 2026-02-12__20-47-36 | 89 | 57 | 0.6477 |
| Simple-Codex__GPT-5.3-Codex | simple-codex-gpt-5.3-codex-5x-duplicate | 445 | 332 | 0.7563 |
| Terminus-KIRA__Claude-Opus-4.6 | 2026-02-13__11-48-54 | 445 | 331 | 0.7489 |
| Terminus-KIRA__Gemini-3.1-Pro-Preview | 2026-02-20__11-30-30 | 445 | 333 | 0.7517 |
| Terminus2__Claude-Opus-4.6 | 2026-02-05__16-08-28 | 89 | 61 | 0.6854 |
| Terminus2__Claude-Opus-4.6 | 2026-02-05__17-41-47 | 356 | 219 | 0.6222 |
| Terminus2__DeepSeek-V3.2 | 2026-02-07__07-47-43 | 445 | 176 | 0.3982 |
| Terminus2__GLM-4.7 | 2026-01-27__12-34-00 | 445 | 147 | 0.3475 |
| Terminus2__GLM-5 | 2026-02-14__13-57-51 | 445 | 231 | 0.5397 |
| Terminus2__GPT-5.3-Codex | terminus-gpt-5.3-codex-5x | 445 | 288 | 0.6545 |
| Terminus2__Kimi-k2.5 | 2026-01-26__22-34-00 | 445 | 189 | 0.4385 |
| Terminus2__Minimax-m2.5 | 2026-02-18__13-31-00 | 445 | 188 | 0.4292 |
| dakou__qwen3-coder-480b | 2025-12-25__23-49-10 | 445 | 121 | 0.275 |
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

| submission | exception_type | n |
| --- | --- | --- |
| Terminus2__GLM-4.7 | DaytonaError | 17 |
| MAYA__Claude-4.6-opus | EnvironmentStartTimeoutError | 9 |
| Terminus2__Kimi-k2.5 | DaytonaError | 9 |
| Gemini_CLI__Gemini-3-Flash-Preview | VerifierTimeoutError | 6 |
| MAYA__Claude-4.5-sonnet | VerifierTimeoutError | 6 |
| OpenSage__GPT-5.3-Codex | VerifierTimeoutError | 5 |
| Droid__Claude-Opus-4.6 | RewardFileNotFoundError | 4 |
| IndusAGICodingAgent__gpt-5.3-codex | EnvironmentStartTimeoutError | 4 |
| Judy__Gemini-3.1-Pro-Preview | VerifierTimeoutError | 4 |
| OpenSage__Gemini-3-Pro-Preview | VerifierTimeoutError | 4 |
| Ante__Gemini-3.1-Pro-Preview | VerifierTimeoutError | 3 |
| Capy__Claude-Opus-4.6 | VerifierTimeoutError | 3 |
| Deep-Agents__GPT-5.2-Codex | DaytonaError | 3 |
| Judy__Claude-Opus-4.6 | VerifierTimeoutError | 3 |
| MAYA__Claude-4.5-sonnet | EnvironmentStartTimeoutError | 3 |
| Terminus-KIRA__Claude-Opus-4.6 | EnvironmentStartTimeoutError | 3 |
| Terminus2__GLM-5 | AddTestsDirError | 3 |
| dakou__qwen3-coder-480b | DownloadVerifierDirError | 3 |
| ClaudeCode__GLM-4.7 | VerifierTimeoutError | 2 |
| Crux__Claude-Opus-4.6 | RewardFileNotFoundError | 2 |
| MAYA__Claude-4.6-opus | VerifierTimeoutError | 2 |
| OB-1_GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | VerifierTimeoutError | 2 |
| Simple-Codex__GPT-5.3-Codex | DaytonaError | 2 |
| CodeBrain-1__GPT-5.3-Codex | VerifierTimeoutError | 1 |
| Forge__Gemini-3.1-Pro-Preview | RewardFileNotFoundError | 1 |
| Mux__GPT-5.2 | VerifierTimeoutError | 1 |
| OB-1_GPT-5.4-GPT-5.3-Codex-Claude-Opus-4.5-Claude-Opus-4.6 | VerifierTimeoutError | 1 |
| Terminus2__DeepSeek-V3.2 | RewardFileNotFoundError | 1 |
| Terminus2__GLM-4.7 | DownloadVerifierDirError | 1 |
| Terminus2__Kimi-k2.5 | AddTestsDirError | 1 |
| Terminus2__Minimax-m2.5 | RewardFileNotFoundError | 1 |
| Terminus2__Minimax-m2.5 | VerifierTimeoutError | 1 |
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

| task_name | failure_rate_pct |
| --- | --- |
| make-doom-for-mips | 100.0 |
| filter-js-from-html | 96.4 |
| caffe-cifar-10 | 96.0 |
| install-windows-3.11 | 93.6 |
| sam-cell-seg | 93.5 |
| train-fasttext | 92.5 |
| raman-fitting | 91.4 |
| extract-moves-from-video | 90.9 |
| gpt2-codegolf | 88.3 |
| video-processing | 79.6 |
| torch-pipeline-parallelism | 78.7 |
| dna-assembly | 76.3 |
| make-mips-interpreter | 74.2 |
| model-extraction-relu-logits | 72.8 |
| mteb-retrieve | 71.1 |
| db-wal-recovery | 69.7 |
| mteb-leaderboard | 69.2 |
| dna-insert | 68.1 |
| torch-tensor-parallelism | 61.8 |
| regex-chess | 59.8 |
| gcode-to-text | 58.1 |
| polyglot-c-py | 54.3 |
| query-optimize | 54.0 |
| polyglot-rust-c | 50.5 |
| path-tracing | 50.0 |
| adaptive-rejection-sampler | 48.1 |
| path-tracing-reverse | 48.1 |
| configure-git-webserver | 46.3 |
| qemu-alpine-ssh | 45.1 |
| chess-best-move | 41.5 |
| write-compressor | 38.4 |
| protein-assembly | 37.6 |
| winning-avg-corewars | 37.6 |
| extract-elf | 36.8 |
| cancel-async-tasks | 35.6 |
| tune-mjcf | 34.4 |
| financial-document-processor | 33.5 |
| overfull-hbox | 32.6 |
| mailman | 31.4 |
| sanitize-git-repo | 30.5 |
| schemelike-metacircular-eval | 29.9 |
| compile-compcert | 28.8 |
| feal-linear-cryptanalysis | 26.4 |
| qemu-startup | 26.2 |
| break-filter-js-from-html | 25.0 |
| circuit-fibsqrt | 24.7 |
| rstan-to-pystan | 24.6 |
| build-pmars | 22.5 |
| largest-eigenval | 22.0 |
| sparql-university | 21.4 |
| large-scale-text-editing | 20.2 |
| build-cython-ext | 19.3 |
| bn-fit-modify | 18.8 |
| pytorch-model-recovery | 18.7 |
| count-dataset-tokens | 17.7 |
| crack-7z-hash | 17.6 |
| mcmc-sampling-stan | 17.2 |
| password-recovery | 16.7 |
| pytorch-model-cli | 16.6 |
| llm-inference-batching-scheduler | 16.0 |
| feal-differential-cryptanalysis | 15.7 |
| reshard-c4-data | 15.2 |
| openssl-selfsigned-cert | 15.0 |
| sqlite-db-truncate | 15.0 |
| sqlite-with-gcov | 15.0 |
| fix-code-vulnerability | 13.4 |
| fix-ocaml-gc | 13.1 |
| build-pov-ray | 13.0 |
| kv-store-grpc | 12.8 |
| hf-model-inference | 11.9 |
| headless-terminal | 11.3 |
| pypi-server | 10.2 |
| merge-diff-arc-agi-task | 9.1 |
| regex-log | 7.4 |
| git-multibranch | 6.5 |
| portfolio-optimization | 6.0 |
| distribution-search | 5.3 |
| log-summary-date-ranges | 5.3 |
| cobol-modernization | 4.8 |
| code-from-image | 4.3 |
| prove-plus-comm | 4.3 |
| custom-memory-heap-crash | 4.3 |
| modernize-scientific-stack | 3.8 |
| multi-source-data-merger | 3.7 |
| vulnerable-secret | 3.7 |
| nginx-request-logging | 3.2 |
| constraints-scheduling | 2.7 |
| fix-git | 2.7 |
| git-leak-recovery | 1.1 |
<!--[[[end]]]-->
