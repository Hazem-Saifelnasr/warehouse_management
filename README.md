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

| **Endpoint**       | **Method** | **Description**                      | **Access** |
|--------------------|------------|--------------------------------------|------------|
| `/users/create`    | `POST`     | Create a new user                    | Admin      |
| `/users/login`     | `POST`     | Log in a user and return a JWT token | Public     |
| `/users/{user_id}` | `GET`      | Get details of a user by ID          | Admin      |
| `/users/{user_id}` | `PUT`      | Update user details                  | Admin      |
| `/users/{user_id}` | `DELETE`   | Delete a user by ID                  | Admin      |
| `/users/list`      | `GET`      | List of all users                    | Admin      |

---

### **2. Permission Management**

| **Endpoint**                            | **Method** | **Description**                                      | **Access** |
|-----------------------------------------|------------|------------------------------------------------------|------------|
| `/permissions/add`                      | `POST`     | Assign a permission to a user                        | Admin      |
| `/permissions/{permission_id}`          | `DELETE`   | Revoke a permission by its ID                        | Admin      |
| `/permissions/user/{user_id}`           | `GET`      | Get all permissions assigned to a specific user      | Admin      |
| `/permissions/warehouse/{warehouse_id}` | `GET`      | Get all permissions assigned to a specific warehouse | Admin      |
| `/permissions/project/{project_id}`     | `GET`      | Get all permissions assigned to a specific project   | Admin      |
| `/permissions/location/{location_id}`   | `GET`      | Get all permissions assigned to a specific location  | Admin      |
| `/permissions/bulk`                     | `POST`     | Assign bulk permissions to a users                   | Admin      |

---

### **3. Item Management**

| **Endpoint**                    | **Method** | **Description**              | **Access** |
|---------------------------------|------------|------------------------------|------------|
| `/items/add`                    | `POST`     | Create a new item            | Admin      |
| `/items/{item_id}`              | `GET`      | Get details of an item by ID | Admin/User |
| `/items/{item_id}`              | `PUT`      | Update an item’s details     | Admin      |
| `/items/{item_id}`              | `DELETE`   | Delete an item               | Admin      |
| `/items/list`                   | `GET`      | List all items	              | Admin/User |
| `/items/{item_id}/upload-photo` | `POST`     | Upload photo to item	        | Admin/User |

---

### **4. Warehouse Management**

| **Endpoint**                         | **Method** | **Description**                          | **Access** |
|--------------------------------------|------------|------------------------------------------|------------|
| `/warehouses/add`                    | `POST`     | Create a new warehouse                   | Admin      |
| `/warehouses/{warehouse_id}`         | `GET`      | Get details of a warehouse by ID         | Admin/User |
| `/warehouses/{warehouse_id}`         | `PUT`      | Update warehouse details                 | Admin      |
| `/warehouses/{warehouse_id}`         | `DELETE`   | Delete a warehouse                       | Admin      |
| `/warehouses/list`                   | `GET`      | List all warehouses                      | Admin/User |
| `/warehouses/location/{location_id}` | `GET`      | List all warehouses in specific location | Admin/User |

---

### **5. Location Management**

| **Endpoint**                        | **Method** | **Description**                 | **Access** |
|-------------------------------------|------------|---------------------------------|------------|
| `/locations/add`                    | `POST`     | Create a new location           | Admin      |
| `/locations/{location_id}`          | `GET`      | Get details of a location by ID | Admin/User |
| `/locations/{location_id}`          | `PUT`      | Update location details         | Admin      |
| `/locations/{location_id}`          | `DELETE`   | Delete a location               | Admin      |
| `/locations/list`                   | `GET`      | List all locations              | Admin/User |
| `/locations/{location_id}/entities` | `GET`      | List all entities by locations  | Admin/User |

---

### **6. Project Management**

