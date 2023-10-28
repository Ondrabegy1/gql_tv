from fastapi import FastAPI

app = FastAPI()

print("All initialization is done ")

@app.get('/hello')
def hello():
   return {'hello': 'world'}
