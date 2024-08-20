from PyPDF2 import PdfReader, PdfWriter
import os


def strip_quotes(path):
    return path.strip('\"').strip('\'')


def split_pdf(input_pdf, start_page, end_page, output_pdf):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for i in range(start_page - 1, end_page):
        writer.add_page(reader.pages[i])

    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)


if __name__ == "__main__":
    input_pdf = strip_quotes(input("Enter the path to the PDF file: "))
    start_page = int(strip_quotes(input("Enter the start page number: ")))
    end_page = int(strip_quotes(input("Enter the end page number: ")))
    output_pdf = strip_quotes(input("Enter the name for the output PDF file: "))

    # Split the PDF
    split_pdf(input_pdf, start_page, end_page, output_pdf)
    print(f"Pages {start_page} to {end_page} have been split and saved as {output_pdf}")
