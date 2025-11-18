# Benchmark Results

- Transcripts: `AI engineer assignment/AI engineer assignment transcripts.txt`
- Cues: `solution/repair_cues.txt`
- Iterations per run: `100`
- k values: `10, 50, 200`

| k | method | ms/turn | speedup_vs_regex |
|---|--------|--------:|-----------------:|
| 10 | aho | 0.0134 | - |
| 10 | regex | 0.0099 | 0.74 |
| 50 | aho | 0.0142 | - |
| 50 | regex | 0.0195 | 1.37 |
| 200 | aho | 0.0143 | - |
| 200 | regex | 0.0545 | 3.80 |
