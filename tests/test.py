#!/usr/bin/env python

import sys

sys.path.insert(0, '..')
import ezt

class _item:
  pass

t = ezt.Template('test.ezt')

nonseq = _item()
nonseq.attr = 'nonseq.attr'

seqitem = _item()
seqitem.attr = 'seqitem.attr'
nonseq.seq = [ seqitem, seqitem ]

data = {
  'nonseq' : nonseq,
  'sensitive' : '<cool & stuff>',
  }

t.generate(sys.stdout, data)
