from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import docx

def convert_docx_to_txt(path,caratula=False):
    doc = docx.Document(path)
    text = []

    for para in doc.paragraphs:
        text.append(para.text)

    text = '\n'.join(text)
    return text


def convert_pdf_to_txt(path,caratula=False):
	retstr = StringIO()
	rsrcmgr = PDFResourceManager()

	laparams = LAParams()
	device = TextConverter(rsrcmgr, retstr, laparams=laparams)
	try:
	    interpreter = PDFPageInterpreter(rsrcmgr, device)
	    fp = open(path, 'rb')
	    iterPDF = iter(PDFPage.get_pages(fp, set(), maxpages=0, password="",caching=True, check_extractable=True))
	    
	    if not caratula:
	    	next(iterPDF)

	    for page in iterPDF:
	        interpreter.process_page(page)
	        text = retstr.getvalue()

	    fp.close()
	    device.close()
	    retstr.close()
	    return text
	except Exception as e:
		fp.close()
		device.close()
		retstr.close()
		return 'error'

