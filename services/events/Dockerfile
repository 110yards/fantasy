FROM node:18-alpine

ENV NODE_ENV=production
WORKDIR /usr/src/app

COPY package.json package-lock.json ./
RUN npm install --production

COPY src/ .

CMD ["node", "index.js"]
