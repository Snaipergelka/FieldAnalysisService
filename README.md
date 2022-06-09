# FieldAnalysisService

# About
The main idea of this project is to implement a service which can 
download satellite imagery, calculate NDVI and provide field NDVI image 
via REST API.

# How to start
To start this application you need to start docker compose by command: 
```
docker-compose up
```

# Supported features
The service provides an API you can interact with. 
You should preserve following API calls order:
- add field
- trigger download satellite data task
- trigger ndvi calculation task
- get ndvi image


# Implementation details
It is A FastAPI project, which consists of  
- Backend application `backend\`:
  - **Satellite data provider** `backend\app\satellite_data_providers` - this directory includes 
files `\satellite_data_client.py` and `\satellite_data_extractor.py` which consists of functions 
that get data from Copernicus open access hub api by footprint and extracts file paths to Red and NIR 
images 
  - **Analytics** `backend\app\analytics` - this directory includes file `\ndvi_counter.py` which consists
of functions which calculates NDVI, creates NDVI image and invokes function to save NDVI image
  - **File system** `backend\app\fs` - this directory includes `\file_system_storage.py` and 
`\image_saver.py` which consist of functions that provide path to saved satellite data and NDVi images
and save NDVI image
  - **File unzipper** `backend\app\utils.py` - this file includes function that unzips satellite data, 
delete zipped archive and saves unzipped file
- Database `backend\app\database` - we use PostgreSQL to store field id, field GeoJSON, path to NDVI image,
status of calculating NDVI image
- Celery tasks `backend\app\celery_tasks.py` - celery tasks are responsible for getting unzipped satellite data
and calculating NDVI and saving NDVI image

# Examples of use
## Add field to database and get field ID  
```
curl -X 'POST' \
  'http://127.0.0.1:8000/field/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "type": "string",
  "features": [
    {
      "type": "string",
      "geometry": {
        "coordinates": [
          "string",
          "string"
        ],
        "type": "string"
      },
      "properties": {},
      "id": "string",
      "bbox": [
        "string",
        "string",
        "string",
        "string"
      ]
    }
  ],
  "bbox": [
    "string",
    "string",
    "string",
    "string"
  ]
}'
```
You should pass GeoJSON in the following format 
```
{
  "type": "string",
  "features": [
    {
      "type": "string",
      "geometry": {
        "coordinates": [
          "string",
          "string"
        ],
        "type": "string"
      },
      "properties": {},
      "id": "string",
      "bbox": [
        "string",
        "string",
        "string",
        "string"
      ]
    }
  ],
  "bbox": [
    "string",
    "string",
    "string",
    "string"
  ]
}
```
## Get satellite image of the field
```
curl -X 'POST' \
  'http://127.0.0.1:8000/field/image' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "field_id": int
}'
```
You should pass JSON in the following format
```
{
    "field_id": int
}
```
## Calculate NDVI and save NDVI image to server file system
```
curl -X 'POST' \
  'http://127.0.0.1:8000/field/ndvi' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "field_id": int
}'
```
You should pass JSON in the following format
```
{
    "field_id": int
}
```
## Get NDVI image
```
curl -X 'GET' \
  'http://127.0.0.1:8000/field/ndvi/image?field_id=int' \
  -H 'accept: application/json'
```
## Delete field from database and file system
```
curl -X 'DELETE' \
  'http://127.0.0.1:8000/field/?field_id=int' \
  -H 'accept: application/json'
```


