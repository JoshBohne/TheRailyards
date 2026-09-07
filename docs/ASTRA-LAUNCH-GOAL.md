# Astra integration and launch-preparation goal

User request, 2026-09-07: after the GPT Pro website PR and Fable's Blender corrections are ready, start a fresh Astra Ultra Codex task with a proper goal to improve the whole Railyards experience, leaving roughly 10% weekly Codex allowance for Josh's review and fixes. Prepare eventual publication through Sites and a launch tweet. The repository is now PUBLIC: https://github.com/JoshBohne/TheRailyards. Old descriptions of private repo/releases are outdated.

## Launch gates

1. Identify the actual website PR from the ChatGPT task “Tweet stadium visualization website” (conversation 6a9f1489-07bc-83e9-b147-2b58bb7c833e). Do not mistake V11 PR #1 for that new website work. Confirm pushed source/head and actual build output.
2. Fable's fresh Claude task “Railyards stadium proportions” must have finished and pushed its V12 geometry, with saved scene and visual evidence recoverable. Its worktree began at `.claude/worktrees/railyards-stadium-proportions-cb24d4`; discover current status instead of assuming completion from silence or a clean worktree. Preserve ownership and avoid overwriting active scene writes.
3. Record both delivered commits/PRs and paths to scene/export artifacts. Integrate from those heads in a new isolated Codex worktree, preserving the earlier versions. If integration needs merging/cherry-picking, do it locally on the integration branch; do not silently merge unfinished source PRs to main.
4. The requested Astra name was “GPT 5.6 Astra Ultra”; this host currently exposes `gpt-6-astra` with `ultra`. A model-name confirmation is pending in the coordinating task. Use the confirmed Astra model, never silently substitute a different family.

## Goal for the new task

Explicitly create a goal: integrate the delivered website and corrected Blender model; substantially improve the most important remaining visual, interactive and performance problems; deliver a coherent, tested Railyards experience ready for Josh's review, plus a publishing package and launch draft, within the remaining usage allowance.

The experience should let visitors understand the proposed park from perspectives the original aerial renderings did not show. Prioritize enjoyable human-scale exploration, beautiful actual renders, intuitive viewpoint selection, good mobile behavior, useful source comparisons and coherent transitions. Preserve working seat selection/shared-clock replay unless a replacement clearly improves the visitor experience. Keep the build/process/model/token story on a secondary page; use only grounded usage/cost numbers, clearly labeled when incomplete or estimated.

Inspect the incoming PR and scene skeptically, then choose substantial changes justified by visible evidence. Address outstanding stadium proportions, outfield corners, Roosevelt park/arch/restaurant/bleacher levels, RF/tower junction, dugout clearances and flag if still wrong. Do not hide defective geometry by moving cameras. Read `docs/FABLE-5.1-V12-HANDOFF.md`, the exact user north image and all newer Fable evidence. Verify source fidelity with fixed north/south/bridge comparisons and affected human-scale views. Label inferred architecture and illustrative flight honestly.

Improve the site as a whole: guided exploration, loading behavior, device-appropriate assets, camera/framing quality, responsive navigation, touch/keyboard operation, fallback media, shareable views, credits and clear proposal context. Inspect actual browser results early and iterate. Make the smallest coherent implementation for each improvement; do not churn working code or spend tokens merely to exhaust the allowance.

## Usage and time guardrails

The September 7 15:44 Central account reading is 16% used / 84% remaining in the 10080-minute `codex` window, resetsAt 1789356993 (September 13 22:36:33 Central). Josh reports a special reset tonight; the account tool does not confirm it. Do not assume the special reset has occurred or extend the run into a fresh allowance automatically.

At startup, each goal continuation, at least every five minutes during active work, and before expensive phases, read `get_usage_limits`. Use `rateLimitsByLimitId.codex` and identify its weekly window by duration; remaining = 100 - usedPercent. This is an account-wide soft guard, not an enforceable per-task spending cap. All parallel account work counts.

Start packaging/checkpointing around 15% remaining. Stop initiating work by 12% remaining to target about 10% left after finishing small in-flight actions. Stop sooner if the review-ready objective is achieved. If usage is missing, the weekly reset timestamp changes, or used percentage unexpectedly drops significantly, checkpoint and return for user review instead of spending the new allowance. Do not redeem resets, buy credits, or change account settings.

This authorization is for the September 7 pre-reset work period. Stop and deliver a checkpoint no later than local midnight (2026-09-08T05:00:00Z) unless Josh explicitly extends it or supplies a more precise deadline. If inputs are still missing then, do not launch late automatically.

The goal is a reviewable outcome within these limits. Before ending, push the current coherent branch and supply a truthful completion/remaining-work report with runnable preview and evidence. Do not call unfinished geometry or unchecked UI complete merely because the budget is low. Do not leave an autonomous goal repeatedly continuing past the allowance guard: structure its objective around delivering this bounded review checkpoint and complete it when that checkpoint has actually been delivered.

## Delivery and publication

Keep source, specifications, docs and PRs centralized in JoshBohne/TheRailyards. Generated Blender scenes, renders and large exports stay outside ordinary Git; provide versioned recoverable release assets and checksums, remembering that this repository and its releases are public. Never include credentials or private account/session data in site content or artifacts.

Reopen/render the saved scene; test geometry changes meaningfully; build/typecheck/test the site; inspect actual desktop and mobile browser output, playback, camera transitions, comparisons and share URLs. Report real-device or hosted-network limits accurately. Bind the served artifacts and PR to the final pushed commit.

Prepare Sites publication using the installed `sites-building` and `sites-hosting` skills, verifying static assets/GLB/media and the deployment contract. Do not publish the site publicly or post the tweet before Josh's review/approval of the concrete result. Prepare the publication package, representative media and a concise launch tweet for that review. Preserve the main fan experience as the deliverable, with the technical build story secondary.
