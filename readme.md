uvicorn main:app --host="0.0.0.0" --reload
uvicorn main:app --host "0.0.0.0" --port 9776 --log-level "info"  --reload



docker build -t api_envios:1.0 .



en repair si busca por un responsable que ya no exista da errpr
deberia solo omitir si ya tiene responsable

no se esta enviando el nombre del responsable "mobil" cuando se aigna por qr