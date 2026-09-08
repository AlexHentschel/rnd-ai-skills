# The `ai-notes/` folder convention

**Authored:** 2026-09-07. Standalone: a fresh AI with no prior context can follow it.
**Status:** operational discipline. Best-practice default plus the tolerated exceptions.
**Audience:** an AI running a task in someone's repo. Companion to `working-notes-lean-context.md` (which uses
`ai-notes/` as the proposed name for the task-notes root and covers *what goes inside* it and how to keep the chat
lean). This file covers the folder's *git and lifecycle status*: whether it is committed, where it lives, and what
must never depend on it.

---

## 1. What it is

`ai-notes/` is a folder for an AI assistant's **ephemeral working scratch**: local, per-person, per-machine, and by
default **not committed to version control**. It holds the interim material that helps you do a task but is not itself
the deliverable: running notes, a scratch analysis, pending-work reminders, temporary details you are still sorting,
your own session and working context, and resume prompts for continuing the work in a later session.

It exists to fill a specific gap. An agent's built-in cross-session memory is often too sparse to carry the interim
continuity a multi-session task needs, and the chat window is a cache that gets compacted or dropped. `ai-notes/` is
the on-disk continuity buffer. Most of its contents become obsolete once the final, versioned deliverable (the spec,
the code, the doc) is produced.

## 2. The mental model: scratch, not source of truth

- The **versioned repo** (committed spec, code, docs) is the source of truth and the shared team artifact.
- `ai-notes/` is **private scratch** and is neither. Nothing in it is authoritative, and no colleague is expected to
  read it.
- **Durable, team-relevant content belongs in the versioned deliverable, not in `ai-notes/`.** When something in your
  notes turns out to matter permanently, that is the signal to lift it out into the real deliverable, not to keep it
  in scratch.

## 3. The rules

1. **Default to gitignored. This is the best practice.** Add the folder to `.gitignore` at the right scope (see §4).
   A pattern like `**/ai-notes/` catches nested ones. Never commit it as part of normal work.
2. **Keep the dependency one-directional.** Notes may reference the versioned deliverable; the deliverable must never
   reference the notes, and it must stand alone if `ai-notes/` vanished. A committed file that points into `ai-notes/`
   is a defect: every colleague reads committed files, and they do not have your local scratch.
3. **Do not build shared or committed structure inside it.** No per-author committed subfolders, no "shared" committed
   subfolder. If you want structure that others would rely on, that content has outgrown scratch and belongs in the
   repo.
4. **Never reference machine-local or per-person state from any committed file.** Absolute local paths, another
   person's memory, `ai-notes/` paths: none of these are equally available to every reader, so none may appear in
   anything committed. Before writing a path into a committed file, ask whether every colleague has that exact thing.
5. **Never untrack an already-tracked `ai-notes/` on your own initiative.** Adding a not-yet-tracked path to
   `.gitignore` is fine. Removing an already-tracked path from version control changes shared history, so surface it
   and get the human's sign-off first. Keep the files locally either way.

## 4. Scoping: `ai-notes/` is not necessarily one-per-repo

Place `ai-notes/` at the granularity that matches the work, not always at the repo root.

- A conventional single-purpose repo has one `ai-notes/` at its root.
- A repo that is a **collection of stand-alone units** (for example, one folder per self-contained experiment) may
  instead give **each unit its own `ai-notes/`** (an experiment keeps its own experiment-scoped scratch beside it).
  This is explicitly fine and often clearer: the scratch lives next to the thing it serves. Gitignore the matching
  paths accordingly.

## 5. The tolerated exception (best practice still stands)

You may find a repo where an `ai-notes/` folder **is** checked in. This is an accepted **transitional state**, not the
target: it usually means durable and ephemeral content have not yet been separated, so the folder stays committed
until they are. Handle it like this:

- Treat it as a **cleanup opportunity, not a template to copy.** The end state is durable content lifted into the
  versioned deliverable and the ephemeral remainder gitignored.
- **Do not untrack it on your own initiative** (rule 5). Surface it and let the human decide.
- Until then, keep applying rule 2: add no new committed references that point into it.
- When you author fresh guidance or set up a new folder, the recommended default is still gitignored.

## 6. Quick checklist

- Is this content **ephemeral scratch** (into `ai-notes/`) or **durable deliverable** (into the versioned repo)?
- Is `ai-notes/` **gitignored** at the right scope (repo-root or per-unit)?
- Does any **committed** file reference `ai-notes/` or other machine-local state? (Must be none.)
- About to **untrack** an already-tracked `ai-notes/`? (Stop: ask the human first.)
- Found a **checked-in** `ai-notes/`? (Flag it as a transitional state to clean up; do not replicate it.)

## Cross-references

- `working-notes-lean-context.md` — what to put *inside* the notes folder (NOTES.md, INDEX.md, returns/, briefs/,
  spec-staging/) and how to keep the chat window lean. That file treats `ai-notes/` as the proposed working-notes
  root name; this file governs its git and lifecycle status.
- `cold-ai-paradigm.md` — writing notes so a future or different reader needs no prior context.
- `05-CODE-AND-DOCUMENTS.md` — self-contained committed documents and why they must not reference machine-local
  state (the committed-side of rule 4).
