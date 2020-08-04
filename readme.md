uvicorn main:app --host="0.0.0.0" --reload
uvicorn main:app --host "0.0.0.0" --port 9777 --log-level "info"  --reload



docker build -t api_envios:1.0 .


