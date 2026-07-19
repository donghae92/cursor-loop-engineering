# Flutter project example

Install Cursor Loop Engineering into a **Flutter/Dart** repository.

## Prerequisites

- Flutter SDK (`flutter doctor` clean)
- Python 3.10+
- Clone of [cursor-loop-engineering](https://github.com/your-org/cursor-loop-engineering)

## Install

```bash
export CLE_ROOT="$HOME/src/cursor-loop-engineering"
pip install -e "$CLE_ROOT"

cd ~/projects/my_flutter_app

python3 -m cursor_loop install .
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
python3 -m cursor_loop status
```

## Project layout

Typical Flutter tree after install:

```
my_flutter_app/
├── .cursor/           # framework assets
├── .cursor-loop/      # runtime memory
├── lib/
├── test/
├── pubspec.yaml
└── AGENTS.md          # created if missing
```

## Customize `AGENTS.md`

```markdown
## Flutter commands

flutter pub get
flutter analyze
flutter test
```

## Cursor rules

`.cursor/rules/flutter.mdc`:

```yaml
---
description: Flutter widget and state conventions
globs: "lib/**/*.dart"
alwaysApply: false
---

# Flutter

- Prefer const constructors where possible.
- Run `flutter analyze` before PR.
```

## Verification with app tests

```bash
flutter test
python3 -m cursor_loop verify
```

Use the `validation` skill in Cursor after editing platform channels or native embedders.

## CI

```yaml
- uses: subosito/flutter-action@v2
  with:
    channel: stable
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- run: pip install -e ./cursor-loop-engineering
- run: flutter pub get
- run: flutter test
- run: python3 -m cursor_loop bootstrap
- run: python3 -m cursor_loop verify
```

## Update

```bash
python3 -m cursor_loop update
python3 -m cursor_loop verify
```
