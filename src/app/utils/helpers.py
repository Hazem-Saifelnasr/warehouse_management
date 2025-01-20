from src.app.models import (
    User, Department, Item, Project, Warehouse, Location, Stock, Permission, Invoice
)
from src.app.services import (
    user_service, department_service, item_service, project_service,
    warehouse_service, location_service, stock_service, permission_service, invoice_service
)

ENTITY_MODEL_MAPPING = {
    "user": User,
    "department": Department,
    "item": Item,
    "project": Project,
    "warehouse": Warehouse,
    "location": Location,
    "stock": Stock,
    "permission": Permission,
    "invoice": Invoice,
}

ENTITY_SERVICE_MAPPING = {
    "user": user_service.UserService,
    "department": department_service.DepartmentService,
    "item": item_service.ItemService,
    "project": project_service.ProjectService,
    "warehouse": warehouse_service.WarehouseService,
    "location": location_service.LocationService,
    "stock": stock_service.StockService,
    "permission": permission_service.PermissionService,
    "invoice": invoice_service.InvoiceService,
}
