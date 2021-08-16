clean:
	docker rmi piano_scales

run:
	git pull
	docker build -t piano_scales .
	docker run --rm -p 8001:8001 piano_scales
