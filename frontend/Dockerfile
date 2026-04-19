FROM node:18-alpine AS builder

WORKDIR /app

# Copy files
COPY package*.json ./
RUN npm install

COPY . .

# Build
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/dist ./dist

ENV PORT=3000

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]
