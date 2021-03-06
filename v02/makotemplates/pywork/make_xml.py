# coding=utf-8
""" make_xml.py
 Reads/Writes utf-8
"""
from __future__ import print_function
import xml.etree.ElementTree as ET
import sys, re,codecs
from hwparse import init_hwrecs,HW
xmlroot = HW.dictcode  

%if dictlo in ['skd','vcp']:
def adjust_slp1(x):
 # in skd, all text is Devanagari.  But, the text is skd.txt does not use
%endif
%if dictlo not in ['skd','vcp','sch','md','shs','wil','ap90','bur','acc','yat']:
def unused_adjust_slp1(x):
 # in vcp, all text is Devanagari.  But, the text is vcp.txt does not use
%endif
%if dictlo not in ['sch','md','shs','wil','ap90','bur','acc','yat']: 
 #  the {#..#} markup to denote Devanagari.
 # We want to add <s>..</s> markup.
 # This requires that we separate out other markup  (always in form
 # <...>)
 outarr = []
 import string
 regex = r'(<[^>]+>)|(\[Page.*?\])|([^%s])' %string.printable
 parts = re.split(regex,x) 
 for part in parts: 
  if not part: #why needed? 
   pass 
  elif part.startswith('<') and part.endswith('>'):
   outarr.append(part)
  elif part.startswith('[Page') and part.endswith(']'):
   outarr.append(part)
 # elif part.startswith('&') and part.endswith(';'):
  elif part[0] not in string.printable:
   outarr.append(part)
  else: # assume text slp1
   # put it into <s></s>
   y = part
   outarr.append("<s>%s</s>" % y)
 ans = ''.join(outarr)
 return ans

%endif
%if dictlo == 'krm':
def close_divs_krm(newline):
 newline = newline.replace('</Poem> </div>','</div></Poem>')
 newline = newline.replace(u'<Poem><s>“grAsasya karmakartftve nizWAnatvaM Bavet ziYaH .</s> </div>',u'</div> <Poem><s>“grAsasya karmakartftve nizWAnatvaM Bavet ziYaH .</s>')
 newline = newline.replace(u'</Poem> <s>iti prakriyAsarvasvam .</s> </div>',
  u'</div></Poem> <s>iti prakriyAsarvasvam .</s> ')
 return newline

%endif
%if dictlo not in ['ap','skd','sch','md','shs','cae','wil','ap90','bur','acc','yat']:  # These have their own code
def dig_to_xml_specific(x):
%if dictlo in ['pw','pwg','bhs','gra','ae','gst','ieg','mwe','pgn','pui','vei','mw72','snp','bor','mw','inm','bop']:
 """ no changes particular to digitization"""
 return x
%else:
 """ changes particular to digitization"""
%endif
%if dictlo == 'pd':
 x = re.sub(r' < ',' &lt; ',x)  # 6 cases
 return x
%endif
%if dictlo == 'krm':
 x = x.replace('</F>','')
 x = x.replace('<F>','<div n="F">');
 return x
%endif
%if dictlo not in ['vcp']:
 # There are a couple entries with an <H> element.
 # Just remove these lines
 if x.startswith('<H>'):
  print("REMOVING <H> LINE",x.encode('utf-8'))
  return ''
%endif
%if dictlo in ['vcp']:
 x = re.sub(r'<>','<lb/>',x) # <lb/>
 x = re.sub(r'<HI>','<div n="HI">',x) # 3362 cases
%endif
%if dictlo in ['bhs','gra','krm']:
 #x = re.sub(r'<P>','<div n="P">',x) # 2322 cases
%else:
 x = re.sub(r'<P>','<div n="P">',x) # 2322 cases
%endif
%if dictlo not in ['vcp']:
 #if '<g></g>' in x: # once only. Already converted in stc.txt
 # x = x.replace('<g></g>','<lang n="greek"></lang>')
 #x = re.sub(r'<Picture>','<div n="Picture">',x) # 71 cases
%endif
%if dictlo in ['vcp']:
 if re.search(r'^<H>',x):
  x = re.sub(r'<H>','<div n="H">',x)  # 18 cases
  print("Unexpected <H>:",x.encode('utf-8'))
 x = re.sub(r'<Picture>','<div n="Picture">',x) # 71 cases
%endif
 # markup like <C1>x1<C2>x2...  indicates tabular data in vcp.
