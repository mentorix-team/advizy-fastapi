bash```
Step 1: Clone the repository
git clone https://github.com/mentorix-team/advizy-fastapi.git
cd advizy-fastapi

bash```
#Step 2: Create virtual environment
python -m venv venv

bash```
source venv/bin/activate

bash```
venv\Scripts\activate

bash```
pip install --upgrade pip
pip install -r requirements.txt

bash```
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
GROQ_API_KEY=your_groq_api_key

bash```
uvicorn main:app --reload --host 0.0.0.0 --port 8000

##docker

bash```
docker pull sidhu18/advizy-fastapi:latest



bash```
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
GROQ_API_KEY=your_groq_api_key


bash```
run docker
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name advizy-fastapi \
  sidhu18/advizy-fastapi:latest

bash```
docker ps



###useful commands
🔧 Useful Docker Commands

Stop the container:

docker stop advizy-fastapi


Restart the container:

docker start advizy-fastapi


Remove the container:

docker rm -f advizy-fastapi
