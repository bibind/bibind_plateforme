import odoorpc

# Prepare the connection to the server
odoo = odoorpc.ODOO('91.121.79.171', port=8069)

# Check available databases
print(odoo.db.list())

# Login
odoo.login('dev_bibind', 'admin', 'Bibind@74')

# Current user
user = odoo.env.user
print(user.name)            # name of the user connected
print(user.company_id.name) # the name of its company

