#!/bin/sh

case "$1" in
  docs)  rsync -rv --temp-dir=/tmp --delete --size-only \
  --exclude=docs/_build/html/.buildinfo \
docs/_build/html/ \
  unti@draco.uberspace.de:/home/unti/virtual/dev.unterwaditzer.net/python-webuntis/ ;;
  
  lib) rsync -rv --temp-dir=/tmp --delete --size-only \
      --exclude=__pycache__ \
      --exclude=*.pyc \
      --exclude=.git/ \
      ./ \
      unti@draco.uberspace.de:/home/unti/builddir/webuntis ;;

  *) exit 1

esac
