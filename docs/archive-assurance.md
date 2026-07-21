# Archive Assurance

Run the complete deterministic archive assurance harness with:

```console
pixi run archive-assurance
```

The harness builds a fixed mixed-access graph and checks every public serializer
for restricted text and vector canaries, verifies public/private compatibility,
and checks projection scaling. It then runs a fixed-seed sample of archive
mutants with the focused archive tests. Any serializer leak, compatibility
change, performance bound violation, mutation survivor, or tooling error fails
the command.

For fast local iteration, the non-mutation lanes can be run with:

```console
python scripts/archive_assurance.py --skip-mutation
```
