from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn


app = FastAPI()


@app.get("/")
def read_root():
    html_content = '''
        <html>
            <head>
                <title>Some HTML in here</title>
                <script src="https://telegram.org/js/telegram-web-app.js"></script>
            </head>
            <body>
                <script>
                    let tg = window.Telegram.WebApp;
                    tg.sendData("Hello World!");
                    // tg.close();
                </script>
                <h1>Look ma! HTML!</h1>
            </body>
        </html>
    '''
    return HTMLResponse(content=html_content, status_code=200)


if __name__ == '__main__':
    uvicorn.run("server:app",
                host="0.0.0.0",
                port=8000,
                reload=True,
                ssl_keyfile="./localhost+2-key.pem",
                ssl_certfile="./localhost+2.pem")