%if dictlo not in ['vcp']:
 #x = re.sub(r'<C([0-9]+)>',r'<C n="\1"/>',x)
%else:
 x = re.sub(r'<C([0-9]+)>',r'<C n="\1"/>',x)
%endif
 # change '--' to mdash
%if dictlo in ['bhs','gra','ae','krm']:
 #x = x.replace('--',u'—')  #597 cases
%else:
 x = x.replace('--',u'—')  #597 cases
%endif
%if dictlo not in ['vcp']:
 #{^X^}  superscript
 x = re.sub(r'{\^(.*?)\^}',r'<sup>\1</sup>',x)
%endif
%if dictlo in ['vcp']:
 x = adjust_slp1(x) # add <s> markup to text
%endif
 return x
%endif # dictionaries other than ap,skd
%if dictlo == 'ap':
def dig_to_xml_specific(x):
 """ changes particular to digitization"""
 # There is one instance of a 'Poem' tag, under hw=akzOhiRI
 #  <Poem>...
 #  ...
 #   ... </Poem>
 # change this to <div n="Poem">...</div>
 if re.search('Poem>',x):
  x = x.replace('<Poem>','<div n="Poem">')
  # Because of the the 'close_div' logic, we just remove </Poem>.
  # The close-div logic will add the </div>
  #x = x.replace('</Poem>','</div>')
  x = x.replace('</Poem>','')
  return x
 # in AP, ‡ is used in Devanagari text to indicate a line-break hyphen
 # This is different from the usage of this symbol in AP90.
 # Replace with '-'
 x = re.sub(u'‡','-',x) 
 # in ap.txt, the Currency symbol € is markup indicating a root. It has no
 # correspondent in the printed text. About 3000+ instances.
 # For now, replace it with an empty '<root/>' element, and do not display
 # it in 'disp.php'
 x = x.replace(u'€','<root/>')
 # Divisions are indicated by lines starting with a period.
 # Three types are seen:
 # .{#-BaH#}   
 # .²1 Absence  ...
 # .³({%a%})    
 if re.search(u'^[.][²]',x):
 # there may be nothing else on the line (300+ cases), in particular no space
 # do same thing anyway, not requiring the trailing space.
  x = re.sub(u'[.][²]([^ ]*) ',r'<div n="2" name="\1">\1 ',x)
  x = re.sub(u'[.][²]([^ ]*)',r'<div n="2" name="\1">\1 ',x)
 elif re.search(u'^[.][³]',x):
  m = re.search('[.][³]([^ ]*) ',x)
  if not m:
   m = re.search('[.][³]([^ ]*)',x)
  assert m ,"adjust_xml. PROBLEM 1:x=\n%s"%x.encode('utf-8')
  data = m.group(1)
  # data = ({%x%})
  m = re.search(r'\(<i>(.)</i>\)',data)
  assert m ,"adjust_xml. PROBLEM 2:x=\n%s"%x.encode('utf-8')
  name=m.group(1)
  x = re.sub(u'[.][³]([^ ]*) ',r'<div n="3" name="%s">\1 '%name,x)
  x = re.sub(u'[.][³]([^ ]*)',r'<div n="3" name="%s">\1 '%name,x)

 # introduce line-break (call it a plain div) at any line starting with
 # a period.  This was the convention used by Thomas to designate
 # divisions. This is the /{#-BaH#} type case
 if x.startswith('.'):
  #print("extra div:",x.encode('utf-8'))
  x = re.sub(r'^[.]','<div n="Q">',x)
 return x
