# Warehouse Inventory Management System

This Warehouse Inventory Management System is a backend system built with **FastAPI**. It provides robust APIs for
managing users, permissions, items, warehouses, locations, projects, and reports. The system uses **PostgreSQL** for
data storage and follows best practices such as role-based access control (RBAC), JWT authentication, and modular
architecture.

---

## Features

- **User Management**: Admins can create, update, and delete users. Users can log in and update their details.
- **Role-Based Access Control**: Permissions can be assigned for projects and warehouses with read, write, and delete
  access.
- **Inventory Management**: Manage items, including CRUD operations, and track inventory by location or warehouse.
- **Warehouse Management**: Organize inventory across multiple warehouses.
- **Location Management**: Track items and projects across geographical locations.
- **Reports**: Export inventory data and generate reports for stock summaries.
- **Authentication**: Secure JWT-based authentication.

---

## API Endpoints

### **1. User Management**

| **Endpoint**                   | **Method** | **Description**                             | **Access**      |
|--------------------------------|------------|---------------------------------------------|-----------------|
| `/users/create`                | `POST`     | Create a new user                           | Admin           |
| `/users/login`                 | `POST`     | Log in a user and return a JWT token        | Public          |
| `/users/{user_id}`             | `GET`      | Get details of a user by ID                 | Admin           |
| `/users/{user_id}`             | `PUT`      | Update user details                         | Admin/User      |
| `/users/{user_id}`             | `DELETE`   | Delete a user by ID                         | Admin           |

---

### **2. Permission Management**

| **Endpoint**                   | **Method** | **Description**                             | **Access**      |
|--------------------------------|------------|---------------------------------------------|-----------------|
| `/permissions`                 | `POST`     | Assign a permission to a user               | Admin           |
| `/permissions/{permission_id}` | `DELETE`   | Revoke a permission by its ID               | Admin           |
| `/permissions/user/{user_id}`  | `GET`      | Get all permissions assigned to a user      | Admin/User      |

---

### **3. Item Management**

| **Endpoint**                      | **Method** | **Description**                       | **Access** |
|-----------------------------------|------------|---------------------------------------|------------|
| `/items`                          | `POST`     | Create a new item                     | Admin      |
| `/items/{item_id}`                | `GET`      | Get details of an item by ID          | Admin/User |
| `/items/{item_id}`                | `PUT`      | Update an item’s details              | Admin      |
| `/items/{item_id}`                | `DELETE`   | Delete an item                        | Admin      |
| `/items/location/{location_id}`   | `GET`      | Get all items in a specific location  | Admin/User |
| `/items/warehouse/{warehouse_id}` | `GET`      | Get all items in a specific warehouse | Admin/User |
| `/items/project/{project_id}`     | `GET`      | Get all items in a specific project   | Admin/User |
| `/items`                          | `GET`      | List all items	                       | Admin/User |

---

### **4. Warehouse Management**

| **Endpoint**                   | **Method** | **Description**                             | **Access**      |
|--------------------------------|------------|---------------------------------------------|-----------------|
| `/warehouses`                  | `POST`     | Create a new warehouse                      | Admin           |
| `/warehouses/{warehouse_id}`   | `GET`      | Get details of a warehouse by ID            | Admin/User      |
| `/warehouses/{warehouse_id}`   | `PUT`      | Update warehouse details                    | Admin           |
| `/warehouses/{warehouse_id}`   | `DELETE`   | Delete a warehouse                          | Admin           |
| `/warehouses`                  | `GET`      | List all warehouses                         | Admin/User      |

---

### **5. Location Management**

| **Endpoint**                   | **Method** | **Description**                             | **Access**      |
|--------------------------------|------------|---------------------------------------------|-----------------|
| `/locations`                   | `POST`     | Create a new location                       | Admin           |
| `/locations/{location_id}`     | `GET`      | Get details of a location by ID             | Admin/User      |
| `/locations/{location_id}`     | `PUT`      | Update location details                     | Admin           |
| `/locations/{location_id}`     | `DELETE`   | Delete a location                           | Admin           |
| `/locations`                   | `GET`      | List all locations                          | Admin/User      |

---

### **6. Project Management**

| **Endpoint**                   | **Method** | **Description**                             | **Access**      |
|--------------------------------|------------|---------------------------------------------|-----------------|
| `/projects`                    | `POST`     | Create a new project                        | Admin           |
| `/projects/{project_id}`       | `GET`      | Get details of a project by ID              | Admin/User      |
| `/projects/{project_id}`       | `PUT`      | Update project details                      | Admin           |
| `/projects/{project_id}`       | `DELETE`   | Delete a project                            | Admin           |
| `/projects`                    | `GET`      | List all projects                           | Admin/User      |

---

### **7. Reports**

