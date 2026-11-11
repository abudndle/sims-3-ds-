# Public/private GitHub integration

The source repository is `abudndle/sims-3-ds-` (public).
The reference repository is `abudndle/sims-3-ds-private-` (private).

## Connection
The **private** repository runs `.github/workflows/cross-repo-integration.yml`, which checks out:
- `abudndle/sims-3-ds-private-` into `private/` using its automatic GitHub token.
- `abudndle/sims-3-ds-` into `public/` as a public checkout.

This avoids requiring a private read token in a public workflow. The runner validates source syntax, public self-contained tests and the private binary-reference inventory. No private files are committed or uploaded to the public repository, and the workflow has only `contents: read` permissions.

## Triggers
The private integration workflow runs on private reference pushes, hourly on the private repo, or through **Actions → Cross-repository integration (private runner) → Run workflow**. The public source checker runs independently on commits, pull requests, manual dispatch and its configured five-minute schedule.

## Limitations
- This creates a one-way **read-only integration workspace**, not automatic syncing of private assets into the public repository.
- Public pushes do not directly trigger private integration; hourly/manual runs pick up the latest public `main`.
- Private reference binaries are present, but the full original `.nds`, `.cci` and `.cia` archives are not in GitHub. No ROM build is performed.
- The public workflow cannot directly access private files; this is intentional to prevent disclosure.
- Never add private repository credentials to public PR workflows or print contents of private reference files.

## Verified code status
Static ARM7/ARM9 references and research scripts do not constitute an integrated gameplay mod. Touchscreen X/Y origin and the playable ROM patch are still open milestones.
