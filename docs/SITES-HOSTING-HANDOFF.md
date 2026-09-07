# Recreating The Railyards hosting handoff

Hosted owner-only review: https://therailyards.jbohne.chatgpt.site
Sites slug therailyards was accepted. Sites returned the workspace-qualified URL above, not therailyards.chatgpt.site.

Site project: appgprj_6a9f369e05c0819187b6fd8d2f4ad167
Manifest: sites/public/.openai/hosting.json
Isolated Sites source checkout: /Users/joshbohne/Developer/TheRailyards-pro-site/work/hosted-site
Sites source commit: 935cc2a130e960706d99a8c4800ad3fc8147ae18
Version 3: appgprj_6a9f369e05c0819187b6fd8d2f4ad167~appgver_04fb46cc2fa08191a92689e2e0178eb2
Successful deployment: appgdep_6a9f3b06558c8191acb8521d08cc18c1

Central implementation is PR #3, stacked over Pro PR #2. The exact requested title is Recreating The Railyards. Use a whole-stadium aerial, direct exploration, short viewpoint labels, comparisons, and a secondary build page. The user rejected the long headline, filler prose, diagram map, and Roosevelt-first framing. Do not restore those.

Build with sites/build-hosted.py using sites/public templates. V11 public/review release archives are checksum-pinned. The 28 MB Draco GLB exceeds the Sites 25 MiB individual-file limit; the hosted build losslessly splits its buffer into external glTF buffers. All 70 buffer views were verified byte-identical, and all files are under the hosting limit. The archived replay bundle is adjusted to load venue.gltf. This repackages the V11 model without changing geometry. Future V12 exports must receive the same limit check.

The build and link/media/anchor checks passed. Deployment succeeded. No fresh browser QA of this simplified hosted version was performed. Existing old Pro preview testing is not proof of this revision. The hosted copy remains private for Josh to review; do not post a tweet or change public access without his instruction.

At September 7 22:18 UTC the account reported 92% weekly usage used, 8% remaining. The Astra launch automation is PAUSED under the existing allowance guard. Do not launch the large task or consume a fresh allowance automatically. Fable checkout was at 27baf11 with an untracked move-arrival receipt; verify completion and pushed artifacts separately.

Reuse this existing Site and source checkout. Do not create another Sites project. Source credentials are short-lived and not saved; obtain a fresh credential for this project when needed. New source/template changes must be committed/pushed to the Sites source repository, built, packaged with the Sites helper, saved as a version, and deployed to existing access.

## Four-page simplification

User reference: https://chat-archive.mweinbach.chatgpt.site/ . Use Overview / Gallery / 3D / Build navigation and the exact title Recreating The Railyards. Light, restrained typography and large renders replace the dense dark landing page. Gallery retains films and source comparison; 3D embeds the existing replay with full-screen access. Build preserves the explicitly incomplete early usage snapshot and distinguishes the API-equivalent estimate from actual charges. Legacy process.html redirects to build.html.

Validation: static production build, all local HTML links/media, four-page navigation, JavaScript syntax, hosting file-size limits, and diff checks. No browser QA requested or claimed.

## V12 content and interaction update

Integrated Fable V12 release from feat/v12-stadium-proportions (fc06d26), including all 29,566 seats. Overview starts with a new 10.5-second native V12 film: above the diamond until 6.549 seconds, then river level, with a single shared play clock and an illustrative splash. The ball is enlarged for legibility. Native frame samples were inspected at contact, flight, river level, and splash. Source comparisons moved to Overview, with side-by-side and true opacity-overlay modes. Gallery has all 36 V12 stills and five videos with All / Videos / Pictures filtering. 3D uses persistent Pick your seat / Pick your view modes; four main cameras plus More viewpoints.

Source assets are the checksum-pinned V12 public/review release ZIPs plus railyards-v12-site-additions.zip on the same release. The additions archive contains the new film, supplemental V12 stills, and the rebuilt replay. Reproduce with sites/render-overview.py and sites/build-v12-media.py; saved model source remains in Fable’s worktree and V12 release. The hosted build verifies all three archive hashes.

Validation: five exported-data tests, TypeScript/Vite production build, JavaScript syntax, 72-file hosted build, local links/media, picture/video counts, V12 scene/seat metadata, disclosures, file-size limits, and clean diff. No new browser QA claimed.

Disclosures name the White Sox, MLB, Crain’s Chicago Business, AECOM and Canal Edge, distinguish concept imagery from our reconstruction, and state that the design/play/sightlines are unofficial and inferred. These statements do not establish image permission or guarantee legal protection.