| **Endpoint**                        | **Method** | **Description**                       | **Access** |
|-------------------------------------|------------|---------------------------------------|------------|
| `/reports/items/export`             | `GET`      | Export all items to an Excel/CSV file | Admin      |
| `/reports/warehouse/{warehouse_id}` | `GET`      | Generate stock report for a warehouse | Admin/User |
| `/reports/location/{location_id}`   | `GET`      | Generate stock report for a location  | Admin/User |
| `/reports/project/{project_id}`     | `GET`      | Generate stock report for a project   | Admin/User |

---

## API Documentation

### 1. User Management

#### 1.1 Create User

**Endpoint:** `POST /users/create`

**Request:**

```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "securepassword"
}
```
**Response:**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "testuser@example.com"
}
```

#### 1.2 Login

**Endpoint:** `POST /users/login`

**Example:** `POST /users/login?username=testuser&password=securepassword`

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}
```

#### 1.3 Get User

**Endpoint:** `GET /users/{user_id}`

**Example:** `GET /users/1`

**Response:**

```json
{
  "id": 1,
  "username": "testuser",
  "email": "testuser@example.com"
}
```

#### 1.4 Update User

**Endpoint:** `PUT /users/{user_id}`

**Example:** `PUT /users/1`

**Request:**

```json
{
  "username": "testuser",
  "email": "updateduser@example.com"
}
```

**Response:**

```json
{
  "id": 1,
  "username": "testuser",
  "email": "updateduser@example.com"
}
```

#### 1.5 Delete User

**Endpoint:** `DELETE /users/{user_id}`

**Example:** `DELETE /users/1`

**Response:**

```json
{
  "detail": "User deleted successfully"
}
```

---

### 2. Permission Management

#### 2.1 Assign Permission

**Endpoint:** `POST /permissions`

**Request:**
```json
{
  "user_id": 1,
  "entity": "warehouse",
  "entity_id": 10,
  "access_type": "read"
}
```
**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "entity": "warehouse",
  "entity_id": 10,
  "access_type": "read"
}
```

#### 2.2 Revoke Permission

**Endpoint:** `DELETE /permissions/{permission_id}`

**Example:** `DELETE /permissions/1`

**Response:**
```json
{
  "detail": "Permission revoked successfully"
}
```

#### 2.3 Get Permissions for User

**Endpoint:** `GET /permissions/user/{user_id}`

**Example:** `GET /permissions/user/1`

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "entity": "warehouse",
    "entity_id": 10,
    "access_type": "read"
  },
  {
    "id": 2,
    "user_id": 1,
    "entity": "project",
    "entity_id": 5,
    "access_type": "write"
  }
]
```

---

### 3. Item Management

#### 3.1 Create Item

**Endpoint:** `POST /items`

**Request:**
- warehouse_ids: Optional list[int]
- project_ids: Optional list[int]

```json
{
  "item_code": "ABC123",
  "description": "Sample Item",
  "photo": "/images/sample.png",
  "total_qty": 100,
  "location_id": 2,
  "warehouse_ids": [1, 2],
  "project_ids": [3]
}
```

**Response:**
```json
{
  "id": 1,
  "item_code": "ABC123",
  "description": "Sample Item",
  "photo": "/images/sample.png",
  "total_qty": 100,
  "location_id": 2
}
```

#### 3.2 Get Item

**Endpoint:** `GET /items/{item_id}`

**Example:** `GET /items/1`

**Response:**

```json
{
  "id": 1,
  "item_code": "ABC123",
  "description": "Sample Item",
  "photo": "/images/sample.png",
  "total_qty": 100,
  "location_id": 2
}
```

#### 3.3 Update Item

**Endpoint:** `PUT /items/{item_id}`

**Example:** `PUT /items/1`

**Request:**
- warehouse_ids: Optional list[int] 
- project_ids: Optional list[int]

```json
{
  "item_code": "ABC123",
  "description": "Sample Item",
  "photo": "/images/sample.png",
  "total_qty": 100,
  "location_id": 2,
  "warehouse_ids": [1, 2],
  "project_ids": [3]
}
```

**Response:**

```json
{
  "id": 1,
  "item_code": "ABC123",
  "description": "Sample Item",
  "photo": "/images/sample.png",
  "total_qty": 150,
  "location_id": 2
}
```

#### 3.4 Delete Item
**Endpoint:** `DELETE /items/{item_id}`

**Example:** `DELETE /items/1`

**Response:**

```json
{
  "detail": "Item deleted successfully"
}
```

#### 3.5 Get Items in a Location
**Endpoint:** `GET /items/location/{location_id}`

**Example:** `GET /items/location/1`

