# ArjanCodes design calibration

**Reviewed:** 2026-09-20. **Status:** Research and recommendations; no implementation language or extension mechanism selected.

## Evidence and scope

Inspected the 2025 and 2026 directories of [ArjanCodes/examples](https://github.com/ArjanCodes/examples) at commit `be939a5cfa5f970a98a4658756d86cbe70e417a9`. Selected six videos using the examples, retrieved their English captions and metadata with yt-dlp, and reviewed relevant transcript passages alongside code. Video descriptions explicitly link the corresponding example directories. Dates below are video upload dates, not assumptions based on directory names. Captions can contain recognition errors; code is the stronger evidence for exact identifiers and behavior. This is a targeted review, not a survey of every video or a claim about the author's approval of refs.

The repository checkout and caption downloads were temporary research inputs. This note preserves the findings and source links, not copies of the transcripts. Video titles can change: the ports video's channel listing and individual metadata returned different titles for the same ID.

## Selected material

### 1. Abstractions should emerge from actual variation

[You Don’t Need That Design Pattern](https://www.youtube.com/watch?v=xns3InDkAiA), 2026-06-19. [Example](https://github.com/ArjanCodes/examples/tree/be939a5cfa5f970a98a4658756d86cbe70e417a9/2026/pattern). Useful sections: 2:14 functions; 6:40 adapter; 13:25 decision rule.

Prompt strategy classes and a factory become functions and a dictionary. An LLM protocol then groups generation, token counting, and context limits because the summarization workflow needs these related capabilities. The adapter translates provider responses into an application-owned result.

For refs, this supports simple functions for transformations and a coherent provider boundary where needed. It does not justify a universal LLM interface for search, summarization, and Jev classification. The example's model calls are simulated, and its chunking is illustrative rather than a production context-budget solution.

### 2. Define interfaces from the consumer's needs

[You Think This Is Good OOP… It’s Not](https://www.youtube.com/watch?v=RqcEK7sWesQ), 2026-08-28. [Example](https://github.com/ArjanCodes/examples/tree/be939a5cfa5f970a98a4658756d86cbe70e417a9/2026/oop). Useful sections: 8:33 oversized base classes; 12:30 substitutability; 15:18 premature abstraction; 17:56 synthesis.

The examples separate authentication and inventory capabilities, and read and write contracts. Configuration values replace subclasses; independent features avoid combinatorial inheritance. Similar-looking importers remain separate when their meaning differs. His closing guidance explicitly supports classes for invariants and meaningful state, protocols for interfaces, and functions where state or identity adds nothing.

For refs, separate search, indexing, classification, and enrichment contracts as their workflows require. A provider should not acquire unsupported methods merely to satisfy an oversized base class. Bibliographic import and web capture need not share an internal algorithm just because both create sources.

### 3. Protect the domain boundary

[Ports and adapters video](https://www.youtube.com/watch?v=FXwBWS4qDAA), 2026-03-06. [Example](https://github.com/ArjanCodes/examples/tree/be939a5cfa5f970a98a4658756d86cbe70e417a9/2026/ports). Useful sections: 3:11 architecture; 12:54 consumer-defined port; approximately 24:00 production qualification.

Domain types and errors replace framework-shaped inputs and outputs. A protocol expresses inventory operations; adapters perform SQL and HTTP translation. The domain workflow remains testable without those frameworks. It still invokes effectful operations through the port, so framework independence should not be confused with mathematical purity.

For refs, preserve application-owned identities, decisions, and errors across CLI and provider boundaries. The video acknowledges that production reservation should be atomic. Our contracts must explicitly cover conflicts and transactions; interface shape alone cannot establish those guarantees.

### 4. Compose policies, with limits on configurability

[Don’t Use Boolean Flags in Python, Use Policies Instead](https://www.youtube.com/watch?v=wYeDGkdMi3g), 2026-04-24. [Example](https://github.com/ArjanCodes/examples/tree/be939a5cfa5f970a98a4658756d86cbe70e417a9/2026/policy). Useful sections: 6:51 functions; 10:56 configuration; 14:07 tradeoffs.

Policy classes become functions operating on explicit inputs. An ordered registry and settings select the pipeline. The explanation distinguishes selecting an algorithm from composing multiple rules and acknowledges the additional structure.

For refs, this is useful for configurable enrichment and assignment preferences. Mandatory vocabulary validation, human overrides, and catalog integrity must remain enforced regardless of optional pipeline configuration. I would normally use a straightforward loop instead of the example's reduce/lambda when that makes execution easier to inspect. The later OOP example also uses a boolean option: the video title should not become a blanket ban on booleans.

### 5. Registration is distinct from provider behavior

[Registry pattern video](https://www.youtube.com/watch?v=g7EGMWvJ1fI), 2025-10-17. [Example](https://github.com/ArjanCodes/examples/tree/be939a5cfa5f970a98a4658756d86cbe70e417a9/2025/registry). Useful sections: 9:50 registry; 12:33 extension; 14:18 pitfalls.

Functions register as CLI commands; importing modules discovers extensions. The author explicitly warns about hidden registration and import order and says simpler branches sometimes suffice.

For refs, selectable providers and independently installable extensions are separate requirements. This example demonstrates discovery, but does not establish a complete external-package contract. Specify compatibility, duplicate names, configuration failures, and explicit selection before adopting a loader. Keep capability implementations independent of CLI registration.

### 6. Include a counterexample to the usual preferences

[I Designed a Python SDK That Relies on… Deep Inheritance?!](https://www.youtube.com/watch?v=Ov8JsEnNLCM), 2025-07-11. [Example](https://github.com/ArjanCodes/examples/tree/be939a5cfa5f970a98a4658756d86cbe70e417a9/2025/sdk). Useful sections: 8:05 injected client; 11:33 global client; 15:23 generic base model; 20:40 tradeoffs.

The SDK deliberately trades explicit client passing for a shared module client and uses inheritance to share resource operations. He acknowledges harder testing and stronger coupling. This qualifies any description of his style as categorically opposed to inheritance or global state.

I would reject the shared-client choice for refs' evaluation boundary: two differently configured providers should coexist in one comparison without overwriting global configuration. Shared implementation may still be justified inside an adapter. Source records should not acquire provider-specific network operations merely for convenient syntax.

## Resulting approach for refs

Start from a concrete workflow and expected changes. Keep simple transformations as functions. Introduce a small interface where it protects the workflow from meaningful variation, and use classes for coherent state, lifecycle, or invariants. Construct dependencies at the application boundary. Keep required catalog policy independent of selected providers. Verify replacement using two real implementations and versioned inputs.

The characterization is pragmatic typed Python combining functional composition with objects, rather than a fixed preference ordering that settles every design. These examples make the reasoning more precise; they do not select Python or imply that every implementation detail is suitable for refs.

For a future “WWAD” review, report: the relevant documented principle; the concrete change or dependency it addresses; the simpler alternative; the evidence that the boundary helps; and any deliberate departure with its reason. Follow the reasoning while retaining independent judgment.
