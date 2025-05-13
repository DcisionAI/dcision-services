FROM node:18-alpine
WORKDIR /app
 COPY package*.json ./
 # Install all dependencies (including dev for build)
 RUN npm install
 COPY . .
 # Build TypeScript and remove dev dependencies
 RUN npm run build && npm prune --production
CMD ["npm","start"]