%endif # ap dictionary
%if dictlo == 'skd':
def dig_to_xml_specific(x):
 """ changes particular to skd digitization
  Use empty <mark n="..."/> tags instead of divs for H and P
  EXCEPT for "F" (footnote), which is coded as a div
  and <C n="..."/>
 """
 x = re.sub(r'<>','<lb/>',x) # <lb/>
 # <P> seems to indicate that the line is indented. 
 x = re.sub(r'<P>','<mark n="P"/>',x) # 
 x = re.sub(r'<Picture>','<mark n="Picture"/>',x)  
 if re.search(r'^<H>',x):
  # There are many case. 
  # In the preparation of meta-line version, some (noticeably letter-breaks)
  # have been put OUTSIDE of the <L>...<LEND> scope which we are parsing
  # here.  The other <H> indicate intermediate titles. But it seems safer
  # to view them now as EMPTY tags, rather than divs. That is the 
  # purpose of the <mark n="..."/> tag.
  x = re.sub(r'<H>','<mark n="H"/>',x)  

  #print("Unexpected <H>:",x.encode('utf-8'))
 # text has <F>...</F> five cases
 # This is the only 'div' markup used.
 # We close the div HERE, and do NOT call close_divs function
 x = re.sub(r'<F>','<div n="F">',x) # 5 cases in skd: Footnote
 x = re.sub(r'</F>','</div>',x) 
 # markup like <C1>x1<C2>x2...  indicates tabular data in skd.
 x = re.sub(r'<C([0-9]+)>',r'<C n="\1"/>',x)
 # change '--' to mdash
 x = x.replace('--',u'—')  # many cases
 x = adjust_slp1(x) # add <s> markup to text
 return x
%endif
%if dictlo == 'sch':
def dig_to_xml_specific(x):
 """ changes particular to sch digitization"""
 # 04-24-2017.  Several changes
 # {!x!}  a pw homonym number
 x = re.sub(r'{!(.%?)!}',r'<hom n="pwk">\1</hom>',x)
 # {part=,seq=6766,type=,n=5}
 m = re.search(r'{part=(.*?),seq=(.*?),type=(.*?),n=(.*?)}',x)
 if m:
  temp = m.group(0)
  part = m.group(1)
  seq = m.group(2)
  t = m.group(3) # type
  n = m.group(4)
  if t != '':
   telt = '<type>%s</type>'% t
  else:
   telt = ''
  attribs=[]
  attribs.append('seq="%s"'%seq)
  attribs.append('n="%s"' %n)
  if part != '':
   attribs.append('part="%s"' % part)
  attribstr = ' '.join(attribs)
  infoelt = '<info %s/>' %attribstr
  new = '%s%s' %(telt,infoelt)
  #new = '<info part="%s" seq="%s" n="%s"/><type>%s</type>'%(part,seq,n,t)
  x = x.replace(temp,new)
 # introduce '<div>' before each EM DASH
 x = x.replace(u'—',u'<div>—')
 return x
%endif
%if dictlo == 'md':
def dig_to_xml_specific(x):
 """ changes particular to digitization"""
 # we maintain line breaks and don't put in divs.
 #  the pattern <b>-   is a promising pattern for a div 
 #  but there are two many variations for which this does not
 #  render properly. Thus we postpone this enhancement for now.
 # and retain line-breaks.
 divflag = False
 # for experimenting.  When divflag is True, remove '<>' and introduce <div>
 if divflag:
  x =  re.sub(r'<>','',x)  # main
 else:
  x =  re.sub(r'<>','<lb/>',x)  # main
 # change -- to mdash
 x = re.sub(r'--',u'—',x)
 # change ‡ to _  (two vowels that will be combined via sandhi)
 x = re.sub(u'‡','_',x)
 # remove the ¤ symbol. It brackets some numbers (e.g. ¤2¤) but there
 # is no obvious typographical feature.
 x = re.sub(u'¤','',x)
 # change <g>X</g> to <lang n="greek">x</lang>
 x = re.sub(r'<g>(.*?)</g>',r'<lang n="greek">\1</lang>',x)
 if divflag:
  # add divs for <b>-
  x = re.sub(r'<b>-','<div n="1" ><b>-',x)
 """
 # add divs for other bold
 x = re.sub(r'<b>([^-])',r'<div n="2" ><b>\1',x)
 """
 return x
%endif
%if dictlo == 'shs':
def dig_to_xml_specific(x):
 """ changes particular to digitization"""
 x = re.sub('<>','<lb/>',x)
 x = re.sub(r' E[.]','<div n="E"> E.',x)
 x = re.sub(r' ([mfn]+[.] *\(<s>.*?</s>\))',r' <div n="1">\1',x)
 x = re.sub(r' ([mfn]+[.] *)$',r' <div n="1">\1',x)
 x = re.sub(r' ([0-9]+[.])',r' <div n="2"> \1',x)
 x = re.sub(r'<Poem>','<div n="Poem">',x)
 x = re.sub(r'</Poem>','',x)  # the 'Poem' div will be closed in closed_divs
 # divs for roots
 x = re.sub(r' (r[.] [1-9])',r'<div n="1">\1',x)
 x = re.sub(r' ([wW]ith *<s>.*?</s>)',r'<div n="1">\1',x)
 return x
