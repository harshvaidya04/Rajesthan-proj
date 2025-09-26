from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import xlrd

app = FastAPI(title="Marks Transformation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Grade computation function
# --------------------------
def compute_grade_and_points(marks, th_max="", ce_max="", pr_max="", total_max="", grace=0, is_practical=False, passing_scheme="scheme1"):
    if str(marks).strip().upper() == "AB":
        return "AB", 0

    try:
        marks = float(marks)
    except:
        return "", 0

    if is_practical:
        percent = marks + grace
        if passing_scheme == "scheme1":
            min_passing = 40
        else:
            min_passing = 36
    else:
        if total_max and str(total_max).strip() not in ["", "nan", "None"]:
            try:
                total_max = float(total_max)
                if total_max > 0:
                    percent = ((marks + grace) / total_max) * 100
                else:
                    return "", 0
            except:
                return "", 0
        else:
            total_max = 0
            for val in [th_max, ce_max, pr_max]:
                try:
                    if str(val).strip() not in ["", "nan", "None"]:
                        total_max += float(val)
                except:
                    pass

            if total_max <= 0:
                return "", 0

            percent = ((marks + grace) / total_max) * 100
        min_passing = 36

    if percent >= 91: return "O", 10
    elif percent >= 81: return "A+", 9
    elif percent >= 71: return "A", 8
    elif percent >= 61: return "B+", 7
    elif percent >= 51: return "B", 6
    elif percent >= 41: return "C+", 5
    elif percent >= min_passing: return "C", 4
    else: return "F", 0


# --------------------------
# Transform function with passing scheme support
# --------------------------
def transform_row(row, passing_scheme="scheme1"):
    new_row = {}

    # --- Direct mappings ---
    new_row["ORG_NAME"] = row.get("ORG_NAME", "")
    new_row["ACADEMIC_COURSE_ID"] = row.get("ACADEMIC_COURSE_ID", "")
    new_row["COURSE_NAME"] = row.get("COURSE_NAME", "")
    new_row["ADMISSION_YEAR"] = row.get("ADMISSION_YEAR", "")
    new_row["SESSION"] = row.get("SESSION", "")
    new_row["AADHAAR_NAME"] = row.get("AADHAAR_NAME", "")
    
    # Format DOB to dd/mm/yyyy
    dob = row.get("DOB", "")
    if dob and str(dob).strip():
        try:
            if isinstance(dob, str):
                if "/" in dob:
                    parts = dob.split("/")
                    if len(parts) == 3:
                        if len(parts[0]) == 4:
                            new_row["DOB"] = f"{parts[2].zfill(2)}/{parts[1].zfill(2)}/{parts[0]}"
                        elif len(parts[2]) == 4:
                            new_row["DOB"] = f"{parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
                        else:
                            new_row["DOB"] = dob
                    else:
                        new_row["DOB"] = dob
                elif "-" in dob:
                    parts = dob.split("-")
                    if len(parts) == 3 and len(parts[0]) == 4:
                        new_row["DOB"] = f"{parts[2].zfill(2)}/{parts[1].zfill(2)}/{parts[0]}"
                    else:
                        new_row["DOB"] = dob
                else:
                    new_row["DOB"] = dob
            else:
                import datetime
                if isinstance(dob, datetime.datetime):
                    new_row["DOB"] = dob.strftime("%d/%m/%Y")
                else:
                    new_row["DOB"] = str(dob)
        except:
            new_row["DOB"] = str(dob)
    else:
        new_row["DOB"] = ""

    new_row["MRKS_REC_STATUS"] = row.get("MRKS_REC_STATUS", "")
    new_row["STREAM"] = row.get("STREAM", "")
    new_row["RROLL"] = row.get("RNO", "")
    new_row["REGN_NO"] = row.get("ENO", "")
    new_row["CNAME"] = row.get("NAME", "")
    new_row["FNAME"] = row.get("FNAME", "")
    new_row["MNAME"] = row.get("MNAME", "")
    new_row["GENDER"] = row.get("SEX", "")
    new_row["CASTE"] = row.get("CAST", "")
    new_row["RESULT"] = row.get("RESULT", "")

    grand_tot = str(row.get("GTOT", "")).strip()
    if "/" in grand_tot:
        parts = grand_tot.split("/")
        new_row["GRAND_TOT_MRKS"] = parts[0].strip()
        new_row["GRAND_TOT_MAX"] = parts[1].strip()
    else:
        new_row["GRAND_TOT_MRKS"] = grand_tot
        new_row["GRAND_TOT_MAX"] = row.get("TTOT", "")

    new_row["PERCENT"] = row.get("PER", "")
    new_row["ABC_ACCOUNT_ID"] = row.get("ABCID", "")

    new_row["YEAR"] = row.get("YEAR", "")
    new_row["MONTH"] = row.get("MONTH", "")
    new_row["SEM"] = row.get("SEM", "")
    new_row["EXAM_TYPE"] = row.get("CAT", "")
    new_row["TERM_TYPE"] = "Semester"

    subject_counter = 1
    theory_subjects = []
    practical_subjects = []
    subject_meta = {}

    # --- First loop: subjects ---
    for i in range(1, 20):
        sub_name = str(row.get(f"TIT{i}", "")).strip()
        sub_detail = str(row.get(f"SUB{i}", "")).strip()
        sub_code = str(row.get(f"COD{i}", "")).strip()

        if not sub_name and not sub_detail:
            continue

        sub_idx = subject_counter
        th_marks = row.get(f"EA{i}", "")
        ce_marks = row.get(f"IA{i}", "")
        total_max_marks = row.get(f"T{i}_MAX", "")

        # Check if T{i}_MAX exists and has a value
        use_total_max = (total_max_marks and str(total_max_marks).strip() not in ["", "nan", "None"])
        
        if use_total_max:
            calculated_total = pd.to_numeric(row.get(f"T{i}", ""), errors="coerce")
            new_row[f"SUB{sub_idx}_TH_MAX"] = ""
            new_row[f"SUB{sub_idx}_CE_MAX"] = ""
            new_row[f"SUB{sub_idx}_TH_MRKS"] = th_marks if th_marks not in ["", None] else ""
            new_row[f"SUB{sub_idx}_CE_MRKS"] = ce_marks if ce_marks not in ["", None] else ""
            try:
                max_marks_for_calculation = float(total_max_marks)
            except:
                max_marks_for_calculation = 100
        else:
            # Standard case with EA/IA
            try:
                th_val = float(th_marks) if th_marks not in ["", None, "AB"] else 0
                ce_val = float(ce_marks) if ce_marks not in ["", None, "AB"] else 0
                calculated_total = th_val + ce_val
            except:
                calculated_total = pd.to_numeric(row.get(f"T{i}", ""), errors="coerce")

            new_row[f"SUB{sub_idx}_TH_MAX"] = 70
            new_row[f"SUB{sub_idx}_CE_MAX"] = 30
            new_row[f"SUB{sub_idx}_TH_MRKS"] = th_marks
            new_row[f"SUB{sub_idx}_CE_MRKS"] = ce_marks
            max_marks_for_calculation = 100

        # Common subject fields
        new_row[f"SUB{sub_idx}NM"] = sub_detail
        new_row[f"SUB{sub_idx}"] = sub_code
        new_row[f"SUB{sub_idx}_PR_MAX"] = ""
        new_row[f"SUB{sub_idx}_PR_MRKS"] = ""
        new_row[f"SUB{sub_idx}_TOT"] = calculated_total
        new_row[f"SUB{sub_idx}_GRADE"] = ""
        new_row[f"SUB{sub_idx}_GRADE_POINTS"] = ""
        new_row[f"SUB{sub_idx}_CREDIT"] = row.get(f"CH{sub_idx}", "")
        new_row[f"SUB{sub_idx}_CREDIT_POINTS"] = ""
        new_row[f"SUB{sub_idx}_TOTAL_MAX"] = total_max_marks if use_total_max else ""

        theory_subjects.append((sub_idx, calculated_total, max_marks_for_calculation))
        subject_meta[sub_idx] = "theory"
        subject_counter += 1

        # --- Practical (if exists) ---
        prsub = row.get(f"PRSUB{i}", "")
        if pd.notna(prsub) and str(prsub).strip() != "":
            sub_idx = subject_counter
            pract_tot = str(row.get(f"P{i}", "")).strip()
            new_row[f"SUB{sub_idx}NM"] = str(prsub).strip()
            new_row[f"SUB{sub_idx}"] = str(row.get(f"PR{i}", "")).strip()
            
            pract_marks_raw = ""
            pract_max_raw = ""
            
            if "/" in pract_tot:
                parts = pract_tot.split("/")
                try:
                    pract_marks = pd.to_numeric(parts[0].strip(), errors="coerce")
                    pract_max = pd.to_numeric(parts[1].strip(), errors="coerce")
                    converted_marks = (pract_marks / pract_max) * 100
                    new_row[f"SUB{sub_idx}_PR_MRKS"] = parts[0].strip()
                    new_row[f"SUB{sub_idx}_PR_MAX"] = parts[1].strip()
                    new_row[f"SUB{sub_idx}_TOT"] = round(converted_marks, 2) if pd.notna(converted_marks) else ""
                    pract_marks_raw = pract_marks
                    pract_max_raw = pract_max
                except:
                    new_row[f"SUB{sub_idx}_PR_MRKS"] = parts[0].strip()
                    new_row[f"SUB{sub_idx}_PR_MAX"] = parts[1].strip()
                    new_row[f"SUB{sub_idx}_TOT"] = parts[0].strip()
            else:
                try:
                    pract_marks = pd.to_numeric(pract_tot, errors="coerce")
                    converted_marks = (pract_marks / 50) * 100
                    new_row[f"SUB{sub_idx}_PR_MRKS"] = pract_tot
                    new_row[f"SUB{sub_idx}_PR_MAX"] = 50
                    new_row[f"SUB{sub_idx}_TOT"] = round(converted_marks, 2) if pd.notna(converted_marks) else ""
                    pract_marks_raw = pract_marks
                    pract_max_raw = 50
                except:
                    new_row[f"SUB{sub_idx}_PR_MRKS"] = pract_tot
                    new_row[f"SUB{sub_idx}_PR_MAX"] = 50
                    new_row[f"SUB{sub_idx}_TOT"] = pract_tot

            new_row[f"SUB{sub_idx}_TH_MAX"] = ""
            new_row[f"SUB{sub_idx}_CE_MAX"] = ""
            new_row[f"SUB{sub_idx}_TH_MRKS"] = ""
            new_row[f"SUB{sub_idx}_CE_MRKS"] = ""
            new_row[f"SUB{sub_idx}_GRADE"] = ""
            new_row[f"SUB{sub_idx}_GRADE_POINTS"] = ""
            new_row[f"SUB{sub_idx}_CREDIT"] = row.get(f"CH{sub_idx}", "")
            new_row[f"SUB{sub_idx}_CREDIT_POINTS"] = ""
            
            # Store practical subject info for grace calculation
            if pd.notna(pract_marks_raw) and pd.notna(pract_max_raw):
                practical_subjects.append((sub_idx, pract_marks_raw, pract_max_raw))
            
            subject_meta[sub_idx] = "practical"
            subject_counter += 1

    # --- Due papers ---
    for i in range(1, 20):
        due_paper = row.get(f"DP{i}", None)
        if pd.notna(due_paper) and str(due_paper).strip().lower() not in ["", "nan", "none"]:
            sub_idx = subject_counter
            new_row[f"SUB{sub_idx}NM"] = "DUE OF PREVIOUS SEM"
            new_row[f"SUB{sub_idx}"] = str(due_paper).strip()
            new_row[f"SUB{sub_idx}_CREDIT"] = row.get(f"DCR{i}", "")
            due_total = pd.to_numeric(row.get(f"DPM{i}", ""), errors="coerce")
            new_row[f"SUB{sub_idx}_TOT"] = "" if pd.isna(due_total) else due_total
            new_row["REMARKS"] = row.get(f"DPR{i}", "")
            subject_meta[sub_idx] = "due"
            subject_counter += 1

    # --- Grace Marks calculation based on passing scheme ---
    total_theory_max = sum(max_marks for (_, _, max_marks) in theory_subjects)
    grace_limit = min(total_theory_max * 0.01, 6)

    # Find failed subjects based on passing scheme
    failed_subjects = []
    
    # Theory subjects (36% for both schemes)
    for (idx, tot_marks, max_marks) in theory_subjects:
        try:
            marks = float(tot_marks)
            percent = (marks / max_marks) * 100 if max_marks > 0 else 0
            if percent < 36:
                failed_subjects.append((idx, marks, max_marks, "theory"))
        except:
            pass
    
    # Practical subjects (different criteria based on scheme)
    practical_min = 40 if passing_scheme == "scheme1" else 36
    for (idx, tot_marks, max_marks) in practical_subjects:
        try:
            marks = float(tot_marks)
            percent = (marks / max_marks) * 100 if max_marks > 0 else 0
            if percent < practical_min:
                failed_subjects.append((idx, marks, max_marks, "practical"))
        except:
            pass

    # Calculate shortfall
    shortfall = 0
    for (_, marks, max_marks, sub_type) in failed_subjects:
        min_percent = 0.36 if sub_type == "theory" else (0.40 if passing_scheme == "scheme1" else 0.36)
        shortfall += max(0, (min_percent * max_marks) - marks)

    # Initialize grace for theory subjects
    for sub_idx in subject_meta:
        if subject_meta[sub_idx] == "theory":
            new_row[f"SUB{sub_idx}_GRACE"] = "G-0"

    # Distribute grace marks
    if shortfall <= grace_limit:
        for (idx, marks, max_marks, sub_type) in failed_subjects:
            min_percent = 0.36 if sub_type == "theory" else (0.40 if passing_scheme == "scheme1" else 0.36)
            needed = max(0, (min_percent * max_marks) - marks)
            if needed > 0 and grace_limit > 0:
                grace_given = min(needed, grace_limit)
                if sub_type == "theory":  # Only theory subjects get grace marks
                    new_row[f"SUB{idx}_GRACE"] = f"G-{int(round(grace_given))}"
                grace_limit -= grace_given

    # Calculate grades and points
    total_credits = 0
    total_credit_points = 0
    for sub_idx in subject_meta:
        marks = new_row.get(f"SUB{sub_idx}_TOT", "")
        grace_val = new_row.get(f"SUB{sub_idx}_GRACE", "")

        # Convert "G-<num>" back to numeric for calculations
        if isinstance(grace_val, str) and grace_val.startswith("G-"):
            try:
                grace_val = float(grace_val.replace("G-", ""))
            except:
                grace_val = 0
        else:
            grace_val = 0

        # Clean up grace display
        if grace_val > 0:
            new_row[f"SUB{sub_idx}_GRACE"] = f"G-{int(grace_val)}"
        else:
            new_row[f"SUB{sub_idx}_GRACE"] = ""

        is_practical = subject_meta[sub_idx] == "practical"

        # Update compute_grade_and_points calls to include total_max parameter
        grade, gp = compute_grade_and_points(
            marks,
            th_max=new_row.get(f"SUB{sub_idx}_TH_MAX", ""),
            ce_max=new_row.get(f"SUB{sub_idx}_CE_MAX", ""),
            pr_max=new_row.get(f"SUB{sub_idx}_PR_MAX", ""),
            total_max=new_row.get(f"SUB{sub_idx}_TOTAL_MAX", ""),
            grace=int(round(grace_val)),
            is_practical=is_practical,
            passing_scheme=passing_scheme
        )

        new_row[f"SUB{sub_idx}_GRADE"] = grade
        new_row[f"SUB{sub_idx}_GRADE_POINTS"] = gp

        try:
            credit = float(new_row.get(f"SUB{sub_idx}_CREDIT", 0))
        except:
            credit = 0

        credit_points = gp * credit
        new_row[f"SUB{sub_idx}_CREDIT_POINTS"] = credit_points
        total_credits += credit
        total_credit_points += credit_points

    # Calculate SGPA and overall result
    if total_credits > 0:
        new_row["TOT_CREDIT"] = total_credits
        new_row["TOT_CREDIT_POINTS"] = total_credit_points
        sgpa = total_credit_points / total_credits
        new_row["SGPA"] = round(sgpa, 2)
        
        # Overall result based on aggregate 40% criteria
        try:
            grand_tot_marks = float(new_row.get("GRAND_TOT_MRKS", 0))
            grand_tot_max = float(new_row.get("GRAND_TOT_MAX", 0))
            if grand_tot_max > 0:
                aggregate_percent = (grand_tot_marks / grand_tot_max) * 100
                if aggregate_percent >= 40 and sgpa >= 4.0:
                    new_row["RESULT"] = "PASS"
                else:
                    new_row["RESULT"] = "FAIL"
        except:
            pass
    else:
        new_row["TOT_CREDIT"] = 0
        new_row["TOT_CREDIT_POINTS"] = 0
        new_row["SGPA"] = 0.0

    return new_row

# --------------------------
# Scheme dictionary
# --------------------------
scheme_map = {
    "scheme1": [
        "B.A.", "B.Ed.", "B.Sc.", "B.A.-B.Ed.S", "B.COM", "B.Ed.(CD)", "B.ED.(G)",
        "B.Ed.-M.Ed.", "B.Sc.-B.Ed.", "BPES", "M.A. ARCHEOLOGY", "M.A.Education",
        "M.Ed.", "P.G. DIPLOMA IN GUIDANCE & COUNSELLING", "P.G. DIPLOMA IN LABOUR WELFARE"
    ],
    "scheme2": [
        "B.Sc.-AGRICULTURE", "B.Sc.-BIO/BCZ/SBS/CBZ", "B.Sc.-BIO-TECHNOLOGY",
        "B.Sc.-PCM", "B.Sc.-PMC", "B.Sc.-PMS", "DIPLOMA IN ARCHEOLOGY",
        "DIPLOMA IN HOTEL MANAGEMENT - HOUSEKEEPING", "M.A. JYOTIRVIGYAN", "M.A. MUSIC",
        "M.A. PHYSICAL EDUCATION", "M.A. PSYCHOLOGY", "M.A. SOCIOLOGY", "M.A. YOGA",
        "M.A.-ECONOMICS", "M.A.-ENGLISH", "M.A.-GEOGRAPHY", "M.A.-HINDI", "M.A.-HISTORY",
        "M.A.-POLITICAL SCIENCE", "M.A.-SANSKRIT", "M.COM. ACCOUNTING", "M.COM.-BUSINESS ADMINISTRATION",
        "M.PED.", "M.Sc. BioTechnology", "M.Sc. BOTANY", "M.Sc. CHEMISTRY", "M.Sc. ENVIRONMENTAL SCIENCE",
        "M.Sc. MATHS", "M.Sc. PHYSICS", "M.Sc. ZOOLOGY", "MASTER OF SOCIAL WORK",
        "P.G. DIPLOMA IN MENTAL HEALTH & COUNSELLING", "P.G. DIPLOMA IN POPULATION STUDIES"
    ]
}


# --------------------------
# API Endpoint
# --------------------------
@app.post("/transform/")
async def transform_marks(course: str = Form(...), file: UploadFile = File(...)):
    # Identify passing scheme based on course
    if course in scheme_map["scheme1"]:
        selected_scheme = "scheme1"
    elif course in scheme_map["scheme2"]:
        selected_scheme = "scheme2"
    else:
        return JSONResponse({"error": f"Course '{course}' not found in scheme mapping."}, status_code=400)

    # Check file
    if not file:
        return JSONResponse({"error": "No file uploaded"}, status_code=400)

    try:
        if file.filename and file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename and file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file)
        elif file.filename and file.filename.endswith(".xls"):
            df = pd.read_excel(file.file, engine="xlrd")
        else:
            return JSONResponse({"error": "Unsupported file format"}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"Error reading file: {str(e)}"}, status_code=500)

    # Process rows
    transformed = [transform_row(row, passing_scheme=selected_scheme) for _, row in df.iterrows()]
    df_out = pd.DataFrame(transformed)

    # Convert DataFrame to CSV
    output = io.StringIO()
    df_out.to_csv(output, index=False)
    output.seek(0)

    filename = f"transformed_marks_{selected_scheme}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
