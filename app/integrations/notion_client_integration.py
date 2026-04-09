from notion_client import Client


def get_client(token):
    return Client(auth=token)

def find_databases(token):
    notion = get_client(token)
    response = notion.search(filter={"property": "object", "value": "database"})

    return response["results"] #type: ignore

def find_pages(token):
    notion = get_client(token)
    response = notion.search(filter={"property": "object", "value": "page"})
    return response["results"] #type: ignore

def create_database(token):
    notion = get_client(token)

    pages = find_pages(token)

    if not pages:
        return None

    parent_page_id = pages[0]["id"]

    db = notion.databases.create(
        parent={
                "type": "page_id",
                "page_id": parent_page_id
                },
        title=[{"text": {"content": "Tareas SynCal"}}],
        properties={
            "Name": {"title": {}},
            "Fecha": {"date": {}},
            "Categoria": {
                "select": {
                    "options": [
                        {"name": "Parcial", "color": "red"},
                        {"name": "Entrega", "color": "blue"}
                    ]
                }
            }
        }
    )

    return db["id"]

def ensure_schema(token, db_id):
    notion = get_client(token)

    notion.databases.update(
        database_id=db_id,
        properties={
            "Fecha": {"date": {}},
            "Categoria": {
                "select": {
                    "options": [
                        {"name": "Parcial", "color": "red"},
                        {"name": "Entrega", "color": "blue"}
                    ]
                }
            }
        }
    )



def setup_user_database(token):
    notion = get_client(token)

    dbs = find_databases(token)

    for db in dbs:
        db_id = db["id"]

        try:
            # probar acceso real
            notion.databases.retrieve(database_id=db_id)

            # si funciona → usarla
            ensure_schema(token, db_id)
            return db_id

        except Exception as e:
            print(" DB sin acceso:", db_id)

    #  si ninguna sirve → crear nueva
    print("🆕 Creando nueva DB...")
    return create_database(token)



def create_task(token, db_id, title, date, category):
    notion = get_client(token)

    return notion.pages.create(
        parent={"database_id": db_id},
        properties={
            "Name": {
                "title": [{"text": {"content": title}}]
            },
            "Fecha": {
                "date": {"start": date}
            },
            "Categoria": {
                "select": {"name": category.capitalize()}
            }
        }
    )