FROM node:22-alpine

WORKDIR /app
ENV NODE_ENV=production PORT=80 HOSTNAME=0.0.0.0

COPY .next/standalone ./
COPY .next/static ./.next/static
COPY data ./data

RUN test -f server.js && test -f data/entries.json

EXPOSE 80
CMD ["node", "server.js"]
