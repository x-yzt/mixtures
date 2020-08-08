# Mixtures

Mixtures website source code.

## Technical docs

### About SASS

Mixtures uses SASS for generating its stylesheets. Each app has its own
`.scss` files in its `static` directory, accompagnated by generated and
minified `.min.css` files.

In order to customize the MaterializeCSS framework, custom SASS
variables (such as colors) are injected in the main library file. Those
variables lie in a `_variables-custom.scss` file near to the library.

From time to time, this customisation file is loaded from other SASS
files unrelated to the MaterializeCSS framework. As the SASS compiler
expects `_custom-variables.scss` to be in a *load path*, this can make
the compilation to fail if incorrectly used.

To prevent this, a ready to use script, `sass-compile.ps1`, passes
requiered arguments to the Dart SASS compiler. Using another way for
SASS compilation is therefore unrecommanded.
