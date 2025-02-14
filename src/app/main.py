from app.config import config
import uvicorn


def main():
    print("Starting API server...")
    uvicorn.run("app.api:app", host="0.0.0.0", port=config.API_PORT, reload=False)


if __name__ == "__main__":
    main()
