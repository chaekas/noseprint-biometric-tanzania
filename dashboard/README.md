# Streamlit interface

Run from the repository root after installing requirements and starting the API:

```bash
streamlit run dashboard/streamlit_app.py
```

Set `NOSEPRINT_API_URL` if the API is not at `http://127.0.0.1:8000/api/v1`.

The browser camera component works on localhost. For an Android phone accessing the app over a LAN, browsers generally require a secure HTTPS origin for camera access. Configure a trusted HTTPS reverse proxy for remote-device testing; do not expose the development API or database directly to the public internet.
