import pandas as pd
from typing import Dict, Any, Tuple
import datetime

# --------------------------
# Configuration Section: Defines grading schemes for different courses
# Each scheme specifies:
# - theory_passing: Minimum percentage required to pass theory subjects
# - practical_passing: Minimum percentage required to pass practical subjects
# - aggregate_passing: Overall passing percentage required
# - courses: List of courses that follow this scheme
# --------------------------
SCHEME_CONFIG = {
    # Scheme 1: Standard passing criteria (36/40/40)
    "scheme1": {
        "theory_passing": 36,
        "practical_passing": 40,
        "aggregate_passing": 40,
        "courses": [
            "B.A.", "B.A.-B.Ed.S", "B.COM", "B.Ed.(CD)", 
            "B.ED.(G)", "B.Ed.-M.Ed.", "B.Sc.-B.Ed.", "BPES", "M.A. ARCHEOLOGY", 
            "M.Ed."
        ]
    },
    # Scheme 2: Modified practical criteria (36/36/40)
    "scheme2": {
        "theory_passing": 36,
        "practical_passing": 36,
        "aggregate_passing": 40,
        "courses": [
            "B.Sc.-AGRICULTURE", "B.Sc.-BIO/BCZ/SBS/CBZ", "B.Sc.-BIO-TECHNOLOGY",
            "B.Sc.-PCM", "B.Sc.-PMC", "B.Sc.-PMS", "DIPLOMA IN ARCHEOLOGY",
            "M.A. JYOTIRVIGYAN", 
            "M.A. MUSIC", "M.A. PHYSICAL EDUCATION", "M.A. PSYCHOLOGY", 
            "M.A. SOCIOLOGY", "M.A. YOGA", "M.A.-ECONOMICS", "M.A.-ENGLISH", 
            "M.A.-GEOGRAPHY", "M.A.-HINDI", "M.A.-HISTORY", "M.A.-POLITICAL SCIENCE", 
            "M.A.-SANSKRIT", "M.COM. ACCOUNTING", "M.COM.-BUSINESS ADMINISTRATION",
            "M.PED.", "M.Sc. BioTechnology", "M.Sc. BOTANY", "M.Sc. CHEMISTRY", 
            "M.Sc. ENVIRONMENTAL SCIENCE", "M.Sc. MATHS", "M.Sc. PHYSICS", 
            "M.Sc. ZOOLOGY", "MASTER OF SOCIAL WORK"
        ]
    },
    # Scheme 3: Higher passing criteria (40/50/50)
    "scheme3": {
        "theory_passing": 40,
        "practical_passing": 50,
        "aggregate_passing": 50,
        "courses": ["M.Sc. COMPUTER SCIENCE", "BCA", "MCA", "MHRM", "PGDCA", "B.Sc.-DATA SCIENCE"] 
    },
    # Scheme 4: Business courses (BBA/MBA) with standard passing criteria
    "scheme4": {
        "theory_passing": 40,
        "practical_passing": 40,
        "aggregate_passing": 50,
        "courses": ["BBA", "MBA"]  
    },
    # Scheme 5: Specialized BBA TT course
    "scheme5": {
        "theory_passing": 40,
        "practical_passing": 40,
        "aggregate_passing": 45,
        "courses": ["BBA TT"] 
    },
    # Scheme 6: Physiotherapy course (BPT) with higher passing marks
    "scheme6": {
        "theory_passing": 50,
        "practical_passing": 50,
        "aggregate_passing": 50,
        "courses": ["BPT"]
    },
    # Scheme 7: Agriculture MSc with highest passing criteria
    "scheme7": {
        "theory_passing": 60,
        "practical_passing": 60,
        "aggregate_passing": 60,
        "courses": ["M.Sc. Agriculture"] 
    },
    # Scheme 8: Specialized diploma in Criminal Laws and Forensic Science
    "scheme8": {
        "theory_passing": 40,
        "practical_passing": 40,
        "aggregate_passing": 48,
        "courses": ["P.G. DIPLOMA IN CRIMINAL LAWS AND FORENSIC SCIENCE"]
    }
}


