import plantuml

def todo_app_architecture():
    with plantuml.PlantUML() as p:
        # include crowsfoot notation
        p.include('crowsfoot')
        p.actor("User")
        with p.activity("View Todos"):
            p.participant("TodoController")
            p.crowsfoot("Todo", "1..*", "uses", "0..1")
            p.database("TodoStore", "uses")
        with p.activity("Add Todo"):
            p.participant("TodoController")
            p.crowsfoot("Todo", "1", "uses", "0..1")
            p.database("TodoStore", "uses")
        with p.activity("Edit Todo"):
            p.participant("TodoController")
            p.crowsfoot("Todo", "1", "uses", "0..1")
            p.database("TodoStore", "uses")
        with p.activity("Delete Todo"):
            p.participant("TodoController")
            p.database("TodoStore", "uses")

    # generate the diagram
    p.create_png()

# call the function
todo_app_architecture()
