# CSV streaming benchmark

Run from the repository root after installing the package:

```sh
python -m pip install -e .
python benchmarks/csv_memory.py
```

Synthetic workload: 5 sessions, 50 exercises per session, 20 sets per exercise,
52 weeks: 260,000 data rows plus the header. The benchmark compares the old
buffered approach (build CSV text and write it to a file) with the new streaming
approach on the same validated program, using ordinary UTF-8 file writes.
It records separately measured wall time, Python allocations traced by
`tracemalloc`, output size and SHA-256.

Observed on Python 3.13.5, Linux x86_64:

| Metric | Buffered | Streaming |
| --- | ---: | ---: |
| Output bytes | 27,086,134 | 27,086,134 |
| Peak traced Python allocation (bytes) | 60,949,235 | 157,613 |
| Wall time (seconds) | 0.7244 | 0.5514 |

Both hashes: `f0200c679e2429a44885fbbcfcc63e9ac1d9878ed1565ba71a37774b38460308`.

This is a single experimental observation, not an RSS measurement, speed
guarantee, or comparison with a different product. It excludes parsing, fsync,
and atomic publication overhead. The pre-existing buffered API remains supported.
Streaming is required to preserve the byte contract; no benchmark result is a
license to weaken correctness or security.
