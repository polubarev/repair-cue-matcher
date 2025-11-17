# Benchmark Results

- Transcripts: `AI engineer assignment/AI engineer assignment transcripts.txt`
- Cues: `solution/repair_cues.txt`
- Iterations per run: `50`
- k values: `10, 50, 200`

| k | method | ms/turn | speedup_vs_regex |
|---|--------|--------:|-----------------:|
| 10 | aho | 0.0138 | - |
| 10 | regex | 0.0102 | 0.74 |
| 50 | aho | 0.0144 | - |
| 50 | regex | 0.0193 | 1.34 |
| 200 | aho | 0.0145 | - |
| 200 | regex | 0.0538 | 3.72 |
