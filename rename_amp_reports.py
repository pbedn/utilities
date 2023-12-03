import argparse
import pathlib
import shutil
import sys

from datetime import datetime
from decimal import Decimal

from pdfquery import PDFQuery


CURRENT_DIR = pathlib.Path(__file__).parent
DATA_FORMAT = "%m/%d/%y"
FILE_DATA_FORMAT = "%Y_%m_%d"


def main(source_dir, target_dir):
    if not pathlib.Path(target_dir).exists():
        pathlib.Path(target_dir).mkdir(parents=True)

    for pdf_file in source_dir.glob("*.PDF"):
        print("Reading file: ", pdf_file)
        if "Periodic" in pdf_file.name:
            rename_monthly_files(pdf_file, target_dir)
        else:
            rename_daily_files(pdf_file, target_dir)


def rename_daily_files(pdf_file, target_dir):
    pdf = PDFQuery(pdf_file)
    pdf.load()

    report_date = pdf.pq('LTTextBoxHorizontal:contains("Account Summary")')[0].text
    report_date = report_date.replace("Account Summary as of ", "").strip()
    date_object = datetime.strptime(report_date, DATA_FORMAT)
    print("Report Date:", report_date)

    trade_confirmations = pdf.pq(
        "LTTextLineHorizontal:contains('T R A D E S C O N F I R M A T I O N S')"
    )
    journal_entries = pdf.pq(
        "LTTextLineHorizontal:contains('J O U R N A L E N T R I E S')"
    )

    payments = 0
    if journal_entries:
        monthly_data_subscription = pdf.pq(
            "LTTextLineHorizontal:contains('CQG CME NP L1 Bundled')"
        )
        wire_transfer = pdf.pq("LTTextLineHorizontal:contains('Wire Tsf')")

        payments = pdf.pq('LTTextLineHorizontal:contains("PAYMENTS")')[-1].text
        payments = (
            payments.replace("CR", "")
            .replace("DR", "")
            .replace("PAYMENTS/RECEIPTS", "")
        )
        if monthly_data_subscription:
            print("Monthly Data Subscription:", payments)
        if wire_transfer:
            print("Incoming Wire Transfer:", payments)

    old_acc_balance = pdf.pq('LTTextLineHorizontal:contains("ACCOUNT CASH BALANCE")')[
        -1
    ].text
    old_acc_balance = old_acc_balance.replace("CR", "").replace(
        "ACCOUNT CASH BALANCE", ""
    )

    new = pdf.pq('LTTextLineHorizontal:contains("(today)")')[-1].text
    new = new.replace("(today)", "").replace("CR", "")
    new_acc_balance, realized_profit_loss = new.split()

    if trade_confirmations:
        only_trading = Decimal(realized_profit_loss) - Decimal(payments)
        print("Realized P/L:", only_trading)

    print("Old acc balance:", old_acc_balance)
    print("New acc balance:", new_acc_balance)

    save_to_file(f"{date_object.strftime(FILE_DATA_FORMAT)}.pdf", pdf_file, target_dir)
    print()


def save_to_file(new_file_name, pdf_file, target_dir):
    print(f"Saving to file {new_file_name}")
    shutil.copy(pdf_file, target_dir / new_file_name)


def rename_monthly_files(pdf_file, target_dir):
    pdf = PDFQuery(pdf_file)
    pdf.load()

    report_date = pdf.pq('LTTextBoxHorizontal:contains("Account Summary")')[0].text
    report_date = report_date.replace("Account Summary from ", "").strip()
    month, _, year = report_date.split(" to ")[0].split("/")
    year = datetime.strptime(year, "%y").strftime("%Y")
    report_date = f"{year}-{month}"
    print("Report Date:", report_date)

    file_ending = pdf_file.stem.split("-")[0]
    save_to_file(f"{year}_{month}_{file_ending}.pdf", pdf_file, target_dir)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--source_dir",
        default=".",
        type=pathlib.Path,
        help="(optionally) path to source directory, defaults to current working directory",
    )
    parser.add_argument(
        "-t",
        "--target_dir",
        default=".",
        type=pathlib.Path,
        help="(optionally) path to output directory, defaults to current working directory",
    )
    args = parser.parse_args()

    try:
        print("Starting application.")
        main(args.source_dir, args.target_dir)
    except Exception as e:
        raise e
    finally:
        input("Closing application (Press key to exit).")
        sys.exit()