| **Endpoint**                       | **Method** | **Description**                        | **Access** |
|------------------------------------|------------|----------------------------------------|------------|
| `/projects/add`                    | `POST`     | Create a new project                   | Admin      |
| `/projects/{project_id}`           | `GET`      | Get details of a project by ID         | Admin/User |
| `/projects/{project_id}`           | `PUT`      | Update project details                 | Admin      |
| `/projects/{project_id}`           | `DELETE`   | Delete a project                       | Admin      |
| `/projects/list`                   | `GET`      | List all projects                      | Admin/User |
| `/projects/location/{location_id}` | `GET`      | List all projects in specific location | Admin/User |

---

| **Endpoint**                        | **Method** | **Description**                       | **Access** |
|-------------------------------------|------------|---------------------------------------|------------|
| `/reports/items/export`             | `GET`      | Export all items to an Excel/CSV file | Admin      |
| `/reports/warehouse/{warehouse_id}` | `GET`      | Generate stock report for a warehouse | Admin/User |
| `/reports/location/{location_id}`   | `GET`      | Generate stock report for a location  | Admin/User |
| `/reports/project/{project_id}`     | `GET`      | Generate stock report for a project   | Admin/User |

### **7. Stock Management**

| **Endpoint**                                  | **Method** | **Description**                                                                               | **Access** |
|-----------------------------------------------|------------|-----------------------------------------------------------------------------------------------|------------|
| /stocks/add                                   | POST       | Add stock to a specific project or warehouse                                                  | Admin      |
| /stocks/deduct                                | POST       | Deduct stock from a specific project or warehouse                                             | Admin/User |
| /stocks/transfer                              | POST       | Transfer stock between locations, projects, or warehouses                                     | Admin/User |
| /stocks/location/{location_id}                | GET        | Retrieve stock report for a specific location                                                 | Admin/User |
| /stocks/warehouse/{warehouse_id}              | GET        | Retrieve stock report for a specific warehouse                                                | Admin/User |
| /stocks/project/{project_id}                  | GET        | Retrieve stock report for a specific project                                                  | Admin/User |
| /stocks/item/{item_id}/project/{location_id}  | GET        | Retrieve stock report for a specific location by item                                         | Admin/User |
| /stocks/item/{item_id}/project/{warehouse_id} | GET        | Retrieve stock report for a specific warehouse by item                                        | Admin/User |
| /stocks/item/{item_id}/project/{project_id}   | GET        | Retrieve stock report for a specific project by item                                          | Admin/User |
| /stocks/item/{item_id}/locations              | GET        | Get all locations and quantities for a specific item                                          | Admin/User |
| /stocks/item/{item_id}/total                  | GET        | Retrieve the total quantity of a specific item across all locations, warehouses, and projects | Admin/User |

### **8. Reports**

| **Endpoint**                               | **Method** | **Description**                                                    | **Access** |
|--------------------------------------------|------------|--------------------------------------------------------------------|------------|
| `/reports/{entity_type}`                   | `GET`      | Export all data of entity type to an Excel/CSV file                | Admin      |
| `/reports/stock/{entity_type}`             | `GET`      | Export all stock by entity type to an Excel/CSV file               | Admin/User |
| `/reports/stock/{entity_type}/{entity_id}` | `GET`      | Export all stock by entity type and entity id to an Excel/CSV file | Admin/User |
| `/reports/stock/item/{item_id}`            | `GET`      | Export all stock by item to an Excel/CSV file                      | Admin/User |

---

## API Documentation

### 1. User Management

#### 1.1 Create User

**Endpoint:** `POST /users/add`

**Request:**

```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "securepassword",
  "role": "user"
}
```

**Response:**

```json
{
  "id": 1,
  "username": "testuser",
  "email": "testuser@example.com",
  "role": "user"
}
```

#### 1.2 Get User

**Endpoint:** `GET /users/{user_id}`

**Example:** `GET /users/1`

**Response:**

```json
{
  "id": 1,
  "username": "testuser",
  "email": "testuser@example.com",
  "role": "user"
}
```

