.phony: all upload

all:
	@echo "run 'make upload' to upload"

upload:
	zip -r build.zip .
	aws lambda update-function-code --zip-file=fileb://build.zip --function-name=$(LAMBDA_ARN)
