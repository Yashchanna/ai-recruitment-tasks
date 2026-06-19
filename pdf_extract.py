from pypdf import PdfReader
r = PdfReader(r"E:\Syn Assesment\Gen AI Task.pdf")
text = []
for p in r.pages:
    t = p.extract_text() or ""
    text.append(t)
open(r"E:\Syn Assesment\Gen AI Task.txt","w",encoding="utf-8").write("\n\n".join(text))
print('WROTE')