#### 1.3 Update User

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
  "email": "updateduser@example.com",
  "role": "user"
}
```

#### 1.4 Delete User

**Endpoint:** `DELETE /users/{user_id}`

**Example:** `DELETE /users/1`

**Response:**

```json
{
  "detail": "User deleted successfully"
}
```

#### 1.5 List Users

**Endpoint:** `GET /users/list`

**Response:**

```json
[
  {
    "id": 1,
    "username": "testuser1",
    "email": "testuser1@example.com",
    "role": "admin"
  },
  {
    "id": 2,
    "username": "testuser2",
    "email": "testuser2@example.com",
    "role": "user"
  },
  {
    "id": 3,
    "username": "testuser3",
    "email": "testuser3@example.com",
    "role": "user"
  }
]
```

---

### 2. Permission Management

#### 2.1 Assign Permission

**Endpoint:** `POST /permissions/add`

**Request:**

```json
{
  "user_id": 1,
  "entity": "warehouse",
  "entity_id": "10",
  "access_type": "read"
}
```

**Response:**

```json
{
  "id": 1,
  "user_id": 1,
  "entity": "warehouse",
  "entity_id": "10",
  "access_type": "read"
}
```

#### 2.2 Assign Bulk Permissions

**Endpoint:** `POST /permissions/bulk`

**Request:**

```json
[
  {
    "user_id": 2,
    "entity": "warehouse",
    "entity_id": "2",
    "access_type": "read"
  },
  {
    "user_id": 3,
    "entity": "project",
    "entity_id": "*",
    "access_type": "read"
  },
  {
    "user_id": 3,
    "entity": "project",
    "entity_id": "2",
    "access_type": "read"
  }
]
```

**Response:**

```json
[
  {
    "id": 1,
    "user_id": 2,
    "entity": "warehouse",
    "entity_id": "2",
    "access_type": "read"
  },
  {
    "id": 2,
    "user_id": 3,
    "entity": "project",
    "entity_id": "*",
    "access_type": "read"
  },
  {
    "id": 2,
    "user_id": 3,
    "entity": "project",
    "entity_id": "2",
    "access_type": "read"
  }
]
```

#### 2.3 Revoke Permission

**Endpoint:** `DELETE /permissions/{permission_id}`

**Example:** `DELETE /permissions/1`

**Response:**

```json
{
  "detail": "Permission revoked successfully"
}
```

#### 2.4 Get Permissions for User

**Endpoint:** `GET /permissions/user/{user_id}`

**Example:** `GET /permissions/user/1`

**Response:**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "entity": "warehouse",
    "entity_id": "10",
    "access_type": "read"
  },
  {
    "id": 2,
    "user_id": 1,
    "entity": "project",
    "entity_id": "*",
    "access_type": "*"
  }
]
```

#### 2.5 List Permissions by Warehouse

**Endpoint:** `GET /permissions/warehouse/{warehouse_id}`

**Example:** `GET /permissions/warehouse/1`

**Response:**

```json
[
  {
    "id": 2,
    "user_id": 1,
    "entity": "warehouse",
    "entity_id": 1,
    "access_type": "read"
  }
]
```

#### 2.6 List Permissions by Project

**Endpoint:** `GET /permissions/project/{project_id}`

**Example:** `GET /permissions/project/1`

**Response:**

```json
[
  {
    "id": 4,
    "user_id": 2,
    "entity": "project",
    "entity_id": 1,
    "access_type": "read"
  },
  {
    "id": 5,
    "user_id": 1,
    "entity": "project",
    "entity_id": 1,
    "access_type": "read"
  }
]
```

#### 2.7 Get Permissions for Location

**Endpoint:** `GET /permissions/location/{location_id}`

**Example:** `GET /permissions/location/1`

**Response:**

```json
[
  {
    "id": 3,
    "user_id": 1,
    "entity": "location",
    "entity_id": 1,
    "access_type": "read"
  },
  {
    "id": 6,
    "user_id": 2,
    "entity": "location",
    "entity_id": 1,
    "access_type": "write"
  }
]
```

---

### 3. Item Management

