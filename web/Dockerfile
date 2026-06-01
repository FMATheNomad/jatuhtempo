FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
COPY web/package.json web/package-lock.json* ./
RUN npm install --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY web/ .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=deps /app/node_modules ./node_modules
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
