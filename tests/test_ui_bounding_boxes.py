import pytest
import time
import requests

def test_streamlit_server_responsive():
    """Verify Streamlit web app server is running on http://localhost:8501."""
    try:
        res = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        assert res.status_code == 200, f"Health check returned status code {res.status_code}"
    except Exception as e:
        pytest.fail(f"Streamlit server health check failed: {str(e)}")

if __name__ == "__main__":
    test_streamlit_server_responsive()
    print("Streamlit server health check passed cleanly!")