#### 3.1 Create Item

**Endpoint:** `POST /items/add`

**Request:**

```json
{
  "item_code": "ITEM001",
  "description": "Sample Item",
  "photo": "/images/item1.png",
  "unit_of_measure": "m"
}
```

**Response:**

```json
{
  "id": 1,
  "item_code": "ITEM001",
  "description": "Sample Item",
  "photo": "/images/item1.png",
  "unit_of_measure": "m"
}
```

#### 3.2 Get Item

**Endpoint:** `GET /items/{item_id}`

**Example:** `GET /items/1`

**Response:**

```json
{
  "id": 1,
  "item_code": "ITEM001",
  "description": "Sample Item",
  "photo": "/images/item1.png",
  "unit_of_measure": "m"
}
```

#### 3.3 Update Item

**Endpoint:** `PUT /items/{item_id}`

**Example:** `PUT /items/1`

**Request:**

```json
{
  "item_code": "ITEM001",
  "description": "Sample Item",
  "photo": "/images/item1.png",
  "unit_of_measure": "kg"
}
```

**Response:**

```json
{
  "id": 1,
  "item_code": "ITEM001",
  "description": "Sample Item",
  "photo": "/images/item1.png",
  "unit_of_measure": "kg"
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

#### 3.5 List All Items

**Endpoint:** `GET /items/list`

**Example:** `GET /items/list`

**Response:**

```json
[
  {
    "id": 1,
    "item_code": "ITEM001",
    "description": "Sample Item",
    "photo": "/images/item1.png",
    "unit_of_measure": "m"
  },
  {
    "id": 2,
    "item_code": "ITEM002",
    "description": "Sample Item",
    "photo": "/images/item2.png",
    "unit_of_measure": "kg"
  }
]
```

#### 3.6 Upload Photo to Item

**Endpoint:** `POST /items/{item_id}/upload-photo`

**Example:** `POST /items/1/upload-photo`

**Response:**

```json
[
  {
    "id": 1,
    "item_code": "ITEM001",
    "description": "Sample Item",
    "photo": "/images/item1.png",
    "unit_of_measure": "m"
  },
  {
    "id": 2,
    "item_code": "ITEM002",
    "description": "Sample Item",
    "photo": "/images/item2.png",
    "unit_of_measure": "kg"
  }
]
```

---

### 4. Warehouse Management

#### 4.1 Create Warehouse

**Endpoint:** `POST /warehouses/add`

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

**Endpoint:** `GET /warehouses/list`

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

#### 4.6 List Warehouses by location

**Endpoint:** `GET /warehouses/location/{location_id}`

**Example:** `GET /warehouses/location/1`

**Response:**

```json
[
  {
    "id": 1,
    "name": "Central Warehouse",
    "location_id": 1
  },
  {
    "id": 2,
    "name": "South Warehouse",
    "location_id": 1
  }
]
```

---

### 5. Location Management

#### 4.1 Create Location

**Endpoint:** `POST /locations/add`

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

**Endpoint:** `GET /locations/list`

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

#### 4.6 List All Entities by Locations

**Endpoint:** `GET /locations/{location_id}/entities`

**Example:** `GET /locations/2/entities`

**Response:**

```json
{
  "warehouses": [
    {
      "id": 2,
      "name": "Jeddah Warehouse",
      "location_id": 2
    }
  ],
  "projects": [
    {
      "id": 3,
      "project_name": "Hilton",
      "location_id": 2
    },
    {
      "id": 4,
      "project_name": "Rixos",
      "location_id": 2
    }
  ]
}
```

---

### 6. Project Management

#### 6.1 Create Project

**Endpoint:** `POST /projects/add`

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

#### 6.5 List Projects

**Endpoint:** `GET /projects/list`

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
    "location_id": 1
  }
]
```

#### 6.5 List Projects by location

**Endpoint:** `GET /projects/location/{location_id}`

**Example:** `GET /projects/location/1`

**Response:**

