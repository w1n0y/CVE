# Evidence capture

## Environment

- Vulnerable build: compiled from the official source archive of tag v1.4.0 with clang 16, running with the sample configuration, api_secret left unset.
- Fixed build: distribution package 1.4.1, same configuration.
- The directory /tmp/x.alaw was created before the tests so that the traversal path satisfies the extension check.

## Requests

All requests were sent to the HTTP API: POST /janus with janus create, then janus attach to janus.plugin.streaming, then janus message with a create body containing the filename field.

## Files

- 1.4.0_traversal_accepted.json: vulnerable build accepted /tmp/x.alaw/../../etc/passwd and created the mountpoint.
- 1.4.1_traversal_rejected.json: fixed build rejected the same request.
- 1.4.0_plain_path_rejected.json: control case, plain /etc/passwd rejected by the extension check.

## Note

Mountpoint ids are generated per run and therefore differ between executions. Session and handle values are specific to each run.

- 1.4.0_chain_self_staged.json: the full two step chain on 1.4.0, audiobridge record_dir creates the staging directory and streaming ondemand then opens the traversal path, both answered created with no prior directory on disk.

- Reproduction captures from the live deployment (file content retrieved) belong in this folder; add them next to the local JSON captures.
