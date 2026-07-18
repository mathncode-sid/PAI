from core.database import db

# Just to query the courses I created created 
query = "MATCH (c:Course) RETURN c.code AS code, c.name AS name"
results = db.execute_query(query)

print(" Courses Found in AuraDB ")
for record in results:
    print(f"Code: {record['code']} | Name: {record['name']}")


db.close()