# Negative Examples

These are examples that should usually not trigger delegation.

## English

1. `Fix this typo in the README.`
2. `Rename this variable in one file.`
3. `What port is the dev server using right now?`
4. `Do not use subagents for this task.`
5. `delegation_context: delegated-subagent; parent Dispatch Authorization already granted; goal: Extract candidate papers from this source list.`

## Chinese

6. `把这个函数名改一下。`
7. `这个报错是什么意思？先别用 subagent。`
8. `就修这个单文件的小 bug，不要并行拆分。`
9. `先回答我这个关键问题：这个接口到底返回什么？`
10. `delegation_context: delegated-subagent; parent Dispatch Authorization already granted; goal: 按这个 handoff 抽取候选文献。`
11. `Optimize this CLI parser. It feels slow on large files.`
12. `Review this small README typo fix.`
13. `Add some tests here, not sure what exactly.`
14. `Make this secure.`
15. `Read this one-line config value and summarize it.`
16. `$grill-with-docs Design this one component; repeat the same design work in a second lane.`

Why these are negative examples:

- the task is too small or too direct
- there is no bounded Child Contribution with a material benefit
- the request is blocked on one immediate answer
- the user has explicitly opted out
- delegated subagent handoffs already have Dispatch Authorization and should execute, not select another lineup
- waiting alone is not a benefit, and duplicate focused-skill work is still wasteful
- Web performance specialists should not be used for non-Web performance tasks, write-capable testing should not start from unclear behavior, and vague security wording should be clarified before suggesting a security lineup

Borderline note:

If a request grows to include a bounded autonomous Child Contribution with material benefit and safe ownership, it may become positive later in the conversation. A separate Root deliverable is not required.