```json
[
  {
    "id": 1,
    "project_name": "First Project",
    "location_id": 1
  },
  {
    "id": 2,
    "project_name": "New Project",
    "location_id": 1
  }
]
```

---

### 7. Stock Management

#### 7.1 Add Stock

**Endpoint:** `GET /stocks/add`

**Request:**

```json
{
  "item_id": 1,
  "project_id": 1,
  "quantity": 50.0
}
```

or

```json
{
  "item_id": 1,
  "warehouse_id": 2,
  "quantity": 40.0
}
```

**Response:**

```json
{
  "id": 1,
  "item_id": 1,
  "project_id": 1,
  "warehouse_id": null,
  "quantity": 50.0,
  "last_updated": "2024-12-25T09:51:06.825862"
}
```

#### 7.2 Deduct Stock

**Endpoint:** `GET /stocks/deduct`

**Request:**

```json
{
  "item_id": 1,
  "project_id": 1,
  "quantity": 50.0
}
```

or

```json
{
  "item_id": 1,
  "warehouse_id": 2,
  "quantity": 40.0
}
```

**Response:**

```json
[
  {
    "id": 7,
    "item_id": 5,
    "project_id": null,
    "warehouse_id": 2,
    "quantity": 3.0,
    "last_updated": "2024-12-25T13:07:07.285911"
  }
]
```

#### 7.3 Transfer Stock

**Endpoint:** `GET /stocks/transfer`

**params:**</br>
`item_id` (int): ID of the item being transferred.</br>
`from_project_id` or `from_warehouse_id` (Optional[int]): ID of the source.</br>
`to_project_id` or `to_warehouse_id` (Optional[int]) :ID of the destination.</br>
`quantity` (float): The quantity of stock to transfer

**Response:**

```json
{
  "id": 9,
  "item_id": 5,
  "project_id": null,
  "warehouse_id": 1,
  "quantity": 3.0,
  "last_updated": "2024-12-25T13:12:42.452269"
}
```

#### 7.4 List Stocks for a Location

**Endpoint:** `GET /stocks/location/{location_id}`

**Example:** `GET /stocks/location/1`

**Response:**

```json
[
  {
    "id": 9,
    "item_id": 5,
    "project_id": null,
    "warehouse_id": 1,
    "quantity": 3.0,
    "last_updated": "2024-12-25T13:12:42.452269"
  },
  {
    "id": 1,
    "item_id": 1,
    "project_id": 1,
    "warehouse_id": null,
    "quantity": 40.0,
    "last_updated": "2024-12-25T09:50:07.346788"
  },
  {
    "id": 2,
    "item_id": 1,
    "project_id": 2,
    "warehouse_id": null,
    "quantity": 20.0,
    "last_updated": "2024-12-25T09:50:18.197375"
  }
]
```

#### 7.5 List Stocks for a Warehouse

**Endpoint:** `GET /stocks/warehouse/{warehouse_id}`

**Example:** `GET /stocks/warehouse/1`

**Response:**

```json
[
  {
    "id": 6,
    "item_id": 4,
    "project_id": null,
    "warehouse_id": 2,
    "quantity": 100.0,
    "last_updated": "2024-12-25T13:22:41.481952"
  }
]
```

#### 7.6 List Stocks for a Project

**Endpoint:** `GET /stocks/project/{project_id}`

**Example:** `GET /stocks/project/1`

**Response:**

```json
[
  {
    "id": 1,
    "item_id": 1,
    "project_id": 1,
    "warehouse_id": null,
    "quantity": 40.0,
    "last_updated": "2024-12-25T09:50:07.346788"
  },
  {
    "id": 4,
    "item_id": 3,
    "project_id": 1,
    "warehouse_id": null,
    "quantity": 42.5,
    "last_updated": "2024-12-25T09:50:35.734668"
  }
]
```

#### 7.7 List Stocks for a Location by item

**Endpoint:** `GET /stocks/item/{item_id}/location/{location_id}`

**Example:** `GET /stocks/item/3/location/1`

