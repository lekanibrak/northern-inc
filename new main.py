# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

app = FastAPI(
    title="The Northern Inc API",
    version="0.1.0",
    description="Backend skeleton for The Northern Inc logistics platform."
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# -----------------------------
# Mock Auth & User Models
# -----------------------------
class User(BaseModel):
    id: int
    full_name: str
    role: str  # "driver", "warehouse", "admin"


# In real app: validate token & fetch from DB
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # TODO: decode JWT, fetch user
    # For now: always return a mock driver
    return User(id=101, full_name="John Doe", role="driver")


# -----------------------------
# Auth Endpoints
# -----------------------------
class LoginRequest(BaseModel):
    phone: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: User


@app.post("/auth/login", response_model=LoginResponse)
def login(body: LoginRequest):
    # TODO: verify phone/password against DB
    mock_user = User(id=101, full_name="John Doe", role="driver")
    return LoginResponse(token="mock-token-123", user=mock_user)


@app.get("/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# -----------------------------
# Driver Dashboard & Status
# -----------------------------
class InboxPreviewItem(BaseModel):
    id: int
    subject: str
    created_at: datetime
    is_read: bool


class DriverStatus(BaseModel):
    code: str  # not_checked_in, checked_in, loading, route_activated
    color: str  # red, blue, yellow, green


class DriverDashboardResponse(BaseModel):
    today: date
    earnings_today: float
    weekly_total: float
    status: DriverStatus
    assigned_dock: Optional[int]
    next_route: Optional[dict]
    inbox_preview: List[InboxPreviewItem]


class DriverCheckInRequest(BaseModel):
    warehouse_id: int


class DriverCheckInResponse(BaseModel):
    status: str
    color: str


@app.get("/driver/dashboard", response_model=DriverDashboardResponse)
def driver_dashboard(current_user: User = Depends(get_current_user)):
    # TODO: query DB for real values
    return DriverDashboardResponse(
        today=date.today(),
        earnings_today=100.0,
        weekly_total=350.0,
        status=DriverStatus(code="checked_in", color="blue"),
        assigned_dock=None,
        next_route={"route_id": 501, "route_date": date.today(), "total_stops": 15},
        inbox_preview=[
            InboxPreviewItem(
                id=9001,
                subject="Dock 3 delayed by 10 min",
                created_at=datetime.utcnow(),
                is_read=False
            )
        ]
    )


@app.post("/driver/check-in", response_model=DriverCheckInResponse)
def driver_check_in(body: DriverCheckInRequest, current_user: User = Depends(get_current_user)):
    # TODO: create driver_status_history row & update dashboard state
    return DriverCheckInResponse(status="checked_in", color="blue")


# -----------------------------
# Drivers List (Admin/Warehouse)
# -----------------------------
class DriverListItem(BaseModel):
    driver_id: int
    driver_code: int
    name: str
    status: str
    status_color: str
    phone: Optional[str]


@app.get("/drivers", response_model=List[DriverListItem])
def list_drivers(status: Optional[str] = None, current_user: User = Depends(get_current_user)):
    # TODO: filter by status from DB
    return [
        DriverListItem(
            driver_id=20, driver_code=20, name="Sejal Ibrak",
            status="checked_in", status_color="blue", phone="+17050001111"
        ),
        DriverListItem(
            driver_id=7, driver_code=7, name="Mike Doe",
            status="not_checked_in", status_color="red", phone="+17050002222"
        )
    ]


# -----------------------------
# Warehouses & Docks
# -----------------------------
class Warehouse(BaseModel):
    id: int
    name: str
    city: str
    region: str


class Dock(BaseModel):
    id: int
    warehouse_id: int
    dock_number: int
    is_active: bool


@app.get("/warehouses", response_model=List[Warehouse])
def list_warehouses(current_user: User = Depends(get_current_user)):
    # TODO: fetch from warehouses table
    return [
        Warehouse(id=1, name="Sudbury WH1", city="Sudbury", region="ON"),
        Warehouse(id=2, name="North Bay WH2", city="North Bay", region="ON"),
    ]


@app.get("/warehouses/{warehouse_id}/docks", response_model=List[Dock])
def list_docks(warehouse_id: int, current_user: User = Depends(get_current_user)):
    # TODO: filter docks by warehouse
    return [
        Dock(id=1, warehouse_id=warehouse_id, dock_number=1, is_active=True),
        Dock(id=2, warehouse_id=warehouse_id, dock_number=2, is_active=True),
    ]


# -----------------------------
# Routes & Route Assignment
# -----------------------------
class AssignDockRequest(BaseModel):
    driver_id: int
    warehouse_id: int
    dock_id: int


class AssignDockResponse(BaseModel):
    route_id: int
    driver_id: int
    dock_id: int
    status: str


@app.post("/routes/assign-dock", response_model=AssignDockResponse)
def assign_dock(body: AssignDockRequest, current_user: User = Depends(get_current_user)):
    # TODO: create/find today's route & assign dock
    return AssignDockResponse(
        route_id=501,
        driver_id=body.driver_id,
        dock_id=body.dock_id,
        status="loading"
    )


class RouteSummary(BaseModel):
    id: int
    driver_id: int
    driver_name: str
    warehouse_id: int
    route_date: date
    status: str


@app.get("/routes", response_model=List[RouteSummary])
def list_routes(date_: Optional[date] = None, warehouse_id: Optional[int] = None,
                current_user: User = Depends(get_current_user)):
    # TODO: filter by date & warehouse
    return [
        RouteSummary(
            id=501, driver_id=20, driver_name="Sejal Ibrak",
            warehouse_id=1, route_date=date.today(), status="loading"
        )
    ]


@app.get("/routes/{route_id}", response_model=RouteSummary)
def get_route(route_id: int, current_user: User = Depends(get_current_user)):
    # TODO: fetch from DB
    return RouteSummary(
        id=route_id, driver_id=20, driver_name="Sejal Ibrak",
        warehouse_id=1, route_date=date.today(), status="active"
    )


# -----------------------------
# Route Stops & Parcels
# -----------------------------
class RouteStop(BaseModel):
    stop_id: int
    stop_number: int
    display_code: str
    customer_name: str
    customer_phone: str
    address: str
    parcel_id: int
    delivery_instructions: Optional[str]
    status: str


class RouteStopsResponse(BaseModel):
    route_id: int
    driver_code: int
    stops: List[RouteStop]


@app.get("/driver/routes/{route_id}/stops", response_model=RouteStopsResponse)
def get_route_stops(route_id: int, current_user: User = Depends(get_current_user)):
    # TODO: query route_stops, parcels, drivers
    return RouteStopsResponse(
        route_id=route_id,
        driver_code=20,
        stops=[
            RouteStop(
                stop_id=7001, stop_number=1, display_code="20-1",
                customer_name="John Walker", customer_phone="705-222-1111",
                address="22 Main St, North Bay", parcel_id=3001,
                delivery_instructions="Ring bell, leave at door",
                status="pending"
            )
        ]
    )


@app.get("/driver/stops/{stop_id}", response_model=RouteStop)
def get_stop(stop_id: int, current_user: User = Depends(get_current_user)):
    # TODO: fetch from DB
    return RouteStop(
        stop_id=stop_id, stop_number=1, display_code="20-1",
        customer_name="John Walker", customer_phone="705-222-1111",
        address="22 Main St, North Bay", parcel_id=3001,
        delivery_instructions="Ring bell, leave at door",
        status="pending"
    )


# -----------------------------
# Scanning (Universal Scan)
# -----------------------------
class ProofPayload(BaseModel):
    type: str  # "photo", "signature"
    url: str


class ScanRequest(BaseModel):
    barcode: str   # e.g. "20-1" or parcel code
    scan_type: str # vendor_intake, sorting, loading, delivery, return_customer, return_vendor
    warehouse_id: Optional[int] = None
    route_id: Optional[int] = None
    proof: Optional[ProofPayload] = None


class ScanResponse(BaseModel):
    parcel_id: int
    status: str
    message: str


@app.post("/scan", response_model=ScanResponse)
def scan_parcel(body: ScanRequest, current_user: User = Depends(get_current_user)):
    # TODO: lookup parcel by barcode/display_code, update status, insert scan_events
    return ScanResponse(
        parcel_id=3001,
        status="loaded" if body.scan_type == "loading" else "delivered",
        message=f"Parcel {body.barcode} scanned as {body.scan_type}."
    )


class ConfirmLoadingResponse(BaseModel):
    route_id: int
    status: str
    driver_status: str
    driver_color: str


@app.post("/routes/{route_id}/confirm-loading", response_model=ConfirmLoadingResponse)
def confirm_route_loading(route_id: int, current_user: User = Depends(get_current_user)):
    # TODO: validate all parcels scanned; update routes + driver_status_history
    return ConfirmLoadingResponse(
        route_id=route_id,
        status="active",
        driver_status="route_activated",
        driver_color="green"
    )


# -----------------------------
# Parcels – Returns
# -----------------------------
class ReturnRequest(BaseModel):
    reason: str


@app.post("/parcels/{parcel_id}/return-to-warehouse")
def return_to_warehouse(parcel_id: int, body: ReturnRequest,
                        current_user: User = Depends(get_current_user)):
    # TODO: update parcel status + scan_events
    return {"parcel_id": parcel_id, "status": "return_to_warehouse", "reason": body.reason}


@app.post("/parcels/{parcel_id}/return-to-vendor")
def return_to_vendor(parcel_id: int, body: ReturnRequest,
                     current_user: User = Depends(get_current_user)):
    # TODO: update parcel status + scan_events
    return {"parcel_id": parcel_id, "status": "return_to_vendor", "reason": body.reason}


# -----------------------------
# Messaging (Inbox)
# -----------------------------
class MessageCreate(BaseModel):
    recipient_user_id: int
    subject: str
    body: str


class Message(BaseModel):
    id: int
    sender_user_id: int
    recipient_user_id: int
    subject: str
    body: str
    is_read: bool
    created_at: datetime


@app.post("/messages", response_model=Message)
def send_message(body: MessageCreate, current_user: User = Depends(get_current_user)):
    # TODO: insert into messages table
    return Message(
        id=9001,
        sender_user_id=current_user.id,
        recipient_user_id=body.recipient_user_id,
        subject=body.subject,
        body=body.body,
        is_read=False,
        created_at=datetime.utcnow()
    )


@app.get("/driver/inbox", response_model=List[Message])
def driver_inbox(current_user: User = Depends(get_current_user)):
    # TODO: query messages for current_user.id
    return [
        Message(
            id=9001,
            sender_user_id=999,
            recipient_user_id=current_user.id,
            subject="Dock 3 delayed",
            body="Dock 3 will be ready in 10 minutes. Please wait in your vehicle.",
            is_read=False,
            created_at=datetime.utcnow()
        )
    ]


@app.post("/messages/{message_id}/read")
def mark_message_read(message_id: int, current_user: User = Depends(get_current_user)):
    # TODO: update messages set is_read = true
    return {"message_id": message_id, "status": "read"}


# -----------------------------
# Driver Payouts
# -----------------------------
class PayoutItem(BaseModel):
    payout_date: date
    route_id: int
    amount: float
    status: str


class PayoutSummary(BaseModel):
    driver_id: int
    total_amount: float
    items: List[PayoutItem]


@app.get("/driver/payouts", response_model=PayoutSummary)
def get_driver_payouts(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    current_user: User = Depends(get_current_user)
):
    # TODO: query driver_payouts for current_user.id
    return PayoutSummary(
        driver_id=20,
        total_amount=850.0,
        items=[
            PayoutItem(
                payout_date=date.today(),
                route_id=501,
                amount=100.0,
                status="approved"
            )
        ]
    )


if __name__ == "__main__":
    # Run directly: python3 "# main.py for The Northern inc.py"
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=800)
