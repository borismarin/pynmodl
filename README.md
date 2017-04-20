# nmodl

TODO: Write project description.

This is textX language project scaffolding for language `nmodl`.

textX grammar (a.k.a. meta-model in textX) can be found in
`nmodl/nmodl.tx`.

Meta-model loading, post-processing and registration can be found in
`nmodl/lang.py`

This language is registered in setuptools entry point `textx_lang` inside setup.py.
After installation it will be visible to the textx tool.

It is recommended to install this project in development mode during
development.

To do that run this from the project folder:

    $ pip install -e .

This command will list all registered languages.

    $ textx list-langs

To check the syntax of your grammar use:

    $ textx check nmodl/nmodl.tx

To visualize your grammar use:

    $ textx vis nmodl/nmodl.tx

This will produce `dot` file (see [GraphViz](http://graphviz.org/)).

Render model image either by using dot tool:

    $ dot -Tpng -O nmodl/nmodl.tx.dot

or by using some of available `dot` viewers (e.g.
[xdot](https://github.com/jrfonseca/xdot.py)):

    $ xdot nmodl/nmodl.tx.dot


Write model on your language and test its syntax with:

    $ textx check -l nmodl <path to your model>

Or visualize it with:

    $ textx vis -l nmodl <path to your model>


By all means, you should be using
[virtualenv](https://github.com/pypa/virtualenv).

