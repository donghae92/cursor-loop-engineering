# Android project example

Install Cursor Loop Engineering into a **Gradle-based Android** repository (Kotlin or Java).

## Prerequisites

- Android Studio or command-line SDK
- Python 3.10+ on your machine
- Clone of [cursor-loop-engineering](https://github.com/your-org/cursor-loop-engineering)

## Install

```bash
export CLE_ROOT="$HOME/src/cursor-loop-engineering"

pip install -e "$CLE_ROOT"

# From your Android project root (contains settings.gradle or settings.gradle.kts)
cd ~/projects/my-android-app

python3 -m cursor_loop install .
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
python3 -m cursor_loop status
```

## Recommended `.gitignore` entries

```gitignore
.cursor-loop/quarantine/
.cursor-loop/runtime/
.cursor-loop/checkpoints/
```

Many teams **commit** `.cursor/` after install to pin framework policy versions.

## Customize `AGENTS.md`

If install created a starter `AGENTS.md`, extend it with Android-specific commands:

```markdown
## Build

./gradlew assembleDebug
./gradlew testDebugUnitTest
```

## Cursor usage

- Add `.cursor/rules/android.mdc` with `globs: "**/*.{kt,java,xml}"` for module conventions.
- Use the `developer` agent for feature work; `qa` agent after Gradle test tasks.
- Run `python3 -m cursor_loop verify` before release checkpoints.

## CI (GitHub Actions)

```yaml
jobs:
  cursor-loop:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ./cursor-loop-engineering
      - run: python3 -m cursor_loop bootstrap
      - run: python3 -m cursor_loop verify
  android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"
      - run: ./gradlew testDebugUnitTest
```

## Update framework

```bash
pip install -e "$CLE_ROOT"
python3 -m cursor_loop update
python3 -m cursor_loop verify
```

See [docs/migration-guide.md](../../docs/migration-guide.md).