%endif
%if dictlo == 'cae':
def dig_to_xml_specific(x):
 """ no changes particular to digitization"""
 return x
%endif 
%if dictlo == 'wil':
def dig_to_xml_specific(x):
 """ changes particular to digitization"""
 if x.startswith('<H>'):
  # Start of section beginning with a particular letter. Drop this line
  x = ''
 elif re.search(u'^[.]²[0-9]+',x):
  # a division coded by Thomas
  # drop the initial '.²'
  # and start <div n="1">
  x = '<div n="1">' + x[2:]
 elif re.search(r'^[.]E[.]',x):
  # an Etymology division 
  # drop the initial '.'
  # and start <div n="E">
  x = '<div n="E">' + x[1:]
 elif re.search(r'^[.]',x):
  # unknown division
  print("UNKNOWN DIVISION: ",x.encode('utf-8'))
  x =  " " + x
 else:
  # assume a simple continuation line
  x = " " + x
 # In a currently small number of cases (as with root 'RI'), sub-meanings
 # are coded with superscript letters, as '^a'. We'll code these as
 # <div n="2">
 x = re.sub(r'[\^]','<div n="2">',x)
 return x
%endif 
%if dictlo == 'ap90':
def dig_to_xml_specific(x):
 """ changes particular to ap90 digitization"""
 # introduce '<div>' before each EM DASH
 #x = x.replace(u'—',u'<div>—')
 x = x.replace('<>','<lb/>')
 x = x.replace('<P>','<P/>')
 if '<H>' in x:  # this has been removed (20170701)
  print("Skipping",x.encode('utf-8'))
  x = ''
 x = x.replace('<NI>','<P/>') # under kAlidAsa in Appendix II
 return x
%endif
%if dictlo == 'bur':
def dig_to_xml_specific(x):
 """ changes particular to digitization"""
 if re.search(r'^<P>',x):
  x = re.sub(r'<P>','<div n="P">',x)
 elif re.search(r'^<H>',x):
  x = re.sub(r'<H>','<H/>',x)
  print("Unexpected <H>:",x.encode('utf-8'))
 # -- div takes precedence over || div
 # change '||' to a div, type = 3
 #  do NOT Retain the '||' , an aesthetic choice
 x = x.replace('||','<div n="3">')
 # We want most mdashes to start a div. but not all.
 # Restricting to the desired group is tricky. Here is a try.
 x = re.sub(u'(-- *[A-Z])',r'<div n="2">\1',x)
 x = re.sub(u'(-- *<ab>[SMFN][.])',r'<div n="2">\1',x)
 # additional abbreviations before ANY abbreviation (only about 100 cases left)
 x = re.sub(u'(-- *<ab>)',r'<div n="2">\1',x)
 # {%X%} has already been changed to <i>X</i>
 x = re.sub(u'(-- *<i>)',r'<div n="2">\1',x)
 x = re.sub(u'(-- *\()',r'<div n="2">\1',x)
 # change '--' to mdash
 x = x.replace('--',u'—')
 return x
%endif
%if dictlo == 'acc':
def dig_to_xml_specific(x):
 """ changes particular to digitization"""
 if re.search(r'^<>',x):
  x = re.sub(r'<>','<br/>',x)
 elif re.search(r'^<P>',x):
  x = re.sub(r'<P>','<div n="P">',x)
 elif re.search(r'^<HI1>',x):
  x = re.sub(r'<HI1>','<div n="2">',x)  # add closing div later.
 elif re.search(r'^<HI>',x):
  x = re.sub(r'<HI>','<div n="3">',x)
 elif re.search(r'^<H>',x):
  x = re.sub(r'<H>','<H/>',x)
 return x
%endif
%if dictlo == 'yat':
def dig_to_xml_specific(x):
 """ changes particular to digitization"""
 if re.search(r'^<>',x):
  x = re.sub(r'<>','<br/>',x)
 return x
%endif

def dig_to_xml_general(x):
 """ These changes likely apply to ALL digitizations"""
 # xml requires that an ampersand be represented by &amp; entity
 x = x.replace('&','&amp;')
 # remove broken bar.  In xxx.txt, this usu. indicates a headword end
 x = x.replace(u'¦',' ') 
 # bold, italic, and Sanskrit markup converted to xml forms.
