# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy TypeScript config and source
COPY tsconfig.json ./
COPY src ./src

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner
WORKDIR /app

# Environment
ENV NODE_ENV=production

# Copy built files and install production deps
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --only=production

# Expose port and start
EXPOSE 3000
CMD ["node", "dist/index.js"]