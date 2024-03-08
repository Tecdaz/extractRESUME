import sys
import pdfplumber
import json


def format_consume(consume, is_taxe):
    result = {}
    consume = consume.split(" ")
    has_date = True if len(consume[0].split("-")) == 3 else False
    result["date"] = consume[0] if has_date else None

    result['amount'] = float(consume[-1].replace(".", "").replace(",", "."))
    # If is a taxe, the description is before the last element
    limit = -1 if is_taxe else -2
    start = 1 if has_date else 0
    result['description'] = " ".join(consume[start:limit])

    result['divisa'] = 'USD' if 'USD' in result['description'] else 'PESOS'
    return result


def run():
    # Get file name
    file_name = sys.argv[1]

    text = ""
    # Extract text from pdf
    with pdfplumber.open(file_name) as pdf:
        for i in range(1, 3):
            page = pdf.pages[i]
            text += page.extract_text()

    # Split text by lines
    list_of_lines = text.split("\n")

    # Get consumes, total consumes, taxes and actual consumes
    pointer = 0
    consumes = []
    taxes = []
    total_consumes = ""
    actual_consumes = ""

    while pointer <= len(list_of_lines):
        if list_of_lines[pointer].startswith("Consumos"):
            pointer += 2
            # Save consumes
            while not list_of_lines[pointer].startswith("TOTAL"):
                consumes.append(list_of_lines[pointer])
                pointer += 1
            # Save total of consumes
            total_consumes += list_of_lines[pointer]
            pointer += 3
            # Save taxes
            while not list_of_lines[pointer].startswith("SALDO"):
                taxes.append(list_of_lines[pointer])
                pointer += 1
            # Save actual consumes
            actual_consumes += list_of_lines[pointer]
            break
        pointer += 1

    consumes = [format_consume(consume, False) for consume in consumes]
    taxes = [format_consume(taxe, True) for taxe in taxes]
    total_consumes_pesos = sum(map(lambda x: x.get(
        'amount', 0) if x.get("divisa") == "PESOS" else 0, consumes))
    total_consumes_usd = sum(
        map(lambda x: x.get('amount', 0) if x.get('divisa') == "USD" else 0, consumes))
    total_taxes = sum(map(lambda x: x.get('amount', 0), taxes))
    actual_consumes_pesos = total_consumes_pesos + total_taxes
    actual_consumes_usd = total_consumes_usd

    results = {
        "consumes": consumes,
        "total_consumes_pesos": total_consumes_pesos,
        "total_consumes_usd": total_consumes_usd,
        "taxes": taxes,
        "total_taxes": total_taxes,
        "actual_consumes_pesos": actual_consumes_pesos,
        "actual_consumes_usd": actual_consumes_usd
    }

    with open(f"results{file_name[:-4]}.json", "w") as file:
        file.write(json.dumps(results, indent=2))


if __name__ == "__main__":
    run()
