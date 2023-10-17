import sqlite3

# Setup
connection = sqlite3.connect('smarthome.db')
instance = connection.cursor()

# Create table
# instance.execute(
#     """CREATE TABLE day (
#         avg_temp integer,
#         lamp_runtime integer,
#         heater_runtime integer,
#         fan_runtime integer
# )
# """)

# Inject data
# instance.execute("INSERT INTO day VALUES (20, 456, 200, 13)")

instance.execute("SELECT * FROM day")
print(instance.fetchone())
# Commit command
connection.commit()
print("Command executed successfully!")
# Close connection
connection.close()
