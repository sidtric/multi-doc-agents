import io
import csv
from pypdf import PdfReader
from PIL import Image
import pytesseract
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)


def load_pdf(file_bytes, filename):
    reader = PdfReader(io.BytesIO(file_bytes))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return splitter.split_text(text)


def load_image(file_bytes, filename):
    image = Image.open(io.BytesIO(file_bytes))
    text = pytesseract.image_to_string(image)
    return splitter.split_text(text)


def load_csv(file_bytes, filename):
    content = file_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    rows = [", ".join(f"{k}: {v}" for k, v in row.items()) for row in reader]
    return splitter.split_text("\n".join(rows))


def load_txt(file_bytes, filename):
    return splitter.split_text(file_bytes.decode("utf-8"))


_loaders = {
    "pdf":  load_pdf,
    "png":  load_image,
    "jpg":  load_image,
    "jpeg": load_image,
    "csv":  load_csv,
    "txt":  load_txt,
    "md":   load_txt,
}


def load_file(file_bytes, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in _loaders:
        raise ValueError(f"Unsupported file type: .{ext}")
    return _loaders[ext](file_bytes, filename)
