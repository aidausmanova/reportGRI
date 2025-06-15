# Step 1: Build the app using Node.js and Vite
FROM node:20-alpine as build

# Set working directory
WORKDIR /frontend

# Copy all source files
COPY ./ /frontend/

# Install dependencies
RUN npm install

# Build the app for production
RUN npm run build

# Step 2: Serve the app using a lightweight server (Nginx)
FROM nginx:alpine

# Copy built files from the build stage
COPY --from=build /frontend/dist /usr/share/nginx/html

# Expose port 80 for serving the app
EXPOSE 80

# Start the Nginx server
CMD ["nginx", "-g", "daemon off;"]
