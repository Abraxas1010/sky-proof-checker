# Release Checks

```bash
python3 tests/test_reducer.py
python3 tests/test_cli_parity.py
python3 tests/test_customer_examples.py
cd rust && cargo run -- ../examples/trivial_true.sky.json
cd go && go run checker.go ../examples/trivial_true.sky.json
cd typescript && npm ci && npx ts-node src/reducer.ts ../examples/trivial_true.sky.json
```
