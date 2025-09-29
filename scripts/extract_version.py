import re
from pathlib import Path
p = Path(__file__).with_name('version.txt')
text = p.read_text(encoding='utf-8')
fv = re.search(r"StringStruct\('FileVersion',\s*'([^']+)'\)", text)
pv = re.search(r"StringStruct\('ProductVersion',\s*'([^']+)'\)", text)
print(fv.group(1) if fv else '')
print(pv.group(1) if pv else '')

