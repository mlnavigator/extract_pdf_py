from PIL import Image, ImageOps
import pymupdf
import re
from pdf2image import convert_from_path
import pytesseract
import sys
"""
requirements:

# install tesseract on linux
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
sudo apt install tesseract-ocr-rus
pip install pytesseract

pip install PyMuPDF
pip install pdf2image
pip install Pillow
"""


def clear_text(text: str) -> str:
    for _ in range(3):
        text = re.sub(r'([a-zа-я,—\-]+) *\n[\n ]*([a-zа-я]+)', '\g<1> \g<2>', text, flags=re.DOTALL)

    text = re.sub(r' [^\dавкос] ', ' ', text)
    text = re.sub(r'\n +[^\dавкос] ', '\n', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'[\n ]*\n\n+[\n ]*', '\n\n', text)
    text = text.replace('®', ' - ')
    text = text.replace('\n\n','\n<>')
    parts = [p.strip() for p in text.split('\n')]
    parts = [p for p in parts if len(p) > 5]
    text = '\n'.join(parts)
    text = text.replace('<>','\n\n')
    text = re.sub(r'\n\n{2,}', '\n\n', text)

    return text


def is_has_text(pdf_file_path: str) -> bool:
    try:
        with pymupdf.open(pdf_file_path) as fd:
            for i, page in enumerate(fd):
                if len(page.get_text()) > 200:
                    return True
                if i > 2:
                    break
    except Exception as e:
        print(f'Error: {e}')
        return False

    return False


def extract_text_layer(pdf_file_path: str) -> str:
    try:
        with pymupdf.open(pdf_file_path) as fd:
            doc = ''
            for page in fd:
                doc += page.get_text()

            doc = clear_text(doc)
    except Exception as e:
        print(f'Error: {e}')

    return clear_text(doc)


def extract_text_from_image(image: Image) -> str:
    try:
        image1 = ImageOps.grayscale(image)
        text = pytesseract.image_to_string(image1, lang='rus+eng')
        return text
    except Exception as e:
        print(f'Error: {e}')
        return ''


def ocr_pdf(pdf_file_path: str) -> str:
    try:
        pages: list[Image]= convert_from_path(pdf_file_path)
    except Exception as e:
        print(f'Error: {e}')
        return ''

    doc = ''
    for page in pages:
        try:
            text = extract_text_from_image(page)
            doc += '\n'
            doc += clear_text(text)
        except Exception as e:
            print(f'Error: {e}')

    return doc.strip()


def extract_text_from_pdf(pdf_file_path: str, verbose: bool = True) -> str:
    has_text_layer = is_has_text(pdf_file_path)

    if has_text_layer:
        if verbose:
            print('Has text layer')
        return extract_text_layer(pdf_file_path)
    else:
        if verbose:
            print('No text layer, use OCR')
        return ocr_pdf(pdf_file_path)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python extract_pdf.py <in_pdf_file_path.pdf> <out_text_file_path.txt>')
        exit(1)

    pdf_file_path = sys.argv[1]
    out_text_file_path = sys.argv[2]
    text = extract_text_from_pdf(pdf_file_path)
    with open(out_text_file_path, 'w') as f:
        f.write(text)
