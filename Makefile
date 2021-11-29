build-and-push-pi:
	docker buildx build --platform linux/arm/v7 --push -t rameezk/solarman-mqtt .

run:
	python run.py