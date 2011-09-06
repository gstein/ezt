#!/usr/bin/python
#
# Copyright 2006 Google Inc. All Rights Reserved.

"""Unittest for ezt module"""

import sys
import unittest
import cStringIO

sys.path.insert(0, '..')
import ezt


class EztUnitTest(unittest.TestCase):
  def _runTemplate(self, template, data, fmt=ezt.FORMAT_RAW):
    t = ezt.Template()
    t.parse(template, base_format=fmt)
    o = cStringIO.StringIO()
    t.generate(o, data)
    return o.getvalue()

  def _runTemplateFile(self, path, data):
    t = ezt.Template('ezt_test_data/' + path)
    o = cStringIO.StringIO()
    t.generate(o, data)
    return o.getvalue()

  def testSimpleReplacement(self):
    d = self._runTemplate('this is a [X].', {'X': 'test'})
    self.assertEquals('this is a test.', d)

  def testLiteral(self):
    d = self._runTemplate('this is a ["trivial test"].', {})
    self.assertEquals('this is a trivial test.', d)

  def testAttributes(self):
    class _BlahBlah:
      def __init__(self, foo, bar):
        self.foo = foo
        self.bar = bar
    o = _BlahBlah('freedom', 'slavery')
    d = self._runTemplate('[X.foo] = [X.bar]', {'X': o})
    self.assertEquals('freedom = slavery', d)

  def testFor(self):
    o = [1, 4, 9, 16, 25]
    d = self._runTemplate('[for X][X] [end]', {'X': o})
    self.assertEquals('1 4 9 16 25 ', d)

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
    self.assertEquals('\n!O1\n!O2\nO3\nO4\n!O1O2\nO1O4\n', d)

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
    self.assertEquals(x, d)

  def testIsVarLiteral(self):
    t = '[is WAR "peace"]yes[else]no[end][is FREEDOM "slavery"]yes[else]no[end]'
    d = self._runTemplate(t, {'WAR': 'war', 'FREEDOM': 'slavery'})
    self.assertEquals('noyes', d)

  def testIsLiteralVar(self):
    t = '[is "peace" WAR]yes[else]no[end][is "slavery" FREEDOM]yes[else]no[end]'
    d = self._runTemplate(t, {'WAR': 'peace', 'FREEDOM': 'freedom'})
    self.assertEquals('yesno', d)

  def testIsVarVar(self):
    t = '[is PEACE WAR]yes[else]no[end][is SLAVERY FREEDOM]yes[else]no[end]'
    v = {
      'WAR': 'war',
      'FREEDOM': 'freedom',
      'PEACE': 'peace',
      'SLAVERY': 'slavery',
    }
    d = self._runTemplate(t, v)
    self.assertEquals('nono', d)

  def testIsLiteralLiteral(self):
    t = '[is "yes" "yes"]yes[else]no[end][is "no" "no"]maybe[else]sure![end]'
    d = self._runTemplate(t, {})
    self.assertEquals('yesmaybe', d)

  def testSubst(self):
    d = self._runTemplate('["%2%% of 10 does not %0 %1!" A B C]',
        {'A': 'equal', 'B': '12345', 'C': 56789})
    self.assertEquals('56789% of 10 does not equal 12345!', d)

  def testSubstVarFormat(self):
    d = self._runTemplate('[FMT A B C]',
        {'A': 'equal', 'B': '12345', 'C': 56789,
         'FMT': '%2%% of 10 does not %0 %1!'})
    self.assertEquals('56789% of 10 does not equal 12345!', d)

  def testFormatNotLiteral(self):
    d = self._runTemplate('[D A B C]',
        {'A': 'equal', 'B': '12345', 'C': 56789,
         'D': '%2%% of 10 still does not %0 %1!'})
    self.assertEquals('56789% of 10 still does not equal 12345!', d)

  def testInclude(self):
    d = self._runTemplateFile('include01.ezt',
                              {'MUCH': 'much', 'LITTLE': 'little'})
    self.assertEquals('not much here, but\nthis file contains little\n\n', d)

  def testIncludeNonLiteral(self):
    d = self._runTemplateFile('include03.ezt',
                              {'WHICH': 'include02.ezt', 'LITTLE': 'much'})
    self.assertEquals('ha ha ha this file contains much\n ha ha ha\n', d)

  def testInsert(self):
    d = self._runTemplateFile('insert01.ezt',
                              {'HERE': 'here'})
    self.assertEquals('food goes in [HERE]\n\n', d)

  def testInsertNonLiteral(self):
    d = self._runTemplateFile('insert03.ezt',
                              {'WHICH': 'insert02.ezt', 'HERE': 'here'})
    self.assertEquals('[HERE]\n is the place\n', d)

  def testDefineSimple(self):
    d = self._runTemplate('[define RED]blue[end]RED = [RED]', {})
    self.assertEquals('RED = blue', d)

  def testExceptionOnMissingVar(self):
    try:
      self._runTemplate('\n\n[GREEN]\n[RED]\n', {'GREEN': 'green'})
    except ezt.UnknownReference, e:
      self.assertEquals(e.line_number, 4)
    else:
      self.fail('ezt.UnknownReference not raised')

  def testReplacementEscapeHTML(self):
    d = self._runTemplate('test [X].', {'X': '<>\'\"&'}, ezt.FORMAT_HTML)
    self.assertEquals('test &lt;&gt;&#39;&quot;&amp;.', d)

  def testReplacementEscapeJS(self):
    d = self._runTemplate('test [X].', {'X': u'<>\'\"&\u2029'},
                          ezt.FORMAT_JS)
    self.assertEquals('test \\x3c\\x3e\\x27\\x22\\x26\\u2029.', d)

  def testReplacementEscapeURL(self):
    d = self._runTemplate('test [X].', {'X': u'<>\'\"&% \u2029'},
                          ezt.FORMAT_URL)
    self.assertEquals('test %3C%3E%27%22%26%25+%E2%80%A9.', d)

  def testFormat(self):
    d = self._runTemplate('[format "html"][X][end][format "js"][X][end]',
                          {'X': '<>\'\"&'})
    self.assertEquals(r'&lt;&gt;&#39;&quot;&amp;\x3c\x3e\x27\x22\x26', d)

  def testFormatNested(self):
    t = '[format "html,html"][X][end][format "html,js"][X][end]'
    d = self._runTemplate(t, {'X': '<>\'\"&'})
    htmlhtml_expected = r'&amp;lt;&amp;gt;&amp;#39;&amp;quot;&amp;amp;'
    htmljs_expected = r'\x26lt;\x26gt;\x26#39;\x26quot;\x26amp;'
    self.assertEquals(htmlhtml_expected + htmljs_expected, d)

  def testFormattedSubst(self):
    d = self._runTemplate('[format "html"]["%0" A][end]',
        {'A': '<b>hello</b>'})
    self.assertEquals('&lt;b&gt;hello&lt;/b&gt;', d)

  def testFormattedSubstVarFmt(self):
    d = self._runTemplate('[format "html"][FMT A][end]',
        {'A': '<b>hello</b>', 'FMT': '%0'})
    self.assertEquals('&lt;b&gt;hello&lt;/b&gt;', d)

  def testDoubleEndException(self):
    try:
      d = self._runTemplate('\n\n[if-any A]\n[A]\n[end]\n[end]\n', {'A': 'A'})
    except ezt.UnmatchedEndError, e:
      self.assertEquals(e.line_number, 6)
    else:
      self.fail('ezt.UnmatchedEndError not raised')

  def testForOnNonSequence(self):
    self.assertRaises(ezt.NeedSequenceError, self._runTemplate,
                      '\n\n[for A]\n[A]\n[end]\n', {'A': 'A'})


if __name__ == '__main__':
  unittest.main()
