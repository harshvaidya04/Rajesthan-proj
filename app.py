from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
from transformer import transform_dataframe, SCHEME_CONFIG, get_scheme_for_course

app = FastAPI(
    title="Marks Transformation API",
    description="API for transforming student marks based on different grading schemes",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Marks Transformation API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API information",
            "GET /schemes": "List all available schemes and their courses",
            "GET /courses": "List all available courses",
            "POST /transform": "Transform marks file"
        }
    }


@app.get("/schemes")
async def get_schemes():
    """Get all available schemes with their configurations."""
    schemes = {}
    for scheme_name, config in SCHEME_CONFIG.items():
        schemes[scheme_name] = {
            "theory_passing": config["theory_passing"],
            "practical_passing": config["practical_passing"],
            "aggregate_passing": config["aggregate_passing"],
            "courses": config["courses"],
            "total_courses": len(config["courses"])
        }
    return {"schemes": schemes}


@app.get("/courses")
async def get_courses():
    """Get all available courses grouped by scheme."""
    all_courses = []
    course_scheme_map = {}
    
    for scheme_name, config in SCHEME_CONFIG.items():
        for course in config["courses"]:
            all_courses.append(course)
            course_scheme_map[course] = {
                "scheme": scheme_name,
                "theory_passing": config["theory_passing"],
                "practical_passing": config["practical_passing"],
                "aggregate_passing": config["aggregate_passing"]
            }
    
    return {
        "total_courses": len(all_courses),
        "courses": sorted(all_courses),
        "course_scheme_mapping": course_scheme_map
    }


@app.post("/transform")
async def transform_marks(
    course: str = Form(..., description="Course name"),
    file: UploadFile = File(..., description="Input file (CSV, XLS, or XLSX)")
):
    """
    Transform marks file based on the course grading scheme.
    
    Parameters:
    - course: Name of the course (must match exactly with configured courses)
    - file: Upload file in CSV, XLS, or XLSX format
    
    Returns:
    - Transformed CSV file with grades, credits, and SGPA calculated
    """
    
    # Validate course
    try:
        scheme_name, scheme_config = get_scheme_for_course(course)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Validate file upload
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")
    
    # Read file based on extension
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file, engine='openpyxl')
        elif file.filename.endswith(".xls"):
            df = pd.read_excel(file.file, engine='xlrd')
        else:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload CSV, XLS, or XLSX file"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error reading file: {str(e)}"
        )
    
    # Validate dataframe
    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    
    # Transform the data
    try:
        df_transformed = transform_dataframe(df, course)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error transforming data: {str(e)}"
        )
    
    # Convert to CSV for download
    output = io.StringIO()
    df_transformed.to_csv(output, index=False)
    output.seek(0)
    
    # Generate filename
    safe_course_name = course.replace(" ", "_").replace(".", "").replace("/", "-")
    filename = f"transformed_{safe_course_name}_{scheme_name}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Scheme-Used": scheme_name,
            "X-Theory-Passing": str(scheme_config["theory_passing"]),
            "X-Practical-Passing": str(scheme_config["practical_passing"]),
            "X-Aggregate-Passing": str(scheme_config["aggregate_passing"])
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Marks Transformation API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)