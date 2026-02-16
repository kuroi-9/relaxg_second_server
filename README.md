# RelaxG : The Second - Back
- [django](https://github.com/django/django) selected framework

## Objectives
The first iteration of [RelaxG](https://github.com/kuroi-9/relaxg) accomplished its objectives of manga images restoration, with an access over the internet. Thought, it was not enough to meet my reliability needs. Therefore, the second iteration of RelaxG is currently being developed to address these issues.
The issues addressed in the second iteration of RelaxG include:
- Adapted architecture to improve scalability and performance
- Enhanced error handling and logging mechanisms
- Implemented automated testing and (WIP) continuous integration pipelines

## Getting Started

### Prerequisites
- Docker engine with compose
- At least 1 available dedicated GPU with active CUDA support

### Installation
1. Clone the repository:
   ```bash
   https://github.com/kuroi-9/relaxg_second_server
   ```
   
2. Navigate to the project directory:
   ```bash
   cd relaxg_second_server
   ```

4. Fill the .env. If you want the server to be available in your VPN, fill the VPS_ID_ADRESS variable accordingly to the host IP on this network.

3. Start building, the result will be full prepared docker containers ready to serve to the client:
   ```bash
   docker compose -f docker-compose.yml up --force-recreate --build -d
   ```

4. The containers are running and usable. If you need to restart them, force recreate them but no need to rebuild:
   ```bash
   docker compose -f docker-compose.yml up --force-recreate -d
   ```

5. You may now start a shell in a new process associated to the **web** container just created :
   a) Make and run migrations
   b) Create a django superuser inside (You'll need one to use the app as intended)
   ```bash
   docker exec -it relaxg_second_server-web-1 sh
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

7. Open your browser and visit `http://<localhost/VPS_ID_ADRESS>:8000`

8. Setup the [frontend server](https://github.com/kuroi-9/relaxg_second_front)