**Response:**

```json
[
  {
    "id": 3,
    "item_id": 3,
    "project_id": 2,
    "warehouse_id": null,
    "quantity": 35.0,
    "last_updated": "2024-12-25T09:50:29.902213"
  },
  {
    "id": 4,
    "item_id": 3,
    "project_id": 1,
    "warehouse_id": null,
    "quantity": 42.5,
    "last_updated": "2024-12-25T09:50:35.734668"
  }
]
```

#### 7.8 List Stocks for a Warehouse by item

**Endpoint:** `GET /stocks/item/{item_id}/warehouse/{warehouse_id}`

**Example:** `GET /stocks/item/1/warehouse/1`

**Response:**

```json
[
  {
    "id": 9,
    "item_id": 5,
    "project_id": null,
    "warehouse_id": 1,
    "quantity": 3.0,
    "last_updated": "2024-12-25T13:12:42.452269"
  }
]
```

#### 7.9 List Stocks for a Project by item

**Endpoint:** `GET /stocks/item/{item_id}/project/{project_id}`

**Example:** `GET /stocks/item/1/project/2`

**Response:**

```json
[
  {
    "id": 2,
    "item_id": 1,
    "project_id": 2,
    "warehouse_id": null,
    "quantity": 20.0,
    "last_updated": "2024-12-25T09:50:18.197375"
  }
]
```

#### 7.10 List Location and QTY for item

**Endpoint:** `GET /stocks/item/{item_id}/locations `

**Example:** `GET /stocks/item/3/locations `

**Response:**

```json
[
  {
    "location": "Riyadh",
    "type": "project",
    "name": "NBE",
    "quantity": 42.5
  },
  {
    "location": "Riyadh",
    "type": "project",
    "name": "GAMI",
    "quantity": 35.0
  }
]
```

#### 7.11 Total QTY for item

**Endpoint:** `GET /stocks/item/{item_id}/total `

**Example:** `GET /stocks/item/3/total `

**Response:**

```json
{
  "item_code": "ITEM001",
  "item_description": "Sample Item",
  "total_quantity": 77.5,
  "unit_of_measure": "m"
}
```

---

### 8. Reports

#### 8.1 Export All Data of Entity Type

**Endpoint:** `GET /reports/{entity_type}`

**Example:** `GET /reports/location`

**Response:**

```json
{
  "detail": "Report generated at src/assets/reports/locations_report.xlsx",
  "stock": [
    {
      "id": 1,
      "name": "Riyadh"
    },
    {
      "id": 2,
      "name": "Jeddah"
    },
    {
      "id": 4,
      "name": "Damam"
    }
  ]
}
```

#### 8.2 Export All Stock by Entity Type

**Endpoint:** `GET /reports/stock/{entity_type}`

**Example:** `GET /reports/stock/warehouse`

**Response:**

```json
{
  "detail": "Report generated at src/assets/reports/warehouses_stock_report.xlsx",
  "items": [
    {
      "Item Code": "ITEM003",
      "Description": "Sample Item",
      "Unit of Measure": "m",
      "Total Quantity": 3.0,
      "Entity Type": "Warehouse",
      "Entity Name": "Riyadh Warehouse"
    },
    {
      "Item Code": "ITEM002",
      "Description": "Sample Item",
      "Unit of Measure": "m",
      "Total Quantity": 100.0,
      "Entity Type": "Warehouse",
      "Entity Name": "Jeddah Warehouse"
    }
  ]
}
```

#### 8.3 Export All Stock by Entity Type and Entity ID

**Endpoint:** `GET /reports/stock/{entity_type}/{entity_id}`

**Example:** `GET /reports/stock/project/1`

**Response:**

```json
{
  "detail": "Report generated at src/assets/reports/NBE_stock_report.xlsx",
  "stock": [
    {
      "Item Code": "ITEM006",
      "Description": "Sample Item",
      "Quantity": 40.0,
      "Location": "NBE"
    },
    {
      "Item Code": "ITEM001",
      "Description": "Sample Item",
      "Quantity": 42.5,
      "Location": "NBE"
    }
  ]
}
```

