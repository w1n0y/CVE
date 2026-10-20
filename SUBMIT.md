# Submission sheet, copy and paste into the CVE request form

Request type: Report Vulnerability / Request CVE ID

- Vendor or project: Meetecho
- Product name: Janus WebRTC Server
- Platforms: Linux
- Source repository: https://github.com/meetecho/janus-gateway
- Source-code file: src/plugins/janus_streaming.c
- Modules, components or features: streaming plugin, ondemand media path handling
- Purl: pkg:github/meetecho/janus-gateway

Versions

- Affected: start 1.2.3, up to and including 1.4.0
- Status change: fixed in 1.4.1 for streaming, fixed in 1.4.2 for audiobridge
- versionType: semver

Problem type: CWE-22 and CWE-306

Vulnerability description

Janus WebRTC Server accepts a caller supplied media path when an ondemand stream is created. The path is validated only by checking whether it contains one of the audio extensions, and is then passed to the file source, which opens it. No canonicalization is performed and no directory allowlist is enforced, so an unauthenticated caller can make the server open an arbitrary local file and use it as a media source, with content delivered to viewers as RTP audio. No credentials and no user interaction are required because api_secret and auth_token default to unset. Fixed in 1.4.1 for the streaming path handling and in 1.4.2 for the audiobridge directory creation.

References

- https://github.com/meetecho/janus-gateway/pull/3637
- https://github.com/meetecho/janus-gateway/pull/3676
- https://github.com/meetecho/janus-gateway/releases/tag/v1.4.1
- https://github.com/meetecho/janus-gateway/releases/tag/v1.4.2

Metrics

- CVSS 3.1: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N, 7.5 High

Optional fields

- Required configuration for exposure: streaming plugin loaded, api_secret and auth_token unset, and a directory whose name contains alaw, mulaw or opus available or creatable through audiobridge
- Workaround: set api_secret and auth_token, avoid loading the streaming and audiobridge plugins
- Solution: upgrade to 1.4.2 or later, at minimum 1.4.1
- Credits: TO BE FILLED
- Source of vulnerability discovery: external
- Taxonomy mappings: CWE-22, CWE-306

Note for the CNA

The fix for this weakness shipped in 1.4.1 through pull request 3637, which also credits another reporter for other issues in the same change set. This report is an independent discovery, verified against a build of 1.4.0 and against 1.4.1, and asks the CNA to assess whether it is already covered or should be assigned separately.
