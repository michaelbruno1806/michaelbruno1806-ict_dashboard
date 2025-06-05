#Flask Dashboard

A web-based dashboard built with Flask to display system/device statuses from:
- Cisco Meraki
- Lycia
- CUCM (Cisco Unified Communications Manager)

Includes filtering by system and status, and secure API key management using `.env`.

#Features

- View real-time device data from Meraki, Lycia, and CUCM
- Filter devices by status (online/offline)
- Modern UI with responsive design
- Deployable on platforms like Render.com
- Secure secret management using `python-dotenv`

---

#Requirements

- Python 3.7+
- Flask
- Meraki SDK
- Requests
- Python-dotenv

Install all dependencies with:

```bash
pip install -r requirements.txt
