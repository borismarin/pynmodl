[![Build Status](https://travis-ci.org/borismarin/pynmodl.svg?branch=master)](https://travis-ci.org/borismarin/pynmodl)
# Parsing and compiling `nmodl` files ([ɴᴇᴜʀᴏɴ simulator](http://neuron.yale.edu/neuron/))

This project provides infrastructure for parsing and post-processing (e.g.
compiling) [`nmodl` files](https://www.neuron.yale.edu/neuron/static/docs/help/neuron/nmodl/nmodl.html),
using the [textX](https://github.com/igordejanovic/textx) language workbench (python).

Currently, there are two experimental backends: unparsing (a good starting point for
developing new targets) and [LEMS](https://github.com/LEMS/LEMS).