%if dictlo in ['ben','ccs','mci','stc','bhs','gra','pe','gst','ieg','mwe','pgn','pui','vei','pd','mw72','snp','bor','krm','inm','skd','bop','vcp']:
 # These are not applicable to vcp, but do no harm
%endif
%if dictlo == 'mw':
 # These are not applicable to mw, skip for efficiency
 #x = re.sub(r'{@','<b>',x)
 #x = re.sub(r'@}','</b>',x)
 #x = re.sub(r'{%','<i>',x)
 #x = re.sub(r'%}','</i>',x)
 #x = re.sub(r'{#','<s>',x)
 #x = re.sub(r'#}','</s>',x)
%elif dictlo == 'krm':
 x = re.sub(r'{@','<b>',x)
 x = re.sub(r'@}','</b>',x)
 x = re.sub(r'{%','<i>',x)
 x = re.sub(r'%}','</i>',x)
 #x = re.sub(r'{#','<s>',x)
 #x = re.sub(r'#}','</s>',x)
%elif dictlo == 'cae':
 # No bold in cae.txt
 #x = re.sub(r'{@','<b>',x)
 #x = re.sub(r'@}','</b>',x)
 x = re.sub(r'{%','<i>',x)
 x = re.sub(r'%}','</i>',x)
 x = re.sub(r'{#','<s>',x)
 x = re.sub(r'#}','</s>',x)
%else:
 x = re.sub(r'{@','<b>',x)
 x = re.sub(r'@}','</b>',x)
 x = re.sub(r'{%','<i>',x)
 x = re.sub(r'%}','</i>',x)
 x = re.sub(r'{#','<s>',x)
 x = re.sub(r'#}','</s>',x)
%endif
 return x

def dig_to_xml(xin):
 x = xin
 x = dig_to_xml_general(x)
 x = dig_to_xml_specific(x)
 return x

def dbgout(dbg,s):
 if not dbg:
  return
 filedbg = "make_xml_dbg.txt"
 fout = codecs.open(filedbhg,"a","utf-8")
 fout.write(s + '\n')
 fout.close()

def close_divs(line):
 """ line is the full xml record, but the <div> elements have not been
  closed.  Don't close empty div tags.
 """
%if dictlo in ['bor']:
 # we assume this closure already done
 return line
%endif
%if dictlo == 'sch':  
 divregex = r'<div>' # sch has '<div>' with no attributes.
%else:
 divregex = r'<div[^>]*?[^/]>'
%endif
 if not re.search(divregex,line):
  # no divs to close
  return line
 ans = [] # strings parts of data
 idx0 = 0
 # div can have attribute
 for m in re.finditer(divregex,line): 
   idx1=m.start()
   idx2 = m.end()
   line1 = line[idx0:idx1] # text preceding this div
   ans.append(line1)
   if idx0 != 0: 
    # close the previous div
    ans.append('</div>')
   # include this div
   linediv = line[idx1:idx2]
   ans.append(linediv)
   idx0 = idx2 # reset for next iteration
 # construct string for all text in line upto position idx0
 new = ''.join(ans) 
 # The last div will not be closed
 rest = line[idx0:]  
 # We can assume that rest contains 
 # <type>*</type></body> -> </div><type>*</type></body>
 # (no type)</body> -> </div></body>
 if re.search(r'(<type>.*?</type>)</body>',rest):
  newrest = re.sub(r'<type>',r'</div><type>',rest)
 elif re.search(r'</body>',rest):
  newrest = re.sub(r'</body>','</div></body>',rest)
 else:
  raise ValueError("close_divs_error: %s"%line.encode('utf-8'))
 newline = new + newrest
%if dictlo == 'krm':
 newline = close_divs_krm(newline)
%endif
 return newline

def construct_xmlhead(hwrec):
 key2 = hwrec.k2
 key1 = hwrec.k1
 hom = hwrec.h
 if hom == None:
  # no homonym
  h = "<key1>%s</key1><key2>%s</key2>" % (key1,key2)
 else:
  h = "<key1>%s</key1><key2>%s</key2><hom>%s</hom>" % (key1,key2,hom)
 return h

