from pathlib import Path
import os

import pandas as pd
from pandas.api.types import is_string_dtype
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


VALID_GRADES = ["A", "B", "C", "D", "E", "E", "F"]
CHART_COLORS = [
    "#14A44D", "#91CC75", "#6080E0", "#FFC107", "#FD9552", "#EE4C4C"]


def read_file(file_path):
    """Read result file.

    Returns
    -------
    output: pd.DataFrame -> Return the content of the file as a
    dataframe.
    """
    if Path(file_path).suffix == '.csv':
        df = pd.read_csv(file_path, dtype=str, header=None)
        print(df)
    elif Path(file_path).suffix == '.xlsx':
        df = pd.read_excel(file_path, dtype=str)
    else:
        raise ValueError(
            "Invalid file type selected. Only .xlsx and CSV files are allowed."
        )
    df.columns = range(len(df.columns))
    return df


def process_result_file_content(file_content: pd.DataFrame):
    """Extract results from the content of the input file."""
    results_row_df = pd.DataFrame()
    reg_no_col = None

    # Find registration number column
    for col in file_content.columns:
        df_gen = (
            file_content[
                file_content[col]
                .str
                .contains(pat="^[0-9]{4}\/[0-9]{6}", regex=True, na=False)
            ]
        )

        if not df_gen.empty:
            reg_no_col = col
            results_row_df = df_gen
            break

    if reg_no_col is None:
        raise ValueError("No registration numbers detected in input file")

    # define list of valid grades
    valid_grades = VALID_GRADES + ["FF"]
    expected_grade_col = None

    for col in range(reg_no_col+1, len(results_row_df.columns)):
        if not is_string_dtype(results_row_df[col]):
            continue
        results_row_df[col] = (
            results_row_df[col].apply(lambda x: x.strip().upper()))
        results_row_df["grade_checker"] = (
            results_row_df[col].apply(lambda x: x in valid_grades))
        if results_row_df["grade_checker"].sum() >= len(results_row_df) * 0.75:
            expected_grade_col = col
            df_gen.rename(
                columns={
                    expected_grade_col: "letter_grade",
                    reg_no_col: "reg_no"
                },
                inplace=True)

    if expected_grade_col is None:
        raise ValueError(
            "Problem processing file. Could not detect the grade column.")
    df_gen = df_gen[["reg_no", "letter_grade"]]
    print(df_gen.letter_grade.value_counts().sort_index())
    return df_gen


def chart_interpretation(file_name, grade_summary):
    grade_block = (
        grade_summary
        .rename(columns={"letter_grade": "Grade"})
        .Grade
        .value_counts()
        .sort_index()
    )
    grade_str = '\n'
    for grade, count in grade_block.items():
        grade_str += f"    {grade}:  {count:<8}\n"
    line_div = '-'*120
    msg = (f'''
    Source file: {file_name}
    {line_div}
    {grade_str}

    Total: {len(grade_summary):<8}
    {line_div}
    ''')
    return msg


def generate_analytics(files, destination_dir=None):
    """Generate analytics for hte cleaned data."""
    pdf = PdfPages(
        os.path.join(
            Path(files[0]).parent,
            f"Result analytics.pdf"
        )
    )
    for file in files:
        file_cont = read_file(file)
        grade_summary = process_result_file_content(file_cont)
        plt.pie(
            grade_summary.letter_grade.value_counts().sort_index(),
            labels=list(
                grade_summary.letter_grade.value_counts().sort_index().index),
            autopct="%1.2f%%",
            colors=CHART_COLORS
        )
        plt.title(Path(file).stem)
        plt.legend(loc='upper left')
        pdf.savefig()
        plt.close()
        fig = plt.figure(figsize=(11.69, 8.27))
        fig.clf()
        plt.text(
            0.05, 0.5,
            chart_interpretation(file, grade_summary),
            transform=fig.transFigure,
            size=16,
            ha="left")
        plt.axis('off')
        pdf.savefig()
        plt.close()
    pdf.close()
