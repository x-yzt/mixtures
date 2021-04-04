# Mixtures

[![Maintainability](https://api.codeclimate.com/v1/badges/77793bc01946a6e772b9/maintainability)](https://codeclimate.com/github/x-yzt/mixtures/maintainability)

Mixtures website source code.

## Technical docs

### Application structure

Mixtures mainly use a central django app, `drugcombinator`, where all
templates, models and logic are encapsulated.

However, another small app, named `drugportals`, is kind of plugged into
it. This app contains all stuff related to thematic portals. It was
designed this way because:

1. Thematic portals are meant to be independant from a user pespective;
2. Hence, they use a separate frontend design;
3. And last but not least, we are not sure if they will survive
   after Mixtures goes out of beta.

Finally, some generic parts (like the about page or 404 templates) lie
in project-wide directories.

### Subdomains

The `drugportals` app uses a special subdomain routing. It uses a fork
of `django-hosts` that fixes bare subdomain routing -which is supposed
to be merged at some point- to serve portals pages.

This means **any relevant subdomain (eg. `portalname.exemple.com`)
should be routed to Django** for portals to work, either on a production
or development environment.

#### When using the dev server

One caveat of this approach is some inconsistencies in the behaviors of
a local dev server and a production environment, due to the `localhost`
domain not containing a `.` in it.

This is mainly because:

- The vast majority of web browsers does not allow setting a wildcard
  cookie domain to a hostname that does not contains a not, such as
  `.com` or -you guessed it- `.localhost`;
- Of how `django-hosts` parses URLs (however, with the forked version it
  should be consistent).

One easy solution to this is to serve the application on another host in
the dev environment, such as `local.host`, for exemple by editing the
hosts configuration file. Some `settings.py` entries will need updating
to reflect this.

### Views

This project uses a mix of function-based and class-based views.
Function-based views are prefered for simplicity, but CBVs better suit
certain scenarios (e.g. when inheritance is required).

#### CBVs

In addition to usual Django conventions, CBVs implement a `get_context`
method returning a `SimpleNamespace` object. This allows dot notation
to be used when setting up the context in the view code, and overriding
of the `get_context` method when inherited classes need to append
objects to view context. The `get`, `post` or `dispatch` methods are
then responsible to call `vars()` on the `SimpleNamespace` object to
pass an usual `dict` to the template renderer.

### Sitemaps

In addition to the `django.contrib.sitemaps` package, this project uses
a few tweaks:

- Static pages sitemaps use a custom child class which allows shorter
  definition;
- Sitemaps of objects that are served by a subdomain use a custom child
  class which support fully qualified domain names in reversed URLs;
- Each app has its own `sitemaps` module, which is responsible for
  defining a `SITEMAPS` dict containing the sitemaps such as
  `{'sitemap_name': sitemap_object}`;
- A `get_apps_sitemaps` function is used in order to collect those
  sitemaps and prefix them.

Relevant source code lives in the `utils/sitemaps` directory.

### About SASS

Mixtures uses SASS for generating its stylesheets. Each app has its own
`.scss` files in its `static` directory, accompagnated by generated and
minified `.min.css` files.

In order to customize the MaterializeCSS framework, custom SASS
variables (such as colors) are injected in the main library file. Those
variables lie in a `_variables-custom.scss` file near to the library.

From time to time, SASS files that lie in a given app are loaded from
others SASS files which belong to another app. As the SASS compiler
expects those files to be in a *load path*, this can make the
compilation to fail.

To prevent this, a ready to use script, `sass-compile.ps1`, passes
requiered arguments to the Dart SASS compiler. Using another way for
SASS compilation is therefore unrecommanded.