def construct_xmltail(hwrec):
 L = hwrec.L
 pagecol = hwrec.pc
 tail = "<L>%s</L><pc>%s</pc>" % (L,pagecol)
 if hwrec.type == None:
  # normal
  return tail
 # otherwise, also <hwtype n="type" ref="LP"
 hwtype = '<hwtype n="%s" ref="%s"/>' %(hwrec.type,hwrec.LP)
 tail = tail + hwtype
 return tail

def body_alt(bodylines,hwrec):
 """
  insert an extra body line at the top.
 """
 hwtype = hwrec.type
 assert hwtype in ['alt','sub'],"body_alt error: %s"%hwtype
 LP = hwrec.LP  # L-number of parent
 hwrecP = HW.Ldict[LP]
 key1P = hwrecP.k1
 key1 = hwrec.k1
 templates = {
  'alt':'<alt>%s is an alternate of %s.</alt>',
  'sub':'<alt>%s is a sub-headword of %s.</alt>'
 }
 if HW.Sanskrit:
  # prepare for conversion from slp1 to user choice
  key1P = '<s>%s</s>' %key1P
  key1 = '<s>%s</s>' %key1
 template = templates[hwtype]
 extraline = template %(key1,key1P)
 # insert extraline at the front
 return [extraline]+bodylines

%if dictlo == 'inm':
def body_inm(lines):
 ans0 = []
 # phase 1: append <sup> lines to previous line
 nsup=0
 for idx,line in enumerate(lines):
  if line.startswith('<sup>'): # footnote marker
   idx0 = len(ans0) - 1
   ans0[idx0] = ans0[idx0] + line
  else:
   ans0.append(line)
 # phase 2: close each line beginning with <div
 for idx,line in enumerate(ans0):
  if line.startswith('<div'):
   if line.endswith('</F>'):
    ans0[idx] = re.sub('</F>','</div></F>',line)
   else:
    ans0[idx] = line + '</div>'
 return ans0

%endif
%if dictlo == 'bop':
def body_bop(lines):
 ans0 = []
 # phase 1: append <sup> lines to previous line
 nsup=0
 for idx,line in enumerate(lines):
  if line.startswith('<sup>'): # footnote marker
   idx0 = len(ans0) - 1
   ans0[idx0] = ans0[idx0] + line
  else:
   ans0.append(line)
 # phase 2: close each line beginning with <div
 for idx,line in enumerate(ans0):
  if line.startswith('<div'):
   if line.endswith('</F>'):
    ans0[idx] = re.sub('</F>','</div></F>',line)
   else:
    ans0[idx] = line + '</div>'
 return ans0

%endif
def construct_xmlstring(datalines,hwrec):
 dbg = False
 datalines1 = []
 # 1. h (head)
 h = construct_xmlhead(hwrec)
 dbgout(dbg,"head: %s" % h)  
 #2. construct tail
 tail = construct_xmltail(hwrec)
 dbgout(dbg,"tail: %s" % tail)  
 #3. construct body
%if dictlo in ['sch','ap90']:
 # To mimic current display of Sch, we remove the 'head' from first line:
 for i,x in enumerate(datalines):
  if i == 0:
   m = re.search(u'^(.*?¦)(.*)$' ,x)
   if not m:
    print("xml_string ERROR at =",x.encode('utf-8'))
    exit(1)
   head = m.group(1)
   rest = m.group(2)
   x = rest
  datalines1.append(x)
 datalines = datalines1
%endif
 bodylines = [dig_to_xml(x) for x in datalines]
 if hwrec.type != None:
  bodylines = body_alt(bodylines,hwrec)
%if dictlo == 'inm':
 bodylines = body_inm(bodylines)
%endif
%if dictlo == 'bop':
 # bop closing divs is awkward in presence of <F>X</F>
 bodylines = body_bop(bodylines)
%endif
 body0 = ' '.join(bodylines)
 dbgout(dbg,"chk4: %s" % body0)
 body = body0
 dbgout(dbg,"body0: %s" % body0)
 ##3a. Remove <LEND>. datalines does not include <LEND>. See get_datalines
 #body = body.replace('<LEND>','') # Line ending mark needs to be removed.
 #4. construct result
%if dictlo != 'mw':
 data = "<H1><h>%s</h><body>%s</body><tail>%s</tail></H1>" % (h,body,tail)
