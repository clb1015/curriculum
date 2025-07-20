web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --max-requests 1000
release: python -c "import os; print('Release phase - checking environment')"
