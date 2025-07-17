# frontend/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app

# รับค่า NEXT_PUBLIC_API_URL เป็น build-arg
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

COPY package*.json ./
RUN npm ci
COPY . .

# Build จะอ่าน NEXT_PUBLIC_API_URL จาก ENV ข้างบน
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/ ./
ENV NODE_ENV=production
EXPOSE 3000
CMD ["npm", "run", "start"]