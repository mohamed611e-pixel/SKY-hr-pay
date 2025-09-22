# Hosting Guide for Payslip Project

## 1. Local Hosting

1. Clone or download the project to your local machine.
2. Create a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables for admin credentials (optional, defaults are set in code):
   - `ADMIN_USERNAME` (default: Ehab)
   - `ADMIN_PASSWORD_HASH` (default: sha256 hash of 'Ehab611_')
   
   Example (Linux/macOS):
   ```bash
   export ADMIN_USERNAME=Ehab
   export ADMIN_PASSWORD_HASH=<your_sha256_hash>
   ```
   
   Example (Windows CMD):
   ```cmd
   set ADMIN_USERNAME=Ehab
   set ADMIN_PASSWORD_HASH=<your_sha256_hash>
   ```
5. Run the Flask app:
   ```bash
   python payslip_site.py
   ```
6. Access the app locally at: [http://localhost:5000](http://localhost:5000)

---

## 2. Local Tunneling with ngrok

1. Download and install ngrok from [https://ngrok.com/download](https://ngrok.com/download).
2. Authenticate ngrok with your authtoken:
   ```bash
   ngrok config add-authtoken <your_authtoken>
   ```
3. Run your Flask app locally as above.
4. In a new terminal, run:
   ```bash
   ngrok http 5000
   ```
5. ngrok will provide a public URL forwarding to your local server, which you can share for testing.

---

## 3. Deploying on Render.com

1. Push your project code to a Git repository (GitHub, GitLab, etc.).
2. Create an account on [Render.com](https://render.com) and connect your Git repository.
3. Render will detect the `render.yaml` file and use it for deployment:
   - Runtime: python3
   - Build command: `pip install -r requirements.txt`
   - Start command: `python payslip_site.py`
4. Set environment variables `ADMIN_USERNAME` and `ADMIN_PASSWORD_HASH` securely in the Render dashboard.
5. Deploy the service. Render will build and start your app automatically.
6. Access your deployed app via the Render-provided URL.

---

## 4. Alternative Hosting Options

- You can deploy this Flask app on other platforms like Heroku, AWS Elastic Beanstalk, or DigitalOcean.
- The key steps are to install dependencies, set environment variables, and run the app with a WSGI server (e.g., Gunicorn).

---

## Notes

- Ensure the `uploaded_payslips` folder has proper write permissions on the host.
- For production, consider using a production-ready WSGI server like Gunicorn.
- Secure your admin credentials and never expose the password hash publicly.
