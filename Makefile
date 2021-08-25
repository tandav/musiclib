.PHONY: frontend

clean:
	docker rmi piano_scales

run:
	git pull
	docker build -t piano_scales .
	docker run --rm -p 8001:8001 piano_scales

dev:
	uvicorn piano_scales.server:app --host 0.0.0.0 --port 8001 --reload

frontend:
	docker run -it --rm -v frontend:/home --workdir='/home' node bash
