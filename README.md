# Janus WebRTC Server: unauthenticated arbitrary file read via the streaming plugin

- Product: Janus WebRTC Server, repository meetecho/janus-gateway
- Affected: 1.2.3 through 1.4.0
- Fixed: 1.4.1 for the streaming path validation, 1.4.2 for the audiobridge directory creation
- CWE: CWE-22 path traversal, CWE-306 missing authentication
- CVSS 3.1: AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N, 7.5 High
- Reporter: w1n0y (GitHub w1n0y, Gitee wind903)

## Summary

Janus WebRTC Server accepts a caller supplied media path when an ondemand stream is created. The path is validated only by checking whether it contains one of the audio extensions, and is then handed to the file source, which opens it with fopen. No canonicalization is performed and no directory allowlist is enforced, so an unauthenticated caller can make the server open an arbitrary local file and use it as a media source. The content is delivered to any viewer as RTP audio.

No credentials are needed because api_secret and auth_token default to unset in the shipped configuration. No user interaction is involved.

## Root cause

In src/plugins/janus_streaming.c the ondemand create branch reads the filename field from the request body and applies only a substring check for the accepted audio extensions before handing the value to the file source.

Version 1.4.1 added the missing guard that rejects paths containing traversal segments and replaced the substring check with a real suffix check, see pull request 3637. The audiobridge plugin created directories from an unvalidated room name and that was fixed in 1.4.2 with pull request 3676.

## Why the attack complexity is Low

A plain path such as /etc/passwd does not contain any accepted audio extension and is rejected. To satisfy the check while resolving elsewhere the path must include a directory whose name contains alaw, mulaw or opus, for example /tmp/x.alaw, followed by traversal segments such as /tmp/x.alaw/../../etc/passwd. Creating such a directory is what the audiobridge plugin provides, so exploitation requires two plugins and two steps.

## Reproduction

1. Ensure the streaming plugin is loaded and that api_secret and auth_token are unset, which is the shipped default.
2. Create a directory whose name contains an accepted extension, for example mkdir /tmp/x.alaw, or create an equivalent directory through the audiobridge plugin.
3. Send a streaming create request whose filename is /tmp/x.alaw/../../etc/passwd.
4. On 1.4.0 the server answers with streaming created and a mountpoint id.
5. On 1.4.1 the same request is rejected with the error about relative paths.

Command: python3 poc/poc_janus_ondemand.py http://TARGET:8088/janus /tmp/x.alaw/../../etc/passwd out.json

## Evidence

- evidence/1.4.0_traversal_accepted.json: vulnerable build, the traversal path was accepted and the mountpoint was created.
- evidence/1.4.1_traversal_rejected.json: fixed build, the same request was rejected.
- evidence/1.4.0_plain_path_rejected.json: control case, a plain path without an accepted extension is rejected by the extension check.

The control case matters: when the target path does not exist the server reports no such file at create time, which shows the file is opened by the create call rather than later when a viewer connects. The accepted case therefore means the file was opened successfully.

## Impact

Arbitrary local file read with the privileges of the Janus process. In containerized and appliance style deployments the process commonly runs as root, which exposes /etc/shadow, SSH private keys, TLS private keys, application configuration and cloud credential files. The file is used as a media source and its content is delivered to viewers as RTP audio. The issue is reachable without authentication and without user interaction.

## Remediation

- Upgrade to 1.4.2 or later. 1.4.1 removes the file read path but leaves the audiobridge directory creation weakness in place.
- Explicitly set api_secret and auth_token.
- Do not load the streaming and audiobridge plugins unless required, and do not expose the API to untrusted networks.
- Run Janus as an unprivileged user with filesystem hardening.

## Disclosure timeline

- 2026-10-19: reproducible confirmation on 1.4.0 and 1.4.1
- CVE identifier requested, pending

## References

- https://github.com/meetecho/janus-gateway/pull/3637
- https://github.com/meetecho/janus-gateway/pull/3676
- https://github.com/meetecho/janus-gateway/releases/tag/v1.4.1
- https://github.com/meetecho/janus-gateway/releases/tag/v1.4.2

## Credit

- Reporter: w1n0y (GitHub w1n0y, Gitee wind903)

## Related public advisories and independent discovery

- CVE-2026-110717: path traversal through a Record and Play filename. Different plugin and different code path.
- CVE-2026-108830: race condition in the VideoRoom plugin.
- CVE-2026-108831: hard-coded credentials in the bundled admin demo page.
- GHSA-3r63-4x64-cq8f: AudioBridge record_file and record_dir are passed to fopen in write mode, bypassing protected_folders and truncating arbitrary files. That is an arbitrary file write issue, distinct from the directory creation step used here.

The fix for the issue described here shipped in 1.4.1 through pull request 3637. That pull request also credits another reporter for other issues addressed in the same change set. This report documents an independent discovery of the streaming ondemand path handling issue, verified against a build of 1.4.0 and against 1.4.1, and asks the CNA to assess whether the weakness is already covered or should be assigned separately.

The published advisory list for this repository was reviewed on 2026-10-19 and contains eight entries. None of them covers the streaming ondemand media path being opened without canonicalization, which is the weakness reported here.

## Verified full chain, unauthenticated and self staged

Two API requests are enough and no pre-existing directory is required.

Step 1, staging: send an audiobridge create with record enabled and record_dir set to a path whose last segment contains an accepted extension, for example /tmp/jpoc.mulaw. The plugin creates that directory from the caller supplied value and no authentication is required.

Step 2, read: send a streaming create of type ondemand with filename set to /tmp/jpoc.mulaw/../../etc/passwd. The extension check passes because the path contains mulaw and the traversal resolves to /etc/passwd, which the file source then opens.

Both steps were executed against the 1.4.0 build during verification and the server answered created for both. Because the attacker creates the staging directory themselves, no special condition is required, so the attack complexity is Low and the score is 7.5 rather than 6.5.

This section supersedes any earlier wording in this document that described the staging directory as pre-existing.

- CVSS 4.0, as submitted on the request form: 8.7 High, CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N
- CVSS 3.1 equivalent: 7.5 High, CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N

