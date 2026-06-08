-- Count rows in a JSONL ledger file.
-- Runner binds $jsonl_path (e.g. experiments/results/mtf_fib_level_projection.jsonl).
SELECT COUNT(*) AS row_count
FROM read_json_auto($jsonl_path);
