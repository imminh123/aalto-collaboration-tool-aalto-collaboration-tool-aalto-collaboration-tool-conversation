# Use an official Node.js runtime as a base image
FROM node:20

# Create and set the working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install app dependencies
RUN npm install

# Copy the application files to the working directory
COPY . .

# Expose the port that your app is running on
EXPOSE 8080

# Install pm2 globally
RUN npm install -g pm2

# Start the application using pm2
CMD ["pm2-runtime", "app.js"]
