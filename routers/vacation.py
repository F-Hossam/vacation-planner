from datetime import date
import os
from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from starlette import status
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
import models
import copy
import re
from database import engine, SessionLocal
from .auth import get_current_user, verify_password, get_password_hash
from chains.agent import GenerateAIResponse
from features.pdf_generator import PdfGenerator
from tempfile import NamedTemporaryFile


router = APIRouter(
    prefix= "/vacation",
    tags=["vacation"]
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

aiRequest: GenerateAIResponse = None
response: dict = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def format_itinerary(itinerary):
    x_dict = {}

    x_list = itinerary.split("Day")
    x_list.remove("")

    for i in range(len(x_list)):
        x_dict[f"Day {i+1}"] = {
            "Morning":re.findall("Morning:?\s*([\s\S]*?)(?=\s*Afternoon|\Z)", x_list[i]),
            "Afternoon":re.findall("Afternoon:?\s*([\s\S]*?)(?=\s*Evening|\Z)", x_list[i]),
            "Evening":re.findall("Evening:?\s*([\s\S]*?)$", x_list[i])
            }
        
    return x_dict

def format_budget_breakdown(text: str):
    pattern = r'([^:]+:.*?\$\d+(?:\.\d+)?(?:\s*-\s*\$\d+)?)'
    expenses = re.findall(pattern, text, re.DOTALL)
    
    return expenses


#API endpoints
@router.get("/")
async def vacation_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    vacations = db.query(models.Vacations).filter(models.Vacations.user_id == user.get("id")).all()

    return templates.TemplateResponse("home.html", {"request": request, "user": user, "vacations": vacations})


@router.get("/open-vacation/{vacation_id}")
async def open_vacation(vacation_id: int, request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    vacation_model = db.query(models.Vacations).filter(models.Vacations.id == vacation_id,
                                                       models.Vacations.user_id == user.get("id")).first()
    if vacation_model is None:
        return templates.TemplateResponse("page-404.html", {"request": request, "user": user})
    
    response_dict = {
        "vacation_id": vacation_model.id,
        "city_of_residence": vacation_model.city_of_residence,
        "destination": vacation_model.destination,
        "itinerary": format_itinerary(vacation_model.iternary),
        "budget_breakdown": format_budget_breakdown(vacation_model.budget_breakdown),
        "total_estimated_cost": vacation_model.total_estimated_cost,
        "travel_dates": vacation_model.travel_dates}
    
    return templates.TemplateResponse("open-vacation.html", {"request": request, "user": user, "response_dict": response_dict})


@router.get("/download-pdf/{vacation_id}")
async def download_plan_pdf(request: Request, vacation_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    vacation_model = db.query(models.Vacations).filter(models.Vacations.id == vacation_id,
                                                       models.Vacations.user_id == user.get("id")).first()

    if vacation_model is None:
        return templates.TemplateResponse("page-404.html", {"request": request, "user": user})
    
    logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "planner", "images", "logo.png")
    regular_font = os.path.join(os.path.dirname(__file__), "..", "static", "planner", "fonts", "Poppins-Regular.ttf")
    bold_font = os.path.join(os.path.dirname(__file__), "..", "static", "planner", "fonts", "Poppins-Bold.ttf")
    pdf_file = PdfGenerator(vacation_model.destination,format_itinerary(vacation_model.iternary),
                            format_budget_breakdown(vacation_model.budget_breakdown),vacation_model.travel_dates,
                            vacation_model.total_estimated_cost,vacation_model.city_of_residence,logo_path,regular_font,bold_font)
    document = pdf_file.generate_pdf()
    
    return FileResponse(document)
    

@router.get("/create-vacation", response_class= HTMLResponse)
async def create_vacation_page(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("new-vacation.html", {"request": request, "user": user})


@router.get("/settings", response_class= HTMLResponse)
async def get_user_settings(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("settings.html", {"request": request, "user": user})


@router.post("/settings", response_class= HTMLResponse)
async def change_password(request: Request, email: str = Form(...), oldpassword: str = Form(...),
                          newpassword: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    user_model = db.query(models.Users).filter(models.Users.username == email).first()
    if user_model is None or user_model.username != user.get("username") or not verify_password(oldpassword, user_model.hashed_password):
        msg = "Invalid Request"
        return templates.TemplateResponse("settings.html", {"request": request, "user": user, "msg": msg})
    
    user_model.hashed_password = get_password_hash(newpassword)
    db.add(user_model)
    db.commit()

    msg = "Password Changed Successfully"
    return templates.TemplateResponse("settings.html", {"request": request, "user": user, "msg": msg})


@router.post("/create-vacation", response_class= HTMLResponse)
async def create_vacation(request: Request, domicile: str = Form(...), destination: str = Form(...), departuretime: date = Form(...),
                          budget: float = Form(...), numdays: int = Form(...), hobbies: str = Form(...)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    hobbies = hobbies.strip().split(",")[:-1]

    global aiRequest
    aiRequest = GenerateAIResponse(destination, departuretime, numdays, hobbies, budget, domicile)
    
    global response
    response = await aiRequest.generate_response()

    response_dict = copy.deepcopy(response)
    response_dict['itinerary'] = format_itinerary(response_dict['itinerary'])
    response_dict['budget_breakdown'] = format_budget_breakdown(response_dict["budget_breakdown"])

    return templates.TemplateResponse("agent-response.html", {"request": request, "user": user, "response_dict": response_dict})


@router.get("/low-options", response_class= HTMLResponse)
async def get_low_options(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    global response
    response = await aiRequest.generate_other_options("give me low cost options. The budget has been decreased by $100.")

    response_dict = copy.deepcopy(response)
    response_dict['itinerary'] = format_itinerary(response_dict['itinerary'])
    response_dict['budget_breakdown'] = format_budget_breakdown(response_dict["budget_breakdown"])

    return templates.TemplateResponse("agent-response.html", {"request": request, "user": user, "response_dict": response_dict})


@router.get("/standard-options", response_class= HTMLResponse)
async def get_standard_options(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    global response
    response = await aiRequest.generate_other_options("give me mid-range cost options. The budget has been increased by $100.")

    response_dict = copy.deepcopy(response)
    response_dict['itinerary'] = format_itinerary(response_dict['itinerary'])
    response_dict['budget_breakdown'] = format_budget_breakdown(response_dict["budget_breakdown"])

    return templates.TemplateResponse("agent-response.html", {"request": request, "user": user, "response_dict": response_dict})


@router.get("/expensive-options", response_class= HTMLResponse)
async def get_expensive_options(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    global response
    response = await aiRequest.generate_other_options("give me expensive cost options. The budget has been increased by $200.")

    response_dict = copy.deepcopy(response)
    response_dict['itinerary'] = format_itinerary(response_dict['itinerary'])
    response_dict['budget_breakdown'] = format_budget_breakdown(response_dict["budget_breakdown"])

    return templates.TemplateResponse("agent-response.html", {"request": request, "user": user, "response_dict": response_dict})


@router.get("/good", response_class= HTMLResponse)
async def validate_response(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    vacation_model = models.Vacations(
        city_of_residence = aiRequest.city_of_residence,
        destination = response['destination'],
        iternary = response['itinerary'],
        budget_breakdown = response['budget_breakdown'],
        total_estimated_cost = response['cost_range'],
        user_id = user.get("id"),
        travel_dates = response['travel_dates']
    )
    db.add(vacation_model)
    db.flush()
    vacation_id = vacation_model.id
    db.commit()

    return RedirectResponse(url=f"/vacation/open-vacation/{vacation_id}", status_code=status.HTTP_302_FOUND)


@router.get("/give-up", response_class= HTMLResponse)
async def give_up_response(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url="/vacation/create-vacation", status_code=status.HTTP_302_FOUND)


@router.get("/again", response_class= HTMLResponse)
async def get_another_response(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    global response
    response = await aiRequest.generate_response()

    response_dict = copy.deepcopy(response)
    response_dict['itinerary'] = format_itinerary(response_dict['itinerary'])
    response_dict['budget_breakdown'] = format_budget_breakdown(response_dict["budget_breakdown"])

    return templates.TemplateResponse("agent-response.html", {"request": request, "user": user, "response_dict": response_dict})
