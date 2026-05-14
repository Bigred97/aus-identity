# aus-identity

Foundational join-keys library for the Australian Public Data MCP portfolio.
This is **not** an MCP — it's the shared crosswalk library that the MCPs
(abs-mcp, ato-mcp, apra-mcp, aihw-mcp, asic-mcp, etc.) depend on for
postcode/state/identifier normalisation.

See `../CLAUDE.md` for portfolio-wide conventions.

## What this package is

| | |
|--|--|
| Purpose | Cross-source join keys for AU public data — postcode/state crosswalks, state-code normalisation, etc. |
| Licence | MIT (code only — no government data is bundled) |
| Python module | `aus_identity` |
| PyPI package | `aus-identity` |
| GitHub | https://github.com/Bigred97/aus-identity |
| Runtime deps | None — pure Python, zero-dependency, wheel < 20 KB |

## What's in v0.1.0

- `postcode_to_state(code)` — handles the three ACT-inside-NSW carve-outs (`0200-0299`, `2600-2618`, `2900-2920`)
- `normalize_postcode(x)` — accepts `"2000"`, `2000`, `" 2000 "`, `"0800"`, `800` → canonical 4-digit string
- `is_valid_postcode(x)` — boolean, never raises
- `normalize_state(x)` — accepts long names, short codes, "Tassie", "AU-VIC" → canonical short code
- `state_full_name(code)` — `"NSW"` → `"New South Wales"`

## Why it exists separately

Every sister MCP needs the same postcode/state logic. Inlining the same 200
lines into 8 repos and then having them drift is the failure mode this package
prevents. Each MCP imports `aus-identity>=0.1.0` rather than maintaining its
own copy.

## Anti-patterns — DO NOT do these

- Don't add runtime dependencies. The whole point is "zero-dep, < 20 KB, drop into anything"
- Don't bundle government data fixtures here — those belong in the consuming MCP's curated YAMLs
- Don't add MCP tools — this is a library, not an MCP server
- Don't break the public API. This is used by every sister MCP; semver minor bumps must stay back-compat

## Common operations

```bash
uv sync --extra dev        # install
uv run pytest              # tests
uv build                   # wheel + sdist (for tag-driven OIDC publish)
```

## Release workflow

Trusted Publishing via OIDC (no PyPI tokens). Tag `vX.Y.Z` → `release.yml`
fires → publishes to PyPI.

```
1. Bump version in pyproject.toml
2. Update CHANGELOG.md
3. uv run pytest
4. git commit -am "X.Y.Z: <reason>"
5. git tag -a vX.Y.Z -m "..."
6. git push origin main vX.Y.Z
```
