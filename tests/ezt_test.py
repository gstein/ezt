#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2006 Google Inc. All Rights Reserved.

"""Unittest for ezt module"""

import sys
import unittest
try:
  from StringIO import StringIO
  PY3 = False
except:
  from io import StringIO
  PY3 = True

sys.path.insert(0, '..')
import ezt


class EztUnitTest(unittest.TestCase):
  def _runTemplate(self, template, data, fmt=ezt.FORMAT_RAW):
    # parse() takes a str, not bytes. assume utf-8.
    if PY3 and isinstance(template, bytes):
      template = template.decode('utf-8')
    t = ezt.Template()
    t.parse(template, base_format=fmt)
    o = StringIO()
    t.generate(o, data)
    return o.getvalue()

  def _runTemplateFile(self, path, data):
    t = ezt.Template('ezt_test_data/' + path)
    o = StringIO()
    t.generate(o, data)
    return o.getvalue()

  def testSimpleReplacement(self):
    d = self._runTemplate('this is a [X].', {'X': 'test'})
    self.assertEqual('this is a test.', d)

  @unittest.skipIf(sys.version_info[0] >= 3, 'Does not work on Python3')
  def testSimpleReplacementUtf8Encoded(self):
    ### fails because _runTemplate changes the bytes back to
    ### a unicode string so that _parse() can .split() it.

    # If all inputs are byte strings encoded with an encoding that is a superset
    # of ASCII (e.g. UTF-8), the output will be a byte string with the same
    # encoding. This mode of operation may not be supported in future ezt
    # versions running on Python 3.
    t = u'◄ [X] ►'.encode('utf-8')
    d = self._runTemplate(t, {'X': u'♥'.encode('utf-8')})
    self.assertEqual(u'◄ ♥ ►'.encode('utf-8'), d)

  def testSimpleReplacementUnicode(self):
    d = self._runTemplate(u'◄ [X] ►', {'X': u'♥'})
    self.assertEqual(u'◄ ♥ ►', d)

  def testSimpleReplacementStrTemplateAndUnicodeVariable(self):
    # Mixing str and unicode objects is allowed as long as the str objects only
    # contain ASCII characters (i.e. ord(c) < 128). When ezt is converted to
    # Python 3 this test will become redundant and can be deleted (it will be
    # equivalent to testSimpleReplacementUnicode).
    d = self._runTemplate('I [verb] Python', {'verb': u'♥'})
    self.assertEqual(u'I ♥ Python', d)

  def testSimpleReplacementUnicodeTemplateAndStrVariable(self):
    # Just like testSimpleReplacementStrTemplateAndUnicodeVariable above, this
    # test can be safely deleted after the switch to Python 3.
    d = self._runTemplate(u'I ♥ [language]', {'language': 'Python'})
    self.assertEqual(u'I ♥ Python', d)

  def testLiteral(self):
    d = self._runTemplate('this is a ["trivial test"].', {})
    self.assertEqual('this is a trivial test.', d)

  @unittest.skipIf(sys.version_info[0] >= 3, 'Does not work on Python3')
  def testLiteralUtf8Encoded(self):
    ### fails because _runTemplate changes the bytes back to
    ### a unicode string so that _parse() can .split() it.
    d = self._runTemplate(u'◄ ["♥"] ►'.encode('utf-8'), {})
    self.assertEqual(u'◄ ♥ ►'.encode('utf-8'), d)

  def testLiteralUnicode(self):
    d = self._runTemplate(u'◄ ["♥"] ►', {})
    self.assertEqual(u'◄ ♥ ►', d)

  def testAttributes(self):
    class _BlahBlah:
      def __init__(self, foo, bar):
        self.foo = foo
        self.bar = bar
    o = _BlahBlah('freedom', 'slavery')
    d = self._runTemplate('[X.foo] = [X.bar]', {'X': o})
    self.assertEqual('freedom = slavery', d)

  def testFor(self):
    o = [1, 4, 9, 16, 25]
    d = self._runTemplate('[for X][X] [end]', {'X': o})
    self.assertEqual('1 4 9 16 25 ', d)

  def testIsAny(self):
    t = """
[if-any O1]O1[else]!O1[end]
[if-any O2]O2[else]!O2[end]
[if-any O3]O3[else]!O3[end]
[if-any O4]O4[else]!O4[end]
[if-any O1 O2]O1O2[else]!O1O2[end]
[if-any O1 O4]O1O4[else]!O1O4[end]
"""
    d = self._runTemplate(t, {'O1': [], 'O2': None, 'O3': 0, 'O4': 'hi'})
    self.assertEqual('\n!O1\n!O2\nO3\nO4\n!O1O2\nO1O4\n', d)

  def testIfIndex(self):
    o = [1, 4, 9, 16, 25]
    t = """
[for X][X] [if-index X first]FIRST [else]!FIRST [end][if-index X last]LAST [else]!LAST [end][if-index X odd]ODD [else]!ODD [end][if-index X even]EVEN [else]!EVEN [end][if-index X 3]THREE[else]!THREE[end]
[end]"""
    x = """
1 FIRST !LAST !ODD EVEN !THREE
4 !FIRST !LAST ODD !EVEN !THREE
9 !FIRST !LAST !ODD EVEN !THREE
16 !FIRST !LAST ODD !EVEN THREE
25 !FIRST LAST !ODD EVEN !THREE
"""
    d = self._runTemplate(t, {'X': o})
    self.assertEqual(x, d)

  def testIsVarLiteral(self):
    t = '[is WAR "peace"]yes[else]no[end][is FREEDOM "slavery"]yes[else]no[end]'
    d = self._runTemplate(t, {'WAR': 'war', 'FREEDOM': 'slavery'})
    self.assertEqual('noyes', d)

  def testIsLiteralVar(self):
    t = '[is "peace" WAR]yes[else]no[end][is "slavery" FREEDOM]yes[else]no[end]'
    d = self._runTemplate(t, {'WAR': 'peace', 'FREEDOM': 'freedom'})
    self.assertEqual('yesno', d)

  def testIsVarVar(self):
    t = '[is PEACE WAR]yes[else]no[end][is SLAVERY FREEDOM]yes[else]no[end]'
    v = {
      'WAR': 'war',
      'FREEDOM': 'freedom',
      'PEACE': 'peace',
      'SLAVERY': 'slavery',
    }
    d = self._runTemplate(t, v)
    self.assertEqual('nono', d)

  def testIsLiteralLiteral(self):
    t = '[is "yes" "yes"]yes[else]no[end][is "no" "no"]maybe[else]sure![end]'
    d = self._runTemplate(t, {})
    self.assertEqual('yesmaybe', d)

  def testSubst(self):
    d = self._runTemplate('["%2%% of 10 does not %0 %1!" A B C]',
        {'A': 'equal', 'B': '12345', 'C': 56789})
    self.assertEqual('56789% of 10 does not equal 12345!', d)

  def testSubstVarFormat(self):
    d = self._runTemplate('[FMT A B C]',
        {'A': 'equal', 'B': '12345', 'C': 56789,
         'FMT': '%2%% of 10 does not %0 %1!'})
    self.assertEqual('56789% of 10 does not equal 12345!', d)

  def testFormatNotLiteral(self):
    d = self._runTemplate('[D A B C]',
        {'A': 'equal', 'B': '12345', 'C': 56789,
         'D': '%2%% of 10 still does not %0 %1!'})
    self.assertEqual('56789% of 10 still does not equal 12345!', d)

  def testInclude(self):
    d = self._runTemplateFile('include01.ezt',
                              {'MUCH': 'much', 'LITTLE': 'little'})
    self.assertEqual('not much here, but\nthis file contains little\n\n', d)

  def testIncludeNonLiteral(self):
    d = self._runTemplateFile('include03.ezt',
                              {'WHICH': 'include02.ezt', 'LITTLE': 'much'})
    self.assertEqual('ha ha ha this file contains much\n ha ha ha\n', d)

  def testInsert(self):
    d = self._runTemplateFile('insert01.ezt',
                              {'HERE': 'here'})
    self.assertEqual('food goes in [HERE]\n\n', d)

  def testInsertNonLiteral(self):
    d = self._runTemplateFile('insert03.ezt',
                              {'WHICH': 'insert02.ezt', 'HERE': 'here'})
    self.assertEqual('[HERE]\n is the place\n', d)

  def testDefineSimple(self):
    d = self._runTemplate('[define RED]blue[end]RED = [RED]', {})
    self.assertEqual('RED = blue', d)

  def testDefineUnicode(self):
    d = self._runTemplate(u'[define HEART]♥[end]HEART = [HEART]', {})
    self.assertEqual(u'HEART = ♥', d)

  def testExceptionOnMissingVar(self):
    try:
      self._runTemplate('\n\n[GREEN]\n[RED]\n', {'GREEN': 'green'})
    except ezt.UnknownReference as e:
      self.assertEqual(e.line_number, 4)
    else:
      self.fail('ezt.UnknownReference not raised')

  def testReplacementEscapeHTML(self):
    d = self._runTemplate('test [X].', {'X': '<>\'\"&'}, ezt.FORMAT_HTML)
    self.assertEqual('test &lt;&gt;&#39;&quot;&amp;.', d)

  def testReplacementEscapeJS(self):
    d = self._runTemplate('test [X].', {'X': u'<>\'\"&\u2029'},
                          ezt.FORMAT_JS)
    self.assertEqual('test \\x3c\\x3e\\x27\\x22\\x26\\u2029.', d)

  def testReplacementEscapeURL(self):
    d = self._runTemplate('test [X].', {'X': u'<>\'\"&% \u2029'},
                          ezt.FORMAT_URL)
    self.assertEqual('test %3C%3E%27%22%26%25+%E2%80%A9.', d)

  def testFormat(self):
    d = self._runTemplate('[format "html"][X][end][format "js"][X][end]',
                          {'X': '<>\'\"&'})
    self.assertEqual(r'&lt;&gt;&#39;&quot;&amp;\x3c\x3e\x27\x22\x26', d)

  def testFormatNested(self):
    t = '[format "html,html"][X][end][format "html,js"][X][end]'
    d = self._runTemplate(t, {'X': '<>\'\"&'})
    htmlhtml_expected = r'&amp;lt;&amp;gt;&amp;#39;&amp;quot;&amp;amp;'
    htmljs_expected = r'\x26lt;\x26gt;\x26#39;\x26quot;\x26amp;'
    self.assertEqual(htmlhtml_expected + htmljs_expected, d)

  def testFormattedSubst(self):
    d = self._runTemplate('[format "html"]["%0" A][end]',
        {'A': '<b>hello</b>'})
    self.assertEqual('&lt;b&gt;hello&lt;/b&gt;', d)

  def testFormattedSubstUnicode(self):
    d = self._runTemplate(u'◄[format "html"]["%0" A][end]►',
        {'A': u'<b>♥</b>'})
    self.assertEqual(u'◄&lt;b&gt;♥&lt;/b&gt;►', d)

  def testFormattedSubstVarFmt(self):
    d = self._runTemplate('[format "html"][FMT A][end]',
        {'A': '<b>hello</b>', 'FMT': '%0'})
    self.assertEqual('&lt;b&gt;hello&lt;/b&gt;', d)

  def testDoubleEndException(self):
    try:
      d = self._runTemplate('\n\n[if-any A]\n[A]\n[end]\n[end]\n', {'A': 'A'})
    except ezt.UnmatchedEndError as e:
      self.assertEqual(e.line_number, 6)
    else:
      self.fail('ezt.UnmatchedEndError not raised')

  def testForOnNonSequence(self):
    self.assertRaises(ezt.NeedSequenceError, self._runTemplate,
                      '\n\n[for A]\n[A]\n[end]\n', {'A': 'A'})


if __name__ == '__main__':
  unittest.main()
