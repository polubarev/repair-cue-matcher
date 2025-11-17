# Benchmark Results

- Transcripts: `AI engineer assignment/AI engineer assignment transcripts.txt`
- Cues: `solution/repair_cues.txt`
- Iterations per run: `1000`
- k values: `10, 50, 200, 1000`

| k | method | ms/turn | speedup_vs_regex |
|---|--------|--------:|-----------------:|
| 10 | aho | 0.0128 | - |
| 10 | regex | 0.0098 | 0.77 |
| 50 | aho | 0.0141 | - |
| 50 | regex | 0.0192 | 1.37 |
| 200 | aho | 0.0141 | - |
| 200 | regex | 0.0544 | 3.87 |
| 1000 | aho | 0.0142 | - |
| 1000 | regex | 0.2338 | 16.51 |
