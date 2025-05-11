# Use light Python Image and Low  Vulnerabilities
FROM python:3.12-alpine

# Set WORKDIR in Container
WORKDIR /app

# Copy The Current Dir Content To Container at /app  dir
COPY . . 

# Command to Run The App
CMD [ "python", "hivebox.py" ]