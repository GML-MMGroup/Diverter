# Recommend auto during explicit installation mode choice

Fresh installations will explicitly ask the user to choose a Delegation Policy and recommend `auto` as the Ultra-distilled proactive experience, while keeping `ask` available for approval-first operation. This replaces ADR-0007's silent initialization of `ask`; Diverter never silently defaults a user to `auto`, and missing or invalid configuration still falls back safely to `ask`.
