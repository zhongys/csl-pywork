echo "BEGIN redo_xml.sh"
%if dictlo in ['pw','pwg']:
echo "construct ${dictlo}0.xml..."
python make_xml.py ../orig/${dictlo}.txt ${dictlo}hw.txt ${dictlo}0.xml # > redoxml_log.txt
echo "construct ${dictlo}.xml"
python make_xml_ls.py ${dictlo}0.xml ${dictlo}auth/${dictlo}bib.txt ${dictlo}.xml
%elif (dictlo == 'mw') and cologne_flag: # use python3
echo "construct ${dictlo}.xml..."
python3 make_xml.py ../orig/${dictlo}.txt ${dictlo}hw.txt ${dictlo}.xml # > redoxml_log.txt
%else:
echo "construct ${dictlo}.xml..."
python make_xml.py ../orig/${dictlo}.txt ${dictlo}hw.txt ${dictlo}.xml # > redoxml_log.txt
%endif
echo "xmllint on ${dictlo}.xml..."
xmllint --noout --valid ${dictlo}.xml
echo "${dictlo}.sqlite..."
#  construct things that depend on xxx.xml
sh redo_postxml.sh
echo "END redo_xml.sh"
