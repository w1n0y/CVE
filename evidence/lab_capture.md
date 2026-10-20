# Lab capture, Janus 1.4.0 vs 1.4.1

All commands below were run on a local instance. No third party system was involved.

## Environment

- 1.4.0: built from the official source archive of tag v1.4.0, compiled with clang 16, sample configuration, api_secret left unset.
- 1.4.1: distribution package, same configuration.

## Step 1, create the staging directory through audiobridge

 python3 poc/janus_poc_generic.py http://127.0.0.1:8088/janus /etc/passwd --stage

Observed on 1.4.0: the audiobridge create request answers created and the directory whose name contains mulaw is created on disk.

## Step 2, open the traversal path through streaming

Observed on 1.4.0: the streaming create request with filename /tmp/jpoc.mulaw/../../etc/passwd answers streaming created with a mountpoint id, which shows the path was accepted and the file was opened.

Observed on 1.4.1: the same request answers error 456 with the message that relative paths cannot be used.

## Control case

A filename without an accepted audio extension, for example /etc/passwd, is rejected on both versions with error 456 unsupported format, which shows the extension check is the only filter in place.

## Raw responses

See the json files in this folder for the exact server responses.
