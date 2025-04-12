FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Copy the shell script
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8000

# Run the script to start both FastAPI and the scheduler
CMD ["/start.sh"]

EXPOSE 8000

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]