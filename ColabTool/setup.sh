# chmod +x setup.sh

docker build -t colab-docs .          
docker run -d -p 8080:8080 --name colab-docs colab-docs