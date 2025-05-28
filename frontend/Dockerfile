FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . ./
COPY docs ./
RUN npm run build
CMD cp -r build result_build