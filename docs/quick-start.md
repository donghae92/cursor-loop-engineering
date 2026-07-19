# Quick start

```bash
git clone https://github.com/donghae92/cursor-loop-engineering.git
cd cursor-loop-engineering
pip install -e ".[dev]"
cle bootstrap --self
cle verify
```

Install into another project:

```bash
cle install ~/projects/my-app
cle verify --path ~/projects/my-app
```

If verify fails:

```bash
cle doctor --path ~/projects/my-app --repair
cle loop --once --path ~/projects/my-app
cle verify --path ~/projects/my-app
```
