import tabula
import pandas as pd


def strip_quotes(path):
    return path.strip('\"').strip('\'')


def ensure_xlsx_extension(filename):
    if not filename.lower().endswith('.xlsx'):
        filename += '.xlsx'
    return filename


def extract_tables_from_pdf():
    # Prompt for the PDF file path
    pdf_path = strip_quotes(input("Enter the path to the PDF file: "))

    # Prompt for the output Excel file name
    excel_output = strip_quotes(input("Enter the name for the output Excel file: "))
    excel_output = ensure_xlsx_extension(excel_output)

    # Extract tables from the PDF
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

    # Create a Pandas Excel writer using openpyxl as the engine.
    with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
        for i, table in enumerate(tables):
            # Convert each table to a DataFrame
            df = pd.DataFrame(table)

            # Save each table to a separate sheet in the Excel file
            df.to_excel(writer, sheet_name=f'Table_{i + 1}', index=False)

    print(f"Data has been extracted and saved to {excel_output}")


if __name__ == "__main__":
    extract_tables_from_pdf()
