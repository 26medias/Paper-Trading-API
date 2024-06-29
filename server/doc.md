# Paper API Documentation

*Base URL*: `http://localhost:8080`

This documentation provides details on how to integrate with the Paper Trading API. The API allows managing projects, buying and selling trades, viewing logs, managing watchlists, and more.

### Endpoints

---

#### 1. Create Project
**URL:** `/project/create`

**Method:** `POST`

**Description:** Creates a new project.

**Parameters:**
- `cash` (number): Initial cash for the project.

**Request Body:**
```
{
  "cash": 100000
}
```

**Response:**
```
{
  "project_name": "example_project",
  "cash": 100000
}
```

---

#### 2. Fund Project
**URL:** `/project/fund`

**Method:** `POST`

**Description:** Adds funds to an existing project.

**Parameters:**
- `project` (string): The name of the project.
- `amount` (number): Amount to add to the project.

**Request Body:**
```
{
  "project": "example_project",
  "amount": 5000
}
```

**Response:**
```
{
  "project": "example_project",
  "cash": 105000
}
```

---

#### 3. Get Project Data
**URL:** `/project/data`

**Method:** `GET`

**Description:** Retrieves data for a specific project.

**Parameters:**
- `project` (string): The name of the project.

**Request:**
`GET /project/data?project=example_project`

**Response:**
```
{
  "project": "example_project",
  "cash": 105000,
  "initial_cash": 100000
}
```

---

#### 4. Buy Trade
**URL:** `/trade/buy`

**Method:** `POST`

**Description:** Buys a specific quantity of a stock for a project.

**Parameters:**
- `project` (string): The name of the project.
- `ticker` (string): The ticker symbol of the stock.
- `price` (number): The price at which the stock is bought.
- `qty` (number): The quantity of the stock to buy.

**Request Body:**
```
{
  "project": "example_project",
  "ticker": "AAPL",
  "price": 150,
  "qty": 10
}
```

**Response:**
```
{
  "qty": 10,
  "value": 1500,
  "cash": 93500
}
```

---

#### 5. Sell Trade
**URL:** `/trade/sell`

**Method:** `POST`

**Description:** Sells a specific quantity of a stock for a project.

**Parameters:**
- `project` (string): The name of the project.
- `ticker` (string): The ticker symbol of the stock.
- `price` (number): The price at which the stock is sold.
- `qty` (number): The quantity of the stock to sell.

**Request Body:**
```
{
  "project": "example_project",
  "ticker": "AAPL",
  "price": 150,
  "qty": 10
}
```

**Response:**
```
{
  "qty": 0,
  "value": 1500,
  "gains": 0.67,
  "profits": 10,
  "cash": 95000
}
```

---

#### 6. Get Trade Stats
**URL:** `/trade/stats`

**Method:** `GET`

**Description:** Retrieves trading statistics for a specific project.

**Parameters:**
- `project` (string): The name of the project.

**Request:**
`GET /trade/stats?project=example_project`

**Response:**
```
{
  "positions": [
    {
      "ticker": "AAPL",
      "qty": 10,
      "avg_cost": 150,
      "current_price": 155,
      "gains": 3.33
    }
  ],
  "cash": 95000,
  "invested_value": 1500,
  "open_value": 1550,
  "gains": 3.33,
  "unrealized_gains": 3.33
}
```

---

#### 7. Get Positions
**URL:** `/trade/positions`

**Method:** `GET`

**Description:** Retrieves the current positions for a specific project.

**Parameters:**
- `project` (string): The name of the project.

**Request:**
`GET /trade/positions?project=example_project`

**Response:**
```
{
  "positions": [
    {
      "ticker": "AAPL",
      "qty": 10,
      "avg_cost": 150,
      "current_price": 155,
      "gains": 3.33,
      "profit": 50
    }
  ],
  "invested_value": 1500,
  "open_value": 1550
}
```

---

#### 8. Get Prices
**URL:** `/trade/prices`

**Method:** `GET`

**Description:** Retrieves the current prices for specified tickers.

**Parameters:**
- `tickers` (string): Comma-separated list of ticker symbols.

**Request:**
`GET /trade/prices?tickers=AAPL,GOOGL`

**Response:**
```
{
  "AAPL": 150.25,
  "GOOGL": 2750.50
}
```

---

#### 9. Get Trade Logs
**URL:** `/trade/logs`

**Method:** `GET`

**Description:** Retrieves trade logs for a specific project with pagination.

**Parameters:**
- `project` (string): The name of the project.
- `page` (number, optional, default 1): The page number.
- `per_page` (number, optional, default 50): The number of logs per page.

**Request:**
`GET /trade/logs?project=example_project&page=1&per_page=50`

**Response:**
```
{
  "pagination": {
    "total": 100,
    "page_count": 2,
    "page": 1,
    "per_page": 50
  },
  "data": [
    {
      "create_date": "2024-06-29T12:34:56Z",
      "project": "example_project",
      "type": "buy",
      "ticker": "AAPL",
      "qty": 10,
      "price": 150
    }
  ]
}
```

---

#### 10. Manage Watchlist
**URL:** `/trade/watchlist`

**Method:** `POST`

**Description:** Manages the watchlist by adding, removing, or listing tickers.

**Parameters:**
- `project` (string): The name of the project.
- `ticker` (string, required if `action` is "add" or "remove"): The ticker symbol to add or remove.
- `action` (string): The action to perform (add/remove/list).

**Request Body:**
```
{
  "project": "example_project",
  "ticker": "AAPL",
  "action": "add"
}
```

**Response:**
```
{
  "watchlist": ["AAPL"]
}
```
