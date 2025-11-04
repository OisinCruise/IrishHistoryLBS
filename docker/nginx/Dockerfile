FROM nginx:1.25-alpine

WORKDIR /etc/nginx

# Install additional tools
RUN apk add --no-cache curl

# Create log directory
RUN mkdir -p /var/log/nginx && touch /var/log/nginx/access.log /var/log/nginx/error.log

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

LABEL maintainer="Oisin Cruise <oisincruise@gmail.com>" \
      description="Nginx reverse proxy for Irish Civil War LBS" \
      version="1.0.0"
