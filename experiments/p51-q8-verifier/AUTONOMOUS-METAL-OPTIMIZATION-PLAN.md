# Project 51 — Isolated M1 Max Metal Optimization Lab (PROPOSED, not deployed)

Date: 2026-10-25. Canonical research cutoff at initial proposal: 2026-10-25T18:45:03Z.
State: `DESIGN-ONLY`. No runner, workflows, schedule, orchestration endpoint, Claude key or hardware benchmark has been installed or verified by this document.

## Evidence gates added October 25, 18:33 EDT (DESIGN-ONLY)

- **Strata #4144** Mac parking defect means the runner's first acceptance test must alternate 2 independent long tool-using agent threads through real backend state, inspect explicit macOS free-memory samples, and compare restored GDN/PLE/QSA/indexer/MTP hashes, actual reused tokens and wall time; do **not** assume the bug occurs in separate paperniuk ds4 without checking.
- **Strata #4141** M4 K-quant tile-grid bug demonstrates wrong-but-fast prefill: compare Metal against reference logits/KL and top1 at actual source-GGUF layer quant types, and flag every missing output tile even if a speed result looks better. UD-Q4_K_XL evidence does not automatically apply to original DASLab IQ3_S.
- **Basalt multi-slot refactor** serves global context divided among `--parallel` slots by default: qualifying independent 128/262K-agent tests require explicit actual per-slot allowance, backed physical allocation and cache reuse counters, plus successful tool-final outputs. No scheduling throughput accepted from truncated reasoning-only requests.
- **KVarN memory accounting** includes metadata/tail/temporary FP16 fallback overhead and actual resident/wired bytes. Fail before kernel work when planner savings cannot close 262K fit safely with OS headroom.
- **Relay** require per-worker KV group ownership and reserved pad/scratch for recurrent state; reject stale transfers and null-page writes before running long agents.

## Purpose and trust boundary

Build a *measured* native Metal QVarN/KVarN + sparse-QSA experiment platform on one **M1 Max 64GiB / 32GPU** while leaving the other Mac available for independent work. Original ISTA-DASLab Qwen3.8-Flash-Next GSQ-RCO **IQ3_S** is canonical quality ruler; IQ3_XXS is an independent capacity/speed comparator, not a substitute. No untrusted forks/PRs to execute on the runner. Keep all original verifier/runtime promoted-stack invariants in README.md, RUNTIME-STATE.md, CURRENT.md and P51J_CERTIFICATION.md.

The connected GitHub integration supplies read, files, refs/commits, workflow-run inspection and reruns but **does not expose a native workflow_dispatch create-run action**. Do NOT imply a ChatGPT web session can run indefinitely. A separately deployed and authenticated dispatcher/controller is required for unattended scheduling; GitHub REST `POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches` through a restricted GitHub App or GitHub CLI is a candidate *outside* this connector and must be configured explicitly. Web ChatGPT review can inspect and approve work, but cannot autonomously wake itself and schedule follow-on turns.

## Security requirements before registering machine

- Dedicated macOS account with empty home, no Apple ID/personal documents/SSH agent/keychain sync/browser sessions, isolated work directory and low privileges; no privileged container or device management credential exposed to job.
- Dedicated runner label and runner group restricted to this repository; verify repository visibility, access policies, runner isolation options and security implications. Prefer ephemeral one-job runner with automated clean rebuild, or a strictly resettable dedicated system account. A self-hosted runner is inherently dangerous for untrusted code; process-level cleanup alone is not a secure boundary.
- **No pull_request or pull_request_target jobs on the self-hosted runner; no fork code, unreviewed workflows or actor-controlled branch strings.** Trigger only via trusted, protected workflow_dispatch on pinned immutable SHA with separate allowlist/approval. Experimental change still runs as untrusted code in dedicated credentialless environment; never grant access to personal machine content.
- `GITHUB_TOKEN` permissions minimized (prefer `contents: read`; result publication via scoped upload artifact rights); no persistent PAT, Claude/OpenAI credentials, registry tokens or cloud keys on runner. Disable write tokens/OIDC by default. If Claude review exists it runs in the separate controller with rate caps, input redaction and a restricted outbound interface; logs contain no secrets.
- Outbound allowlisting where possible, no inbound listening services, disk quota, compile/network timeout and energy/thermal bounds, per-workflow concurrency=1; validate runner updates and macOS/MLX/Metal OS/compiler/driver fingerprints.
- Never execute a candidate on the trusted branch simply because an agent wrote it. Review diff, pin exact expected SHAs, and keep candidate ref separate. Note that repo branch protection and approval settings may require separate administrative setup; not proven by connector.

## Immutable experiment manifest: schema v0

Each attempt is content-addressed: `experiment_id`, `hypothesis`, `source_parent_sha`, `candidate_sha`, `diff_sha256`, `model_repo_revision`, `GGUF sha256`, `KV format/tile/tail`, `OS/MLX/compiler/metallib fingerprints`, `machine_id`, `context_config`, `actual_processed_tokens`, `exact prefill mode`, `seed/sampling/spec`, `warmup/repetitions`, `decision_model`, `reasoning_effort`, `approval_sha`, `budgets`, `state`, `result_artifact_sha256`. Store benchmark JSONL, build log, device allocation census, MTP/selected-indexer state hashes and output/logit parity; never store secrets or uncensored proprietary prompts.

