## Summary

<!-- What changed and why? Link issues with "Fixes #123" or "Relates to #456". -->

## Type of change

- [ ] Bug fix
- [ ] Feature
- [ ] Documentation
- [ ] Infrastructure / CI
- [ ] Breaking change

## Checklist

- [ ] `python3 -m cursor_loop verify` passes locally
- [ ] `pytest` passes (or N/A with explanation)
- [ ] Docs updated for user-visible CLI, hook, or runtime changes
- [ ] CHANGELOG updated under `[Unreleased]` or release section
- [ ] No secrets, tokens, or credentials included
- [ ] Hook scripts remain executable (or `cle repair` fixes them)

## Test plan

<!-- Concrete steps a reviewer can run. -->

```bash
pip install -e .
python3 -m cursor_loop bootstrap --self
python3 -m cursor_loop verify
pytest
```