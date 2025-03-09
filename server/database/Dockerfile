FROM node:18.12.1-bullseye-slim

WORKDIR /app

# Copy package files and install dependencies first (for better caching)
COPY package.json .
RUN npm install

# Copy application files
COPY app.js .
COPY review.js .
COPY dealership.js .
COPY data/dealerships.json ./data/
COPY data/reviews.json ./data/

EXPOSE 3030

CMD [ "node", "app.js" ]