# fastapi_neon/main.py

from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated


from fastapi_neon import settings

from sqlmodel import Field, Session, SQLModel, create_engine, select

from fastapi import FastAPI, Depends, HTTPException



from fastapi import FastAPI


#table = true means create table of this class
class Todo(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)  #its optional if we dont give it DB create automatically

    content: str = Field(index=True)



# only needed for psycopg 3 - replace postgresql

# with postgresql+psycopg in settings.DATABASE_URL

connection_string = str(settings.DATABASE_URL).replace(

    "postgresql", "postgresql+psycopg"

)



# recycle connections after 5 minutes

# to correspond with the compute scale down

#sslmode (encrypt),
engine = create_engine(

    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300

)



def create_db_and_tables():

    SQLModel.metadata.create_all(engine)



# The first part of the function, before the yield, will

# be executed before the application starts

#lifespan : we want to execute something only on start

@asynccontextmanager

async def lifespan(app: FastAPI):

    print("Creating tables..")

    create_db_and_tables()

    yield

#title, servers this is api extra info
app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    # servers=[
    #     {
    #         #"url": "http://127.0.0.1:8001", # ADD NGROK URL Here Before Creating GPT Action
    #         "description": "Development Server"
    #     }
    #     ]
        )

#session is a memory in DB. We handle it to block extra connection creation
def get_session():
    with Session(engine) as session:
        yield session                   #we can return here also but return not memorize previous return values. 
                                       #yeild knows the previous return and can return it from memory directly


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
        session.add(todo)        #add data, commit and refresh it to get updated one
        session.commit()
        session.refresh(todo)
        return todo


@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    # Retrieve the todo by its ID
    todo = session.get(Todo, todo_id)
    
    # Check if the todo exists
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Delete the todo
    session.delete(todo)
    session.commit()
    
    return {"message": "Todo deleted successfully"}


    #Annotated is syntax to make any datatype
    #Depends class execute first then other code