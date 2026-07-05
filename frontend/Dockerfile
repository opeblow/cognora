ARG NODE_VERSION=20-alpine

FROM node:${NODE_VERSION} AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --only=production

FROM node:${NODE_VERSION} AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_WS_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL
RUN npm run build

FROM node:${NODE_VERSION} AS runner
WORKDIR /app

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NODE_ENV=production

CMD ["node", "server.js"]
