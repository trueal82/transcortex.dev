# transcortex.dev — static site container (unprivileged, no logging).
FROM nginxinc/nginx-unprivileged:alpine

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY site/ /usr/share/nginx/html/

# Bypass the stock entrypoint so the container logs nothing at all
# (the entrypoint scripts print startup chatter to stdout).
ENTRYPOINT ["nginx", "-g", "daemon off;"]

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1