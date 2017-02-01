.phony: all upload

all:
	@echo "run 'make upload' to upload"

upload:
	zip -r build.zip .
	aws lambda update-function-code --zip-file=fileb://build.zip --function-name=arn:aws:lambda:us-east-1:731088383874:function:Clodhopper
