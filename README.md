# About

EaZy Templating (EZT) is a fast and simple templating system for
Python-based software.

EZT focuses on data substitution, rather than placing a Turing-complete
language into template files. The templates are fast to parse, and fast
to render. EZT supports a parse-once and render-many approach if
thousands of renderings are necessary. In most cases, the parse/render
sequence will be fast enough for the application.

(also see: https://github.com/gstein/ezt/blob/wiki/ProjectHome.md;
TBD to fold that into this file)


# Documentation

See: https://github.com/gstein/ezt/blob/wiki/Syntax.md


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
