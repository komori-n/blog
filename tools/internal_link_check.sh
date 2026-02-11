#!/bin/bash

HUGO_BIN="${HUGO_BIN:-hugo}"

"$HUGO_BIN" -D --baseURL http://localhost/

hyperlink public
