# Physical116 complete-fixes IPA release request

User explicitly requested: “Make ipa with all fixes from my logs.” The release gate passed locally for the frozen implementation55d472b7a8ecfe87f1cc7288f7ae8964e193fd86, runtime67cd3e9, cumulative patch ed92adf94c7ff4c161b3a64b054fd708c0bdaa347eee055bb7fe05b7fcada289. Native/app43673650998 and focused GPU43673650970 both passed. This request changes validation/release metadata and archive inspection only; source, pinned dependencies, version0.3.15(116), and patch remain frozen.

Packaging must verify the actual CPU writeback reuse, bounded background compiler, fallback attribution and receive-batch symbols in the IPA, plus all existing packaging, signature, extension, entitlement and source checks. Do not substitute the previously shipped116 IPA. Distinguish this archive by exact release commit and SHA256. Publish the verified artifact and copy the IPA into the user’s Google Drive.

Cloud validation does not prove physical M4/A20 FPS, cooling, Metal4 pixels or the reported iPad termination cause. Preserve these limitations in the release receipt. Upstream PR extraction/publication is a separate task and remains unfinished; do not misrepresent it as complete.
