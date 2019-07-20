# coding=utf-8
""" make_xml.py for  2014-06-10
 Reads/Writes utf-8
 Mar 12, 2015
 Remove conversion of HK to SLP1 - See convertwork/readme.txt
 05-03-2017  <HI1> -> <div n="2">...</div>
 05-19-2017  Revise to use new forms of acc.txt and acchw.txt
"""
import xml.etree.ElementTree as ET
import sys, re,codecs
from hwparse import init_hwrecs,HW
xmlroot = HW.dictcode  

def dig_to_xml_specific(x):
 """ changes particular to md digitization"""
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

def dig_to_xml_general(x):
 """ These changes likely apply to ALL digitizations"""
 # xml requires that an ampersand be represented by &amp; entity
 x = x.replace('&','&amp;')
 # remove broken bar.  In xxx.txt, this usu. indicates a headword end
 x = x.replace(u'Â¦',' ') 
 # bold, italic, and Sanskrit markup converted to xml forms.
 x = re.sub(r'{@','<b>',x)
 x = re.sub(r'@}','</b>',x)
 x = re.sub(r'{%','<i>',x)
 x = re.sub(r'%}','</i>',x)
 x = re.sub(r'{#','<s>',x)
 x = re.sub(r'#}','</s>',x)
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
 """ line is the full xml record, but the '<div> elements have not been
  closed.  
 """
 divregex = r'<div.*?>'
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
 return newline

def construct_xmlhead(hwrec):
 key2 = hwrec.k2
 key1 = hwrec.k1
 hom = hwrec.hom
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
 bodylines = [dig_to_xml(x) for x in datalines]
 if hwrec.type != None:
  bodylines = body_alt(bodylines,hwrec)
 body0 = ' '.join(bodylines)
 dbgout(dbg,"chk4: %s" % body0)
 body = body0
 dbgout(dbg,"body0: %s" % body0)
 ##3a. Remove <LEND>. datalines does not include <LEND>. See get_datalines
 #body = body.replace('<LEND>','') # Line ending mark needs to be removed.
 #4. construct result
 data = "<H1><h>%s</h><body>%s</body><tail>%s</tail></H1>" % (h,body,tail)
 #5. Close the <div> elements
 data = close_divs(data)
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
   print "debug stopping"
   break
  datalines = get_datalines(hwrec,inlines)
  # construct output
  xmlstring = construct_xmlstring(datalines,hwrec)
  # data is a string, which should be well-formed xml
  # try parsing this string to verify well-formed.
  try:
   root = ET.fromstring(xmlstring.encode('utf-8'))
  except:
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
    print out.encode('utf-8')
   #exit(1) continue
  # write output
  fout.write(xmlstring + '\n')
  nout = nout + 1

 # write closing line for xml file.
 out = "</%s>\n" % xmlroot
 fout.write(out)
 fout.close()

if __name__=="__main__":
 filein = sys.argv[1] # acc.txt
 filein1 = sys.argv[2] #acchw2.txt
 fileout = sys.argv[3] # acc.xml
 make_xml(filein,filein1,fileout)
