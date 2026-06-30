# Pet Shop MySQL

This folder stores MySQL initialization scripts for the FastAPI backend.

Create the database locally:

```powershell
cd C:\Users\28235\Desktop\Pet_shop\Pet_Shop_v2\backend
mysql -u root -p < database\init_mysql.sql
```

Then copy `.env.example` to `.env` and update the database username and password.

The default script creates:

- database: `pet_shop_v2`
- user: `pet_shop`
- password: `change_me`

Change the password before production use.