def get_scheme_for_course(course: str) -> Tuple[str, Dict[str, Any]]:
    """
    Maps a course to its grading scheme configuration.
    
    Args:
        course (str): The name of the course
        
    Returns:
        Tuple[str, Dict[str, Any]]: Scheme name and its configuration
        
    Raises:
        ValueError: If course is not found in any scheme
    """
    for scheme_name, config in SCHEME_CONFIG.items():
        if course in config["courses"]:
            return scheme_name, config
    raise ValueError(f"Course '{course}' not found in any scheme configuration")


def compute_grade_and_points(percent_marks, is_practical=False, scheme_config=None):
    """
    Calculates grade letter and grade points based on percentage marks.
    
    Args:
        percent_marks: Percentage marks (0-100)
        is_practical: Whether this is a practical subject
        scheme_config: Grading scheme configuration to use
        
    Returns:
        Tuple[str, int]: Grade letter and grade points
    """
    if scheme_config is None:
        scheme_config = SCHEME_CONFIG["scheme1"]
    
    if str(percent_marks).strip().upper() == "AB":
        return "AB", 0

    try:
        percent = float(percent_marks)
    except:
        return "", 0

    min_passing = scheme_config["practical_passing"] if is_practical else scheme_config["theory_passing"]

    # Grade calculation (standard 10-point scale)
    if percent >= 91: return "O", 10
    elif percent >= 81: return "A+", 9
    elif percent >= 71: return "A", 8
    elif percent >= 61: return "B+", 7
    elif percent >= 51: return "B", 6
    elif percent >= 41: return "C+", 5
    elif percent >= min_passing: return "C", 4
    else: return "F", 0


def format_dob(dob) -> str:
    """
    Standardizes date of birth format to dd/mm/yyyy.
    Handles various input formats:
        - yyyy/mm/dd
        - dd/mm/yyyy
        - yyyy-mm-dd
        - datetime objects
    """
    if not dob or str(dob).strip() == "":
        return ""
    
    try:
        if isinstance(dob, str):
            if "/" in dob:
                parts = dob.split("/")
                if len(parts) == 3:
                    if len(parts[0]) == 4:  # yyyy/mm/dd
                        return f"{parts[2].zfill(2)}/{parts[1].zfill(2)}/{parts[0]}"
                    elif len(parts[2]) == 4:  # dd/mm/yyyy
                        return f"{parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
                    else:
                        return dob
                else:
                    return dob
            elif "-" in dob:
                parts = dob.split("-")
                if len(parts) == 3 and len(parts[0]) == 4:  # yyyy-mm-dd
                    return f"{parts[2].zfill(2)}/{parts[1].zfill(2)}/{parts[0]}"
                else:
                    return dob
            else:
                return dob
        else:
            if isinstance(dob, datetime.datetime):
                return dob.strftime("%d/%m/%Y")
            else:
                return str(dob)
    except:
        return str(dob)


