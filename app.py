import boto3
import botocore.config
import json

from datetime import datetime

'''
This function generates a blog using the AWS Bedrock AI service.
It takes a blog topic as input and returns the generated blog content.
It uses the Llama 3 model from Meta AI, which is hosted on AWS Bedrock.
The function is designed to be used in an AWS Lambda environment, where it can be triggered by HTTP requests or other AWS services.
'''
def blog_generator_using_aws(blog_topic:str)-> str:
    # Create a Bedrock Runtime client in the AWS Region of your choice.
    # read-timeout and connect-timeout are set to 60 seconds. These variables are used to set the read and connect timeouts for the Bedrock Runtime client.
    """
   Generate a blog using AWS Bedrock AI service.
   read_timeout=60 sets the maximum time (in seconds) the client will wait for a complete response from AWS after sending a request.
   connect_timeout=60 sets the maximum time (in seconds) the client will wait to establish a connection to the AWS service. By setting both to 60 seconds, you are increasing the default timeouts, which can help prevent timeout errors when dealing with slow network connections or long-running AWS operations.
   """
    client = boto3.client("bedrock-runtime", region_name="us-east-1", config=botocore.config.Config(read_timeout=300, connect_timeout=60, retries={"max_attempts": 3}))

    # Define the model ID for the Bedrock AI model you want to use.
    model_id = "meta.llama3-8b-instruct-v1:0"

    # Define the prompt for the AI model.
    prompt = f"Generate a 200 word blog on the topic: {blog_topic}"

    # Embed the prompt in Llama 3's instruction format.
    formatted_prompt = formatted_prompt = f"""
    <|begin_of_text|><|start_header_id|>user<|end_header_id|>
    {prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """
    
    # Format the request payload using the model's native structure.
    native_request = {
    "prompt": formatted_prompt,
    
    # It is the maximum number of tokens that the model will generate in response to the prompt.
    "max_gen_len": 512,

    # The temperature parameter controls the randomness of the model's output.
    # A lower temperature (e.g., 0.5) makes the output more focused
    "temperature": 0.5,
}
    
    # Convert the native request to JSON.
    request = json.dumps(native_request)
    
    try:
        # Call the Bedrock AI model to generate the blog content.
        response = client.invoke_model(
            modelId=model_id,
            body=request,
            contentType="application/json",
            accept="application/json"
        )

    # Here AWS Lambda makes sure that all the logs are captured and sent to CloudWatch Logs.
    # If the model invocation fails, it will raise an exception.
    except Exception as e:
        # Handle any exceptions that occur during the model invocation.  
        print(f"Error in generating the Blog: {e}")
        return ""
    
    # Parse the response from the model.
    response_body = json.loads(response["body"].read().decode("utf-8"))
        
    # Extract the generated blog content from the response.
    blog_content = response_body["generation"]
        
    return blog_content


def save_blog_to_s3(s3_bucket: str, s3_key: str, blog_content: str):
    '''
    This function saves the generated blog content to an S3 bucket.
    It takes the S3 bucket name, S3 key (file path), and blog content as input.
    '''
    s3_client = boto3.client('s3')
    
    try:
        # Upload the blog content to the specified S3 bucket and key.
        s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=blog_content)
        print(f"Blog saved to s3://{s3_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving blog to S3: {e}")


'''
This function is the entry point for the AWS Lambda function.
It processes the incoming event, extracts the blog topic, and generates a blog using the AWS Bedrock AI service.
'''
def lambda_handler(event, context):
    event = json.loads(event['body'])

    # Extract the blog topic from the event.
    blog_topic = event.get("blog_topic")
    if not blog_topic:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Blog topic is required."})
        }
    
    # Generate the blog using the AWS Bedrock AI service.
    blog_content = blog_generator_using_aws(blog_topic) 
    if not blog_content:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to generate blog content."})
        }
    else:
        current_time = datetime.now().strftime("%H:%M:%S")
        # Save the generated blog content to an S3 bucket in the format "blog_<current_time>.txt" in the folder "blog-output".
        s3_key = f"blog-output/blog_{current_time}.txt"
        # Create a S3 Bucket to store the generated blog content.
        # You need to create the S3 bucket with the same name in your AWS account.
        s3_bucket = "aws-bedrock-blog-generator1"
        save_blog_to_s3(s3_bucket, s3_key, blog_content)
    
    # Return the generated blog content as the response.
    return{
        'statusCode':200,
        'body':json.dumps('Blog Generation is completed')
    }

# This code is designed to be run in an AWS Lambda environment, where it can be triggered by HTTP requests or other AWS services.