**Response:**
```json
[
    {
        "id": 1,
        "item_code": "ABC123",
        "description": "Sample Item",
        "photo": "/images/sample.png",
        "total_qty": 50,
        "location_id": 1
    },
    {
        "id": 2,
        "item_code": "DEF456",
        "description": "Another Item",
        "photo": "/images/item2.png",
        "total_qty": 75,
        "location_id": 1
    }
]
```

#### 3.6 Get Items in a Warehouse
**Endpoint:** `GET /items/warehouse/{warehouse_id}`

**Example:** `GET /items/warehouse/1`

**Response:**
```json
[
    {
        "id": 1,
        "item_code": "ABC123",
        "description": "Sample Item",
        "photo": "/images/sample.png",
        "total_qty": 50,
        "location_id": 1
    },
    {
        "id": 2,
        "item_code": "DEF456",
        "description": "Another Item",
        "photo": "/images/item2.png",
        "total_qty": 75,
        "location_id": 1
    }
]
```

#### 3.7 Get Items in a Project
**Endpoint:** `GET /items/project/{project_id}`

**Example:** `GET /items/project/1`

**Response:**
```json
[
    {
        "id": 3,
        "item_code": "XYZ789",
        "description": "Project-specific Item",
        "photo": "/images/project_item.png",
        "total_qty": 20,
        "location_id": 1
    }
]
```

#### 3.8 List All Items
**Endpoint:** `GET /items`

**Example:** `GET /items`

**Response:**
```json
[
    {
        "id": 1,
        "item_code": "ABC123",
        "description": "Sample Item",
        "photo": "/images/sample.png",
        "total_qty": 50,
        "location_id": 2,
        "warehouse_id": 1
    },
    {
        "id": 2,
        "item_code": "DEF456",
        "description": "Another Item",
        "photo": "/images/item2.png",
        "total_qty": 75,
        "location_id": 3,
        "warehouse_id": 1
    }
]
```

---

### 4. Warehouse Management

#### 4.1 Create Warehouse

**Endpoint:** `POST /warehouses`

**Request:**

```json
{
  "name": "Riyadh Warehouse",
  "location_id": 1
}
```

**Response:**

```json
{
    "id": 1,
    "name": "Riyadh Warehouse",
    "location_id": 1
}
```

#### 4.2 Get Warehouse

**Endpoint:** `GET /warehouses/{warehouse_id}`

**Example:** `GET /warehouses/1`

**Response:**

```json
{
  "id": 1,
  "name": "Central Warehouse",
  "location_id": 2
}
```

#### 4.3 Update Warehouse

**Endpoint:** `PUT /warehouses/{warehouse_id}`

**Example:** `PUT /warehouses/1`

**Request:**

```json
{
  "name": "Updated warehouse"
}
```

**Response:**

```json
{
  "id": 1,
  "name": "Updated warehouse",
  "location_id": 3
}
```

#### 4.4 Delete Warehouse

**Endpoint:** `DELETE /warehouses/{warehouse_id}`

**Example:** `DELETE /warehouses/1`

**Response:**

```json
{
  "detail": "Warehouse deleted successfully"
}
```

#### 4.5 List Warehouses

**Endpoint:** `GET /warehouses`

**Response:**

```json
[
  {
    "id": 1,
    "name": "Central Warehouse",
    "location_id": 2
  },
  {
    "id": 2,
    "name": "South Warehouse",
    "location_id": 3
  }
]
```

---

### 5. Location Management

#### 4.1 Create Location

**Endpoint:** `POST /locations`

**Request:**

```json
{
  "name": "Riyadh",
  "location_id": 2
}
```

**Response:**

```json
{
  "id": 1,
  "name": "Riyadh"
}
```

#### 4.2 Get Location

**Endpoint:** `GET /locations/{location_id}`

**Example:** `GET /locations/1`

**Response:**

```json
{
  "id": 1,
  "name": "Riyadh"
}
```

#### 4.3 Update Location

**Endpoint:** `PUT /locations/{location_id}`

**Example:** `PUT /locations/1`

**Request:**
```json
{
  "name": "Riyadh"
}
```
**Response:**
```json
{
    "id": 1,
    "name": "Riyadh"
}
```

#### 4.4 Delete Location

**Endpoint:** `DELETE /locations/{location_id}`

**Example:** `DELETE /locations/1`

**Response:**

```json
{
  "detail": "Location deleted successfully"
}
```

#### 4.5 List Locations

**Endpoint:** `GET /locations`

**Response:**

```json
[
  {
    "id": 1,
    "name": "Riyadh"
  },
  {
    "id": 2,
    "name": "Jeddah"
  }
]
```

---

### 6. Project Management

#### 6.1 Create Project

**Endpoint:** `POST /projects`

**Request:**

```json
{
  "project_name": "New Construction Project",
  "location_id": 3
}
```

**Response:**

```json
{
  "id": 1,
  "project_name": "New Construction Project",
  "location_id": 3
}
```

