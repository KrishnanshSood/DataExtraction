import os
from extractors.logger import get_logger
from extractors.acts_sections import extract_acts_sections
from extractors.names import extract_names
from extractors.mobile_numbers import extract_mobile_numbers
from extractors.email_ids import extract_emails
from extractors.pan_gstin import extract_pan_and_gstin
from extractors.passport import extract_passport_numbers
from extractors.bank_details import extract_bank_details
from extractors.address import extract_all_addresses

logger = get_logger("Main")


def read_text_file(path: str) -> str:
    logger.info(f"Reading file: {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        return ""


def print_results(title: str, items: list):
    print(f"\n{title}", flush=True)
    for item in items:
        print("-", item, flush=True)


def print_address_components(address_dict: dict):
    print("\n📍 Address Components Found:")
    for key, value in address_dict.items():
        print(f"- {key}: {value}")


def process_file(filepath: str):
    logger.info(f"📂 Processing: {filepath}")
    text = read_text_file(filepath)
    if not text.strip():
        logger.warning(f"Empty or unreadable file skipped: {filepath}")
        return

    print(f"\n{'=' * 40}\n📄 File: {os.path.basename(filepath)}\n{'=' * 40}")

    # Extract acts & sections first, but delay printing
    acts_sections = extract_acts_sections(text)  # ✅ Will run here
    print_results("📘 Acts & Sections Found:", acts_sections)  # ✅ Output only happens now

    people, orgs = extract_names(text)
    print_results("🧑 People Found:", people)
    print_results("🏢 Organizations Found:", orgs)

    print_results("📱 Mobile Numbers Found:", extract_mobile_numbers(text))
    print_results("📧 Email IDs Found:", extract_emails(text))

    pans, gstins = extract_pan_and_gstin(text)
    print_results("🧾 PAN Numbers Found:", pans)
    print_results("🧾 GSTINs Found:", gstins)

    print_results("🛂 Passport Numbers Found:", extract_passport_numbers(text))

    accounts, ifscs = extract_bank_details(text)
    print_results("🏦 Account Numbers Found:", accounts)
    print_results("🏦 IFSC Codes Found:", ifscs)

    addresses = extract_all_addresses(text)
    if addresses:
        for i, address in enumerate(addresses, 1):
            print(f"\n🏷️ Address Block {i}")
            print_address_components(address)
    else:
        print("\n📍 No structured addresses found.")

def main():
    folder_path = "files"
    logger.info("🚀 Starting extraction pipeline...")

    if not os.path.exists(folder_path):
        logger.error(f"Folder not found: {folder_path}")
        return

    txt_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".txt")]

    if not txt_files:
        logger.warning(f"No .txt files found in {folder_path}")
        return

    for file_path in txt_files:
        process_file(file_path)


if __name__ == "__main__":
    main()
