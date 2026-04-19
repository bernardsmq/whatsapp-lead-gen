FROM node:18-alpine AS builder

WORKDIR /app

# Copy files
COPY package*.json ./
RUN npm install

COPY . .

# Build with environment variables
ARG VITE_API_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_KEY

ENV VITE_API_URL=${VITE_API_URL:-http://localhost:8000}
ENV VITE_SUPABASE_URL=${VITE_SUPABASE_URL}
ENV VITE_SUPABASE_KEY=${VITE_SUPABASE_KEY}

RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/dist ./dist

ENV PORT=3000

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]