Approval state machine: `PROPOSED -> HIGH-APPROVED -> RUNNING -> RESULTS -> AWAITING-HIGH-REVIEW -> REJECTED|PROMOTED`. The current README prescribes GPT-5.6 Sol High as decision authority; the owner requests evaluating GPT-6 High as the new decision agent. **Do not silently rewrite README or auto-promote the new agent.** When explicitly agreed, separately amend the authority policy and require an authorized review/approval manifest. Workflows may trust explicit signed/reviewed repository approvals, but cannot attest the ChatGPT UI's selected model/reasoning effort.

## Implement in bounded phases (no implementation started)

**Phase 0 — prerequisites and cold baseline.** Confirm consent to dedicate one Mac, macOS account/isolation, Xcode command-line tools, developer-mode availability, MLX ABI and true runner restrictions; inspect canonical promoted-stack validator. Establish a no-mutation manual CI smoke (checkout pinned SHA, compiler versions, disk/GPU identity, tiny known-correct shader). Runner is local to owner's hardware; do not assume Mac1 and Mac2 share memory via TB4.

**Phase 1 — physical memory census before KVarN.** Run original source IQ3_S at32K, then genuine filled 131K if it fits; record fixed model/tensors, resident/wired GPU memory, QSA K/V growing bytes by layer/head and dtype, QSA indexer, precision tail, PLE/ngram table, GDN/recurrent/conv, MTP/drafter, temporary prefill/recompute, checkpoint, OS reserve and physical peak. Reconcile with paperniuk full262K **55.2GiB fixed +8.69GiB growing +2GiB margin =65.9GiB planned** (not hardware peak). Calculate compressible bytes and conservative K4V3 metadata/tail/scratch delta **before** claims of 262K fit.

**Phase 2 — portable reference/correctness.** Compare BeeLlama KVarN K4V3+1024 exact tail route against no-compression precision control on actual M1; detect silent CPU/generic Metal fallback and transient FP16 materialization. Emit per-layer QSA selected-index IDs and scores, logits KL/top-k, GDN/PLE/indexer/MTP commitment and rollback, restore across process restart, deterministic greedy completion. Store explicit FAIL when native Metal route cannot be exercised.

**Phase 3 — native Metal microkernels.** Reference scalar CPU/MLX path then incremental Metal tile128 Hadamard/variance normalization, pack/dequant and direct packed attention (avoid FP16 full-cache materialization). Compare K4V2/K4V3, 1024 recent tail and sink precision against native Q8/K8V4-equivalent quality where backends permit; evaluate cache corruption and group-boundary off-by-one before optimization. Require per-kernel exactness and reproducible cost accounting. Promotion bar: <=10% controlled sustained-decode slowdown vs the defined matched baseline, real net allocated GiB savings, and noninferior source-like solved agent/tool outcomes. A faster microkernel alone is not promotion.

**Phase 4 — end-to-end.** Truly occupied 32K, 128/131K and if safely admitted native262K, with cold prefill and sustained >=512 generated tokens; 5 interleaved paired repetitions after fixed warmup, include variance/power/thermals, physical alloc+peak, time-to-valid-agent-solution, 3–5 distinct durable session checkpoint/rollback with mutable histories and prompt edits. No unstable RAM pressure/swap masks, tokenizer/model revision drift, or hidden offload; partial failures count. Compare source IQ3_S against IQ3_XXS without treating IQ3_XXS gains as IQ3_S wins.

**Phase 5 — Relay only after exact owner baseline.** Independently test CUDA5070Ti exporter → MetalM1 importer committed QSA/GDN/PLE/indexer/MTP frontier at 4/32/128K; CRC + end-to-end hashes, transfer bytes/time via actual network, failure/retry/replay against standalone M1. Two Macs remain independent endpoints, no magic unified-memory clustering.

## External controller (optional and strictly capped)

A service outside ChatGPT web polls approved experiment manifests and GitHub Actions artifacts, dispatches **only an approved experiment**, validates provenance/hashes and shuts off when attempts, runtime, disk, spend/Claude review quota, model-quality divergence or thermals exceed limits. It may submit candidate diffs for a *future distinct High-reasoning review*, but MUST NOT promote its own next mutation without an explicit authorized approval. Optional Claude Opus 5.5 review is a secondary diff+log reviewer, not trusted executor or sole certification. If the owner later wants automatic AI review/approval, that is a **new explicit policy change** requiring independent risk review and budgets; ordinary ChatGPT chat itself cannot run continuously.

## Promotion and rollback gates

No merging experimental kernel until (1) exact model/quant and compiled Metal code IDs match, (2) source/noise control and A/B allocation/latency logs exist, (3) long-agent numerical/functional fidelity survives replays/MTP rejection, (4) real resident RAM and 262K eligibility are demonstrated without hidden OS pressure, (5) results are read back and reviewed under the prevailing HIGH-APPROVED decision rule. Restore only a known-good pinned runtime after crash. Report any candidate causing 5% or greater answer/task regression as rejected regardless of raw TG uplift.
