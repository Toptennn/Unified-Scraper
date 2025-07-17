# 1. Base image
FROM node:18-alpine

# 2. Set workdir
WORKDIR /app

# 3. Copy package.json & install deps
COPY package.json package-lock.json ./
RUN npm ci

# 4. Copy source
COPY . .

# 5. Build Next.js
RUN npm run build

# 6. Expose port
EXPOSE 3000

# 7. Start Next.js in production mode
CMD ["npm", "run", "start"]