%endif
%if dictlo == 'mw':
 #data = "<H1><h>%s</h><body>%s</body><tail>%s</tail></H1>" % (h,body,tail)
 data = "<h>%s</h><body>%s</body><tail>%s</tail>" % (h,body,tail)
 tag = 'H%s' %hwrec.e
 data = '<%s>%s</%s>' %(tag,data,tag)
%endif
%if dictlo in ['sch','ap90']:
 #4a. For sch: Put the <info> element into the tail
 data = re.sub('(<info.*?>) *</body><tail>',r'</body><tail>\1',data)
 #4b. For comparison to previous version, remove a space after <body>
 data = re.sub(r'<body> ','<body>',data)
%endif
 #5. Close the <div> elements
%if dictlo not in ['inm','skd','bop']:
 data = close_divs(data)
%endif
 return data

def xml_header(xmlroot):
 # write header lines
 text = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE %s SYSTEM "%s.dtd">
<!-- Copyright Universitat Koln 2013 -->
<%s>
""" % (xmlroot,xmlroot,xmlroot)
 lines = text.splitlines()
 lines = [x.strip() for x in lines if x.strip()!='']
 return lines

def get_datalines(hwrec,inlines):
 # for structure of hwrec, refer to hwparse.py
 n1 = int(hwrec.ln1)
 n2 = int(hwrec.ln2)
 # By construction, n1 is the meta line, and n2 is the <lend> line of
 # this entry in xxx.txt.
 # For our purposes, we do not need this first and last line
 n1 = n1 + 1
 n2 = n2 - 1
 # Next, we make indexes into the inlines array, which are 0-based
 # whereas n1 and n2 are 1-based
 idx1 = n1 - 1
 idx2 = n2 - 1
 datalines = inlines[idx1:idx2+1]
 return datalines

def make_xml(filedig,filehw,fileout):
 # slurp txt file into list of lines
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
    inlines = [line.rstrip('\r\n') for line in f]
 # parse xxxhw.txt 
 hwrecs = init_hwrecs(filehw)
 # open output xml file
 fout = codecs.open(fileout,'w','utf-8')
 nout = 0  # count of lines written to fout
 # generate xml header lines
 lines = xml_header(xmlroot)
 for line in lines:
  fout.write(line + '\n')
  nout = nout + 1
 # process hwrecs records one at a time and generate output
 nerr = 0
 for ihwrec,hwrec in enumerate(hwrecs):
  if ihwrec > 1000000: # 12 
   print("debug stopping")
   break
  datalines = get_datalines(hwrec,inlines)
  # construct output
  xmlstring = construct_xmlstring(datalines,hwrec)
  # data is a string, which should be well-formed xml
  # try parsing this string to verify well-formed.
  try:
   root = ET.fromstring(xmlstring.encode('utf-8'))
  except:
%if dictlo not in ['sch','wil','ap90','acc','yat']:
   outarr = []
   nerr = nerr + 1
   out = "<!-- xml error #%s: L = %s, hw = %s-->" %(nerr,hwrec.L,hwrec.k1)
   outarr.append(out)
   outarr.append("datalines = ")
   outarr = outarr + datalines
   outarr.append("xmlstring=")
   outarr.append(xmlstring)
   outarr.append('')
   for out in outarr:
    print(out.encode('utf-8'))
   #exit(1) continue
%endif
%if dictlo in ['sch','acc','yat']:
   out = "xml error: n=%s,m line=\n%s\n" %(nout+1,xmlstring)
   print(out.encode('utf-8'))
   exit(1)
%endif
%if dictlo in ['wil','ap90']:
   out = "xml error: n=%s,m line=\n%s\n" %(nout+1,xmlstring)
   print(out.encode('utf-8'))
   fout.write(xmlstring + '\n')
   fout.close()
   exit(1)
%endif
  # write output
  fout.write(xmlstring + '\n')
  nout = nout + 1

 # write closing line for xml file.
 out = "</%s>\n" % xmlroot
 fout.write(out)
 fout.close()

if __name__=="__main__":
 filein = sys.argv[1] # xxx.txt
%if dictlo != 'mw':
 filein1 = sys.argv[2] #xxxhw2.txt
%else:
 filein1 = sys.argv[2] #xxxhw.txt
%endif
 fileout = sys.argv[3] # xxx.xml
 make_xml(filein,filein1,fileout)
