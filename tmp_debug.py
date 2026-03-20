import re
from app.services.resume_parser import _collapse_spaced_letters

text = 'AI | n g i n e e r  f o c u s e d   o n'
print('orig:', repr(text))

# remove bullets/pipes
s1 = re.sub(r'[·••–—|\u2022\u2023\u25E6\u2043\u2219]', ' ', text)
print('step1:', repr(s1))

s2 = _collapse_spaced_letters(s1)
print('step2:', repr(s2))

s3 = re.sub(r'[ \t]+', ' ', s2)
print('step3:', repr(s3))
