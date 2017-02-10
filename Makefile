.phony: all zip upload

all:
	@echo "run 'make upload' to upload"

zip:
	zip -r --exclude="*.git*" build.zip .

upload: zip
	aws lambda update-function-code --zip-file=fileb://build.zip --function-name=$(LAMBDA_ARN)