#### 8.4 Export All Stock by Item

**Endpoint:** `GET /reports/stock/item/{item_id}`

**Example:** `GET /reports/stock/item/3`

**Response:**

```json
{
  "detail": "Report generated at src/assets/reports/item_ITEM001_stock_report.xlsx",
  "data": {
    "item": {
      "item_code": "ITEM001",
      "description": "Sample Item",
      "unit_of_measure": "m"
    },
    "stocks": [
      {
        "Warehouse": "N/A",
        "Project": "GAMI",
        "Total Quantity": 35.0
      },
      {
        "Warehouse": "N/A",
        "Project": "NBE",
        "Total Quantity": 42.5
      }
    ]
  }
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
3. Enhanced Reports:
    - Generate monthly or yearly summaries.

## File structure
```plaintext
src/
├── app/
│   ├── __init__.py
│   ├── core/                  # Core utilities and configurations
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings (reads from .env)
│   │   ├── security.py        # Security utilities (JWT, hashing)
│   │   ├── rbac.py            # Role-Based Access Control
│   │   ├── database.py        # Database connection setup
│   ├── models/                # ORM models (e.g., SQLAlchemy, Pydantic schemas)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── item.py
│   │   ├── stock.py
│   │   ├── permission.py
│   │   ├── project.py
│   │   ├── location.py
│   │   ├── warehouse.py
│   ├── routers/               # API route handlers
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── locations.py
│   │   ├── login.py
│   │   ├── users.py
│   │   ├── items.py
│   │   ├── stocks.py
│   │   ├── permissions.py
│   │   ├── reports.py
│   │   ├── projects.py
│   │   ├── warehouses.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── item.py
│   │   ├── stock.py
│   │   ├── permission.py
│   │   ├── project.py
│   │   ├── location.py
│   │   ├── warehouse.py
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── item_service.py
│   │   ├── stock_service.py
│   │   ├── auth_service.py
│   │   ├── report_service.py
│   │   ├── permission_service.py
│   ├── utils/                 # Utility functions
│       ├── __init__.py
│       ├── helpers.py
│       ├── error_handler.py
│       ├── logger.py
├── assets/                    # Static assets like photo, reports
│   ├── logs/   
│   ├── photos/                
│   ├── reports/               
├── web/                       # Templates for the frontend (HTML files)
│   ├── templates/             # HTML templates
│   │   ├── base.html](src%2
│   │   ├── dashboard.html
│   │   ├── error.html
│   │   ├── items.html
│   │   ├── locations.html
│   │   ├── login.html
│   │   ├── permissions.html
│   │   ├── projects.html
│   │   ├── reports.html
│   │   ├── stocks.html
│   │   ├── users.html
│   │   ├── warehouses.html
│   ├── static/                # Static files served by the web app
│   │   ├── css/               # CSS files
│   │   │   ├── styles.css         
│   │   ├── img/               # image files
│   │   │   ├── logo.png        
│   │   │   ├── logo_text.png         
│   │   │   ├── favicon.ico         
│   │   ├── js/                # JavaScript files
│   │   │   ├──dashboard.js
│   │   │   ├──items.js
│   │   │   ├──locations.js
│   │   │   ├──permissions.js
│   │   │   ├──projects.js
│   │   │   ├──reports.js
│   │   │   ├──stocks.js
│   │   │   ├──users.js
│   │   │   ├──utils.js
│   │   │   ├──warehouses.js
│   │   │   ├── styles.css         
│   │   │   ├── scripts.js         
├── main.py                    # Main FastAPI application entry point
├── .env                       # Environment variables (sensitive config)
├── requirements.txt           # Python dependencies
alembic/                       # Alembic for database migrations
   ├── README
   ├── script.py.mako
   ├── env.py
   └── versions/
README.ME
docker-compose.yml
Dockerfile                     # Dockerfile for containerization
```