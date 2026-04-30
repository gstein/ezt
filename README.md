# About

EaZy Templating (EZT) is a fast and simple templating system for
Python-based software.

EZT focuses on data substitution, rather than placing a Turing-complete
language into template files. The templates are fast to parse, and fast
to render. EZT supports a parse-once and render-many approach if
thousands of renderings are necessary. In most cases, the parse/render
sequence will be fast enough for the application.

EZT is used by [Apache Subversion](http://subversion.apache.org/), the
[Apache Software Foundation](http://www.apache.org/), and many other
projects and companies.


# Installation

EZT is available on [PyPI](https://pypi.org/project/ezt/1.1/).

Since EZT is very stable, mature and consists of a single file, grabbing
a copy from [source control](https://github.com/gstein/ezt) is a great
alternative (especially for embedding into your application). Since it is
a single module, this approach works very well for many people.


# Documentation

See [SYNTAX.md](SYNTAX.md) for information about how to use EZT, and the
template syntax.

For a deep technical explanation of how the EZT engine works internally,
see [ARCHITECTURE.md](ARCHITECTURE.md).


# Community

Come visit the [discussion group](http://groups.google.com/group/ezt-discuss)!

## Other Users

EZT is used by [Apache Subversion](http://subversion.apache.org/), the
[Apache Software Foundation](http://www.apache.org/), [Google Code](http://code.google.com/),
[ViewVC](http://www.viewvc.org/), [edna](http://edna.sourceforge.net/),
[SubWiki](http://subwiki.tigris.org/), and many other projects and companies.


# Related Projects

If you use the TextMate editor, then you may be interested in
[this bundle](http://code.google.com/p/ezt-tm/) to improve your template
editing experience.

Looking to parse EZT templates in Java? Look at the
[hapax](http://code.google.com/p/hapax/) parser.


# Development Status

EZT is mature and stable. Current development considerations:

- Update the header and contact info
- Note the official location (now on GitHub)
- Move documentation from docstrings to markdown files

## ViewVC Integration

In the [ViewVC](http://www.viewvc.org/) repository, there are a number of
local changes:
- Allow iterables instead of (just) sequences
- Integrating the callback stuff is tricky because it goes against EZT's ideals
  - The `[CALLBACK ARG1 ARG2]` form is a generic function-callback mechanism
- A number of [patches](http://viewvc.tigris.org/issues/buglist.cgi?component=viewvc&issue_status=UNCONFIRMED&issue_status=NEW&issue_status=STARTED&issue_status=REOPENED&subcomponent=ezt)
  living in the ViewVC issue tracker

## Larger Questions

Visitors: please feel free to provide your thoughts in the
[discussion group](http://groups.google.com/group/ezt-discuss)!

- Start a release process?
- Start a community? (e.g. add a Google group?)


# History

EZT was started as part of the [edna project](http://edna.sf.net/) in
early 2001. However, it was also intended towards use within the
[ViewVC project](http://viewvc.org/). The bulk of EZT development
occured as part of ViewVC during 2001 and 2002.

In 2003, EZT started to get used in additional places: SubWiki,
Subversion's build system, and some infrastructure pieces at the ASF.
Greg also had a little private project which used and further modified
EZT.

The EZT project was started in October 2003 to pull together all of
the various incarnations and derivative developments of EZT into a
single, canonical location. This project was moved to Google Code in
June 2008.

On August 22, 2015, EZT was exported from Google Code (due to its
imminent move to read-only / archival status), and landed
on GitHub: https://github.com/gstein/ezt, where development
continues (glacially, given EZT's mature status).


# License

BSD 2-clause. See ezt.py
