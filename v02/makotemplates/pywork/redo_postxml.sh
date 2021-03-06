# 
# 0. copy xxxheader.xml from pywork to web
cp ${dictlo}header.xml ../web/
# 1. Redo web/xxx.sqlite
cd sqlite
sh redo.sh
cd ../ # back in pywork
# 2. redo db (query_dump) for advanced search
cd webtc2
sh redo.sh
cd ../ # back to pywork
# For applicable dictionaries, update other web/sqlite databases
# abbreviations
%if dictlo in ['stc','bur','cae','mw','pw','pwg']:
 cd ${dictlo}ab
 sh redo.sh
 cd ../ # back to pywork
%endif
# literary source.
%if dictlo in ['mw','pw','pwg']:
 cd ${dictlo}auth
 sh redo.sh
 cd ../ # back to pywork
%endif
# two extra links dbs for mw
%if dictlo == 'mw':
 # Westergaard DAtupAWa links
 cd westmwtab
 sh redo.sh
 cd ../ # back to pywork
 # Whitney roots links.
 cd whitmwtab
 sh redo.sh
 cd ../ # back to pywork
%endif
