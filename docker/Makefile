NAME := umwrg/hydra-json
TAG	:= $$(git rev-parse --short=8 HEAD)
IMG	:= ${NAME}:${TAG}
LATEST := ${NAME}:latest

build:
	@docker build -t ${IMG} . --no-cache
	@docker tag ${IMG} ${LATEST}
