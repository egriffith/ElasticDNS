SHELL := /bin/bash
PROJECT := elasticdns
ACCOUNT := 560684318507
REGION := us-east-1
REPOSITORY := $(ACCOUNT).dkr.ecr.$(REGION).amazonaws.com/$(PROJECT)
-VERSION := $(shell git log -1 --abbrev=12 --pretty=%h)

default:
	@echo "Available commands are:"
	@echo "1. build"
	@echo "2. login"
	@echo "3. push"
	@echo "4. release"
	@echo "5. install"
	@echo "6. clean"

.PHONY: default build login push install uninstall release

build:
	@VERSION ?= ${CODEBUILD_RESOLVED_SOURCE_VERSION}
	if [ -z $$VERSION]; then \
		${error "Fatal: VERSION was not set via either git log nor reading Codebuild env var."}; \
	fi
	@echo "Building Docker image..."
	@docker build --squash -q -t $(PROJECT):$(VERSION) .

login:
	@echo "Logging into Amazon Web Services Elastic Container Repository..."
	@$(shell aws ecr get-login --region $(REGION) --no-include-email)

push: build login
	@echo "Pushing image to repository..."
	@docker tag $(PROJECT):$(VERSION) $(REPOSITORY):$(VERSION)
	@docker push $(REPOSITORY)

install:
	@echo "Would install"

clean:
	@echo "Deleting all images related to ${PROJECT}
	@docker images -a | grep $(PROJECT) | awk '{print $3}' | xargs docker rmi -f

release:
	@echo "Would cut a release"