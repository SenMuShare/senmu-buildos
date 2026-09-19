# Senmu BuildOS product source

This directory is the complete, distributable product source. It may be checked out alone or maintained as a declared subtree; use the actual Git root and source-relative path. Installed copies are execution artifacts, not a place to maintain source.

- Start from the requested capability and its existing owner. Eight peer Skills live in `skills/`; Hooks in `hooks/`; host adapters in `adapters/`. Use `docs/architecture/skill-boundaries.md` when ownership or routing is unclear, not as a universal pre-read.
- Preserve authorization, safety, truthful evidence and approved behavior. Reuse existing implementations and references; update affected consumers rather than duplicating complete rules. Runtime guidance and links remain portable.
- Keep raw feedback, private tasks, credentials, user transcripts and author-only state outside this product. A public, synthetic regression or a useful architecture decision may remain here. Product checks and runtime cannot require a private sibling directory.
- Use a scoped task branch and the project's actual write boundaries. Do not edit an installed cache or force-push unrelated work. A source commit does not authorize installation or public release.

Checks from this source root:

```bash
python3 scripts/validate_package.py
python3 scripts/validate_public_surface.py
python3 scripts/bump_version.py --check
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/hooks/*.test.js
```

Use checks matching the changed contract during development and required integration checks at closeout. Preserve unverified limitations; passing source checks does not prove host activation or model performance. Contributor and release-source guidance is in `CONTRIBUTING.md`.
