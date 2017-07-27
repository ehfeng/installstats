FROM python:3.6-onbuild
WORKDIR /app
COPY . /app
EXPOSE 80
CMD ["python", "install_stats/__init__.py"]
