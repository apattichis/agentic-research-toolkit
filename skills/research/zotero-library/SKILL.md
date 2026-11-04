---
name: zotero-library
description: Find, add and file papers in the user's Zotero library for the current project without changing anything the user already has. Use when a task needs the user's own papers, their PDFs' full text, citations from their library, or adding a paper to the project's reading list.
---

# Zotero library

The user's Zotero library is shared by all their projects. Treat everything already in it as theirs: read it freely, add to it carefully, and never change or remove what is there.

## Setup this skill expects

- The Zotero MCP server (`zotero-mcp-server`) is installed once for the user's account and registered in each client, with `ZOTERO_LOCAL=true` so reads come straight from the local Zotero database.
- Writes go through the Zotero web API, so the user keeps a key in the `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID` environment variables. Never print or copy their values.
- Tools that delete or change existing content are blocked in the client settings. If a tool call is refused, do not look for another way to make the same change.
- The project names its collection in its `AGENTS.md`, for example `Zotero collection: Edge LLMs`. If none is named, ask the user before creating one.

## Rules

1. Never delete anything: no items, collections, notes, annotations or attachments.
2. Never remove a paper from a collection and never rename, move or edit an existing collection.
3. Never edit an existing item's fields, notes or annotations.
4. Allowed: create the project's collection, add new papers, add papers to the project's collection, and attach files only to papers you added.
5. Tag every paper you add `added-by-agent`, so the user can review what came in.

## Workflow

1. **Search first.** Look the paper up by title, DOI or arXiv ID with `zotero_search_items`. My Library holds every paper once, and a paper can belong to several collections.
2. **Already there:** add it to the project's collection with `zotero_set_item_collections` using `add_to` only. Its other collections stay as they are. Never pass `remove_from`, and never use `zotero_update_item` to set collections, because that replaces them all.
3. **Not there:** add it with `zotero_add_item`, giving the DOI or arXiv ID as the source, the project's collection, and the tag `added-by-agent`.
4. **Report** each paper with its item key, whether it was new or already in the library, and the collection it went into.

## Known behaviour

- Pass the collection by name, for example `"Edge LLMs"`, when you file a paper right after creating the collection. A just-created key can fail to resolve in the same session.
- Local reads see web writes only after the Zotero desktop app syncs, so a paper you just added may not appear in a local search for a minute. Confirm a write from the tool's own result.
- In Codex, every Zotero call needs approval. Delegated Codex runs that use Zotero need `--approve-for-me`.

## Citations

For a report or paper, the user exports the project's collection with Better BibTeX (Better BibLaTeX, Keep updated) to the project's `references.bib`. Cite with those citation keys and never edit `references.bib` by hand.
