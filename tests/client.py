def createGQLClient():

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import DBs

    def ComposeCString():
        return "sqlite+aiosqlite:///:memory:"
    
    DBs.ComposeConnectionString = ComposeCString

    import main
    
    client = TestClient(main.app, raise_server_exceptions=False)
    return client