#### 6.2 Get Project

**Endpoint:** `GET /projects/{project_id}`

**Example:** `GET /projects/1`

**Response:**

```json
{
  "id": 1,
  "project_name": "New Construction Project",
  "location_id": 3
}
```

#### 6.3 Update Project

**Endpoint:** `PUT /projects/{project_id}`

**Example:** `PUT /projects/1`

**Request:**

```json
{
  "project_name": "Update Construction Project",
  "location_id": 1
}
```

**Response:**

```json
{
  "id": 1,
  "project_name": "Updated Construction Project",
  "location_id": 3
}
```

#### 6.4 Delete Project

**Endpoint:** `DELETE /projects/{project_id}`

**Example:** `DELETE /projects/1`

**Response:**

```json
{
  "detail": "Project deleted successfully"
}
```

#### 6.5 List Project

**Endpoint:** `GET /projects`

**Response:**

```json
[
  {
    "id": 1,
    "project_name": "First Project",
    "location_id": 2
  },
  {
    "id": 2,
    "project_name": "New Project",
    "location_id": 3
  }
]
```

---

### 7. Reports

#### 7.1 Export Items to Excel

**Endpoint:** `GET /reports/items/export`

**Response:**

```json
{
    "detail": "Report generated at src/assets/reports/inventory_report.xlsx",
    "items": [
        {
            "Item Code": "ITEM001",
            "Description": "Sample Item",
            "Photo": "/images/item1.png",
            "Quantity": 50,
            "Location": "Riyadh",
            "Warehouses": [
                "Riyadh",
                "Jeddah"
            ],
            "Projects": []
        },
        {
            "Item Code": "ABC213",
            "Description": "Sample Item",
            "Photo": "/images/sample.png",
            "Quantity": 100,
            "Location": "Jeddah",
            "Warehouses": [
                "Riyadh",
                "Jeddah"
            ],
            "Projects": []
        }
    ]
}
```

#### 7.2 Warehouse Stock Report

**Endpoint:** `GET /reports/warehouse/{warehouse_id}`

**Example:** `GET /reports/warehouse/1`

**Response:**

```json
{
    "detail": "Report generated at src/assets/reports/inventory_report_warehouse_Riyadh.xlsx",
    "items": [
        {
            "Item Code": "ABC13",
            "Description": "Sample Item",
            "Photo": "/images/sample.png",
            "Quantity": 100,
            "Location": "Riyadh"
        },
        {
            "Item Code": "ABC213",
            "Description": "Sample Item",
            "Photo": "/images/sample.png",
            "Quantity": 100,
            "Location": "Riyadh"
        }
    ]
}
```

#### 7.3 Project Stock Report

**Endpoint:** `GET /reports/project/{project_id}`

**Example:** `GET /reports/project/2`

**Response:**

```json
{
    "detail": "Report generated at src/assets/reports/inventory_report_project_GAMI.xlsx",
    "items": [
        {
            "Item Code": "ITEM002",
            "Description": "Sample Item",
            "Photo": "/images/item1.png",
            "Quantity": 50,
            "Location": "Riyadh"
        }
    ]
}
```

#### 7.4 Generate Stock Report for a Location

**Endpoint:** `GET /reports/location/{location_id}`

**Example:** `GET /reports/location/2`

**Response:**

```json
{
    "detail": "Report generated at src/assets/reports/inventory_report_location_Riyadh.xlsx",
    "items": [
        {
            "Item Code": "ABC123",
            "Description": "Sample Item",
            "Photo": "/images/sample.png",
            "Quantity": 100,
            "Location": "Riyadh"
        },
        {
            "Item Code": "ABC13",
            "Description": "Sample Item",
            "Photo": "/images/sample.png",
            "Quantity": 100,
            "Location": "Riyadh"
        }
    ]
}
```

---

## Authentication

### JWT Token

- After login, the system provides a JWT token.
- Use the token in the Authorization header for protected endpoints:

```makefile
Authorization: Bearer <token>
```

## Setup and Run

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd warehouse_inventory
   ````
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the .env file: </br>
    - Create a `.env` file based on `.env.example` and add the necessary `secrits` and configurations.
    ```bash
    cp .env.example .env
    ```
4. Run the application:
   ```bash
   uvicorn app.main:app --host "localhost" --port 8000 --reload
   ```
5. Access the Swagger UI for API testing: </br>
   Open your browser at http://localhost:8000/docs. </br>

## Future Enhancements

1. Barcode Integration:
    - Scan and manage items using barcodes.
2. Dashboard:
    - Build an admin dashboard for visualizing stock levels.
3. Cloud Integration:
    - Deploy to AWS or Azure for scalability.
4. Enhanced Reports:
    - Generate monthly or yearly summaries.