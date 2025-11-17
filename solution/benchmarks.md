# Benchmark Results

- Transcripts: `AI engineer assignment/AI engineer assignment transcripts.txt`
- Cues: `solution/repair_cues.txt`
- Iterations per run: `1000`
- k values: `10, 50, 200, 1000`

| k | method | ms/turn | speedup_vs_regex |
|---|--------|--------:|-----------------:|
| 10 | aho | 0.0127 | - |
| 10 | regex | 0.0099 | 0.78 |
| 50 | aho | 0.0144 | - |
| 50 | regex | 0.0194 | 1.35 |
| 200 | aho | 0.0142 | - |
| 200 | regex | 0.0542 | 3.81 |
| 1000 | aho | 0.0143 | - |
| 1000 | regex | 0.2330 | 16.25 |
