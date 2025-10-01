# ---------- Build Stage ----------
FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies separately to leverage caching (context root already is project root in compose build)
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund

# Copy source
COPY . .

# Use adapter-node (assumes svelte.config.js updated accordingly)
RUN npm run build

# ---------- Runtime Stage ----------
FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production

# Copy only necessary build artifacts & production deps
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/build ./build
COPY --from=build /app/node_modules ./node_modules

# Expose port used by adapter-node (default 3000)
EXPOSE 3000

# Healthcheck (basic)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD node -e "fetch('http://localhost:3000').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"

CMD ["node", "build/index.js"]
