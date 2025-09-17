 
import argparse
import json
from src.parser import parse_pdf 
import os


def main():
    parser = argparse.ArgumentParser(description="Parse a PDF and extract its content into a structured JSON file.")
    parser.add_argument('--input', type=str, required=True, help='Path to the input PDF file.')
    parser.add_argument('--output', type=str, required=True, help='Path to the output JSON file.')

    args = parser.parse_args()
    extracted_data = parse_pdf(pdf_path=args.input)

    if extracted_data:
        with open(args.output, 'w') as f:
            json.dump(extracted_data, f, indent=4)
        print(f"Successfully created the JSON output at: {args.output}")
    else:
        print("Could not extract data from the PDF.")


if __name__ == "__main__":
    main()