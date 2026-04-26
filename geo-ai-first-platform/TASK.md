Implement the MVP described in PLAN.md.

Requirements:
1. Use Python 3 standard library only. No pip installs.
2. Create a working CLI:
   python3 geo_builder.py examples/sample_company.json --out dist
3. Generate all artifacts listed in PLAN.md.
4. Include clean, readable code split into modules under geo_core/.
5. Include examples/sample_company.json.
6. Include tests using unittest.
7. Include README.md.
8. Verify with:
   python3 geo_builder.py examples/sample_company.json --out dist
   python3 -m unittest discover -s tests

Important product behavior:
- The knowledge core is the source of truth.
- Human pages and AI/search artifacts are generated from the same core.
- Include a claim-evidence map in the report.
- Include AI readiness scoring with clear dimensions and missing items.
- HTML should be simple, clean, and readable. No external assets.

Stay inside this repository. Do not read or modify ~/.hermes, ~/.codex, ~/.gstack, or other home config directories.
