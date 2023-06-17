#!/bin/bash

hugo -D --ignoreCache --baseURL http://localhost/blog

rm -rf tmp
mkdir tmp
mv public tmp/blog

hyperlink tmp