def transform_row(row: Dict[str, Any], scheme_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms a single student record according to the specified grading scheme.
    
    Key operations:
    1. Maps basic student information
    2. Processes theory subjects with grace marks
    3. Processes practical subjects
    4. Handles project marks if present
    5. Calculates SGPA and final result
    
    Args:
        row: Dictionary containing raw student data
        scheme_config: Grading scheme configuration to apply
        
    Returns:
        Dict[str, Any]: Transformed student record with grades and results
    """
    new_row = {}

    # --- Direct mappings ---
    new_row["ORG_NAME"] = row.get("ORG_NAME", "")
    new_row["ACADEMIC_COURSE_ID"] = row.get("ACADEMIC_COURSE_ID", "")
    new_row["COURSE_NAME"] = row.get("COURSE_NAME", "")
    new_row["ADMISSION_YEAR"] = row.get("ADMISSION_YEAR", "")
    new_row["SESSION"] = row.get("SESSION", "")
    new_row["AADHAAR_NAME"] = row.get("AADHAAR_NAME", "")
    new_row["DOB"] = format_dob(row.get("DOB", ""))
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

    new_row["GRAND_TOT_MAX"] = row.get("GTOT_MAX", "")
    
    new_row["TOT_MRKS"] = row.get("GTOT", "")
    new_row["PERCENT"] = row.get("PER", "")
    new_row["ABC_ACCOUNT_ID"] = row.get("ABCID", "") or row.get("ABC_ACCOUNT_ID", "")
    new_row["YEAR"] = row.get("YEAR", "")
    new_row["MONTH"] = row.get("MONTH", "")
    new_row["SEM"] = row.get("SEM", "")
    new_row["EXAM_TYPE"] = row.get("CAT", "")

    subject_counter = 1
    theory_subjects = []
    practical_subjects = []
    subject_meta = {}

    # --- Process theory subjects ---
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

        new_row[f"SUB{sub_idx}NM"] = sub_detail
        new_row[f"SUB{sub_idx}"] = sub_code
        new_row[f"SUB{sub_idx}_PR_MAX"] = total_max_marks if use_total_max else ""
        new_row[f"SUB{sub_idx}_PR_MRKS"] = calculated_total if use_total_max else ""
        new_row[f"SUB{sub_idx}_TOT"] = calculated_total  # Store raw marks
        new_row[f"SUB{sub_idx}_PERCENT"] = (calculated_total / max_marks_for_calculation) * 100 if max_marks_for_calculation > 0 else 0  # Store percentage
        new_row[f"SUB{sub_idx}_GRADE"] = ""
        new_row[f"SUB{sub_idx}_GRADE_POINTS"] = ""
        new_row[f"SUB{sub_idx}_CREDIT"] = row.get(f"CH{sub_idx}", "")
        new_row[f"SUB{sub_idx}_CREDIT_POINTS"] = ""
        new_row[f"SUB{sub_idx}_TOTAL_MAX"] = total_max_marks if use_total_max else ""

        theory_subjects.append((sub_idx, calculated_total, max_marks_for_calculation))
        subject_meta[sub_idx] = "theory"
        subject_counter += 1

        # --- Process PRSUB (old format) practical subjects ---
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
                    new_row[f"SUB{sub_idx}_TOT"] = pract_marks  # Store raw marks
                    new_row[f"SUB{sub_idx}_PERCENT"] = round(converted_marks, 2) if pd.notna(converted_marks) else ""  # Store percentage
                    pract_marks_raw = pract_marks
                    pract_max_raw = pract_max
                except:
                    new_row[f"SUB{sub_idx}_PR_MRKS"] = parts[0].strip()
                    new_row[f"SUB{sub_idx}_PR_MAX"] = parts[1].strip()
                    new_row[f"SUB{sub_idx}_TOT"] = parts[0].strip()
                    new_row[f"SUB{sub_idx}_PERCENT"] = parts[0].strip()
            else:
                try:
                    pract_marks = pd.to_numeric(pract_tot, errors="coerce")
                    converted_marks = (pract_marks / 50) * 100
                    new_row[f"SUB{sub_idx}_PR_MRKS"] = pract_tot
                    new_row[f"SUB{sub_idx}_PR_MAX"] = 50
                    new_row[f"SUB{sub_idx}_TOT"] = pract_marks  # Store raw marks
                    new_row[f"SUB{sub_idx}_PERCENT"] = round(converted_marks, 2) if pd.notna(converted_marks) else ""  # Store percentage
                    pract_marks_raw = pract_marks
                    pract_max_raw = 50
                except:
                    new_row[f"SUB{sub_idx}_PR_MRKS"] = pract_tot
                    new_row[f"SUB{sub_idx}_PR_MAX"] = 50
                    new_row[f"SUB{sub_idx}_TOT"] = pract_tot
                    new_row[f"SUB{sub_idx}_PERCENT"] = pract_tot

            new_row[f"SUB{sub_idx}_TH_MAX"] = ""
            new_row[f"SUB{sub_idx}_CE_MAX"] = ""
            new_row[f"SUB{sub_idx}_TH_MRKS"] = ""
            new_row[f"SUB{sub_idx}_CE_MRKS"] = ""
            new_row[f"SUB{sub_idx}_GRADE"] = ""
            new_row[f"SUB{sub_idx}_GRADE_POINTS"] = ""
            new_row[f"SUB{sub_idx}_CREDIT"] = row.get(f"CH{sub_idx}", "")
            new_row[f"SUB{sub_idx}_CREDIT_POINTS"] = ""
            
            if pd.notna(pract_marks_raw) and pd.notna(pract_max_raw):
                practical_subjects.append((sub_idx, pract_marks_raw, pract_max_raw))
            
            subject_meta[sub_idx] = "practical"
            subject_counter += 1
    
    # --- Process CODP (new format) practical subjects - NO GRACE MARKS ---
    for i in range(1, 20):
        sub_code_p = str(row.get(f"CODP{i}", "")).strip()
        sub_detail_p = str(row.get(f"SUBP{i}", "")).strip()
        
        if not sub_code_p and not sub_detail_p:
            continue
        
        sub_idx = subject_counter
        
        # Check for EAP/IAP format with MAX columns
        eap_marks = row.get(f"EAP{i}", "")
        eap_max = row.get(f"EAP{i}_MAX", "")
        iap_marks = row.get(f"IAP{i}", "")
        iap_max = row.get(f"IAP{i}_MAX", "")
        p_total = row.get(f"P{i}", "")
        p_max = row.get(f"P{i}_MAX", "")
        
        # Check if we have the EAP/IAP format
        has_separate_max = any([
            str(eap_max).strip() not in ["", "nan", "None"],
            str(iap_max).strip() not in ["", "nan", "None"],
            str(p_max).strip() not in ["", "nan", "None"]
        ])
        
        if has_separate_max:
            # New format with separate MAX columns
            try:
                eap_val = float(eap_marks) if eap_marks not in ["", None, "AB"] else 0
                iap_val = float(iap_marks) if iap_marks not in ["", None, "AB"] else 0
                
                # Use P{i} if available, otherwise sum EAP + IAP
                if p_total and str(p_total).strip() not in ["", "nan", "None"]:
                    calculated_total_p = float(p_total)
                else:
                    calculated_total_p = eap_val + iap_val
                
                # Get max marks
                try:
                    total_max = float(p_max) if p_max not in ["", None] else 200
                except:
                    try:
                        eap_max_val = float(eap_max) if eap_max not in ["", None] else 0
                        iap_max_val = float(iap_max) if iap_max not in ["", None] else 0
                        total_max = eap_max_val + iap_max_val if (eap_max_val + iap_max_val) > 0 else 200
                    except:
                        total_max = 200
                
                # Convert to percentage for grading
                percent_marks = (calculated_total_p / total_max) * 100 if total_max > 0 else calculated_total_p
                
            except:
                calculated_total_p = pd.to_numeric(p_total, errors="coerce") if p_total else 0
                total_max = 200
                percent_marks = calculated_total_p
            
            # Store practical subject data
            new_row[f"SUB{sub_idx}NM"] = sub_detail_p
            new_row[f"SUB{sub_idx}"] = sub_code_p
            new_row[f"SUB{sub_idx}_TH_MAX"] = eap_max if str(eap_max).strip() not in ["", "nan", "None"] else ""
            new_row[f"SUB{sub_idx}_CE_MAX"] = iap_max if str(iap_max).strip() not in ["", "nan", "None"] else ""
            new_row[f"SUB{sub_idx}_TH_MRKS"] = eap_marks if str(eap_marks).strip() not in ["", "None"] else ""
            new_row[f"SUB{sub_idx}_CE_MRKS"] = iap_marks if str(iap_marks).strip() not in ["", "None"] else ""
            new_row[f"SUB{sub_idx}_PR_MAX"] = p_max if str(p_max).strip() not in ["", "nan", "None"] else total_max
            new_row[f"SUB{sub_idx}_PR_MRKS"] = calculated_total_p
            new_row[f"SUB{sub_idx}_TOT"] = calculated_total_p  # Store raw marks
            new_row[f"SUB{sub_idx}_PERCENT"] = percent_marks  # Store percentage
            new_row[f"SUB{sub_idx}_GRADE"] = ""
            new_row[f"SUB{sub_idx}_GRADE_POINTS"] = ""
            new_row[f"SUB{sub_idx}_CREDIT"] = row.get(f"CH{i+2}", "") if f"CH{i+2}" in row else row.get(f"CHP{i}", "")
            new_row[f"SUB{sub_idx}_CREDIT_POINTS"] = ""
            new_row[f"SUB{sub_idx}_TOTAL_MAX"] = total_max
            
            # Store for passing calculation
            try:
                if percent_marks > 0:
                    practical_subjects.append((sub_idx, percent_marks, 100))
            except:
                pass
            
            subject_meta[sub_idx] = "practical_with_max"
            subject_counter += 1
            
        else:
            # Old format without separate MAX columns (default 70/30 split)
            th_marks_p = row.get(f"EAP{i}", "")
            ce_marks_p = row.get(f"IAP{i}", "")
            total_p = row.get(f"TP{i}", "")
            
            try:
                th_val_p = float(th_marks_p) if th_marks_p not in ["", None, "AB"] else 0
                ce_val_p = float(ce_marks_p) if ce_marks_p not in ["", None, "AB"] else 0
                calculated_total_p = th_val_p + ce_val_p
            except:
                calculated_total_p = pd.to_numeric(total_p, errors="coerce")
            
            # Store practical subject data
            new_row[f"SUB{sub_idx}NM"] = sub_detail_p
            new_row[f"SUB{sub_idx}"] = sub_code_p
            new_row[f"SUB{sub_idx}_TH_MAX"] = 70
            new_row[f"SUB{sub_idx}_CE_MAX"] = 30
            new_row[f"SUB{sub_idx}_TH_MRKS"] = th_marks_p
            new_row[f"SUB{sub_idx}_CE_MRKS"] = ce_marks_p
            new_row[f"SUB{sub_idx}_PR_MAX"] = ""
            new_row[f"SUB{sub_idx}_PR_MRKS"] = ""
            new_row[f"SUB{sub_idx}_TOT"] = calculated_total_p  # Store raw marks
            new_row[f"SUB{sub_idx}_PERCENT"] = calculated_total_p  # For 100-mark subjects, percent = raw
            new_row[f"SUB{sub_idx}_GRADE"] = ""
            new_row[f"SUB{sub_idx}_GRADE_POINTS"] = ""
            new_row[f"SUB{sub_idx}_CREDIT"] = row.get(f"CHP{i}", "")
            new_row[f"SUB{sub_idx}_CREDIT_POINTS"] = ""
            new_row[f"SUB{sub_idx}_TOTAL_MAX"] = ""
            
            # Store for passing calculation
            try:
                pract_marks = float(calculated_total_p)
                practical_subjects.append((sub_idx, pract_marks, 100))
            except:
                pass
            
            subject_meta[sub_idx] = "practical_no_grace"
            subject_counter += 1

    # --- NEW: Process PROJECT subjects (IPROJ, EPROJ, PROJ, PROJMAX, CHPROJ) ---
    for i in range(1, 20):
        # Check for project-related columns with index
        proj_code = str(row.get(f"CODPROJ{i}", "")).strip()
        proj_name = str(row.get(f"SUBPROJ{i}", "")).strip()
        internal_marks = row.get(f"IPROJ{i}", "")
        external_marks = row.get(f"EPROJ{i}", "")
        total_proj_marks = row.get(f"PROJ{i}", "")
        
        # Handle PROJMAX with space (e.g., "PROJMAX 1")
        proj_max_marks = ""
        if f"PROJMAX{i}" in row:
            proj_max_marks = row.get(f"PROJMAX{i}", "")
        elif f"PROJMAX {i}" in row:
            proj_max_marks = row.get(f"PROJMAX {i}", "")
        
        project_credit = row.get(f"CHPROJ{i}", "")
        
        # Check if any project data exists
        if not any([proj_code, proj_name, str(internal_marks).strip(), str(external_marks).strip()]):
            continue
        
        sub_idx = subject_counter
        
        # Calculate total marks
        try:
            int_val = float(internal_marks) if internal_marks not in ["", None, "AB"] else 0
            ext_val = float(external_marks) if external_marks not in ["", None, "AB"] else 0
            calculated_total_proj = int_val + ext_val
            
            # If total_proj_marks is provided, use it instead
            if total_proj_marks and str(total_proj_marks).strip() not in ["", "nan", "None"]:
                calculated_total_proj = float(total_proj_marks)
        except:
            try:
                if total_proj_marks and str(total_proj_marks).strip() not in ["", "nan", "None"]:
                    calculated_total_proj = float(total_proj_marks)
                else:
                    calculated_total_proj = 0
            except:
                calculated_total_proj = 0
        
        # Determine max marks (default to 200 if not specified)
        try:
            proj_max = float(proj_max_marks) if proj_max_marks not in ["", None] else 200
        except:
            proj_max = 200
        
        # Convert to percentage for consistent grading
        try:
            if proj_max > 0:
                percent_marks = (calculated_total_proj / proj_max) * 100
            else:
                percent_marks = calculated_total_proj
        except:
            percent_marks = calculated_total_proj
        
        # Store project subject data
        new_row[f"SUB{sub_idx}NM"] = proj_name if proj_name else "PROJECT"
        new_row[f"SUB{sub_idx}"] = proj_code if proj_code else f"PROJ{i}"
        new_row[f"SUB{sub_idx}_TH_MAX"] = ""
        new_row[f"SUB{sub_idx}_CE_MAX"] = "150"
        new_row[f"SUB{sub_idx}_TH_MRKS"] = ""
        new_row[f"SUB{sub_idx}_CE_MRKS"] = external_marks if str(external_marks).strip() not in ["", "None"] else ""
        new_row[f"SUB{sub_idx}_PR_MAX"] = "50"
        new_row[f"SUB{sub_idx}_PR_MRKS"] = internal_marks if str(internal_marks).strip() not in ["", "None"] else ""
        new_row[f"SUB{sub_idx}_TOT"] = calculated_total_proj  # Store raw marks
        new_row[f"SUB{sub_idx}_PERCENT"] = percent_marks  # Store percentage for grade calculation
        new_row[f"SUB{sub_idx}_GRADE"] = ""
        new_row[f"SUB{sub_idx}_GRADE_POINTS"] = ""
        new_row[f"SUB{sub_idx}_CREDIT"] = project_credit
        new_row[f"SUB{sub_idx}_CREDIT_POINTS"] = ""
        new_row[f"SUB{sub_idx}_TOTAL_MAX"] = proj_max
        
        # Store for passing calculation - treat as practical
        try:
            if calculated_total_proj > 0 and proj_max > 0:
                practical_subjects.append((sub_idx, percent_marks, 100))
        except:
            pass
        
        subject_meta[sub_idx] = "project"
        subject_counter += 1

    # --- Process due papers ---
    for i in range(1, 20):
        due_paper = row.get(f"DP{i}", None)
        if pd.notna(due_paper) and str(due_paper).strip().lower() not in ["", "nan", "none"]:
            sub_idx = subject_counter
            new_row[f"SUB{sub_idx}NM"] = "DUE OF PREVIOUS SEM"
            new_row[f"SUB{sub_idx}"] = str(due_paper).strip()
            new_row[f"SUB{sub_idx}_CREDIT"] = row.get(f"DCR{i}", "")
            due_total = pd.to_numeric(row.get(f"DPM{i}", ""), errors="coerce")
            new_row[f"SUB{sub_idx}_TOT"] = "" if pd.isna(due_total) else due_total
            new_row[f"SUB{sub_idx}_PERCENT"] = "" if pd.isna(due_total) else due_total
            new_row["REMARKS"] = row.get(f"DPR{i}", "")
            subject_meta[sub_idx] = "due"
            subject_counter += 1

    # --- Grace marks calculation ---
    total_theory_max = sum(max_marks for (_, _, max_marks) in theory_subjects)
    grace_limit = min(total_theory_max * 0.01, 6)

    failed_subjects = []
    
    # Check theory subjects
    theory_passing_percent = scheme_config["theory_passing"]
    for (idx, tot_marks, max_marks) in theory_subjects:
        try:
            marks = float(tot_marks)
            percent = (marks / max_marks) * 100 if max_marks > 0 else 0
            if percent < theory_passing_percent:
                failed_subjects.append((idx, marks, max_marks, "theory"))
        except:
            pass
    
    # Calculate shortfall
    shortfall = 0
    for (_, marks, max_marks, sub_type) in failed_subjects:
        min_percent = (theory_passing_percent / 100 if sub_type == "theory" 
                      else "")
        shortfall += max(0, (min_percent * max_marks) - marks)

    # Initialize grace for theory subjects only
    for sub_idx in subject_meta:
        if subject_meta[sub_idx] == "theory":
            new_row[f"SUB{sub_idx}_GRACE"] = "G-0"

    #  --- New condition: Check if grace should be allowed ---
    try:
        grand_total_maximum = float(row.get("GTOT_MAX", 0)) # Grand Total Marks (Example: 600)   
        # row.get("GTOT_MAX", "")
        grand_total_marks: float = row.get("GTOT", "") # student’s grand total obtained marks (Example: 200)            
        aggregate_passing_percentage = scheme_config["aggregate_passing"]    # passing aggregate threshold (Example: 40)

        if (grand_total_maximum > 0):
            percent = (grand_total_marks / grand_total_maximum) * 100
            print(f"DEBUG_GRACE_PERCENT => Aggregate%={percent:.2f}")
            # Grace allowed only if student is >= aggregate passing percentage
            allow_grace: bool = percent >= aggregate_passing_percentage
            print("Allow Grace", allow_grace)
        else:
            allow_grace: bool = True

        print(
            f"DEBUG_GRACE_CONDITION => GTOT={grand_total_marks}, "
            f"GRAND_TOT_MAX={grand_total_maximum}, Aggregate%={percent:.2f}, "
            f"Passing%={aggregate_passing_percentage}, AllowGrace={allow_grace}",
            flush=True
        )

    # except:
    #     allow_grace = True
    except Exception as e:
        print(f"Error while checking grace condition: {e}", flush=True)
        allow_grace = True  # fallback

    
    print("Final Allow Grace ----------", allow_grace, flush=True)
    # Distribute grace marks (only to theory subjects)
    if allow_grace and shortfall <= grace_limit:
        for (idx, marks, max_marks, sub_type) in failed_subjects:
            # Skip if this is a practical_no_grace, practical, practical_with_max, or project subject
            if subject_meta.get(idx) in ["practical_no_grace", "practical", "practical_with_max", "project"]:
                continue
                
            min_percent = theory_passing_percent / 100
            needed = max(0, (min_percent * max_marks) - marks)
            if needed > 0 and grace_limit > 0:
                grace_given = min(needed, grace_limit)
                new_row[f"SUB{idx}_GRACE"] = f"G-{int(round(grace_given))}"
                grace_limit -= grace_given

    # --- Calculate grades and points using PERCENT field ---
    total_credits = 0
    total_credit_points = 0
    
    for sub_idx in subject_meta:
        # Use the PERCENT field for grade calculation
        percent_marks = new_row.get(f"SUB{sub_idx}_PERCENT", "")
        grace_val = new_row.get(f"SUB{sub_idx}_GRACE", "")

        if isinstance(grace_val, str) and grace_val.startswith("G-"):
            try:
                grace_val = float(grace_val.replace("G-", ""))
            except:
                grace_val = 0
        else:
            grace_val = 0

        if grace_val > 0:
            new_row[f"SUB{sub_idx}_GRACE"] = f"G-{int(grace_val)}"
        else:
            new_row[f"SUB{sub_idx}_GRACE"] = ""

        # For theory subjects, add grace to percentage
        if subject_meta[sub_idx] == "theory" and grace_val > 0:
            try:
                # Calculate grace percentage based on max marks
                th_max = float(new_row.get(f"SUB{sub_idx}_TH_MAX", 100))
                ce_max = float(new_row.get(f"SUB{sub_idx}_CE_MAX", 0))
                total_max = th_max + ce_max if ce_max > 0 else 100
                grace_percent = (grace_val / total_max) * 100
                percent_marks = float(percent_marks) + grace_percent
            except:
                pass

        # Treat projects and practicals with max as practicals for grading
        is_practical = subject_meta[sub_idx] in ["practical", "practical_with_max", "project"]

        grade, gp = compute_grade_and_points(
            percent_marks,
            is_practical=is_practical,
            scheme_config=scheme_config
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

    # --- Calculate SGPA and result ---
    if total_credits > 0:
        new_row["TOT_CREDIT"] = total_credits
        new_row["TOT_CREDIT_POINTS"] = total_credit_points
        sgpa = total_credit_points / total_credits
        new_row["SGPA"] = round(sgpa, 2)
        
        # Overall result based on aggregate passing criteria
        try:
            grand_tot_marks = float(new_row.get("GRAND_TOT_MRKS", 0))
            grand_tot_max = float(new_row.get("GRAND_TOT_MAX", 0))
            aggregate_passing_percent = scheme_config["aggregate_passing"]
            
            if grand_tot_max > 0:
                percent = (grand_tot_marks / grand_tot_max) * 100
                if percent >= aggregate_passing_percent and sgpa >= 4.0:
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


def transform_dataframe(df: pd.DataFrame, course: str) -> pd.DataFrame:
    """
    Processes entire dataset of student records.
    
    Args:
        df: DataFrame containing raw student records
        course: Course name to determine grading scheme
        
    Returns:
        pd.DataFrame: Transformed records with computed grades
    """
    scheme_name, scheme_config = get_scheme_for_course(course)
    print(f"Using {scheme_name} for course: {course}")
    print(f"Configuration: Theory={scheme_config['theory_passing']}%, "
          f"Practical={scheme_config['practical_passing']}%, "
          f"Aggregate={scheme_config['aggregate_passing']}%")
    
    transformed = [transform_row(row.to_dict(), scheme_config) for _, row in df.iterrows()]
    return pd.DataFrame(transformed)


# --------------------------
# Local Testing Configuration
# --------------------------
if __name__ == "__main__":
    """
    Command-line interface for local testing.
    Configure input/output paths and course name here.
    """
    # ========================================
    # CONFIGURATION - Update these values
    # ========================================
    INPUT_FILE = "MSC CS/MSC2SK5.csv"  # Path to your input file
    COURSE_NAME = "M.Sc. COMPUTER SCIENCE"       # Course name
    OUTPUT_FILE = "MSC CS/MSC2SK5_op.csv"  # Path for output file
    # ========================================
    
    print(f"Processing file: {INPUT_FILE}")
    print(f"Course: {COURSE_NAME}")
    
    try:
        # Read input file
        if INPUT_FILE.endswith('.csv'):
            df = pd.read_csv(INPUT_FILE)
        elif INPUT_FILE.endswith('.xlsx'):
            df = pd.read_excel(INPUT_FILE)
        elif INPUT_FILE.endswith('.xls'):
            df = pd.read_excel(INPUT_FILE, engine='xlrd')
        else:
            print("Unsupported file format. Use .csv, .xlsx, or .xls")
            exit(1)
        
        print(f"File loaded successfully. Total rows: {len(df)}")
        
        # Transform
        df_transformed = transform_dataframe(df, COURSE_NAME)
        
        # Save output
        df_transformed.to_csv(OUTPUT_FILE, index=False)
        
        print(f"\n{'='*50}")
        print(f"✓ Transformation complete!")
        print(f"✓ Output saved to: {OUTPUT_FILE}")
        print(f"✓ Total rows processed: {len(df_transformed)}")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"\n{'='*50}")
        print(f"✗ Error: {str(e)}")
        print(f"{'='*50}")
        import traceback
        traceback.print_exc()
        exit(1)