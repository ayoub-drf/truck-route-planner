# syntax=docker/dockerfile:1

# Build stage
FROM node:latest as builder
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app source code
COPY . .

# Build the production version (adjust if your build script is named differently)
RUN npm run build

# Production stage: use nginx to serve the static files
FROM nginx:stable-alpine
# Remove default content
RUN rm -rf /usr/share/nginx/html/*
# Copy the built files from the builder stage into nginx's web directory
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
