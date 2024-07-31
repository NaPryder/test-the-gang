# Banking Application

## Objective

Your assignment is to build an internal API for a fake financial institution using Python and Django.

## Brief

You are tasked with an assignment to replicate one of, if not, the most well-defined Banking application well known to man. Well, at least that's what your Boss said. Actually, you're supposed to replicate a Banking system because your team want to simulate what it's like to serve a live-service application with top notch security.

Unfortunately (or fortunate), you are the only Backend Engineer in the team. All decisions regarding system design will be made by you!
As a talented engineer. You know by heart that, functionality of creating account, inquiry, transaction history, deposit, withdraw, and transfer should be bare minimum. Some sort of authorization is obvious enough as well.

However, since you are your own boss. You are free to add any _nice-to-have_ functionality that you believe it'll benefit users. Still, you will have to be able to explain to your friend why you spend your precious time on them.

Your application should be able to run on your teams' machines. Otherwise, they will be severely disappointed.

### Evaluation Criteria

- Python best practices
- Completeness: did you complete the features?
- Correctness: does the functionality act in sensible, thought-out ways?
- Maintainability: is it written in a clean, maintainable way?
- Testing: is the system adequately tested?
- Documentation: is the API well-documented?

### CodeSubmit

Please organize, design, test and document your code as if it were going into production - then push your changes to the master branch. After you have pushed your code, you may submit the assignment on the assignment page.

All the best and happy coding,

The Gang Technology Team

## Banking application Document

Project was written in Python (version 3.10) using Django and Django Rest Framework
Created by [Nachai Paramesthanakorn](nachai.pf@gmail.com)

## Initially

### Build and run docker following this instruction:

#### If you've not built image, follow this instructions:

1. Create .env file and add _SECRET_KEY_, _DB_NAME_, _DB_USER_, _DB_HOST_, _DB_PORT_, _DB_PASS_ variables

2. Using docker compose for start container

   ```
   docker-compose up -d --build
   ```

3. Execute container 'backend' (container named 'test-the-gang-backend-1') bash

   ```
   docker exec -it test-the-gang-backend-1 bash
   ```

4. Make migration
   ```
   $ python manage.py migrate
   ```
5. Create django super user for using django admin

   ```
   $ python manage.py createsuperuser
   ```

6. You can create mockup data following this statement

```
 $ python manage.py create-mock-data
```

## Endpoints

### There're 3 user roles:

1. ADMIN : for create customer account and make transaction (deposit, withdraw, transfer)
2. STAFF : for create customer account and make transaction (deposit, withdraw, transfer)
3. CUSTOMER : for inquiry owned account and get transaction history

#### Login

    POST api/common/login/

Required field: username, password.
Allow anonymous user but need csrf token header

Example request body:

```json
{
  "username": "test-admin", // or "test-staff" (staff), "test1" (customer)
  "password": "11test2@Pass04"
}
```

Response status code 201

### Customer Account Management

#### Create Customer User

Allow autenticated ADMIN or STAFF

    POST /api/common/registration/

Example request body:

```json
{
  "username": "test-customer-2",
  "password": "P@551234"
}
```

#### Create Customer Account

Allow autenticated ADMIN or STAFF

    POST /api/account/customer/create_account/

Example request body:

```json
{
  "username": "test-customer-2", // username for own an account
  "balance": 100, // beginning balance
  "account_type": "01", // "01" (SAVING ACCOUNT) or "02" (FIXED DEPOSIT ACCOUNT)
  "branch_id": "1" // for branch HQ
}
```

Response status 201

---

#### Inquiry Owned Account

Need authenticated CUSTOMER

    GET /api/account/financial/

Account have 3 status

1. WAIT : initial create account, must activate by admin/staff before using
2. ACTIVE : can make transaction
3. INACTIVE : cannot make any transaction

Example request body:

```json
{
  "username": "test1",
  "accounts": [
    {
      "account_type": "01",
      "account_number": "0000000001",
      "branch": 1,
      "status": "WAIT",
      "balance": 500.0
    },
    {
      "account_type": "02",
      "account_number": "0000002000000002",
      "branch": 1,
      "status": "ACTIVE",
      "balance": 1111.0
    },
    {
      "account_type": "01",
      "account_number": "0000001000000003",
      "branch": 1,
      "status": "INACTIVE",
      "balance": 333.0
    }
  ]
}
```

Response status code 200

---

#### Activate account

Allow autenticated ADMIN or STAFF

    PUT /api/account/customer/{account_number}/activate/

Required parameter: account_number

Response status code 200

---

#### Deactivate account

Allow autenticated ADMIN or STAFF

    PUT /api/account/customer/{account_number}/deactivate/

Required parameter: account_number

Response status code 200

---

#### Deposit

Allow autenticated ADMIN or STAFF

    PUT /api/account/customer/{account_number}/deposit/

Required parameter: account_number
Example request body:

```json
{
  "amount": 1000, // amount for deposit
  "receiver_account_number": ""
}
```

Response status code 200

---

#### Withdraw

Allow autenticated ADMIN or STAFF

    PUT /api/account/customer/{account_number}/withdraw/

Required parameter: account_number
Example request body:

```json
{
  "amount": 200, // amount for withdraw
  "receiver_account_number": ""
}
```

Response status code 200

---

#### Transfer

Allow autenticated ADMIN or STAFF

    PUT /api/account/customer/{account_number}/withdraw/

Required parameter: account_number
Example request body:

```json
{
  "amount": 200, // amount to transfer
  "receiver_account_number": "0000001000000001"
}
```

Response status code 200

---

#### Get transaction history

Need authenticated user

    GET /api/account/financial/{account_number}/statement/

Required parameter: account_number
Optional query parameters:

- start_date: filter by create_at i.e. start_date=2025-02-10
- end_date: filter by create_at i.e. end_date=2025-04-10

Example response:

```json
[
  {
    "transaction_type": "D",
    "amount": 1000.0,
    "message": "Complete Deposit",
    "transfer_to": null,
    "create_at": "2024-07-29T11:09:55.975235Z"
  },
  {
    "transaction_type": "W",
    "amount": 200.0,
    "message": "Complete Withdraw",
    "transfer_to": null,
    "create_at": "2024-07-29T11:12:45.982469Z"
  },
  {
    "transaction_type": "T",
    "amount": 23.0,
    "message": "Complete Transfer",
    "transfer_to": 3,
    "create_at": "2024-07-29T11:13:50.273440Z"
  },
  {
    "transaction_type": "D",
    "amount": 23.0,
    "message": "Complete Deposit",
    "transfer_to": null,
    "create_at": "2024-07-29T11:13:50.276091Z"
  },
  {
    "transaction_type": "T",
    "amount": 100.0,
    "message": "Complete Transfer",
    "transfer_to": 4,
    "create_at": "2024-07-29T11:16:46.558985Z"
  }
]
```

Response status code 200

---
