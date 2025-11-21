# Deployment Plan: Python Chat Application

This document outlines three methods for deploying the Python/FastAPI real-time chat application.

- **Option 1: Simple Uvicorn Server**: Best for quick testing or development environments.
- **Option 2: Standard Production Deployment**: The recommended approach for a robust, secure, and scalable setup using Gunicorn, Nginx, and Systemd.
- **Option 3: Containerized Deployment with Docker**: The most portable and scalable method, ideal for cloud-native environments.

---

## Prerequisites

Before you begin, you will need:
- A server (e.g., an AWS EC2 instance, DigitalOcean Droplet, or any Linux VM) with SSH access.
- A user with `sudo` privileges.
- Python 3.8+ and `pip` installed on the server.
- Git installed, to clone the application repository.
- A domain name pointing to your server's IP address (optional but highly recommended for production).

---

## Option 1: Simple Uvicorn Server (For Testing Only)

This approach runs the Uvicorn server directly and exposes it to the internet. It is **not recommended for production** due to a lack of security and robustness.

1.  **Connect to Your Server:**
    ```bash
    ssh your_user@your_server_ip
    ```

2.  **Clone Your Application:**
    ```bash
    git clone <your_repository_url>
    cd python-chat-app
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Uvicorn:**
    Bind the server to `0.0.0.0` to make it accessible from outside the local machine.
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

5.  **Configure Firewall:**
    Open port 8000 on your server's firewall to allow incoming traffic.
    ```bash
    sudo ufw allow 8000
    ```

You can now access your application at `http://<your_server_ip>:8000`. The process will stop as soon as you close the terminal.

---

## Option 2: Standard Production Deployment (Recommended)

This setup runs the application with Gunicorn as a process manager and uses Nginx as a high-performance reverse proxy. A Systemd service file ensures the application runs persistently.

### Step 1: Install Gunicorn
First, add `gunicorn` to your `requirements.txt` file and install it.

```
# requirements.txt
fastapi
uvicorn
websockets
jinja2
aiofiles
gunicorn  # Add this line
```
```bash
# On your server
pip install -r requirements.txt
```

### Step 2: Create a Systemd Service File
Systemd will manage the Gunicorn process, automatically starting it on boot and restarting it if it crashes.

Create a service file:
```bash
sudo nano /etc/systemd/system/chat-app.service
```

Paste the following configuration, adjusting `User` and `WorkingDirectory`:
```ini
[Unit]
Description=Gunicorn instance for the Python Chat App
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/your/python-chat-app
Environment="PATH=/path/to/your/python-chat-app/venv/bin"
ExecStart=/path/to/your/python-chat-app/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

[Install]
WantedBy=multi-user.target
```

### Step 3: Start and Enable the Service
```bash
sudo systemctl start chat-app
sudo systemctl enable chat-app
```

### Step 4: Install and Configure Nginx
Nginx will act as a reverse proxy, handling incoming HTTP/HTTPS and WebSocket traffic and forwarding it to your Gunicorn application.

1.  **Install Nginx:**
    ```bash
    sudo apt update
    sudo apt install nginx
    ```

2.  **Create an Nginx Server Block:**
    ```bash
    sudo nano /etc/nginx/sites-available/chat-app
    ```

3.  **Paste the following configuration.** This is crucial for correctly proxying WebSocket connections.
    ```nginx
    server {
        listen 80;
        server_name your_domain.com; # Replace with your domain or server IP

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /ws {
            proxy_pass http://127.0.0.1:8000/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "Upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /static {
            alias /path/to/your/python-chat-app/static;
        }
    }
    ```

4.  **Enable the Site and Restart Nginx:**
    ```bash
    sudo ln -s /etc/nginx/sites-available/chat-app /etc/nginx/sites-enabled
    sudo nginx -t # Test configuration
    sudo systemctl restart nginx
    ```

### Step 5: Configure Firewall and Add SSL (Optional)
```bash
sudo ufw allow 'Nginx Full' # Allow HTTP and HTTPS traffic
```
For SSL, use Certbot to get a free certificate from Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

---

## Option 3: Containerized Deployment with Docker (Advanced)

This method packages the application into a self-contained Docker image, making it highly portable.

### Step 1: Create a `Dockerfile`
Create a file named `Dockerfile` in your project root:
```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# Use gunicorn for production with uvicorn workers
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
```

### Step 2: Build the Docker Image
```bash
docker build -t python-chat-app .
```

### Step 3: Run the Container
You can run the container directly or use Docker Compose for a more structured deployment that includes a reverse proxy.

**To run the container directly:**
```bash
docker run -d -p 80:8000 --name chat-app python-chat-app
```
Access the app at `http://<your_server_ip>`.

**For a production setup using Docker Compose with Nginx:**
1.  Create an Nginx configuration file (`nginx.conf`).
2.  Create a `docker-compose.yml` file to orchestrate both your app container and an Nginx container. This setup provides better performance and security.
